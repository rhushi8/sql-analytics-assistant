import streamlit as st
import pandas as pd
import plotly.express as px
import sqlparse
import time
import os

from db import get_connection, get_schema
from llm import query_llm
from validator import validate_sql


# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="SQL Analytics Assistant",
    page_icon="📊",
    layout="wide"
)

# ----------------------------
# SESSION STATE
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "suggested_query" not in st.session_state:
    st.session_state.suggested_query = ""


# ----------------------------
# DATABASE UPLOAD SECTION
# ----------------------------
st.sidebar.header("📂 Database")

uploaded_db = st.sidebar.file_uploader(
    "Upload SQLite Database (.db)",
    type=["db"]
)

if uploaded_db is not None:
    temp_db_path = "uploaded_database.db"
    with open(temp_db_path, "wb") as f:
        f.write(uploaded_db.getbuffer())

    conn = get_connection(temp_db_path)
    st.sidebar.success("Custom database loaded successfully!")
else:
    conn = get_connection()  # default database


# ----------------------------
# Smart Suggestions Engine
# ----------------------------
def generate_suggestions(df):
    suggestions = []

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

    if len(categorical_cols) == 1 and len(numeric_cols) == 1:
        suggestions.append(f"Show {numeric_cols[0]} trend over time")
        suggestions.append(f"Show percentage contribution of {categorical_cols[0]}")
        suggestions.append(f"Identify highest {categorical_cols[0]} by {numeric_cols[0]}")

    elif len(numeric_cols) == 1 and len(df.columns) == 1:
        suggestions.append(f"Show distribution of {numeric_cols[0]}")
        suggestions.append(f"Show average {numeric_cols[0]}")
        suggestions.append(f"Show top 5 records by {numeric_cols[0]}")

    elif len(categorical_cols) == 2 and len(numeric_cols) == 1:
        suggestions.append(f"Compare {numeric_cols[0]} across {categorical_cols[0]}")
        suggestions.append(f"Show trend of {numeric_cols[0]} by {categorical_cols[1]}")
        suggestions.append(f"Identify highest performing {categorical_cols[0]}")

    else:
        suggestions.append("Show all tables")
        suggestions.append("Show total revenue by category")
        suggestions.append("Show average value per customer")

    return suggestions


# ----------------------------
# Improved Chart Logic (Plotly)
# ----------------------------
def render_chart(df):
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    columns = df.columns.tolist()

    if len(columns) == 1 and len(numeric_cols) == 1:
        fig = px.histogram(df, x=numeric_cols[0], template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        return

    if len(columns) == 2 and len(numeric_cols) == 1:
        x_col = [col for col in columns if col not in numeric_cols][0]
        y_col = numeric_cols[0]
        fig = px.bar(df, x=x_col, y=y_col, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        return

    if len(columns) == 3 and len(numeric_cols) == 1:
        y_col = numeric_cols[0]
        cat_cols = [col for col in columns if col != y_col]
        fig = px.bar(
            df,
            x=cat_cols[0],
            y=y_col,
            color=cat_cols[1],
            barmode="group",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
        return

    st.info("No suitable automatic visualization found for this result structure.")


# ----------------------------
# HEADER
# ----------------------------
st.title("📊 SQL Analytics Assistant")
st.caption("Natural Language → SQL → Interactive Visualization → Business Insight")

st.divider()


# ----------------------------
# INPUT
# ----------------------------
default_query = st.session_state.suggested_query
query = st.text_input("💬 Ask a business question:", value=default_query)

st.session_state.suggested_query = ""


# ----------------------------
# MAIN LOGIC
# ----------------------------
if query:

    start_time = time.time()

    schema_info = get_schema(conn)

    # ----------------------------
    # STRICT GROUNDING PROMPT
    # ----------------------------
    prompt_sql = f"""
You are a STRICT SQL generator.

You MUST use ONLY the tables and columns listed below.
If a table or column is not listed, DO NOT use it.
If the question cannot be answered using the schema, return:
INVALID_QUERY

Available Database Schema:
{schema_info}

Rules:
1. Only use listed tables.
2. Only use listed columns.
3. Do NOT invent tables.
4. Do NOT invent columns.
5. Return ONLY raw SQL.
6. No explanation.
7. If unsure, return INVALID_QUERY.

User Question:
{query}
"""

    sql_query = query_llm(prompt_sql, temperature=0).strip()

    # Handle INVALID_QUERY
    if "INVALID_QUERY" in sql_query:
        st.error("The question cannot be answered using the current database schema.")
        st.stop()

    formatted_sql = sqlparse.format(sql_query, reindent=True, keyword_case="upper")

    # Validate SQL
    is_valid, error_message = validate_sql(sql_query)
    if not is_valid:
        st.error(error_message)
        st.stop()

    try:
        result = pd.read_sql_query(sql_query, conn)
        execution_time = round(time.time() - start_time, 3)

        # Save history
        st.session_state.history.append(query)

        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Rows", result.shape[0])
        col2.metric("Columns", result.shape[1])
        col3.metric("Execution Time (s)", execution_time)

        st.divider()

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📊 Results", "📈 Visualization", "🧠 SQL Explanation", "💼 Business Insight"]
        )

        with tab1:
            st.subheader("Generated SQL")
            st.code(formatted_sql, language="sql")
            st.dataframe(result, use_container_width=True)

            csv = result.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download CSV",
                csv,
                "query_results.csv",
                "text/csv"
            )

        with tab2:
            render_chart(result)

        with tab3:
            explanation_prompt = f"Explain this SQL query clearly:\n{sql_query}"
            explanation = query_llm(explanation_prompt, temperature=0.3)
            st.write(explanation)

        with tab4:
            insight_prompt = f"Explain this result in business terms:\n{result.to_string()}"
            insight = query_llm(insight_prompt, temperature=0.3)
            st.write(insight)

        # Smart Suggestions
        st.divider()
        st.subheader("💡 Suggested Next Questions")

        suggestions = generate_suggestions(result)
        cols = st.columns(len(suggestions))

        for i, suggestion in enumerate(suggestions):
            if cols[i].button(suggestion):
                st.session_state.suggested_query = suggestion
                st.rerun()

    except Exception as e:
        st.error(f"Execution failed: {e}")


# ----------------------------
# Query History
# ----------------------------
if st.session_state.history:
    st.divider()
    st.subheader("🕘 Query History (Last 5)")
    for item in reversed(st.session_state.history[-5:]):
        st.write(f"- {item}")
