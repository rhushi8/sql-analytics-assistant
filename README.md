# SQL Analytics Assistant

Ask a business question in plain English and get back a validated SQL query, an automatic chart, a plain-English explanation, and a short business insight — without writing any SQL.

## Why this exists
The people who need answers from a database often can't write SQL, and letting an LLM write SQL unchecked is risky: it hallucinates table/column names and can issue destructive queries. This assistant keeps the LLM useful for language understanding while a validation layer keeps every generated query safe and correct.

## Key features
- **Natural language → SQL** with schema-aware prompting (real table and column names supplied as context).
- **Hybrid reliability** — a deterministic path handles simple queries; the LLM handles complex multi-table joins.
- **Safety guardrails** — SELECT-only, destructive operations blocked, and hallucinated/unknown columns rejected *before* execution.
- **Automatic visualization** — chart chosen by result shape: 1 numeric column → histogram, 1 category + metric → bar chart, 2 categories + metric → grouped bar.
- **Explainability** — explains the generated SQL in plain English and turns the result into a business insight.

## How it works
```
plain-English question → intent routing → schema-aware SQL generation → validation (SELECT-only + column check) → execute on SQLite → auto-visualize + explain + insight
```

## Tech stack
Python · Streamlit · SQLite · Pandas · Matplotlib · SQLParse · Ollama / CodeLlama (local LLM)

## Quickstart
```bash
python -m venv venv
venv\Scripts\activate               # Windows
pip install -r requirements.txt
python database_setup.py            # builds the sample SQLite database
streamlit run app.py
```
Requires a local Ollama model (e.g. CodeLlama) running for SQL generation.

## Project structure
- `app.py` — Streamlit interface
- `llm.py` — natural-language → SQL generation
- `validator.py` — SQL safety & column validation
- `db.py` / `database_setup.py` — database access & sample data
- `database.db` — sample SQLite database (runs out of the box)

## Example
**Ask:** "For each region, show total revenue for January."
→ generates the JOIN + GROUP BY query, runs it, renders a bar chart, explains the SQL in plain English, and summarizes the business takeaway.
