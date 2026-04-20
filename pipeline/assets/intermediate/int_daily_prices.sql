/* @bruin

name: intermediate.int_daily_prices
type: bq.sql
depends:
  - staging.stg_prices

materialization:
  type: table
  strategy: create+replace
  partition_by: price_date
  cluster_by:
    - coin_id

columns:
  - name: price_date
    type: date
    description: Date of the price snapshot
    checks:
      - name: not_null

  - name: coin_id
    type: string
    description: CoinGecko unique identifier
    checks:
      - name: not_null

  - name: symbol
    type: string
    description: Ticker symbol in uppercase

  - name: coin_name
    type: string
    description: Full coin name

  - name: open_price_usd
    type: float64
    description: First recorded price of the day in USD

  - name: close_price_usd
    type: float64
    description: Last recorded price of the day in USD

  - name: high_price_usd
    type: float64
    description: Maximum price recorded during the day in USD

  - name: low_price_usd
    type: float64
    description: Minimum price recorded during the day in USD

  - name: avg_price_usd
    type: float64
    description: Average price across all snapshots of the day in USD

  - name: avg_price_change_pct_24h
    type: float64
    description: Average 24h price change percentage across all snapshots of the day

  - name: avg_volume_usd
    type: float64
    description: Average trading volume across all snapshots of the day in USD

  - name: avg_market_cap_usd
    type: float64
    description: Average market cap across all snapshots of the day in USD

  - name: snapshot_count
    type: int64
    description: Number of price snapshots recorded during the day

@bruin */

WITH ordered AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY ingested_date, coin_id
            ORDER BY ingested_at ASC
        ) AS rn_asc,
        ROW_NUMBER() OVER (
            PARTITION BY ingested_date, coin_id
            ORDER BY ingested_at DESC
        ) AS rn_desc
    FROM staging.stg_prices
),

open_price AS (
    SELECT ingested_date, coin_id, current_price_usd AS open_price_usd
    FROM ordered
    WHERE rn_asc = 1
),

close_price AS (
    SELECT ingested_date, coin_id, current_price_usd AS close_price_usd
    FROM ordered
    WHERE rn_desc = 1
),

aggregated AS (
    SELECT
        ingested_date                       AS price_date,
        coin_id,
        ANY_VALUE(symbol)                   AS symbol,
        ANY_VALUE(coin_name)                AS coin_name,
        MAX(high_24h_usd)                   AS high_price_usd,
        MIN(low_24h_usd)                    AS low_price_usd,
        AVG(current_price_usd)              AS avg_price_usd,
        AVG(price_change_pct_24h)           AS avg_price_change_pct_24h,
        AVG(total_volume_usd)               AS avg_volume_usd,
        AVG(market_cap_usd)                 AS avg_market_cap_usd,
        COUNT(*)                            AS snapshot_count
    FROM staging.stg_prices
    GROUP BY ingested_date, coin_id
)

SELECT
    a.price_date,
    a.coin_id,
    a.symbol,
    a.coin_name,
    o.open_price_usd,
    c.close_price_usd,
    a.high_price_usd,
    a.low_price_usd,
    a.avg_price_usd,
    a.avg_price_change_pct_24h,
    a.avg_volume_usd,
    a.avg_market_cap_usd,
    a.snapshot_count
FROM aggregated a
LEFT JOIN open_price  o ON a.price_date = o.ingested_date AND a.coin_id = o.coin_id
LEFT JOIN close_price c ON a.price_date = c.ingested_date AND a.coin_id = c.coin_id
