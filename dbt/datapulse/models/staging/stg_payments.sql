with source as (

    {% if target.type == 'snowflake' %}
    select
        _raw_data:payment_id::number       as payment_id,
        _raw_data:tenant_id::varchar          as tenant_id,
        _raw_data:order_id::number               as order_id,
        _raw_data:amount::float                     as amount,
        _raw_data:payment_method::varchar              as payment_method,
        _raw_data:status::varchar                        as status,
        _raw_data:paid_at::timestamp_ntz                    as paid_at,
        _raw_data:created_at::timestamp_ntz                    as created_at
    from {{ source('raw', 'payments') }}
    {% else %}
    select payment_id, tenant_id, order_id, amount, payment_method, status, paid_at, created_at
    from {{ source('raw', 'payments') }}
    {% endif %}

)

select * from source
