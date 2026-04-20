# CryptoVibes

> Does the crypto market actually follow the Fear & Greed Index?

CryptoVibes is an end-to-end batch data pipeline that ingests daily cryptocurrency prices (CoinGecko) and market sentiment (Fear & Greed Index), transforms the data through a layered architecture in BigQuery, and visualizes insights through a Streamlit dashboard.

---

## Problem Statement

The crypto market is driven by emotion. The Fear & Greed Index attempts to quantify that emotion — but does price actually follow sentiment? CryptoVibes answers this question by tracking the top 10 cryptocurrencies (BTC, ETH, BNB, SOL, XRP, DOGE, ADA, AVAX, SHIB, DOT) alongside daily sentiment data, exposing misalignments, patterns, and which coins react most strongly to fear or greed.

---

## Architecture

```
CoinGecko API          Fear & Greed API
      │                       │
      ▼                       ▼
 raw.prices            raw.fear_greed
      │                       │
      ▼                       ▼
staging.stg_prices   staging.stg_fear_greed
      │                       │
      ▼                       ▼
intermediate.int_daily_prices
intermediate.int_daily_sentiment
                │
                ▼
    marts.mart_crypto_vs_sentiment
                │
                ▼
        Streamlit Dashboard
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Cloud | Google Cloud Platform (BigQuery) |
| Infrastructure as Code | Terraform |
| Orchestration, Ingestion & Transformation | Bruin |
| Dashboard | Streamlit |
| Environment management | uv |

---

## Dataset

| Source | Description | Update frequency |
|---|---|---|
| [CoinGecko API](https://docs.coingecko.com/v3.0.1/reference/coins-markets) | Prices, market cap, volume for top 10 coins | Hourly |
| [Alternative.me Fear & Greed Index](https://alternative.me/crypto/fear-and-greed-index/) | Market sentiment score (0-100) with full historical backfill | Daily |

---

## Pipeline Layers

### Raw
Append-only ingestion of raw API responses. No transformations applied.

| Table | Description |
|---|---|
| `raw.prices` | Raw price data for 10 cryptocurrencies from CoinGecko |
| `raw.fear_greed` | Raw Fear & Greed Index values with full historical backfill on first run |

### Staging
Cleaned, renamed, and typed data. Duplicates removed. One row per entity per snapshot.

| Table | Description |
|---|---|
| `staging.stg_prices` | Cleaned prices — renamed columns, filtered nulls, typed fields |
| `staging.stg_fear_greed` | Deduplicated sentiment — one record per day, numeric category added |

### Intermediate
Business logic applied. Daily aggregations and window functions.

| Table | Description |
|---|---|
| `intermediate.int_daily_prices` | Daily OHLC-style aggregation per coin (open, close, high, low, avg) |
| `intermediate.int_daily_sentiment` | Daily sentiment with lag comparison vs previous day |

### Marts
Final analytics-ready table optimized for the dashboard. Partitioned and clustered for query performance.

| Table | Description |
|---|---|
| `marts.mart_crypto_vs_sentiment` | Joined daily prices + sentiment with alignment classification |

#### Partitioning & Clustering
`mart_crypto_vs_sentiment` is partitioned by `price_date` and clustered by `coin_id` and `fg_label`. This enables efficient filtering by date range and coin/sentiment in dashboard queries, reducing query costs and latency.

---

## Dashboard

The Streamlit dashboard answers two main questions:

**Tile 1 — Price vs Sentiment over time (temporal distribution)**
Line chart showing daily price change (%) and Fear & Greed value for a selected coin over a selected time range. Highlights misalignment periods.

**Tile 2 — Sentiment distribution by coin (categorical distribution)**
Bar/heatmap showing how often each coin aligned or misaligned with the prevailing sentiment category. Which coins are most contrarian?

---

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- [Bruin CLI](https://getbruin.com/docs/bruin/getting-started/introduction/installation.html)
- [Terraform](https://developer.hashicorp.com/terraform/install)
- A Google Cloud project with BigQuery enabled
- A GCP service account JSON key with BigQuery Admin permissions
- A [CoinGecko Demo API key](https://www.coingecko.com/en/api/pricing) (free)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/cryptovibes.git
cd cryptovibes
```

