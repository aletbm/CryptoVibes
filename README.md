<div align="center">
    <img width="400px" src="./docs/images/cryptovibes_logo.png">
    <h2>Crypto Sentiment Analytics Pipeline</h2>
    <strong>
        End-to-end batch pipeline for analyzing the relationship between cryptocurrency price movements and the Fear & Greed Index — from raw API ingestion to an interactive cloud dashboard.
    </strong>
    <br><br>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
    <img src="https://img.shields.io/badge/BigQuery-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white">
    <img src="https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white">
    <img src="https://img.shields.io/badge/Bruin-F57C00?style=for-the-badge&logoColor=white">
    <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white">
    <img src="https://img.shields.io/badge/uv-000000?style=for-the-badge&logo=astral&logoColor=white">
    <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white">
    <img src="https://img.shields.io/badge/Ruff-D7FF64?style=for-the-badge&logo=ruff&logoColor=black">
</div>

---


**Does the crypto market actually follow the Fear & Greed Index?**

CryptoVibes is an end-to-end batch data pipeline that ingests daily cryptocurrency prices (CoinGecko and yfinance) and market sentiment (Fear & Greed Index), transforms the data through a layered architecture in BigQuery, and visualizes insights through a Streamlit dashboard.

---

![Dashboard Overview](docs/images/price_vs_fg.png)

---

### Problem Statement

Cryptocurrency markets are highly influenced by investor sentiment, often driven by fear and greed rather than fundamentals.
The **Fear & Greed Index** attempts to measure this sentiment, but it is not always clear whether market prices actually move in alignment with it.

This project aims to analyze the relationship between **daily cryptocurrency price movements** and **market sentiment levels**, focusing on the top 10 cryptocurrencies by market capitalization.

To do this, the pipeline ingests:

* daily market prices from CoinGecko
* historical price data from yFinance
* daily sentiment scores from the Fear & Greed Index API

The data is processed through a layered data warehouse architecture and exposed through a dashboard that helps answer:

1. **How does price behavior evolve over time relative to market sentiment?**
2. **Which cryptocurrencies align or diverge the most from the Fear & Greed Index?**

This provides insights into whether market sentiment is a useful indicator of price behavior across different crypto assets.


---

## Architecture

![architecture](docs/images/architecture.png)

---

## Cloud Infrastructure

CryptoVibes runs entirely on managed cloud services — no self-hosted servers or local schedulers required.

### Google Cloud Platform — BigQuery

All data is stored and transformed in **BigQuery** on GCP. The four datasets (`raw`, `staging`, `intermediate`, `marts`) are provisioned automatically via Terraform IaC, ensuring reproducible, version-controlled infrastructure. The mart table is partitioned by `price_date` and clustered by `coin_id` and `fg_label` to minimize query costs and latency from the dashboard.

![Big Query](docs/images/bq.png)

### Bruin Cloud — Pipeline Orchestration

