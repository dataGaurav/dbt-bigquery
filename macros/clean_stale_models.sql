{% macro clean_stale_models(database=target.database, schema=target.schema, dry_run=true) %}
    
    {% set query %}
        select 
            table_type, table_schema, table_name,
            CASE WHEN table_type = 'BASE TABLE' THEN 'TABLE'
                else 'VIEW'
                END as drop_type,
            CONCAT(
                'DROP ',
                CASE 
                    WHEN table_type = 'BASE TABLE' THEN 'TABLE'
                    ELSE 'VIEW'
                END,
                ' `', '{{ database }}', '`.`', table_schema, '`.`', table_name, '`;'
            ) AS drop_query
        from {{ database }}.{{ schema }}.INFORMATION_SCHEMA.TABLES
        where table_schema = '{{ schema }}'
    {% endset %}

    {% set drop_queries = run_query(query).columns[4].values() %}

    {% for query in drop_queries %}
        {% if dry_run %}
            {{ log(query, info=true) }}
        {% else %}
            {{ log('Dropping object with command: ' ~ query, info=true) }}
            {{ run_query(query.drop_query) }}
        {% endif %} 
    {% endfor %}

{% endmacro %}

--dbt run-operation clean_stale_models