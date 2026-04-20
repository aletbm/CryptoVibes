"""@bruin

name: raw.prices
connection: bigquery-default

materialization:
  type: table
  strategy: append

secrets:
  - key: COINGECKO_API_KEY
    inject_as: COINGECKO_API_KEY

columns:
  - name: id
    type: string
    description: CoinGecko unique identifier (e.g. bitcoin)
  - name: symbol
    type: string
    description: Ticker symbol (e.g. btc)
  - name: name
    type: string
    description: Full coin name (e.g. Bitcoin)
  - name: image
    type: string
    description: URL of the coin logo image
  - name: current_price
    type: double
    description: Current price in USD
  - name: market_cap
    type: double
    description: Market capitalization in USD
  - name: market_cap_rank
    type: integer
    description: Global ranking position by market cap
  - name: fully_diluted_valuation
    type: double
    description: Valuation assuming full token supply in circulation
  - name: total_volume
    type: double
    description: Total trading volume in the last 24h in USD
  - name: high_24h
    type: double
    description: Highest price in the last 24h in USD
  - name: low_24h
    type: double
    description: Lowest price in the last 24h in USD
  - name: price_change_24h
    type: double
    description: Absolute price change in the last 24h in USD
  - name: price_change_percentage_24h
    type: double
    description: Percentage price change in the last 24h
  - name: market_cap_change_24h
    type: double
    description: Absolute market cap change in the last 24h in USD
  - name: market_cap_change_percentage_24h
    type: double
    description: Percentage market cap change in the last 24h
  - name: circulating_supply
    type: double
    description: Number of coins currently in circulation
  - name: total_supply
    type: double
    description: Total number of coins in existence
  - name: max_supply
    type: double
    description: Maximum number of coins that can ever exist
  - name: ath
    type: double
    description: All Time High price in USD
  - name: ath_change_percentage
    type: double
    description: Percentage distance from the ATH
  - name: ath_date
    type: timestamp
    description: Date when the ATH was reached
  - name: atl
    type: double
    description: All Time Low price in USD
  - name: atl_change_percentage
    type: double
    description: Percentage distance from the ATL
  - name: atl_date
    type: timestamp
    description: Date when the ATL was reached
  - name: roi
    type: double
    description: Return on investment (frequently null)
  - name: last_updated
    type: timestamp
    description: Timestamp of the last data update from CoinGecko
  - name: price_change_percentage_24h_in_currency
    type: double
    description: 24h percentage price change expressed in the base currency
  - name: ingested_at
    type: timestamp
    description: Timestamp when the pipeline ingested this record

@bruin"""

import requests
import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timezone
from google.cloud import bigquery

API_KEY = os.environ["COINGECKO_API_KEY"]

COINS = {
    "bitcoin": ("BTC", "Bitcoin", "BTC-USD"),
    "ethereum": ("ETH", "Ethereum", "ETH-USD"),
    "binancecoin": ("BNB", "BNB", "BNB-USD"),
    "solana": ("SOL", "Solana", "SOL-USD"),
    "ripple": ("XRP", "XRP", "XRP-USD"),
    "dogecoin": ("DOGE", "Dogecoin", "DOGE-USD"),
    "cardano": ("ADA", "Cardano", "ADA-USD"),
    "avalanche-2": ("AVAX", "Avalanche", "AVAX-USD"),
    "shiba-inu": ("SHIB", "Shiba Inu", "SHIB-USD"),
    "polkadot": ("DOT", "Polkadot", "DOT-USD"),
}

COIN_IDS = ",".join(COINS.keys())
HEADERS = {"x-cg-demo-api-key": API_KEY}

SCHEMA_COLUMNS = [
    "id",
    "symbol",
    "name",
    "image",
    "current_price",
    "market_cap",
    "market_cap_rank",
    "fully_diluted_valuation",
    "total_volume",
    "high_24h",
    "low_24h",
    "price_change_24h",
    "price_change_percentage_24h",
    "market_cap_change_24h",
    "market_cap_change_percentage_24h",
    "circulating_supply",
    "total_supply",
    "max_supply",
    "ath",
    "ath_change_percentage",
    "ath_date",
    "atl",
    "atl_change_percentage",
    "atl_date",
    "roi",
    "last_updated",
    "price_change_percentage_24h_in_currency",
    "ingested_at",
]


def is_first_run(client: bigquery.Client, table_id: str) -> bool:
    try:
        result = client.query(f"SELECT COUNT(*) as total FROM `{table_id}`").result()
        return list(result)[0].total == 0
    except Exception:
        return True


