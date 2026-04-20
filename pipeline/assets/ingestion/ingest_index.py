"""@bruin

name: raw.fear_greed
connection: bigquery-default

materialization:
  type: table
  strategy: append

secrets:
  - key: bigquery-default
    inject_as: bigquery-default

columns:
  - name: value
    type: integer
    description: Fear and Greed score from 0 (Extreme Fear) to 100 (Extreme Greed)
  - name: value_classification
    type: string
    description: Human-readable sentiment label (Extreme Fear, Fear, Neutral, Greed, Extreme Greed)
  - name: timestamp
    type: timestamp
    description: Date this index value corresponds to
  - name: ingested_at
    type: timestamp
    description: Timestamp when the pipeline ingested this record

@bruin"""

import requests
import pandas as pd
from datetime import datetime, timezone
from google.cloud import bigquery
from google.oauth2 import service_account
import os
import json

URL = "https://api.alternative.me/fng/"


def is_first_run(client: bigquery.Client, table_id: str) -> bool:
    try:
        query = f"SELECT COUNT(*) as total FROM `{table_id}`"
        result = client.query(query).result()
        total = list(result)[0].total
        return total == 0
    except Exception:
        return True


def fetch_fear_greed(limit: int) -> pd.DataFrame:
    params = {"limit": limit, "format": "json"}
    response = requests.get(URL, params=params)
    response.raise_for_status()
    data = response.json()["data"]

    df = pd.DataFrame(data)
    if df.empty:
        raise ValueError("No data returned from Fear & Greed API")

    df["value"] = df["value"].astype(int)
    df["timestamp"] = pd.to_datetime(df["timestamp"].astype(int), unit="s", utc=True)
    df = df.drop(columns=["time_until_update"], errors="ignore")
    df["ingested_at"] = datetime.now(timezone.utc)

    return df


def remove_duplicates(
    df: pd.DataFrame, client: bigquery.Client, table_id: str
) -> pd.DataFrame:
    try:
        query = f"SELECT DISTINCT timestamp FROM `{table_id}`"
        existing = client.query(query).result().to_dataframe()
        existing_timestamps = pd.to_datetime(existing["timestamp"], utc=True)
        df = df[~df["timestamp"].isin(existing_timestamps)]
    except Exception:
        pass
    return df


def materialize():
    connection = json.loads(os.environ["bigquery-default"])
    service_account_info = json.loads(connection["service_account_json"])

    credentials = service_account.Credentials.from_service_account_info(
        service_account_info
    )

    client = bigquery.Client(project=connection["project_id"], credentials=credentials)

    table_id = "raw.fear_greed"

    if is_first_run(client, table_id):
        print("First run detected — fetching full history")
        limit = 0
    else:
        print("Incremental run — fetching latest value only")
        limit = 1

    df = fetch_fear_greed(limit)
    df = remove_duplicates(df, client, table_id)

    if df.empty:
        print("No new records to insert")
        return df

    print(f"Inserting {len(df)} new records")
    print(
        f"Latest — value: {df['value'].iloc[0]} ({df['value_classification'].iloc[0]})"
    )
    return df
