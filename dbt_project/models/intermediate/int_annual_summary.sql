
with annual as (
    select * from {{ ref('stg_annual_fatalities') }}
),

road_users as (
    select * from {{ ref('stg_road_user_fatalities') }}
),

joined as (
    select
        a.accident_year,
        a.total_fatalities,
        a.total_accidents,
        a.serious_injuries,
        a.slight_injuries,
        a.fatality_rate_pct,
        a.data_source,

        r.pedestrian_fatalities,
        r.motorcyclist_fatalities,
        r.pillion_fatalities,
        r.passenger_fatalities,
        r.driver_fatalities,
        r.cyclist_fatalities,

        round(r.pedestrian_fatalities   * 100.0 / nullif(a.total_fatalities, 0), 1) as pedestrian_pct,
        round(r.motorcyclist_fatalities * 100.0 / nullif(a.total_fatalities, 0), 1) as motorcyclist_pct,
        round(r.pillion_fatalities      * 100.0 / nullif(a.total_fatalities, 0), 1) as pillion_pct,
        round(r.passenger_fatalities    * 100.0 / nullif(a.total_fatalities, 0), 1) as passenger_pct,
        round(r.driver_fatalities       * 100.0 / nullif(a.total_fatalities, 0), 1) as driver_pct,
        round(r.cyclist_fatalities      * 100.0 / nullif(a.total_fatalities, 0), 1) as cyclist_pct,

        r.pedestrian_fatalities + r.motorcyclist_fatalities
            + r.pillion_fatalities + r.cyclist_fatalities   as vulnerable_fatalities,

        round(
            (r.pedestrian_fatalities + r.motorcyclist_fatalities
             + r.pillion_fatalities + r.cyclist_fatalities)
            * 100.0 / nullif(a.total_fatalities, 0),
        1)                                                  as vulnerable_pct

    from annual a
    left join road_users r on a.accident_year = r.accident_year
),

with_yoy as (
    select
        *,
        total_fatalities
            - lag(total_fatalities) over (order by accident_year)   as yoy_fatality_change,

        round(
            (total_fatalities - lag(total_fatalities) over (order by accident_year))
            * 100.0
            / nullif(lag(total_fatalities) over (order by accident_year), 0),
        1)                                                          as yoy_fatality_pct,

        total_accidents
            - lag(total_accidents) over (order by accident_year)    as yoy_accident_change

    from joined
)

select
    *,
    round(total_fatalities / 365.0, 1)  as avg_daily_fatalities,

    case
        when yoy_fatality_pct >  10  then 'Critical — worsening fast'
        when yoy_fatality_pct >   0  then 'Deteriorating'
        when yoy_fatality_pct =   0  then 'Stable'
        when yoy_fatality_pct > -10  then 'Improving'
        else                              'Significant improvement'
    end                                 as trend_band

from with_yoy
order by accident_year
