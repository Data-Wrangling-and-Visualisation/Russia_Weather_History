from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from datetime import datetime

app = FastAPI()

# something for future
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "stations"  # folder with station CSVs

@app.get("/stations")
def get_stations():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    return [{"id": f.split("_")[1].split(".")[0], "name": f} for f in files]

@app.get("/data/{station_id}")
def get_station_data(station_id: str):
    filepath = os.path.join(DATA_DIR, f"station_{station_id}.csv")
    if not os.path.exists(filepath):
        return {"error": "Station not found"}
    
    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y")
    df = df.dropna(subset=["avg_temp"])
    df = df.sort_values("date")

    # Convert for D3.js
    return df[["date", "avg_temp"]].to_dict(orient="records")

@app.get("/missing/{station_id}")
def get_missing_data(station_id: str):
    filepath = os.path.join(DATA_DIR, f"station_{station_id}.csv")
    if not os.path.exists(filepath):
        return {"error": "Station not found"}
    
    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y")
    df["year"] = df["date"].dt.year

    missing_counts = df.groupby("year").apply(lambda x: x.isna().sum()).drop(columns=["date"])
    return missing_counts.reset_index().to_dict(orient="records")
