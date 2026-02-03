{% set old_relation = adapter.get_relation(
      database = target.database,
      schema = target.schema,
      identifier = "customer_orders"
) %}

{% set dbt_relation = ref('fct_customer_orders') %}

{% if old_relation is not none %}
{{ audit_helper.compare_relations(
    a_relation = old_relation,
    b_relation = dbt_relation,
    primary_key = ["order_id"],
) }}
{% else %}
-- Legacy table customer_orders not present in this target; skip comparison
select 1 as audit_skipped_legacy_table_not_present
{% endif %}
