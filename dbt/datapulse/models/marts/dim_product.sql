with products as (
    select * from {{ ref('stg_products') }}
),

order_items as (
    select * from {{ ref('stg_order_items') }}
),

product_sales as (
    select
        product_id,
        sum(quantity)             as units_sold,
        sum(line_item_amount)        as gross_revenue
    from order_items
    group by product_id
)

select
    p.product_id,
    p.tenant_id,
    p.product_name,
    p.category,
    p.price,
    p.cost,
    round(p.price - p.cost, 2)                as unit_margin,
    coalesce(ps.units_sold, 0)                   as units_sold,
    coalesce(ps.gross_revenue, 0)                   as gross_revenue
from products p
left join product_sales ps on p.product_id = ps.product_id
