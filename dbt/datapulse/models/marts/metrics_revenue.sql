with fact_orders as (
    select * from {{ ref('fact_orders') }}
    where order_status = 'completed'
)

select
    tenant_id,
    order_date_day,
    count(order_id)                                             as order_count,
    sum(collected_amount)                                          as total_revenue,
    round(sum(collected_amount) / nullif(count(order_id), 0), 2)      as average_order_value
from fact_orders
group by tenant_id, order_date_day
