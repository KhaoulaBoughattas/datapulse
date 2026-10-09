with source as (

    {% if target.type == 'snowflake' %}
    select
        _raw_data:product_id::number    as product_id,
        _raw_data:tenant_id::varchar      as tenant_id,
        _raw_data:name::varchar            as product_name,
        _raw_data:category::varchar          as category,
        _raw_data:price::float                 as price,
        _raw_data:cost::float                    as cost,
        _raw_data:created_at::timestamp_ntz        as created_at
    from {{ source('raw', 'products') }}
    {% else %}
    select product_id, tenant_id, name as product_name, category, price, cost, created_at
    from {{ source('raw', 'products') }}
    {% endif %}

)

select * from source
