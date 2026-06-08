
{{
  config(materialized = 'table')
}}

select
    cause,
    cause_category,
    incidents_2023,
    incidents_2022,
    yoy_change,
    yoy_pct_change,
    pct_of_total_2023

from {{ ref('stg_accident_causes') }}
order by incidents_2023 desc
