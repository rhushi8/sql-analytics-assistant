import sqlite3

import pytest

from sql_engine import strip_sql_fences, generate_validated_sql, build_prompt


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE sales (id INTEGER, region TEXT, revenue INTEGER)")
    c.executemany(
        "INSERT INTO sales VALUES (?, ?, ?)",
        [(1, "North", 100), (2, "South", 200), (3, "North", 50)],
    )
    c.commit()
    return c


def make_llm(responses):
    """Return a stub llm() that yields queued responses and records calls/prompts."""
    calls = {"n": 0}
    prompts = []

    def _llm(prompt, temperature=0):
        prompts.append(prompt)
        i = min(calls["n"], len(responses) - 1)
        calls["n"] += 1
        return responses[i]

    _llm.calls = calls
    _llm.prompts = prompts
    return _llm


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("```sql\nSELECT 1\n```", "SELECT 1"),
        ("```\nSELECT 1\n```", "SELECT 1"),
        ("sql\nSELECT 1", "SELECT 1"),
        ("SELECT 1", "SELECT 1"),
    ],
)
def test_strip_sql_fences(raw, expected):
    assert strip_sql_fences(raw) == expected


def test_happy_path_returns_dataframe(conn):
    llm = make_llm(["SELECT region, SUM(revenue) AS total FROM sales GROUP BY region"])
    outcome = generate_validated_sql("revenue by region", "schema", conn, llm=llm)
    assert outcome.error is None
    assert outcome.dataframe is not None
    assert set(outcome.dataframe["region"]) == {"North", "South"}
    assert llm.calls["n"] == 1


def test_invalid_query_short_circuits(conn):
    llm = make_llm(["INVALID_QUERY"])
    outcome = generate_validated_sql("who won the world cup", "schema", conn, llm=llm)
    assert outcome.dataframe is None
    assert "cannot be answered" in outcome.error


def test_destructive_sql_is_rejected_without_execution(conn):
    llm = make_llm(["DROP TABLE sales"])
    outcome = generate_validated_sql("delete everything", "schema", conn, llm=llm)
    assert outcome.dataframe is None
    assert "SELECT" in outcome.error  # validator message
    assert llm.calls["n"] == 1  # never retried, never executed


def test_repair_loop_fixes_hallucinated_column(conn):
    # First response references a non-existent column; second is corrected.
    llm = make_llm(
        [
            "SELECT nonexistent_col FROM sales",
            "SELECT region FROM sales",
        ]
    )
    outcome = generate_validated_sql("regions", "schema", conn, llm=llm)
    assert outcome.error is None
    assert outcome.dataframe is not None
    assert llm.calls["n"] == 2  # one repair attempt used


def test_repair_exhausted_returns_error(conn):
    llm = make_llm(["SELECT bad FROM sales"])  # always bad
    outcome = generate_validated_sql("x", "schema", conn, llm=llm, max_repairs=1)
    assert outcome.dataframe is None
    assert "repair" in outcome.error.lower()
    assert llm.calls["n"] == 2  # initial + 1 repair


def test_build_prompt_without_history_has_no_conversation_block():
    prompt = build_prompt("count sales", "schema")
    assert "Conversation so far" not in prompt


def test_history_is_included_in_prompt(conn):
    history = [{"question": "revenue by region", "sql": "SELECT region, SUM(revenue) FROM sales GROUP BY region"}]
    llm = make_llm(["SELECT region FROM sales"])
    generate_validated_sql("now just the regions", "schema", conn, llm=llm, history=history)
    sent = llm.prompts[0]
    assert "Conversation so far" in sent
    assert "revenue by region" in sent  # prior question threaded in for follow-ups
