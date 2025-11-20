-- {{ union_tables_by_prefix(database='dbt-tutorial', schema='jaffle_shop', prefix='cust') }}

{% macro unioned_tables(database, schema, prefix) %}
    {{ log("Running union for prefix: " ~ prefix, info=true) }}

    {% set sql = union_tables_by_prefix(database, schema, prefix) %}

    {% set queries = run_query(sql) %}

    {{ log("Union completed successfully.", info=true) }}

    {% for query in queries %}
        {{ log(query, info=true) }}
    {% endfor %}

{% endmacro %}

--dbt run-operation unioned_tables --args '{"database": "data-platforms-team-sandbox", "schema": "dbt_gpoojary", "prefix": "stg_jaffle_shop__"}'