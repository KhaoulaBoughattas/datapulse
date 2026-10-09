with source as (

    {% if target.type == 'snowflake' %}
    select
        _raw_data:event_id::varchar          as event_id,
        _raw_data:tenant_id::varchar           as tenant_id,
        _raw_data:customer_id::number             as customer_id,
        _raw_data:session_id::varchar                as session_id,
        _raw_data:event_type::varchar                   as event_type,
        _raw_data:product_id::number                       as product_id,
        _raw_data:event_timestamp::timestamp_ntz              as event_timestamp,
        _raw_data:created_at::timestamp_ntz                      as created_at
    from {{ source('raw', 'events') }}
    {% else %}
    select event_id, tenant_id, customer_id, session_id, event_type, product_id, event_timestamp, created_at
    from {{ source('raw', 'events') }}
    {% endif %}

)

select * from source
