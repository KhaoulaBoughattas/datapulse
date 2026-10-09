with payments as (
    select * from {{ ref('stg_payments') }}
),

orders as (
    select order_id, tenant_id, customer_id from {{ ref('stg_orders') }}
)

select
    p.payment_id,
    p.tenant_id,
    p.order_id,
    o.customer_id,
    p.amount,
    p.payment_method,
    p.status,
    p.paid_at,
    cast(p.paid_at as date)     as paid_date
from payments p
left join orders o on p.order_id = o.order_id
