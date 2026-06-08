-- NTSA 13 Leading Causes Report 2023

select
    trim(cause)                                             as cause,
    initcap(trim(category))                                 as cause_category,
    incidents_2023::int                                     as incidents_2023,
    incidents_2022::int                                     as incidents_2022,

    incidents_2023 - incidents_2022                         as yoy_change,

    round(
        (incidents_2023 - incidents_2022) * 100.0
        / nullif(incidents_2022, 0),
    1)                                                      as yoy_pct_change,

    -- share of 2023 total
    round(
        incidents_2023 * 100.0 / sum(incidents_2023) over (),
    1)                                                      as pct_of_total_2023

from {{ source('ntsa_raw', 'accident_causes') }}
where cause is not null
order by incidents_2023 desc
