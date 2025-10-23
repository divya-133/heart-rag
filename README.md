# MedBot RAG - Heart Health Assistant


**MedBot RAG** is a **Retrieval-Augmented Generation (RAG) system** built on PostgreSQL that enables users to interact with heart health data using natural language queries. The system provides both textual insights and interactive visualizations to help understand key metrics in cardiovascular health.

---

## 🔗 Live Demo

Access the deployed Streamlit app here: [MedBot RAG](https://heart-rag-cjueb5dvxztrbji6k74l4t.streamlit.app/)

---

## 🎯 Project Objective

The objective of this project was to build a RAG system capable of:

1. Understanding **natural language questions** about patient heart health.
2. Retrieving relevant data from a **PostgreSQL database**.
3. Providing **interpretable answers** and **interactive visualizations**.
4. Demonstrating the integration of **cloud database solutions (Neon)** and **frontend deployment (Streamlit Cloud)**.

**Data Source:** Kaggle [Heart Disease UCI Dataset](https://www.kaggle.com/ronitf/heart-disease-uci)

**Key Features:**
- Interactive chat interface for queries.
- Filtering based on metrics such as age, sex, cholesterol, diabetes, and chest pain type.
- Visualizations with **Plotly Express** (bar charts, pie charts, histograms).
- Retrieval-Augmented textual summaries using **SentenceTransformers embeddings**.
- Cloud-ready deployment via **Neon PostgreSQL** and **Streamlit Cloud**.

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/divya-133/heart-rag.git
cd heart-rag

