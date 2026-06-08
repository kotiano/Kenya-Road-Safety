-- final table for Power BI — one row per year
-- materialised as table in ANALYTICS schema

{{
  config(
    materialized = 'table',
    cluster_by   = ['accident_year']
  )
}}

select
    accident_year,

    -- headline KPIs
    total_fatalities,
    total_accidents,
    serious_injuries,
    slight_injuries,
    fatality_rate_pct,
    avg_daily_fatalities,
    trend_band,

    -- YoY
    yoy_fatality_change,
    yoy_fatality_pct,
    yoy_accident_change,

    -- road user breakdown 
    pedestrian_fatalities,
    motorcyclist_fatalities,
    pillion_fatalities,
    passenger_fatalities,
    driver_fatalities,
    cyclist_fatalities,
    vulnerable_fatalities,

    -- road user shares 
    pedestrian_pct,
    motorcyclist_pct,
    pillion_pct,
    passenger_pct,
    driver_pct,
    cyclist_pct,
    vulnerable_pct,

    data_source

from {{ ref('int_annual_summary') }}
order by accident_year
