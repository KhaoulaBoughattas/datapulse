with source as (

    {% if target.type == 'snowflake' %}
    select
        _raw_data:order_id::number         as order_id,
        _raw_data:tenant_id::varchar         as tenant_id,
        _raw_data:customer_id::number          as customer_id,
        _raw_data:order_date::timestamp_ntz       as order_date,
        _raw_data:status::varchar                    as status,
        _raw_data:total_amount::float                  as total_amount,
        _raw_data:created_at::timestamp_ntz              as created_at
    from {{ source('raw', 'orders') }}
    {% else %}
    select order_id, tenant_id, customer_id, order_date, status, total_amount, created_at
    from {{ source('raw', 'orders') }}
    {% endif %}

)

select * from source
