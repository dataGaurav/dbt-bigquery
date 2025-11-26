{# custom schema(staging) only in production, in dev it will be in default schema(dbt_gpoojary) #}

{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set default_schema = target.schema -%}
    {%- set target_name = target.name -%}
    
    {%- if custom_schema_name is none or target_name == 'dev' -%}

        {{ default_schema }}

    {%- else -%}

        {{ custom_schema_name | trim }}

    {%- endif -%}

{%- endmacro %}