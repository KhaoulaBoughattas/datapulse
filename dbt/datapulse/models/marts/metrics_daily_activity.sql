select
    tenant_id,
    event_date,
    count(distinct customer_id)          as daily_active_customers,
    count(event_id)                         as total_events
from {{ ref('fact_events') }}
where customer_id is not null
group by tenant_id, event_date
