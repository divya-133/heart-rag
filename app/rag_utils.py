import os
import re
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import plotly.express as px
from sentence_transformers import SentenceTransformer
import faiss

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
DB_URI = os.getenv("DB_URI")
engine = create_engine(DB_URI)

# -----------------------------
# Load embedding model
# -----------------------------
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# -----------------------------
# Label maps
# -----------------------------
SEX_MAP = {0: "Women", 1: "Men"}
THAL_MAP = {1: "Normal", 2: "Fixed defect", 3: "Reversible defect"}
CP_MAP = {1: "Typical angina", 2: "Atypical angina", 3: "Non-anginal", 4: "Asymptomatic"}
CA_MAP = {0: "0 vessels", 1: "1 vessel", 2: "2 vessels", 3: "3 vessels"}

COLUMN_MAPPING = {
    "age": ["age", "years", "old"],
    "chol": ["cholesterol", "chol"],
    "trestbps": ["blood pressure", "bp", "trestbps"],
    "thalach": ["heart rate", "thalach", "max heart rate", "max hr"],
    "oldpeak": ["st depression", "oldpeak"],
    "target": ["heart disease", "disease rate", "risk", "target"],
    "sex": ["sex", "gender", "men", "women"],
    "cp": ["chest pain", "cp", "angina"],
    "thal": ["thalassemia", "thal"],
    "ca": ["vessels", "ca", "blocked vessels"],
    "fbs": ["fasting blood sugar", "fbs", "diabetes"],
    "summary": ["summary", "report", "notes"]
}

NUMERIC_METRICS = ["age", "chol", "trestbps", "thalach", "oldpeak"]
PERCENT_METRICS = ["target", "fbs"]

# -----------------------------
# Age binning
# -----------------------------
def add_age_bins(df):
    bins = [0, 39, 49, 59, 120]
    labels = ["<40", "40-49", "50-59", "60+"]
    if "age_bin" not in df.columns:
        df["age_bin"] = pd.cut(df["age"], bins=bins, labels=labels, right=True)
    return df

# -----------------------------
# Load dataset
# -----------------------------
def load_full_dataset():
    df = pd.read_sql("SELECT * FROM patients_heart_metrics", engine)
    df = add_age_bins(df)
    return df

# -----------------------------
# Prepare embeddings
# -----------------------------
def prepare_embeddings(df, text_col='summary'):
    texts = df[text_col].fillna("").tolist()
    embeddings = embedding_model.encode(texts, convert_to_numpy=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index, texts

def retrieve_context(query, index, texts, k=3):
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_embedding, k)
    return [texts[i] for i in I[0]]

# -----------------------------
# Map labels
# -----------------------------
def map_label(group_col, val):
    if pd.isna(val): return str(val)
    if group_col == "sex": return SEX_MAP.get(int(val), str(val))
    if group_col == "thal": return THAL_MAP.get(int(val), str(val))
    if group_col == "cp": return CP_MAP.get(int(val), str(val))
    if group_col == "ca": return CA_MAP.get(int(val), str(val))
    if group_col == "age_bin": return str(val)
    return str(val)

# -----------------------------
# Apply filters
# -----------------------------
def apply_filters(df, question):
    q = question.lower()
    df_filtered = df.copy()

    # Heart disease filters
    if "with heart disease" in q or "have heart disease" in q:
        df_filtered = df_filtered[df_filtered["target"] == 1]
    elif "without heart disease" in q or "no heart disease" in q:
        df_filtered = df_filtered[df_filtered["target"] == 0]

    # Diabetes filters
    if "with diabetes" in q or "have diabetes" in q:
        df_filtered = df_filtered[df_filtered["fbs"] == 1]
    elif "without diabetes" in q or "no diabetes" in q:
        df_filtered = df_filtered[df_filtered["fbs"] == 0]

    # Cholesterol filters
    m = re.search(r"cholesterol\s*>\s*(\d+)", q)
    if m: df_filtered = df_filtered[df_filtered["chol"] > int(m.group(1))]
    m2 = re.search(r"cholesterol\s*<\s*(\d+)", q)
    if m2: df_filtered = df_filtered[df_filtered["chol"] < int(m2.group(1))]

    # Age filters
    age_range = re.search(r"(\d+)[-–](\d+)", q)
    if age_range:
        low, high = map(int, age_range.groups())
        df_filtered = df_filtered[(df_filtered["age"] >= low) & (df_filtered["age"] <= high)]
    elif re.search(r"under\s*(\d+)", q):
        val = int(re.search(r"under\s*(\d+)", q).group(1))
        df_filtered = df_filtered[df_filtered["age"] < val]
    elif re.search(r"over\s*(\d+)", q):
        val = int(re.search(r"over\s*(\d+)", q).group(1))
        df_filtered = df_filtered[df_filtered["age"] > val]

    # Very high heart rate filter (top 10%)
    if "very high heart rate" in q or "highest heart rate" in q:
        threshold = df["thalach"].quantile(0.9)
        df_filtered = df_filtered[df_filtered["thalach"] >= threshold]

    return df_filtered

# -----------------------------
# Detect metric
# -----------------------------
def detect_metric(question: str):
    q = question.lower()
    last_match = None
    for col, keywords in COLUMN_MAPPING.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", q):
                last_match = col
    if "chol" in q: return "chol"
    if "heart rate" in q or "thalach" in q: return "thalach"
    return last_match

