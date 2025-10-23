import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load DB_URI from .env
load_dotenv()
DB_URI = os.getenv("DB_URI")

# Connect to Neon
engine = create_engine(DB_URI)

# Load CSV
df = pd.read_csv("data/heart.csv")  # put full path if needed

# Upload to database
df.to_sql("patients_heart_metrics", engine, if_exists="replace", index=False)

print("✅ Data uploaded to Neon successfully!")
