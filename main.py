from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import json
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "stations"
SETTLEMENTS_PATH = os.path.join("settlements", "data.csv")

settlements_df = pd.read_csv(SETTLEMENTS_PATH)
settlement_coords = {
    row["settlement"].lower(): {
        "id": row["id"],
        "name": row["settlement"],
        "lat": row["latitude_dd"],
        "lon": row["longitude_dd"]
    }
    for _, row in settlements_df.iterrows()
}

with open("station_metadata.json", encoding="utf-8") as f:
    station_metadata = json.load(f)

# Map station names to metadata by name
metadata_by_name = {v['name'].lower(): {**v, 'id': k} for k, v in station_metadata.items()}

@app.get("/stations")
def get_stations():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    return [
        {"id": f.split("_")[1].split(".")[0], "name": station_metadata.get(f.split("_")[1].split(".")[0], {}).get("name", f)}
        for f in files
    ]

@app.get("/data/{station_id}")
def get_station_data(station_id: str):
    filepath = os.path.join(DATA_DIR, f"station_{station_id}.csv")
    if not os.path.exists(filepath):
        return {"error": "Station not found"}

    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y")
    df = df.dropna(subset=["avg_temp"])
    df = df.sort_values("date")

    return df[["date", "avg_temp"]].to_dict(orient="records")

@app.get("/mapdata/{year}")
def get_map_data(year: int):
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    result = []

    for f in files:
        try:
            filepath = os.path.join(DATA_DIR, f)
            df = pd.read_csv(filepath)
            df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y")
            df = df[df["date"].dt.year == year]
            df = df.dropna(subset=["avg_temp"])
            if df.empty:
                continue

            avg_temp = df["avg_temp"].astype(float).mean()

            station_id = f.split("_")[1].split(".")[0]
            station_name = station_metadata.get(station_id, {}).get("name")
            if not station_name:
                continue

            name_key = station_name.lower()
            if name_key not in settlement_coords:
                continue

            coords = settlement_coords[name_key]

            result.append({
                "id": coords['id'],
                "name": coords['name'],
                "lat": coords["lat"],
                "lon": coords["lon"],
                "avg_temp": round(avg_temp, 1)
            })
        except Exception:
            continue

    return result
