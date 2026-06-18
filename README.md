# SQL Analytics Assistant

Ask a business question in plain English and get back a validated SQL query, an automatic chart, a plain-English explanation, and a short business insight — without writing any SQL.

## Problem Statement
Most business users who need answers from a database can't write SQL, leaving them dependent on technical teams for routine questions. Bridging that gap with an LLM is risky on its own: left unconstrained, it hallucinates table and column names and can produce unsafe or destructive queries. The problem this project addresses: let non-technical users query data in plain English while guaranteeing that every executed query is valid, read-only, and safe.

## Key features
- **Natural language → SQL** with schema-aware prompting (real table and column names supplied as context).
- **Self-correcting generation** — if a generated query fails (e.g. a hallucinated column), the SQLite error is fed back to the LLM for a single corrective retry before giving up.
- **Conversational memory** — recent question/SQL turns are passed as context so follow-up questions ("now break that down by month") resolve correctly.
- **Safety guardrails** — SELECT-only (and CTEs), destructive keywords blocked on word boundaries, and stacked/multiple statements rejected *before* execution.
- **Automatic visualization** — chart chosen by result shape: 1 numeric column → histogram, 1 category + metric → bar chart, 2 categories + metric → grouped bar.
- **Explainability** — explains the generated SQL in plain English and turns the result into a business insight, degrading gracefully if the LLM is unavailable.

## How it works
```
plain-English question → schema-aware SQL generation → validation (SELECT-only) → execute on SQLite → (on error: one LLM repair attempt) → auto-visualize + explain + insight
```
SQL generation, validation, and repair live in `sql_engine.py`, independent of the UI so they can be unit-tested without Streamlit or a live LLM.

## Tech stack
Python · Streamlit · SQLite · Pandas · Plotly · SQLParse · Ollama / CodeLlama (local LLM)

## Quickstart
```bash
python -m venv venv
venv\Scripts\activate               # Windows
pip install -r requirements.txt
python database_setup.py            # builds the sample SQLite database (database.db)
streamlit run app.py
```
Requires a local Ollama model (e.g. CodeLlama) running for SQL generation.

## Tests
```bash
pip install -r requirements-dev.txt
pytest
```
Covers the SQL validator guardrails and the generation/validation/repair engine using a stub LLM and in-memory SQLite — no Ollama required.

## Project structure
- `app.py` — Streamlit interface
- `sql_engine.py` — SQL generation, validation, and one-shot repair (UI-independent, tested)
- `llm.py` — local LLM client (Ollama) with error handling
- `validator.py` — SQL safety validation
- `db.py` / `database_setup.py` — database access & sample data
- `database.db` — sample SQLite database (runs out of the box)

## Example
**Ask:** "For each region, show total revenue for January."
→ generates the JOIN + GROUP BY query, runs it, renders a bar chart, explains the SQL in plain English, and summarizes the business takeaway.
