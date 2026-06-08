
{{
  config(materialized = 'table')
}}

select
    road_name,
    region,
    accidents_2024,
    fatal_accidents_2024,

    round(
        fatal_accidents_2024 * 100.0 / nullif(accidents_2024, 0),
    1)                                                          as road_fatality_rate_pct,

    row_number() over (order by fatal_accidents_2024 desc)      as fatality_rank,

    round(
        fatal_accidents_2024 * 100.0 / sum(fatal_accidents_2024) over (),
    1)                                                          as pct_of_top10,

    case
        when fatal_accidents_2024 >= 200 then 'Extreme'
        when fatal_accidents_2024 >= 150 then 'High'
        when fatal_accidents_2024 >= 100 then 'Elevated'
        else                                  'Moderate'
    end                                                         as danger_band

from {{ source('ntsa_raw', 'hotspot_roads') }}
order by fatal_accidents_2024 desc