### 2. Configure environment variables

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

```dotenv
PROJECT_ID=your-gcp-project-id
GCP_SERVICE_ACCOUNT_FILE=/path/to/your/service-account.json
BQ_DATASET_RAW=raw
BQ_DATASET_STAGING=staging
BQ_DATASET_INTERMEDIATE=intermediate
BQ_DATASET_MARTS=marts
COINGECKO_API_KEY=your-coingecko-api-key
```

### 3. Provision infrastructure with Terraform

```bash
cd infra
terraform init
terraform apply
```

This creates the four BigQuery datasets: `raw`, `staging`, `intermediate`, `marts`.

### 4. Configure Bruin

Edit `.bruin.yml` with your GCP credentials:

```yaml
default_environment: default

environments:
  default:
    connections:
      google_cloud_platform:
        - name: "bigquery-default"
          project_id: "your-gcp-project-id"
          service_account_file: "/path/to/service-account.json"
          location: US
      generic:
        - name: PROJECT_ID
          value: your-gcp-project-id
        - name: BQ_DATASET_RAW
          value: raw
        - name: BQ_DATASET_STAGING
          value: staging
        - name: BQ_DATASET_INTERMEDIATE
          value: intermediate
        - name: BQ_DATASET_MARTS
          value: marts
        - name: COINGECKO_API_KEY
          value: your-coingecko-api-key
```

### 5. Run the pipeline

```bash
# Windows
scripts\run_bruin.bat

# Linux / macOS
bruin run pipeline --workers 1
```

On the first run, the Fear & Greed asset automatically backfills the full historical dataset (~2000+ days).

### 6. Run the dashboard

```bash
uv run streamlit run dashboard/app.py
```

---

## Project Structure

```
cryptovibes/
├── infra/                        # Terraform IaC
│   ├── main.tf                   # BigQuery dataset definitions
│   ├── providers.tf
│   └── variables.tf
├── pipeline/
│   ├── pipeline.yml              # Bruin pipeline definition
│   └── assets/
│       ├── ingestion/
│       │   ├── ingest_prices.py      # CoinGecko ingestion asset
│       │   ├── ingest_index.py       # Fear & Greed ingestion asset
│       │   └── requirements.txt
│       ├── staging/
│       │   ├── stg_prices.sql
│       │   └── stg_fear_greed.sql
│       ├── intermediate/
│       │   ├── int_daily_prices.sql
│       │   └── int_daily_sentiment.sql
│       └── mart/
│           └── mart_crypto_vs_sentiment.sql
├── dashboard/
│   └── app.py                    # Streamlit dashboard
├── notebooks/                    # Exploratory analysis
├── scripts/
│   └── run_bruin.bat
├── .bruin.yml                    # Bruin connections config
├── .env.example
└── README.md
```

---

## Evaluation Criteria Checklist (DE Zoomcamp 2026)

| Criterion | Implementation | Score |
|---|---|---|
| Problem description | Clearly described: does sentiment predict crypto price movements? | 4/4 |
| Cloud | GCP BigQuery + Terraform IaC | 4/4 |
| Data ingestion (batch) | Bruin end-to-end DAG: ingestion → staging → intermediate → mart | 4/4 |
| Data warehouse | BigQuery with partitioning (`price_date`) and clustering (`coin_id`, `fg_label`) | 4/4 |
| Transformations | Bruin SQL assets across 3 transformation layers | 4/4 |
| Dashboard | 2 tiles: temporal line chart + categorical sentiment distribution | 4/4 |
| Reproducibility | Full instructions, `.env.example`, Terraform, Bruin config | 4/4 |

---

## Data Sources & Attribution

- Price data: [CoinGecko API](https://www.coingecko.com/en/api) — free Demo tier
- Sentiment data: [Alternative.me Fear & Greed Index](https://alternative.me/crypto/fear-and-greed-index/) — free public API

---

## License

MIT
