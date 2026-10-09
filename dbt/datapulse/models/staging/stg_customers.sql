with source as (

    {% if target.type == 'snowflake' %}
    select
        _raw_data:customer_id::number       as customer_id,
        _raw_data:tenant_id::varchar         as tenant_id,
        _raw_data:first_name::varchar         as first_name,
        _raw_data:last_name::varchar           as last_name,
        _raw_data:email::varchar                as email,
        _raw_data:country::varchar                as country,
        _raw_data:signup_date::date                as signup_date,
        _raw_data:created_at::timestamp_ntz          as created_at
    from {{ source('raw', 'customers') }}
    {% else %}
    select customer_id, tenant_id, first_name, last_name, email, country, signup_date, created_at
    from {{ source('raw', 'customers') }}
    {% endif %}

)

select * from source
