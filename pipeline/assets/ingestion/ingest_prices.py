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

FLOAT_COLUMNS = [
    "current_price",
    "market_cap",
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
    "atl",
    "atl_change_percentage",
    "roi",
    "price_change_percentage_24h_in_currency",
]

INT_COLUMNS = ["market_cap_rank"]

DATE_COLUMNS = [
    "ath_date",
    "atl_date",
    "last_updated",
    "ingested_at",
]

SCHEMA_COLUMNS = [
    "id",
    "symbol",
    "name",
    "image",
    *FLOAT_COLUMNS[:2],
    "market_cap_rank",
    *FLOAT_COLUMNS[2:],
    "ath_date",
    "atl_date",
    "last_updated",
    "ingested_at",
]


def enforce_schema(df: pd.DataFrame) -> pd.DataFrame:
    for col in FLOAT_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Float64")

    for col in INT_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)

    return df.reindex(columns=SCHEMA_COLUMNS)


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
        print(f"yfinance backfill: {symbol}")
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
                continue

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
                        "total_volume": float(row.get("volume", 0)) * close,
                        "high_24h": float(row.get("high", 0)),
                        "low_24h": float(row.get("low", 0)),
                        "price_change_24h": close - open_,
                        "price_change_percentage_24h": ((close - open_) / open_ * 100)
                        if open_
                        else None,
                        "price_change_percentage_24h_in_currency": (
                            (close - open_) / open_ * 100
                        )
                        if open_
                        else None,
                        "last_updated": row["date"],
                        "ingested_at": ingested_at,
                    }
                )

        except Exception as e:
            print(f"Error fetching {ticker}: {e}")

    return enforce_schema(pd.DataFrame(all_rows))


def fetch_daily_coingecko() -> pd.DataFrame:
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": COIN_IDS,
        "order": "market_cap_desc",
        "price_change_percentage": "24h",
    }

    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()

    df = pd.DataFrame(resp.json())
    if df.empty:
        raise ValueError("No data returned from CoinGecko")

    df["roi"] = df["roi"].apply(
        lambda x: x.get("percentage") if isinstance(x, dict) else None
    )
    df["ingested_at"] = datetime.now(timezone.utc)

    return enforce_schema(df)


def materialize() -> pd.DataFrame:
    client = bigquery.Client()
    table_id = "raw.prices"

    if is_first_run(client, table_id):
        print("First run: historical backfill")
        return fetch_historical_yfinance()

    print("Incremental run: CoinGecko snapshot")
    return fetch_daily_coingecko()
