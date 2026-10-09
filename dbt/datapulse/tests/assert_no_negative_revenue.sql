select order_id, collected_amount
from {{ ref('fact_orders') }}
where collected_amount < 0
