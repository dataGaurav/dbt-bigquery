-- Time spine with daily granularity for MetricFlow / Semantic Layer (DAY or smaller required).
{{ dbt_utils.date_spine(
    datepart="day",
    start_date="cast('2000-01-01' as date)",
    end_date="cast('2030-12-31' as date)"
   )
}}
