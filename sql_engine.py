"""SQL generation, validation, and one-shot repair.

UI-independent so it can be unit-tested without Streamlit or a live LLM.
"""
import re
from typing import Callable, NamedTuple, Optional

import pandas as pd

from validator import validate_sql

PROMPT_TEMPLATE = """You are a STRICT SQL generator.

You MUST use ONLY the tables and columns listed below.
If a table or column is not listed, DO NOT use it.
If the question cannot be answered using the schema, return:
INVALID_QUERY

Available Database Schema:
{schema}

Rules:
1. Only use listed tables.
2. Only use listed columns.
3. Do NOT invent tables.
4. Do NOT invent columns.
5. Return ONLY raw SQL.
6. No explanation.
7. If unsure, return INVALID_QUERY.
{history}
User Question:
{query}
"""

REPAIR_SUFFIX = """
Your previous SQL failed with this SQLite error:
{error}

Previous SQL:
{sql}

Return ONLY the corrected raw SQL.
"""


class SQLOutcome(NamedTuple):
    sql: Optional[str]
    dataframe: Optional[pd.DataFrame]
    error: Optional[str]


def strip_sql_fences(text: str) -> str:
    """Remove markdown code fences / stray labels the LLM may wrap SQL in."""
    cleaned = text.strip()
    fence = re.match(r"^```[a-zA-Z]*\s*(.*?)\s*```$", cleaned, flags=re.DOTALL)
    if fence:
        cleaned = fence.group(1).strip()
    cleaned = re.sub(r"^\s*sql\s*\n", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def _format_history(history) -> str:
    """Render recent (question, sql) turns so the model can resolve follow-ups."""
    if not history:
        return ""
    lines = ["\nConversation so far (oldest first) — use it to resolve follow-up questions:"]
    for turn in history:
        lines.append(f"Q: {turn['question']}\nSQL: {turn['sql']}")
    return "\n".join(lines) + "\n"


def build_prompt(query, schema_info, history=None, prior_sql=None, prior_error=None) -> str:
    prompt = PROMPT_TEMPLATE.format(
        schema=schema_info, query=query, history=_format_history(history)
    )
    if prior_error:
        prompt += REPAIR_SUFFIX.format(error=prior_error, sql=prior_sql)
    return prompt


def generate_validated_sql(
    query: str,
    schema_info: str,
    conn,
    llm: Callable[..., str],
    history=None,
    max_repairs: int = 1,
) -> SQLOutcome:
    """Generate SQL, validate it, execute it, and repair once on a DB error.

    A hallucinated table/column surfaces as a SQLite error, which is fed back to
    the LLM for a single corrective retry before giving up. `history` is a list
    of prior {"question", "sql"} turns used as conversational context.
    """
    prior_sql = prior_error = None
    for _ in range(max_repairs + 1):
        prompt = build_prompt(query, schema_info, history, prior_sql, prior_error)
        sql = strip_sql_fences(llm(prompt, temperature=0))

        if "INVALID_QUERY" in sql:
            return SQLOutcome(None, None, "The question cannot be answered using the current database schema.")

        is_valid, message = validate_sql(sql)
        if not is_valid:
            return SQLOutcome(sql, None, message)

        try:
            return SQLOutcome(sql, pd.read_sql_query(sql, conn), None)
        except Exception as exc:  # noqa: BLE001 - surface DB errors to repair loop
            prior_sql, prior_error = sql, str(exc)

    return SQLOutcome(prior_sql, None, f"Query failed even after repair: {prior_error}")
