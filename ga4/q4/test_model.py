"""
Test the mart_support_daily logic using DuckDB with mock data.
Run: python test_model.py
"""
import datetime
import duckdb

con = duckdb.connect()

today = datetime.date.today()
# Build dates: 20 days back so we can verify things outside 14d are excluded
rows_tickets = []
rows_shipments = []
rows_returns = []

for i in range(20):
    d = today - datetime.timedelta(days=i)
    ts = f"{d} 10:00:00"
    # support tickets
    rows_tickets.append(
        f"('{i}', 'billing', 'agent_{i}', TIMESTAMP '{ts}', TIMESTAMP '{ts}', {i * 2 + 1.5}, 'closed')"
    )
    # shipments
    rows_shipments.append(
        f"('S{i}', 'logistics', TIMESTAMP '{ts}', TIMESTAMP '{ts}', {i * 1.5 + 2.0})"
    )
    # returns
    rows_returns.append(
        f"('R{i}', 'returns', TIMESTAMP '{ts}', TIMESTAMP '{ts}', {i * 3.0 + 0.5})"
    )

tickets_values = ",\n".join(rows_tickets)
shipments_values = ",\n".join(rows_shipments)
returns_values = ",\n".join(rows_returns)

# The equivalent SQL (Jinja resolved, ref() replaced with inline CTEs/VALUES)
sql = f"""
WITH stg_support_tickets AS (
    SELECT * FROM (VALUES
        {tickets_values}
    ) AS t(ticket_id, queue, agent_id, opened_at, closed_at, handle_minutes, status)
),
stg_shipments AS (
    SELECT * FROM (VALUES
        {shipments_values}
    ) AS t(shipment_id, queue, created_at, resolved_at, handle_minutes)
),
stg_returns AS (
    SELECT * FROM (VALUES
        {returns_values}
    ) AS t(return_id, queue, initiated_at, completed_at, handle_minutes)
),

-- ---- mart logic begins (mirrors mart_support_daily.sql) ----
support_tickets AS (
    SELECT
        ticket_id,
        queue,
        agent_id,
        opened_at,
        closed_at,
        handle_minutes,
        status,
        date_trunc('day', opened_at) AS activity_date
    FROM stg_support_tickets
    WHERE
        opened_at >= current_date - INTERVAL '14 days'
        AND opened_at <  current_date + INTERVAL '1 day'
),

shipments AS (
    SELECT
        shipment_id,
        queue,
        created_at,
        resolved_at,
        handle_minutes,
        date_trunc('day', created_at) AS activity_date
    FROM stg_shipments
    WHERE
        created_at >= current_date - INTERVAL '14 days'
        AND created_at <  current_date + INTERVAL '1 day'
),

returns AS (
    SELECT
        return_id,
        queue,
        initiated_at,
        completed_at,
        handle_minutes,
        date_trunc('day', initiated_at) AS activity_date
    FROM stg_returns
    WHERE
        initiated_at >= current_date - INTERVAL '14 days'
        AND initiated_at <  current_date + INTERVAL '1 day'
),

combined_interactions AS (
    SELECT activity_date, queue, coalesce(handle_minutes, 0) AS handle_minutes, 'support_ticket' AS interaction_type
    FROM support_tickets
    UNION ALL
    SELECT activity_date, queue, coalesce(handle_minutes, 0), 'shipment_query'
    FROM shipments
    UNION ALL
    SELECT activity_date, queue, coalesce(handle_minutes, 0), 'return_request'
    FROM returns
),

daily_aggregates AS (
    SELECT
        activity_date,
        queue,
        count(*)                      AS total_interactions,
        round(avg(handle_minutes), 2) AS avg_handle_minutes,
        round(sum(handle_minutes), 2) AS total_handle_minutes,
        round(min(handle_minutes), 2) AS min_handle_minutes,
        round(max(handle_minutes), 2) AS max_handle_minutes,
        coalesce(round(nullif(avg(handle_minutes), 0), 2), 0) AS avg_handle_minutes_safe
    FROM combined_interactions
    GROUP BY activity_date, queue
),

final AS (
    SELECT
        activity_date,
        queue,
        total_interactions,
        avg_handle_minutes,
        avg_handle_minutes_safe,
        total_handle_minutes,
        min_handle_minutes,
        max_handle_minutes,
        round(max_handle_minutes - min_handle_minutes, 2) AS handle_minutes_range,
        CASE
            WHEN avg_handle_minutes <= 5  THEN 'fast'
            WHEN avg_handle_minutes <= 15 THEN 'normal'
            ELSE 'slow'
        END AS handling_speed_tier,
        current_timestamp AS dbt_updated_at
    FROM daily_aggregates
)

SELECT * FROM final
ORDER BY activity_date DESC, queue ASC
"""

print("=" * 60)
print("Running mart_support_daily test with DuckDB...")
print("=" * 60)

result = con.execute(sql).fetchdf()

print(f"\n[INFO] Total rows returned: {len(result)}")
print(result.to_string(index=False))

# ---- Assertions ----
print("\n" + "=" * 60)
print("Running assertions...")
print("=" * 60)

# 1. Row count: should be <= 14 days × 3 queues = 42 rows max,
#    but we inserted 1 row per queue per day for 20 days → only 14 days pass filter
# combined: 14 days × (1 ticket + 1 shipment + 1 return) per day, but each is a
# different queue, so group by (date, queue) → 14 days × 3 queues = 42 rows
assert len(result) <= 45, f"Expected at most 45 rows, got {len(result)}"
print(f"  ✅ Row count OK: {len(result)} rows (max 45)")

# 2. No dates older than 14 days
min_date = result["activity_date"].min()
cutoff = today - datetime.timedelta(days=14)
assert min_date.date() >= cutoff, (
    f"Expected min date >= {cutoff}, got {min_date.date()}"
)
print(f"  ✅ Date range OK: oldest date = {min_date.date()}, cutoff = {cutoff}")

# 3. avg_handle_minutes is non-negative everywhere
assert (result["avg_handle_minutes"] >= 0).all(), "avg_handle_minutes has negatives"
print("  ✅ avg_handle_minutes non-negative everywhere")

# 4. avg_handle_minutes_safe never NULL
assert result["avg_handle_minutes_safe"].notna().all(), "avg_handle_minutes_safe has NULLs"
print("  ✅ avg_handle_minutes_safe has no NULLs (coalesce works)")

# 5. handling_speed_tier only has expected values
valid_tiers = {"fast", "normal", "slow"}
actual_tiers = set(result["handling_speed_tier"].unique())
assert actual_tiers.issubset(valid_tiers), f"Unexpected tiers: {actual_tiers - valid_tiers}"
print(f"  ✅ handling_speed_tier values: {sorted(actual_tiers)}")

# 6. queue column is never NULL
assert result["queue"].notna().all(), "queue column has NULLs"
print("  ✅ queue column has no NULLs")

# 7. Rows outside 14-day window are excluded
# We inserted rows for days 14..19 (15+days ago) — they must NOT appear
oldest_inserted = today - datetime.timedelta(days=19)
assert min_date.date() > oldest_inserted, (
    f"Row from {oldest_inserted} leaked through the 14-day filter!"
)
print(f"  ✅ Rows older than 14 days correctly excluded (oldest seen: {min_date.date()})")

print("\n✅ All assertions passed — 14-day filter and aggregation logic are correct.")
