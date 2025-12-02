{% test greater_than_five(model, column_name) %}

    select *
    from {{ model }}
    where {{ column_name }} <= 5

{% endtest %}