# -----------------------------
# Detect grouping
# -----------------------------
def detect_group_by(question: str, metric: str):
    q = question.lower()
    if "by age" in q or "age group" in q or "age_bin" in q: 
        return "age_bin"
    if metric == "target":
        if any(k in q for k in ["men", "women", "sex", "gender"]): return "sex"
        if any(k in q for k in ["thal", "thalassemia"]): return "thal"
        if any(k in q for k in ["cp", "chest pain", "angina"]): return "cp"
        if any(k in q for k in ["ca", "vessels", "blocked"]): return "ca"
    return None

# -----------------------------
# Safe mapping function (never overwrite df)
# -----------------------------
def safe_map_column(df, col):
    # Return a mapped copy, do NOT modify original df
    if col == "sex":
        return df[col].map(SEX_MAP).fillna(df[col].astype(str))
    elif col == "cp":
        return df[col].map(CP_MAP).fillna(df[col].astype(str))
    elif col == "thal":
        return df[col].map(THAL_MAP).fillna(df[col].astype(str))
    elif col == "ca":
        return df[col].map(CA_MAP).fillna(df[col].astype(str))
    elif col == "age_bin":
        return df[col].astype(str)
    else:
        return df[col].astype(str)


# -----------------------------
# Safe generate_answer
# -----------------------------
def generate_answer(metric, df, group_by=None, question=None):
    if df.empty:
        return {"answer": "No data found for your query.", "fig": None}

    fig = None
    answer_lines = []

    if group_by and group_by in df.columns:
        grouped = df.groupby(group_by)[metric].mean().reset_index()

        # Use a mapped copy, do NOT overwrite original df
        display_group = safe_map_column(grouped, group_by)

        metric_values = grouped[metric].copy()
        if metric in PERCENT_METRICS or metric == "target":
            metric_values = (metric_values * 100).round(2)
            suffix = "%"
        else:
            metric_values = metric_values.round(2)
            suffix = ""

        for i in range(len(grouped)):
            value = metric_values[i]
            if metric == "oldpeak":
                answer_lines.append(f"{display_group[i]}: {value}")
            elif metric == "age":
                answer_lines.append(f"{display_group[i]}: {value} years")
            elif metric == "chol":
                answer_lines.append(f"{display_group[i]}: {value} mg/dL")
            elif metric == "trestbps":
                answer_lines.append(f"{display_group[i]}: {value} mmHg")
            elif metric == "thalach":
                answer_lines.append(f"{display_group[i]}: {value} bpm")
            else:
                answer_lines.append(f"{display_group[i]}: {value}{suffix}")

        if metric in NUMERIC_METRICS:
            fig = px.bar(
                x=display_group,
                y=metric_values,
                text=metric_values,
                color=display_group,
                labels={
                    "x": group_by.replace('_',' ').title(),
                    "y": metric.replace('_',' ').title()
                },
                title=f"{metric.replace('_',' ').title()} by {group_by.replace('_',' ').title()}"
            )
        else:
            fig = px.pie(
                names=display_group,
                values=metric_values,
                title=f"{metric.replace('_',' ').title()} by {group_by.replace('_',' ').title()}"
            )
        return {"answer": "\n".join(answer_lines), "fig": fig}

    # Single metric
    avg_value = df[metric].mean().round(2)
    metric_name = metric.replace("_", " ").title()

    if metric in NUMERIC_METRICS:
        if metric == "age":
            answer = f"Average {metric_name}: {avg_value} years"
        elif metric == "chol":
            answer = f"Average {metric_name}: {avg_value} mg/dL"
        elif metric == "trestbps":
            answer = f"Average {metric_name}: {avg_value} mmHg"
        elif metric == "thalach":
            answer = f"Average {metric_name}: {avg_value} bpm"
        elif metric == "oldpeak":
            answer = f"Average {metric_name}: {avg_value}"
        else:
            answer = f"Average {metric_name}: {avg_value}"
        fig = px.histogram(
            df,
            x=metric,
            nbins=20,
            color_discrete_sequence=['#636EFA'],
            title=f"Distribution of {metric_name}",
            labels={metric: metric_name}
        )
    else:
        answer = f"Overall {metric_name}: {avg_value}"

    return {"answer": answer, "fig": fig}


# -----------------------------
# Safe analyze_question
# -----------------------------
def analyze_question(question: str) -> dict:
    try:
        df_full = load_full_dataset()
        metric = detect_metric(question)
        if metric is None:
            return {"answer": "Sorry, I can only answer questions related to heart health and medical data.",
                    "fig": None}

        df_filtered = apply_filters(df_full, question)
        group_by = detect_group_by(question, metric)
        q_lower = question.lower()

        if "chest pain" in q_lower or "cp" in q_lower:
            if "oldpeak" in q_lower or "values" in q_lower:
                group_by = "cp"

        elif any(k in q_lower for k in ["men", "women", "sex", "gender"]):
            if any(k in q_lower for k in ["more common", "compare", "risk", "heart disease"]):
                group_by = "sex"
                metric = "target"

        return generate_answer(metric, df_filtered, group_by, question)

    except Exception as e:
        return {"answer": f"Error: {str(e)}", "fig": None}

