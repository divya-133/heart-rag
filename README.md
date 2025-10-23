# MedBot RAG - Retrieval-Augmented Generation for Heart Health Data

MedBot RAG is a **Retrieval-Augmented Generation (RAG)** system built on **PostgreSQL** healthcare data. Users can ask natural language questions about heart health, and the system retrieves meaningful insights, accompanied by interactive visualizations.

The system combines **data retrieval, embeddings, and similarity search** to provide accurate answers and charts for exploratory analysis.

---


## Features

- Natural language question answering on heart health data.
- Data filtering by age, sex, cholesterol, heart disease, diabetes, and other metrics.
- Automatic metric detection and grouping (e.g., by age, sex, chest pain type).
- Interactive **Plotly charts**:
  - Bar charts for numeric metrics.
  - Pie charts for categorical distributions.
  - Histograms for single metrics.
- Embedded semantic search using **FAISS** for contextual summaries.
- Fully deployed **Streamlit Web App**.

---

## Dataset

- Dataset source: [Kaggle Heart Disease Dataset](https://www.kaggle.com/ronitf/heart-disease-uci)
- Stored in **Neon PostgreSQL**.
- Columns include:

| Column      | Description                       |
|------------ |-----------------------------------|
| age         | Age of the patient                 |
| sex         | Gender (0: Women, 1: Men)         |
| cp          | Chest pain type (1-4)              |
| trestbps    | Resting blood pressure             |
| chol        | Serum cholesterol (mg/dL)          |
| fbs         | Fasting blood sugar > 120 mg/dL    |
| thalach     | Max heart rate achieved            |
| oldpeak     | ST depression induced by exercise  |
| thal        | Thalassemia type                   |
| ca          | Number of major vessels blocked    |
| target      | Heart disease presence (0 or 1)   |
| summary     | Text summary of patient's record  |

---

**Explanation:**

- **User**: Types a natural language question in the Streamlit app.  
- **RAG Backend**: Processes the question, filters data, generates embeddings, retrieves context, and produces answers.  
- **FAISS**: Fast similarity search for relevant text summaries.  
- **PostgreSQL**: Stores structured healthcare data and responds to SQL queries.  
- **Streamlit Frontend**: Displays textual answers, interactive charts, and small table previews.  

---

## Approach

1. **Data Upload**
   - CSV data (`heart.csv`) uploaded to **Neon PostgreSQL**.
   - Added derived columns like `age_bin` for grouping.

2. **RAG System**
   - Used **Sentence Transformers (`all-MiniLM-L6-v2`)** to generate embeddings for text summaries.
   - Built **FAISS index** for similarity search.
   - Implemented `analyze_question()`:
     - Detect metrics from question.
     - Apply filters on database table.
     - Group results if needed.
     - Generate textual answers and charts.

3. **Visualization**
   - Bar charts for numeric metrics grouped by age, sex, chest pain, or vessels.
   - Pie charts for categorical metrics.
   - Histograms for single metric distributions.

4. **Frontend**
   - Streamlit app with:
     - Chat-style interface.
     - Sticky header and input box.
     - Typing indicator and message history.
     - Display charts and table previews.

5. **Deployment**
   - Deployed on **Streamlit Cloud**.
   - Configured environment variable `DB_URI` to connect to **Neon PostgreSQL**.

---

## Deployment

- **Streamlit Cloud:** Hosts the interactive web app.
- **Neon PostgreSQL:** Cloud-hosted database for structured heart health data.
- **Environment variable `DB_URI`:** Securely stores the database connection string.
- **Deployed URL:** [MedBot RAG](https://heart-rag-cjueb5dvxztrbji6k74l4t.streamlit.app/)

---

## Technologies Used

- **Python 3.11**
- **Streamlit** – Frontend web app
- **Pandas** – Data processing
- **SQLAlchemy** – PostgreSQL integration
- **Neon PostgreSQL** – Cloud database
- **Sentence Transformers** – Text embeddings
- **FAISS** – Semantic search
- **Plotly Express** – Interactive data visualizations

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/divya-133/heart-rag.git
cd heart-rag



