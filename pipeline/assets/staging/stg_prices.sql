/* @bruin

name: staging.stg_prices
type: bq.sql
depends:
  - raw.prices

materialization:
  type: table
  strategy: create+replace
  partition_by: ingested_date
  cluster_by:
    - coin_id


columns:
  - name: coin_id
    type: string
    description: CoinGecko unique identifier (e.g. bitcoin)
    checks:
      - name: not_null
      - name: unique_combination
        blocking: false

  - name: symbol
    type: string
    description: Ticker symbol in uppercase (e.g. BTC)
    checks:
      - name: not_null

  - name: coin_name
    type: string
    description: Full coin name (e.g. Bitcoin)
    checks:
      - name: not_null

  - name: current_price_usd
    type: double
    description: Current price in USD
    checks:
      - name: not_null

  - name: market_cap_usd
    type: double
    description: Market capitalization in USD

  - name: market_cap_rank
    type: integer
    description: Global ranking position by market cap

  - name: total_volume_usd
    type: double
    description: Total trading volume in the last 24h in USD

  - name: high_24h_usd
    type: double
    description: Highest price in the last 24h in USD

  - name: low_24h_usd
    type: double
    description: Lowest price in the last 24h in USD

  - name: price_change_24h_usd
    type: double
    description: Absolute price change in the last 24h in USD

  - name: price_change_pct_24h
    type: double
    description: Percentage price change in the last 24h

  - name: market_cap_change_pct_24h
    type: double
    description: Percentage market cap change in the last 24h

  - name: circulating_supply
    type: double
    description: Number of coins currently in circulation

  - name: max_supply
    type: double
    description: Maximum number of coins that can ever exist

  - name: roi_pct
    type: double
    description: Return on investment percentage (null when unavailable)

  - name: last_updated_at
    type: timestamp
    description: Timestamp of the last data update from CoinGecko

  - name: ingested_date
    type: date
    description: Date when the pipeline ingested this record
    checks:
      - name: not_null

  - name: ingested_at
    type: timestamp
    description: Full timestamp when the pipeline ingested this record
    checks:
      - name: not_null

@bruin */

SELECT
    id                                          AS coin_id,
    UPPER(symbol)                               AS symbol,
    name                                        AS coin_name,
    current_price                               AS current_price_usd,
    SAFE_CAST(market_cap AS FLOAT64)            AS market_cap_usd,
    SAFE_CAST(market_cap_rank AS INT64)         AS market_cap_rank,
    total_volume                                AS total_volume_usd,
    SAFE_CAST(high_24h AS FLOAT64)              AS high_24h_usd,
    SAFE_CAST(low_24h AS FLOAT64)               AS low_24h_usd,
    price_change_24h                            AS price_change_24h_usd,
    price_change_percentage_24h                 AS price_change_pct_24h,
    market_cap_change_percentage_24h            AS market_cap_change_pct_24h,
    circulating_supply,
    max_supply,
    roi                                         AS roi_pct,
    last_updated                                AS last_updated_at,
    CASE
        WHEN DATE(ingested_at) = DATE(last_updated) THEN DATE(ingested_at)
        ELSE DATE(last_updated)
    END                                         AS ingested_date,
    ingested_at
FROM raw.prices
WHERE current_price IS NOT NULL
  AND id IS NOT NULL
