{% macro cent_to_dollars(column_name, decimals=2) -%}
    round({{ column_name }} / 100, {{ decimals }})
{%- endmacro %}