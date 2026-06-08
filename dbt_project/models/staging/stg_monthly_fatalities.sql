select
    month,
    month_num::int                                          as month_num,
    fatalities_2024::int                                    as fatalities_2024,
    fatalities_2023::int                                    as fatalities_2023,

    fatalities_2024 - fatalities_2023                       as yoy_monthly_change,

    round(
        (fatalities_2024 - fatalities_2023) * 100.0
        / nullif(fatalities_2023, 0),
    1)                                                      as yoy_monthly_pct

from {{ source('ntsa_raw', 'monthly_fatalities') }}
where month_num is not null
order by month_num
