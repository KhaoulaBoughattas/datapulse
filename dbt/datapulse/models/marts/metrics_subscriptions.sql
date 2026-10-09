with subscriptions as (
    select * from {{ ref('stg_subscriptions') }}
),

per_tenant as (
    select
        tenant_id,
        count(case when status = 'active' then 1 end)          as active_subscriptions,
        count(case when status = 'cancelled' then 1 end)          as cancelled_subscriptions,
        count(*)                                                     as total_subscriptions,
        sum(case when status = 'active' then mrr_amount else 0 end)    as mrr
    from subscriptions
    group by tenant_id
)

select
    tenant_id,
    active_subscriptions,
    cancelled_subscriptions,
    total_subscriptions,
    mrr,
    mrr * 12                                                                        as arr,
    round(100.0 * cancelled_subscriptions / nullif(total_subscriptions, 0), 2)          as churn_rate_pct
from per_tenant
