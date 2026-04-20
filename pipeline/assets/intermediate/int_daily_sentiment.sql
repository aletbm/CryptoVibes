/* @bruin

name: intermediate.int_daily_sentiment
type: bq.sql
depends:
  - staging.stg_fear_greed

materialization:
  type: table
  strategy: create+replace
  partition_by: fg_date

columns:
  - name: fg_date
    type: date
    description: Date of the Fear and Greed index value
    checks:
      - name: not_null
      - name: unique

  - name: fg_value
    type: int64
    description: Fear and Greed score (0-100)
    checks:
      - name: not_null

  - name: fg_label
    type: string
    description: Sentiment label
    checks:
      - name: not_null

  - name: fg_category
    type: int64
    description: Numeric category from 1 (Extreme Fear) to 5 (Extreme Greed)

  - name: is_fear
    type: bool
    description: True when market sentiment is fearful (score below 40)

  - name: is_greed
    type: bool
    description: True when market sentiment is greedy (score above 60)

  - name: prev_day_value
    type: int64
    description: Fear and Greed score of the previous day

  - name: value_change_vs_prev_day
    type: int64
    description: Change in Fear and Greed score vs previous day

@bruin */

SELECT
    fg_date,
    fg_value,
    fg_label,
    fg_category,
    fg_value < 40                               AS is_fear,
    fg_value > 60                               AS is_greed,
    LAG(fg_value) OVER (ORDER BY fg_date)       AS prev_day_value,
    fg_value - LAG(fg_value) OVER (
        ORDER BY fg_date
    )                                           AS value_change_vs_prev_day
FROM staging.stg_fear_greed
