import os
import pandas as pd
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime, timedelta, timezone
import dotenv

dotenv.load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID", "cryptovibes")
SA_FILE = os.getenv("GCP_SERVICE_ACCOUNT_FILE", "")


@st.cache_resource
def get_client() -> bigquery.Client:
    if SA_FILE and os.path.exists(SA_FILE):
        creds = service_account.Credentials.from_service_account_file(SA_FILE)
        return bigquery.Client(project=PROJECT_ID, credentials=creds)
    return bigquery.Client(project=PROJECT_ID)


def _run_query(sql: str) -> pd.DataFrame:
    client = get_client()
    return client.query(sql).to_dataframe()


def _date_filter(days: int) -> str:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).date()
    return str(cutoff)


@st.cache_data(ttl=3600)
def load_mart(days: int = 30) -> pd.DataFrame:
    cutoff = _date_filter(days)
    sql = f"""
    SELECT
        price_date, coin_id, symbol, coin_name,
        close_price_usd, avg_price_change_pct_24h,
        avg_volume_usd, avg_market_cap_usd,
        fg_value, fg_label, fg_category,
        is_fear, is_greed, price_vs_sentiment_alignment
    FROM `{PROJECT_ID}.marts.mart_crypto_vs_sentiment`
    WHERE price_date >= '{cutoff}'
    ORDER BY price_date ASC
    """
    df = _run_query(sql)
    df["price_date"] = pd.to_datetime(df["price_date"])
    return df


@st.cache_data(ttl=3600)
def load_fear_greed(days: int = 30) -> pd.DataFrame:
    cutoff = _date_filter(days)
    sql = f"""
    SELECT
        fg_date, fg_value, fg_label, fg_category,
        is_fear, is_greed, value_change_vs_prev_day
    FROM `{PROJECT_ID}.intermediate.int_daily_sentiment`
    WHERE fg_date >= '{cutoff}'
    ORDER BY fg_date ASC
    """
    df = _run_query(sql)
    df["fg_date"] = pd.to_datetime(df["fg_date"])
    return df


@st.cache_data(ttl=86400)
def load_mart_all() -> pd.DataFrame:
    """Todo el histórico disponible sin filtro de fecha."""
    sql = f"""
    SELECT
        price_date, coin_id, symbol, coin_name,
        close_price_usd, avg_price_change_pct_24h,
        avg_volume_usd, avg_market_cap_usd,
        fg_value, fg_label, fg_category,
        is_fear, is_greed, price_vs_sentiment_alignment
    FROM `{PROJECT_ID}.marts.mart_crypto_vs_sentiment`
    ORDER BY price_date ASC
    """
    df = _run_query(sql)
    df["price_date"] = pd.to_datetime(df["price_date"])
    return df


@st.cache_data(ttl=86400)
def load_fear_greed_all() -> pd.DataFrame:
    """Todo el histórico de Fear & Greed."""
    sql = f"""
    SELECT
        fg_date, fg_value, fg_label, fg_category,
        is_fear, is_greed, value_change_vs_prev_day
    FROM `{PROJECT_ID}.intermediate.int_daily_sentiment`
    ORDER BY fg_date ASC
    """
    df = _run_query(sql)
    df["fg_date"] = pd.to_datetime(df["fg_date"])
    return df
