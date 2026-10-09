{{
    config(
        materialized='incremental',
        unique_key='event_id',
        incremental_strategy='merge'
    )
}}

select
    event_id,
    tenant_id,
    customer_id,
    session_id,
    event_type,
    product_id,
    event_timestamp,
    cast(event_timestamp as date)     as event_date
from {{ ref('stg_events') }}

{% if is_incremental() %}
where event_timestamp > (select coalesce(max(event_timestamp), '1970-01-01') from {{ this }})
{% endif %}
