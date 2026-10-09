{# NOTE: datediff() is Snowflake syntax. On the Postgres local target,
   replace with (last_order_date - first_order_date). See docs/dbt.md. #}
select
    tenant_id,
    customer_id,
    lifetime_orders,
    lifetime_revenue,
    round(lifetime_revenue / nullif(lifetime_orders, 0), 2)   as average_order_value,
    first_order_date,
    last_order_date
from {{ ref('dim_customer') }}
where lifetime_orders > 0
