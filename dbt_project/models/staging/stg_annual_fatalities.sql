

select
    year::int                                               as accident_year,
    total_fatalities::int                                   as total_fatalities,
    total_accidents::int                                    as total_accidents,
    serious_injuries::int                                   as serious_injuries,
    slight_injuries::int                                    as slight_injuries,
    data_source,

    -- fatality rate per 100 accidents
    round(total_fatalities * 100.0 / nullif(total_accidents, 0), 2)
                                                            as fatality_rate_pct,
    loaded_at

from {{ source('ntsa_raw', 'annual_fatalities') }}
where year is not null
