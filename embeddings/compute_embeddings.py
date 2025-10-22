import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import pickle

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load heart.csv
df = pd.read_csv(os.path.join(PROJECT_ROOT, "data", "heart.csv"))

# Create text column for embeddings
df['text'] = df.apply(
    lambda r: f"Age: {r['age']}, Chol: {r['chol']}, BP: {r['trestbps']}, Max HR: {r['thalach']}, CP: {r['cp']}, Target: {r['target']}",
    axis=1
)

# Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Compute embeddings
embeddings = model.encode(df['text'].tolist(), show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)

# Save embeddings and dataframe
np.save(os.path.join(PROJECT_ROOT, "embeddings.npy"), embeddings)
df.to_pickle(os.path.join(PROJECT_ROOT, "df.pkl"))

print("✅ Embeddings and df.pkl saved in project root")
