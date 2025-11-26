{% set old_relation = adapter.get_relation(
      database = target.database,
      schema = "dbt_gpoojary",
      identifier = "customer_orders"
) %}

{% set dbt_relation = ref('fct_customer_orders') %}

{{ audit_helper.compare_relations(
    a_relation = old_relation,
    b_relation = dbt_relation,
    primary_key_columns = ["order_id"],
) }}
