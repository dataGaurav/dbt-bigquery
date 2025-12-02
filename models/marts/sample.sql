-- Example: Reference dim_customers version 2
-- select * from {{ ref('dim_customers', v=2) }}

-- Python models are not supported in dbt Fusion
-- The reference to is_holiday_2025 has been removed since Python models don't work in dbt Fusion

-- Example: Reference an existing model instead
select * from {{ ref('dim_customers') }} limit 10