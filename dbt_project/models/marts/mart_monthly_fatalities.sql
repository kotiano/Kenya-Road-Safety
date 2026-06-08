
{{
  config(materialized = 'table')
}}

select
    month,
    month_num,
    fatalities_2024,
    fatalities_2023,
    yoy_monthly_change,
    yoy_monthly_pct

from {{ ref('stg_monthly_fatalities') }}
order by month_num
