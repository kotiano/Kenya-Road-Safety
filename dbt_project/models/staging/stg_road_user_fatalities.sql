select
    year::int                                               as accident_year,
    pedestrians::int                                        as pedestrian_fatalities,
    motorcyclists::int                                      as motorcyclist_fatalities,
    pillion_passengers::int                                 as pillion_fatalities,
    passengers::int                                         as passenger_fatalities,
    drivers::int                                            as driver_fatalities,
    pedal_cyclists::int                                     as cyclist_fatalities,

    -- row total 
    (
        coalesce(pedestrians, 0)        +
        coalesce(motorcyclists, 0)      +
        coalesce(pillion_passengers, 0) +
        coalesce(passengers, 0)         +
        coalesce(drivers, 0)            +
        coalesce(pedal_cyclists, 0)
    )                                                       as user_total_fatalities

from {{ source('ntsa_raw', 'road_user_fatalities') }}
where year is not null
