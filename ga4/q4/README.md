# Q4: dbt Operations Performance Mart

## Task

Build a **dbt mart model** that powers the **support operations dashboard** for Orbit Ops. The model must aggregate **avg handle_minutes** at a **daily grain** covering the **last 14 days**, drawing from upstream staging tables (`stg_support_tickets`, `stg_shipments`, `stg_returns`).

---

## Requirements

* Use `{{ config(...) }}` to declare materialization and freshness metadata.
* Reference upstream models via `{{ ref() }}`.
* Filter rows to the **last 14 days** relative to `current_date`.
* Aggregate results at **daily grain** using `date_trunc`.
* Compute `avg_handle_minutes`; include domain terms such as **queue** and **interaction_type**.
* Handle NULLs with `coalesce` / `ifnull`.
* Return columns ordered by date, ready for BI consumption.
* Compatible with Snowflake / BigQuery SQL dialect.

---

## Approach

### 1. Materialization & Metadata
The model uses `{{ config(materialized='table', tags=[...], meta={...}) }}` to declare it as a table, tag it for orchestration (`mart`, `support`, `daily`), and attach freshness thresholds (`warn_after: 1 day`, `error_after: 2 days`).

### 2. Upstream Source References
Three upstream staging CTEs pull from `{{ ref('stg_support_tickets') }}`, `{{ ref('stg_shipments') }}`, and `{{ ref('stg_returns') }}`. Each CTE applies a `date_trunc('day', ...)` to normalize to daily grain.

### 3. 14-Day Rolling Filter
Each staging CTE filters with:
```sql
where opened_at >= current_date - interval '14 days'
  and opened_at < current_date + interval '1 day'
```
This ensures a strict 14-day rolling window relative to `current_date` without hard-coded dates.

### 4. Unified Interaction Pool
A `combined_interactions` CTE uses `UNION ALL` to merge support tickets, shipment queries, and return requests into one fact layer, preserving the `queue` dimension and labeling each row with an `interaction_type`.

### 5. Daily Aggregation
The `daily_aggregates` CTE groups by `activity_date` and `queue`, computing:
- `count(*)` → `total_interactions`
- `avg(handle_minutes)` → `avg_handle_minutes`
- `sum`, `min`, `max` of `handle_minutes` for further analysis

### 6. NULL Handling
`coalesce(handle_minutes, 0)` is applied in each source CTE before aggregation. A `coalesce(nullif(avg(...), 0), 0)` guard is added in the aggregate layer to prevent division artifacts.

### 7. BI-Ready Output
The `final` CTE adds:
- `handle_minutes_range` (max − min spread)
- `handling_speed_tier` (`fast` / `normal` / `slow`) — a labeled tier for dashboard filtering
- `dbt_updated_at` — pipeline freshness timestamp visible in BI tools

Results are ordered by `activity_date DESC, queue ASC` for direct dashboard consumption.

---

## Code

**Model file:** [`mart_support_daily.sql`](./mart_support_daily.sql)

```sql
{{ config(
    materialized='table',
    tags=['mart', 'support', 'daily'],
    meta={
        'freshness': {
            'warn_after': {'count': 1, 'period': 'day'},
            'error_after': {'count': 2, 'period': 'day'}
        },
        'owner': 'orbit_ops_team'
    }
) }}

with support_tickets as (
    select ticket_id, queue, opened_at, handle_minutes,
           date_trunc('day', opened_at) as activity_date
    from {{ ref('stg_support_tickets') }}
    where opened_at >= current_date - interval '14 days'
),

shipments as (
    select shipment_id, queue, created_at, handle_minutes,
           date_trunc('day', created_at) as activity_date
    from {{ ref('stg_shipments') }}
    where created_at >= current_date - interval '14 days'
),

returns as (
    select return_id, queue, initiated_at, handle_minutes,
           date_trunc('day', initiated_at) as activity_date
    from {{ ref('stg_returns') }}
    where initiated_at >= current_date - interval '14 days'
),

combined_interactions as (
    select activity_date, queue, coalesce(handle_minutes, 0) as handle_minutes
    from support_tickets
    union all
    select activity_date, queue, coalesce(handle_minutes, 0) from shipments
    union all
    select activity_date, queue, coalesce(handle_minutes, 0) from returns
),

daily_aggregates as (
    select
        activity_date,
        queue,
        count(*)                      as total_interactions,
        round(avg(handle_minutes), 2) as avg_handle_minutes,
        round(sum(handle_minutes), 2) as total_handle_minutes,
        round(min(handle_minutes), 2) as min_handle_minutes,
        round(max(handle_minutes), 2) as max_handle_minutes
    from combined_interactions
    group by activity_date, queue
),

final as (
    select
        activity_date,
        queue,
        total_interactions,
        avg_handle_minutes,
        coalesce(avg_handle_minutes, 0)          as avg_handle_minutes_safe,
        total_handle_minutes,
        min_handle_minutes,
        max_handle_minutes,
        round(max_handle_minutes - min_handle_minutes, 2) as handle_minutes_range,
        case
            when avg_handle_minutes <= 5  then 'fast'
            when avg_handle_minutes <= 15 then 'normal'
            else 'slow'
        end                                      as handling_speed_tier,
        current_timestamp                        as dbt_updated_at
    from daily_aggregates
)

select * from final
order by activity_date desc, queue asc
```

---

## Verification

To test this model locally:

1. Set up a dbt project with the Snowflake or BigQuery adapter.
2. Ensure `stg_support_tickets`, `stg_shipments`, and `stg_returns` exist (or mock them as seeds).
3. Place this file under `models/marts/support/mart_support_daily.sql`.
4. Run:
   ```bash
   dbt run --select mart_support_daily
   dbt test --select mart_support_daily
   ```
5. Validate in the warehouse:
   ```sql
   select * from mart_support_daily
   order by activity_date desc
   limit 30;
   ```
6. Confirm rows span exactly 14 days, `avg_handle_minutes` is non-null, `queue` is populated, and `handling_speed_tier` is correctly assigned.
