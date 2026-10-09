with customers as (
    select * from {{ ref('stg_customers') }}
),

customer_orders as (
    select * from {{ ref('int_customer_orders') }}
),

subscriptions as (
    select
        customer_id,
        max(case when status = 'active' then 1 else 0 end) = 1  as has_active_subscription,
        max(mrr_amount)                                             as current_mrr
    from {{ ref('stg_subscriptions') }}
    where status = 'active'
    group by customer_id
)

select
    c.customer_id,
    c.tenant_id,
    c.first_name,
    c.last_name,
    c.email,
    c.country,
    c.signup_date,
    coalesce(co.lifetime_orders, 0)          as lifetime_orders,
    coalesce(co.lifetime_revenue, 0)            as lifetime_revenue,
    co.first_order_date,
    co.last_order_date,
    coalesce(s.has_active_subscription, false)     as has_active_subscription,
    coalesce(s.current_mrr, 0)                        as current_mrr
from customers c
left join customer_orders co on c.customer_id = co.customer_id
left join subscriptions s on c.customer_id = s.customer_id