The ingestion and transformation pipeline runs on **[Bruin Cloud](https://getbruin.com)**, the managed execution environment for Bruin pipelines. The pipeline is scheduled to run daily, pulling fresh price and sentiment data from the APIs and propagating changes through all transformation layers automatically — no local Bruin CLI or manual trigger needed in production.

![Bruin Cloud](docs/images/bruin_cloud.png) -->

### Streamlit Community Cloud — Dashboard

The dashboard is deployed and publicly accessible on **[Streamlit Community Cloud](https://streamlit.io/cloud)**. It connects directly to BigQuery using a service account stored as a Streamlit secret, so the data always reflects the latest pipeline run.

🔗 [**Live Dashboard**](https://cryptovibes26.streamlit.app)

![Streamlit Cloud](docs/images/dashboard.png)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Cloud | Google Cloud Platform (BigQuery) |
| Infrastructure as Code | Terraform |
| Orchestration, Ingestion & Transformation | Bruin / Bruin Cloud |
| Dashboard | Streamlit / Streamlit Community Cloud |
| Environment management | uv |

---

## Dataset

| Source | Description | Update frequency |
|---|---|---|
| [CoinGecko API](https://docs.coingecko.com/v3.0.1/reference/coins-markets) | Current prices, market cap and volume for top 10 coins | Daily |
| [yFinance](https://pypi.org/project/yfinance/) | Full historical OHLCV price data for top 10 coins — used for backfill on first run | On demand (backfill) |
| [Alternative.me Fear & Greed Index](https://alternative.me/crypto/fear-and-greed-index/) | Market sentiment score (0–100) with full historical backfill | Daily |

---

## Pipeline Layers

```mermaid
erDiagram

    RAW_PRICES {
        string id PK "CLUSTER"
        datetime last_updated PK "PARTITION"
        float current_price
        float total_volume
    }

    RAW_FEAR_GREED {
        datetime timestamp PK "PARTITION"
        int value
        string value_classification
    }

    STG_PRICES {
        string id PK "CLUSTER"
        date price_date PK "PARTITION"
        float current_price
        float total_volume
    }

    STG_FEAR_GREED {
        date sentiment_date PK "PARTITION"
        int fear_greed_value
    }

    INT_DAILY_PRICES {
        string id PK "CLUSTER"
        date price_date PK "PARTITION"
        float avg_price
        float daily_volume
        float daily_return_pct
    }

    INT_DAILY_SENTIMENT {
        date sentiment_date PK "PARTITION"
        int fear_greed_value
    }

    MART_CRYPTO_VS_SENTIMENT {
        string id PK "CLUSTER"
        date date PK "PARTITION"
        float avg_price
        float daily_volume
        float daily_return_pct
        int fear_greed_value
    }

    RAW_PRICES ||--o{ STG_PRICES : transforms
    RAW_FEAR_GREED ||--|| STG_FEAR_GREED : transforms
    STG_PRICES ||--o{ INT_DAILY_PRICES : aggregates
    STG_FEAR_GREED ||--|| INT_DAILY_SENTIMENT : aggregates
    INT_DAILY_PRICES ||--o{ MART_CRYPTO_VS_SENTIMENT : joins
    INT_DAILY_SENTIMENT ||--o{ MART_CRYPTO_VS_SENTIMENT : joins
```

### Raw
Append-only ingestion of raw API responses. No transformations applied.

| Table | Description |
|---|---|
| `raw.prices` | Full historical OHLCV data backfilled from yFinance and daily price data for 10 cryptocurrencies from CoinGecko |
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
- yFinance is installed automatically as a dependency — no API key required

### 1. Clone the repository

```bash
git clone https://github.com/aletbm/cryptovibes.git
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

COINGECKO_API_KEY=your-coingecko-api-key
```

### 3. Install the environment

Dependencies are managed with [uv](https://docs.astral.sh/uv/). To sync all dependency groups and create the virtual environment:

```bash
make install
```

This runs `uv sync --all-groups` and resolves the lockfile (`uv.lock`) automatically. No need to create a virtualenv manually — uv handles it.

To run a one-off command inside the environment without activating it:

```bash
uv run <command>
```

### 4. Provision infrastructure with Terraform

CryptoVibes ships with a `Makefile` that wraps the Terraform commands so you don't have to `cd` into `infra/` manually.

**Deploy** — initializes the backend, validates config, and applies:

```bash
make infra-deploy
```

This runs the following Terraform steps internally:

```
terraform -chdir=infra/ init
terraform -chdir=infra/ validate
terraform -chdir=infra/ apply -auto-approve
```

It creates the four BigQuery datasets: `raw`, `staging`, `intermediate`, `marts`.

**Destroy** — tears down all provisioned resources:

```bash
make infra-destroy
```

> **Note:** Make sure your `.env` is filled in before running `make infra-deploy`. Terraform reads `PROJECT_ID` and `GCP_SERVICE_ACCOUNT_FILE` from the environment, which the Makefile exports automatically via the `include .env` directive.

### 5. Configure Bruin

Edit `.bruin.yml` with your GCP credentials. Bruin supports inline service account JSON via the `service_account_json` field — useful for cloud environments where a file path isn't available:

```yaml
default_environment: default

environments:
  default:
    connections:
      google_cloud_platform:
        - name: "bigquery-default"
          project_id: "your-gcp-project-id"
          service_account_json: |
            {
              "type": "service_account",
              "project_id": "your-gcp-project-id",
              "private_key_id": "your-private-key-id",
              "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
              "client_email": "your-sa@your-gcp-project-id.iam.gserviceaccount.com",
              "client_id": "your-client-id",
              "auth_uri": "https://accounts.google.com/o/oauth2/auth",
              "token_uri": "https://oauth2.googleapis.com/token",
              "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
              "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-sa%40your-gcp-project-id.iam.gserviceaccount.com",
              "universe_domain": "googleapis.com"
            }
          location: us-central1

      generic:
        - name: COINGECKO_API_KEY
          value: ${COINGECKO_API_KEY}
```

> **Tip:** The `service_account_json` inline approach is the recommended method for Bruin Cloud deployments. For local development you can alternatively use `service_account_file` pointing to the JSON file on disk.

> **Never commit `.bruin.yml` with real credentials.** Add it to `.gitignore` and use environment variable substitution (`${VAR}`) or Bruin Cloud's secret management for sensitive values.

### 6. Run the pipeline

```bash
make run-pipeline
```

This executes `scripts/run_bruin.bat` on Windows. On Linux / macOS, run directly:

```bash
bruin run pipeline --full-refresh --workers 1
```

On the first run, the assets automatically backfills the full historical dataset (~2000+ days).

### 7. Configure Streamlit secrets

Before launching the dashboard, create a `.streamlit/secrets.toml` file in the root of the project with your API credentials and GCP service account information:

```toml
PROJECT_ID = "your-gcp-project-id"
COINGECKO_API_KEY = "your-coingecko-api-key"

[GCP_SERVICE_ACCOUNT_FILE]
type = "service_account"
project_id = "your-gcp-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account-email"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-client-cert-url"
universe_domain = "googleapis.com"
```

This file is required so the Streamlit app can:

* authenticate with **Google BigQuery**
* access the **CoinGecko API**
* load data into the dashboard properly

Make sure the file path is:

```bash
.streamlit/secrets.toml
```

### 8. Launch the dashboard

Then you can launch the dashboard:

```bash
make run-app
```

This runs:

```bash
uv run streamlit run app/main.py
```

and opens the dashboard at:

```bash
http://localhost:8501
```

> **Important:** Never commit `.streamlit/secrets.toml` to version control.


---

## Makefile Reference

| Target | Description |
|---|---|
| `make install` | Sync all dependency groups with uv |
| `make lint` | Update pre-commit hooks and run linters |
| `make infra-deploy` | Init + validate + apply Terraform |
| `make infra-destroy` | Destroy all Terraform-managed resources |
| `make run-pipeline` | Run the Bruin pipeline |
| `make run-app` | Launch the Streamlit dashboard |

---

## Project Structure

```
CryptoVibes/
├── .github/
│   └── workflows/
│       └── ci.yml                        # CI pipeline
├── app/
│   ├── .streamlit/
│   │   └── config.toml
│   ├── components/
│   │   ├── comparison_chart.py
│   │   ├── kpi_cards.py
│   │   ├── price_chart.py
│   │   ├── sentiment_chart.py
│   │   └── sidebar.py
│   ├── config.py                         # Colors, coin labels, CSS injection
│   ├── data.py                           # BigQuery data fetching
│   ├── main.py                           # Streamlit entrypoint
│   └── requirements.txt
├── infra/                                # Terraform IaC
│   ├── main.tf                           # BigQuery dataset definitions
│   ├── providers.tf
│   └── variables.tf
├── pipeline/
│   ├── pipeline.yml                      # Bruin pipeline definition
│   └── assets/
│       ├── ingestion/
│       │   ├── ingest_prices.py          # CoinGecko daily ingestion asset
│       │   ├── ingest_prices_hist.py     # yFinance historical backfill asset
│       │   ├── ingest_index.py           # Fear & Greed ingestion asset
│       │   └── requirements.txt
│       ├── staging/
│       │   ├── stg_prices.sql
│       │   └── stg_fear_greed.sql
│       ├── intermediate/
│       │   ├── int_daily_prices.sql
│       │   └── int_daily_sentiment.sql
│       └── mart/
│           └── mart_crypto_vs_sentiment.sql
├── notebooks/                            # Exploratory analysis
│   ├── criptogecko.ipynb
│   └── fear_and_greed.ipynb
├── scripts/
│   ├── json_to_toml.py
│   ├── run_bruin.bat
│   └── tree.py
├── .bruin.yml                            # Bruin connections config
├── .env.example
├── .pre-commit-config.yaml
├── Makefile
├── pyproject.toml
├── uv.lock
└── README.md
```
---

## Data Sources & Attribution

- Current price data: [CoinGecko API](https://www.coingecko.com/en/api) — free Demo tier
- Historical price data: [yFinance](https://pypi.org/project/yfinance/) — free, no API key required
- Sentiment data: [Alternative.me Fear & Greed Index](https://alternative.me/crypto/fear-and-greed-index/) — free public API
