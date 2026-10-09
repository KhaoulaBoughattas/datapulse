with source as (

    {% if target.type == 'snowflake' %}
    select
        _raw_data:order_item_id::number   as order_item_id,
        _raw_data:tenant_id::varchar        as tenant_id,
        _raw_data:order_id::number             as order_id,
        _raw_data:product_id::number             as product_id,
        _raw_data:quantity::number                  as quantity,
        _raw_data:unit_price::float                    as unit_price,
        _raw_data:created_at::timestamp_ntz              as created_at
    from {{ source('raw', 'order_items') }}
    {% else %}
    select order_item_id, tenant_id, order_id, product_id, quantity, unit_price, created_at
    from {{ source('raw', 'order_items') }}
    {% endif %}

)

select *, quantity * unit_price as line_item_amount from source
