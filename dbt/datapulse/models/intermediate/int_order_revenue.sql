with orders as (
    select * from {{ ref('stg_orders') }}
),

payments as (
    select * from {{ ref('stg_payments') }}
    where status = 'success'
),

order_revenue as (
    select
        o.order_id,
        o.tenant_id,
        o.customer_id,
        o.order_date,
        o.status                     as order_status,
        o.total_amount                 as charged_amount,
        coalesce(p.amount, 0)             as collected_amount
    from orders o
    left join payments p on o.order_id = p.order_id
)

select * from order_revenue
