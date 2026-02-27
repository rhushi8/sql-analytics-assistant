# 🚀 SQL Analytics Assistant

An AI-powered modular SQL analytics assistant that converts natural language questions into executable SQL queries, explains the query logic, generates business insights, and automatically visualizes results.

Built using a hybrid deterministic + LLM architecture for stability, correctness, and production-style reliability.

---

## 🔥 Features

- 🧠 Natural Language → SQL conversion  
- 🔗 Multi-table JOIN reasoning  
- 📊 Automatic visualization (Histogram, Bar, Grouped Bar)  
- 📖 SQL Explanation Mode  
- 💼 Business Insight generation  
- 🛡 SQL validation guardrails  
- ⚙ Deterministic handling for simple queries  
- 🏗 Modular architecture  
- 🖥 Fully local LLM support (Ollama / CodeLlama compatible)

---

## 🏗 Architecture Overview

User Question  
↓  
Intent Handling (Deterministic Layer)  
↓  
LLM SQL Generation  
↓  
SQL Validation  
↓  
Query Execution  
↓  
Automatic Visualization  
↓  
SQL Explanation + Business Insight  

This system combines:
- Rule-based deterministic logic (for simple queries)
- LLM reasoning (for complex multi-table joins)
- Validation safeguards to prevent hallucinated SQL
- Safe visualization rendering to avoid runtime crashes

---

## 🛠 Tech Stack

- Python  
- Streamlit  
- SQLite  
- Pandas  
- Matplotlib  
- SQLParse  
- Local LLM (via Ollama – CodeLlama)

---

## 📂 Project Structure

```
sql-analytics-assistant/
│
├── app.py
├── db.py
├── llm.py
├── validator.py
├── database_setup.py
├── requirements.txt
└── README.md
```

---

## 🚀 How It Works

### 1️⃣ Natural Language to SQL
The assistant translates business questions into valid SQL queries using schema-aware prompting.

### 2️⃣ SQL Guardrails
- Ensures only SELECT statements are executed  
- Prevents invalid or hallucinated columns  
- Blocks destructive queries  

### 3️⃣ Automatic Visualization
Based on result structure:
- 1 numeric column → Histogram  
- 1 category + 1 metric → Bar chart  
- 2 categories + 1 metric → Grouped bar chart  

### 4️⃣ Explainable AI
The system explains:
- Why JOIN was used  
- Why GROUP BY was needed  
- How aggregation works  

### 5️⃣ Business Interpretation
Converts raw SQL results into executive-level business insights.

---

## 📊 Example

### Input:
```
For each region, show total revenue for Jan.
```

### Generated SQL:
```sql
SELECT region,
       SUM(revenue) AS total_revenue
FROM sales
JOIN customers ON sales.customer_id = customers.customer_id
WHERE month = 'Jan'
GROUP BY region;
```

### Output:
- Bar chart visualization
- SQL explanation
- Business insight summary

---

## ⚡ Installation

### 1️⃣ Clone Repository
```
git clone https://github.com/yourusername/sql-analytics-assistant.git
cd sql-analytics-assistant
```

### 2️⃣ Create Virtual Environment
```
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```
pip install -r requirements.txt
```

### 4️⃣ Run Database Setup
```
python database_setup.py
```

### 5️⃣ Run Application
```
streamlit run app.py
```

---

## 🎯 Future Improvements

- Conversational memory support  
- Advanced visualization intelligence  
- Cloud deployment  
- Real enterprise dataset integration  

---


