import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlparse
import json

from db import get_connection, get_schema
from llm import query_llm
from validator import validate_sql


# ----------------------------
# Simple Safe Chart Logic
# ----------------------------
def render_chart(df):
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    columns = df.columns.tolist()

    # Case 1: Single numeric column → Histogram
    if len(columns) == 1 and len(numeric_cols) == 1:
        plt.figure()
        plt.hist(df[numeric_cols[0]])
        plt.xlabel(numeric_cols[0])
        st.pyplot(plt)

        st.subheader("📊 Visualization Rationale")
        st.write("Histogram selected because the result contains a single numeric column representing a distribution.")
        return

    # Case 2: Two columns → Bar chart
    if len(columns) == 2 and len(numeric_cols) == 1:
        x_col = [col for col in columns if col not in numeric_cols][0]
        y_col = numeric_cols[0]

        plt.figure()
        plt.bar(df[x_col], df[y_col])
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        st.pyplot(plt)

        st.subheader("📊 Visualization Rationale")
        st.write("Bar chart selected because the result compares one numeric metric across categories.")
        return

    # Case 3: Three columns (one numeric + two categorical) → Grouped Bar
    if len(columns) == 3 and len(numeric_cols) == 1:
        y_col = numeric_cols[0]
        cat_cols = [col for col in columns if col != y_col]

        try:
            pivot_df = df.pivot(index=cat_cols[0], columns=cat_cols[1], values=y_col)
            pivot_df.plot(kind="bar")
            st.pyplot(plt)

            st.subheader("📊 Visualization Rationale")
            st.write("Grouped bar chart selected because one metric is compared across two categorical dimensions.")
        except:
            st.warning("Visualization skipped due to incompatible structure.")
        return

    st.warning("No suitable automatic visualization found for this result structure.")


# ----------------------------
# Setup
# ----------------------------
conn = get_connection()

st.title("🚀 Stable Modular LLM SQL Analytics Assistant")

question = st.text_input("Ask a business question:")

if question:

    schema_info = get_schema(conn)
    simple_question = question.lower()

    # ----------------------------
    # Deterministic Handling for Simple Revenue Query
    # ----------------------------
    if (
        "revenue" in simple_question
        and "group" not in simple_question
        and "by" not in simple_question
        and "where" not in simple_question
        and "category" not in simple_question
        and "month" not in simple_question
        and "region" not in simple_question
        and "join" not in simple_question
    ):
        sql_query = "SELECT revenue FROM sales;"
    else:
        prompt_sql = f"""
You are a precise SQL generator.

Database schema:
{schema_info}

Rules:
- Use ONLY listed tables and columns.
- Use JOIN only if required.
- Do NOT assume filters.
- Do NOT add WHERE unless specified.
- Return ONLY valid SELECT SQL.
- No explanations.

Question:
{question}
"""
        sql_query = query_llm(prompt_sql, temperature=0)

    formatted_sql = sqlparse.format(sql_query, reindent=True, keyword_case="upper")

    st.subheader("Generated SQL")
    st.code(formatted_sql, language="sql")

    # ----------------------------
    # SQL Explanation
    # ----------------------------
    explanation_prompt = f"""
Explain this SQL query clearly and simply:

{sql_query}
"""
    explanation = query_llm(explanation_prompt, temperature=0.3)

    st.subheader("🧠 SQL Explanation")
    st.write(explanation)

    # ----------------------------
    # Validate SQL
    # ----------------------------
    is_valid, error_message = validate_sql(sql_query)

    if not is_valid:
        st.error(error_message)
        st.stop()

    try:
        result = pd.read_sql_query(sql_query, conn)

        st.subheader("Query Result")
        st.dataframe(result)

        # ----------------------------
        # Stable Visualization
        # ----------------------------
        render_chart(result)

        # ----------------------------
        # Business Insight
        # ----------------------------
        insight_prompt = f"""
Explain this result in business terms:

{result.to_string()}
"""
        insight = query_llm(insight_prompt, temperature=0.3)

        st.subheader("Business Insight")
        st.write(insight)

    except Exception as e:
        st.error(f"Execution failed: {e}")