/* @bruin

name: marts.mart_crypto_vs_sentiment
type: bq.sql
depends:
  - intermediate.int_daily_prices
  - intermediate.int_daily_sentiment

materialization:
  type: table
  strategy: create+replace
  partition_by: price_date
  cluster_by:
    - coin_id
    - fg_label

columns:
  - name: price_date
    type: date
    description: Date of the combined snapshot
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

  - name: close_price_usd
    type: float64
    description: Last recorded price of the day in USD

  - name: avg_price_change_pct_24h
    type: float64
    description: Average 24h price change percentage

  - name: avg_volume_usd
    type: float64
    description: Average trading volume in USD

  - name: avg_market_cap_usd
    type: float64
    description: Average market cap in USD

  - name: fg_value
    type: int64
    description: Fear and Greed score for the day (0-100)

  - name: fg_label
    type: string
    description: Sentiment label for the day

  - name: fg_category
    type: int64
    description: Numeric sentiment category (1=Extreme Fear to 5=Extreme Greed)

  - name: is_fear
    type: bool
    description: True when market sentiment is fearful

  - name: is_greed
    type: bool
    description: True when market sentiment is greedy

  - name: value_change_vs_prev_day
    type: int64
    description: Change in Fear and Greed score vs previous day

  - name: price_vs_sentiment_alignment
    type: string
    description: Whether price movement aligns with sentiment (aligned / misaligned / neutral)

@bruin */

SELECT
    p.price_date,
    p.coin_id,
    p.symbol,
    p.coin_name,
    p.close_price_usd,
    p.avg_price_change_pct_24h,
    p.avg_volume_usd,
    p.avg_market_cap_usd,
    s.fg_value,
    s.fg_label,
    s.fg_category,
    s.is_fear,
    s.is_greed,
    s.value_change_vs_prev_day,
    CASE
        WHEN s.is_greed  AND p.avg_price_change_pct_24h > 0  THEN 'aligned'
        WHEN s.is_fear   AND p.avg_price_change_pct_24h < 0  THEN 'aligned'
        WHEN s.is_greed  AND p.avg_price_change_pct_24h < 0  THEN 'misaligned'
        WHEN s.is_fear   AND p.avg_price_change_pct_24h > 0  THEN 'misaligned'
        ELSE 'neutral'
    END                                                         AS price_vs_sentiment_alignment
FROM intermediate.int_daily_prices  p
LEFT JOIN intermediate.int_daily_sentiment s
    ON p.price_date = s.fg_date
