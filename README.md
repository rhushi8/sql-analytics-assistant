# 🚀 LLM-Powered SQL Analytics Assistant

An intelligent, schema-adaptive Natural Language to SQL analytics engine built with Streamlit and a local LLM.

---

## 🎯 Overview

This project converts natural language business questions into validated SQL queries, executes them on any uploaded SQLite database, and provides:

- 📊 Interactive visualizations
- 🧠 SQL explanations
- 💼 Business insights
- 💡 Context-aware follow-up suggestions

The system dynamically extracts database schema at runtime and strictly grounds LLM outputs to prevent hallucinated tables or columns.

---

## 🔥 Key Features

- ✅ Schema-adaptive SQL generation
- ✅ Works with any uploaded `.db` file
- ✅ Strict grounding to avoid hallucinated tables
- ✅ SQL validation layer
- ✅ Interactive Plotly visualizations
- ✅ Business interpretation using LLM
- ✅ Smart context-aware query suggestions
- ✅ Query history tracking
- ✅ CSV export

---

## 🧠 Architecture

User Question  
↓  
Schema Extraction  
↓  
Strict LLM SQL Generation  
↓  
SQL Validation  
↓  
Query Execution  
↓  
Visualization + Insight + Suggestions  

---

## 🗂 Example Database Used

Tested with:
- Sales database
- Ecommerce relational database

Tables include:
- customers
- products
- orders
- order_items

---

## 🛠 Tech Stack

- Python
- Streamlit
- SQLite
- Plotly
- Local LLM (Ollama)
- SQLParse

---

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
