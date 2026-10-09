{{
    config(
        materialized='incremental',
        unique_key='order_id',
        incremental_strategy='merge'
    )
}}

with order_revenue as (
    select * from {{ ref('int_order_revenue') }}
)

select
    order_id,
    tenant_id,
    customer_id,
    order_date,
    cast(order_date as date)          as order_date_day,
    order_status,
    charged_amount,
    collected_amount
from order_revenue

{% if is_incremental() %}
where order_date > (select coalesce(max(order_date), '1970-01-01') from {{ this }})
{% endif %}
