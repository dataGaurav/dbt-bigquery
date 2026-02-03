{# Only run legacy comparison when enabled (e.g. prod). When false, skip without calling compare_relations so CI never receives None. #}
{% if var('run_legacy_audit', false) %}
  {% set old_relation = adapter.get_relation(
        database = target.database,
        schema = target.schema,
        identifier = "customer_orders"
  ) %}

  {% set dbt_relation = ref('fct_customer_orders') %}

  {% if old_relation is not none and dbt_relation is not none %}
  {{ audit_helper.compare_relations(
      a_relation = old_relation,
      b_relation = dbt_relation,
      primary_key = ["order_id"],
  ) }}
  {% else %}
  select 1 as audit_skipped_legacy_table_not_present
  {% endif %}
{% else %}
select 1 as audit_skipped_run_legacy_audit_disabled
{% endif %}
