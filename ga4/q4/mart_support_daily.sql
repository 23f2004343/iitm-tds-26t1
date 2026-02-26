{{
    config(
        materialized='table',
        tags=['mart', 'support', 'daily'],
        meta={
            'freshness': {
                'warn_after': {'count': 1, 'period': 'day'},
                'error_after': {'count': 2, 'period': 'day'}
            },
            'owner': 'orbit_ops_team',
            'description': 'Daily support operations performance mart covering the last 14 days'
        }
    )
}}

-- ============================================================
-- mart_support_daily
-- Grain       : one row per (activity_date, queue)
-- Window      : last 14 days relative to current_date
-- Key metric  : avg_handle_minutes per queue per day
-- Sources     : stg_support_tickets, stg_shipments, stg_returns
-- ============================================================

with

-- ----------------------------------------------------------
-- 1. Source CTEs — filter to last 14 days
-- ----------------------------------------------------------
support_tickets as (

    select
        ticket_id,
        queue,
        agent_id,
        opened_at,
        closed_at,
        coalesce(handle_minutes, 0)                     as handle_minutes,
        status,
        date_trunc('day', opened_at)                    as activity_date

    from {{ ref('stg_support_tickets') }}

    where
        -- last 14 days relative to current_date
        opened_at >= current_date - interval '14 days'
        and opened_at <  current_date + interval '1 day'

),

shipments as (

    select
        shipment_id,
        queue,
        created_at,
        resolved_at,
        coalesce(handle_minutes, 0)                     as handle_minutes,
        date_trunc('day', created_at)                   as activity_date

    from {{ ref('stg_shipments') }}

    where
        created_at >= current_date - interval '14 days'
        and created_at <  current_date + interval '1 day'

),

returns as (

    select
        return_id,
        queue,
        initiated_at,
        completed_at,
        coalesce(handle_minutes, 0)                     as handle_minutes,
        date_trunc('day', initiated_at)                 as activity_date

    from {{ ref('stg_returns') }}

    where
        initiated_at >= current_date - interval '14 days'
        and initiated_at <  current_date + interval '1 day'

),

-- ----------------------------------------------------------
-- 3. Combine all queues into one interaction pool
-- ----------------------------------------------------------
combined_interactions as (

    select
        activity_date,
        queue,
        handle_minutes,
        'support_ticket'                                as interaction_type

    from support_tickets

    union all

    select
        activity_date,
        queue,
        handle_minutes,
        'shipment_query'

    from shipments

    union all

    select
        activity_date,
        queue,
        handle_minutes,
        'return_request'

    from returns

),

-- ----------------------------------------------------------
-- 4. Aggregate to daily grain
-- ----------------------------------------------------------
daily_aggregates as (

    select
        activity_date,
        queue,
        count(*)                                        as total_interactions,
        round(avg(handle_minutes), 2)                   as avg_handle_minutes,
        round(sum(handle_minutes), 2)                   as total_handle_minutes,
        round(min(handle_minutes), 2)                   as min_handle_minutes,
        round(max(handle_minutes), 2)                   as max_handle_minutes,
        -- NULL-safe average: coalesce guards against division edge-cases
        coalesce(
            round(nullif(avg(handle_minutes), 0), 2),
            0
        )                                               as avg_handle_minutes_safe

    from combined_interactions

    group by
        activity_date,
        queue

),

-- ----------------------------------------------------------
-- 5. Enrich with BI-ready labels
-- ----------------------------------------------------------
final as (

    select
        activity_date,
        queue,
        total_interactions,
        avg_handle_minutes,
        avg_handle_minutes_safe,
        total_handle_minutes,
        min_handle_minutes,
        max_handle_minutes,
        round(max_handle_minutes - min_handle_minutes, 2)   as handle_minutes_range,

        -- handling_speed_tier: BI filter-friendly categorical column
        case
            when avg_handle_minutes <= 5  then 'fast'
            when avg_handle_minutes <= 15 then 'normal'
            else                               'slow'
        end                                             as handling_speed_tier,

        current_timestamp                               as dbt_updated_at

    from daily_aggregates

)

-- ----------------------------------------------------------
-- Final select: ordered for BI tool consumption
-- ----------------------------------------------------------
select *
from final
order by
    activity_date desc,
    queue asc