def fetch_historical_yfinance() -> pd.DataFrame:
    ingested_at = datetime.now(timezone.utc)
    all_rows = []

    for coin_id, (symbol, name, ticker) in COINS.items():
        print(f"  yfinance backfill: {symbol} ({ticker})...")
        try:
            df = yf.download(
                ticker,
                start="2018-02-01",
                end=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                interval="1d",
                auto_adjust=True,
                progress=False,
            )

            if df.empty:
                print(f"  Warning: no data for {ticker}, skipping")
                continue

            # yfinance puede devolver MultiIndex cuando se descarga un solo ticker
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df = df.reset_index()
            df.columns = [c.lower() for c in df.columns]

            for _, row in df.iterrows():
                close = float(row.get("close", 0))
                open_ = float(row.get("open", 0))
                all_rows.append(
                    {
                        "id": coin_id,
                        "symbol": symbol,
                        "name": name,
                        "image": None,
                        "current_price": close,
                        "market_cap": None,
                        "market_cap_rank": None,
                        "fully_diluted_valuation": None,
                        "total_volume": float(row.get("volume", 0)) * close,
                        "high_24h": float(row.get("high", 0)),
                        "low_24h": float(row.get("low", 0)),
                        "price_change_24h": close - open_,
                        "price_change_percentage_24h": ((close - open_) / open_ * 100)
                        if open_
                        else None,
                        "market_cap_change_24h": None,
                        "market_cap_change_percentage_24h": None,
                        "circulating_supply": None,
                        "total_supply": None,
                        "max_supply": None,
                        "ath": None,
                        "ath_change_percentage": None,
                        "ath_date": None,
                        "atl": None,
                        "atl_change_percentage": None,
                        "atl_date": None,
                        "roi": None,
                        "last_updated": pd.Timestamp(row["date"]).tz_localize("UTC")
                        if pd.Timestamp(row["date"]).tzinfo is None
                        else pd.Timestamp(row["date"]),
                        "price_change_percentage_24h_in_currency": (
                            (close - open_) / open_ * 100
                        )
                        if open_
                        else None,
                        "ingested_at": ingested_at,
                    }
                )

            print(f"    {len(df)} days retrieved")

        except Exception as e:
            print(f"  Error fetching {ticker}: {e}")
            continue

    result = pd.DataFrame(all_rows, columns=SCHEMA_COLUMNS)
    result["market_cap"] = result["market_cap"].astype("Float64")
    result["market_cap_rank"] = result["market_cap_rank"].astype("Int64")
    result["fully_diluted_valuation"] = result["fully_diluted_valuation"].astype(
        "Float64"
    )
    result["market_cap_change_24h"] = result["market_cap_change_24h"].astype("Float64")
    result["market_cap_change_percentage_24h"] = result[
        "market_cap_change_percentage_24h"
    ].astype("Float64")
    result["circulating_supply"] = result["circulating_supply"].astype("Float64")
    result["total_supply"] = result["total_supply"].astype("Float64")
    result["max_supply"] = result["max_supply"].astype("Float64")
    result["ath"] = result["ath"].astype("Float64")
    result["ath_change_percentage"] = result["ath_change_percentage"].astype("Float64")
    result["ath_date"] = pd.to_datetime(result["ath_date"], utc=True)
    result["atl"] = result["atl"].astype("Float64")
    result["atl_change_percentage"] = result["atl_change_percentage"].astype("Float64")
    result["atl_date"] = pd.to_datetime(result["atl_date"], utc=True)
    result["roi"] = result["roi"].astype("Float64")
    result["image"] = result["image"].astype("object")
    print(f"Historical backfill complete: {len(result)} total records")
    return result


def fetch_daily_coingecko() -> pd.DataFrame:
    """Snapshot diario completo con todos los campos via CoinGecko."""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": COIN_IDS,
        "order": "market_cap_desc",
        "price_change_percentage": "24h",
    }

    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    data = resp.json()

    df = pd.DataFrame(data)
    if df.empty:
        raise ValueError("No data returned from CoinGecko markets API")

    df["roi"] = df["roi"].apply(
        lambda x: x.get("percentage") if isinstance(x, dict) else None
    )
    df["ath_date"] = pd.to_datetime(df["ath_date"])
    df["atl_date"] = pd.to_datetime(df["atl_date"])
    df["last_updated"] = pd.to_datetime(df["last_updated"])
    df["ingested_at"] = datetime.now(timezone.utc)

    df = df.reindex(columns=SCHEMA_COLUMNS)
    print(f"Daily ingestion: {len(df)} records from CoinGecko")
    return df


def materialize() -> pd.DataFrame:
    client = bigquery.Client()
    table_id = "raw.prices"

    if is_first_run(client, table_id):
        print(
            "First run detected — running yfinance historical backfill from 2018-02-01"
        )
        return fetch_historical_yfinance()
    else:
        print("Incremental run — fetching daily snapshot from CoinGecko")
        return fetch_daily_coingecko()
