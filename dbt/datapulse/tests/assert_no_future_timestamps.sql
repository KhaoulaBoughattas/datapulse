{# NOTE: dateadd/current_timestamp() is Snowflake syntax; Postgres
   equivalent is current_timestamp + interval '5 minutes'. See docs/dbt.md #}
select event_id, event_timestamp
from {{ ref('fact_events') }}
where event_timestamp > dateadd('minute', 5, current_timestamp())
