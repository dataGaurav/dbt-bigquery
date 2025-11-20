{% macro union_tables_by_prefix(database, schema, prefix) %}
    {%- set tables=dbt_utils.get_relations_by_prefix(database=database, schema=schema, prefix=prefix) -%}
    
    {% for table in tables %}
        {% if not loop.first %}

             union all 
        
        {% endif %}

        select customer_id from {{ table.database }}.{{ table.schema }}.{{ table.identifier }}
    {%- endfor -%}

{% endmacro %}

--dbt run-operation unioned_tables --args '{"database": "data-platforms-team-sandbox", "schema": "dbt_gpoojary", "prefix": "stg_jaffle_shop__"}'