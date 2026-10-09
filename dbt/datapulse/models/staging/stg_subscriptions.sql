with source as (

    {% if target.type == 'snowflake' %}
    select
        _raw_data:subscription_id::number   as subscription_id,
        _raw_data:tenant_id::varchar           as tenant_id,
        _raw_data:customer_id::number             as customer_id,
        _raw_data:plan::varchar                      as plan,
        _raw_data:status::varchar                       as status,
        _raw_data:mrr_amount::float                        as mrr_amount,
        _raw_data:started_at::timestamp_ntz                   as started_at,
        _raw_data:cancelled_at::timestamp_ntz                    as cancelled_at,
        _raw_data:created_at::timestamp_ntz                        as created_at
    from {{ source('raw', 'subscriptions') }}
    {% else %}
    select subscription_id, tenant_id, customer_id, plan, status, mrr_amount, started_at, cancelled_at, created_at
    from {{ source('raw', 'subscriptions') }}
    {% endif %}

)

select * from source
