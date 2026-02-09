with orders as (

    select * from {{ ref('stg_jaffle_shop__orders_legacy') }}

),
payments as (

    select * from {{ ref('stg_stripe__payments_legacy') }}
    where payment_status != 'fail'

),



order_total as (

    select 
        order_id,
        payment_status,
        sum(payment_amount) as order_value_dollars
    from payments
    group by 1,2 

),


order_values_joined as (
    select 
        o.*,
        ot.payment_status,
        ot.order_value_dollars
    from orders o
    left join order_total ot
    on o.order_id = ot.order_id
)

select * from order_values_joined