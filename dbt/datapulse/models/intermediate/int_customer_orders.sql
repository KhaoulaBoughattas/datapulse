with orders as (
    select * from {{ ref('stg_orders') }}
),

customer_order_stats as (
    select
        customer_id,
        tenant_id,
        count(order_id)                                    as lifetime_orders,
        sum(total_amount)                                    as lifetime_revenue,
        min(order_date)                                        as first_order_date,
        max(order_date)                                          as last_order_date,
        sum(case when status = 'completed' then 1 else 0 end)      as completed_orders
    from orders
    group by customer_id, tenant_id
)

select * from customer_order_stats
