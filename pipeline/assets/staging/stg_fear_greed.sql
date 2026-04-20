/* @bruin

name: staging.stg_fear_greed
type: bq.sql
depends:
  - raw.fear_greed

materialization:
  type: table
  strategy: create+replace
  partition_by: fg_date

columns:
  - name: fg_date
    type: date
    description: Date the Fear and Greed index value corresponds to
    checks:
      - name: not_null
      - name: unique

  - name: fg_value
    type: integer
    description: Fear and Greed score from 0 (Extreme Fear) to 100 (Extreme Greed)
    checks:
      - name: not_null

  - name: fg_label
    type: string
    description: Sentiment label (Extreme Fear, Fear, Neutral, Greed, Extreme Greed)
    checks:
      - name: not_null
      - name: accepted_values
        value:
          - Extreme Fear
          - Fear
          - Neutral
          - Greed
          - Extreme Greed

  - name: fg_category
    type: integer
    description: Numeric category from 1 (Extreme Fear) to 5 (Extreme Greed) for sorting

  - name: ingested_at
    type: timestamp
    description: Timestamp when the pipeline ingested this record
    checks:
      - name: not_null

@bruin */

SELECT
    DATE(timestamp)         AS fg_date,
    value                   AS fg_value,
    value_classification    AS fg_label,
    CASE value_classification
        WHEN 'Extreme Fear' THEN 1
        WHEN 'Fear'         THEN 2
        WHEN 'Neutral'      THEN 3
        WHEN 'Greed'        THEN 4
        WHEN 'Extreme Greed'THEN 5
        ELSE NULL
    END                     AS fg_category,
    ingested_at
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY DATE(timestamp) ORDER BY ingested_at DESC) AS rn
    FROM raw.fear_greed
)
WHERE rn = 1
