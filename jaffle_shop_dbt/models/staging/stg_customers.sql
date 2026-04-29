{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ source('jaffle_shop', 'raw_customers') }}
)

SELECT
    id AS customer_id,
    first_name,
    last_name
FROM source
