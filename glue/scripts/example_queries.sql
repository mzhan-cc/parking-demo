-- Get hourly occupancy rate
SELECT 
    year,
    month,
    day,
    hour,
    COUNT(*) as total_events,
    COUNT(CASE WHEN status = 'occupied' THEN 1 END) as occupied_spots,
    CAST(COUNT(CASE WHEN status = 'occupied' THEN 1 END) AS DOUBLE) / COUNT(*) * 100 as occupancy_rate
FROM parking_data
GROUP BY year, month, day, hour
ORDER BY year, month, day, hour;

-- Find peak hours (top 10 busiest hours)
SELECT 
    year,
    month,
    day,
    hour,
    COUNT(*) as total_events,
    COUNT(CASE WHEN status = 'occupied' THEN 1 END) as occupied_spots,
    CAST(COUNT(CASE WHEN status = 'occupied' THEN 1 END) AS DOUBLE) / COUNT(*) * 100 as occupancy_rate
FROM parking_data
GROUP BY year, month, day, hour
ORDER BY occupancy_rate DESC
LIMIT 10;

-- Get average occupancy by day of week
SELECT 
    day_of_week(from_iso8601_timestamp(timestamp)) as day_of_week,
    COUNT(*) as total_events,
    COUNT(CASE WHEN status = 'occupied' THEN 1 END) as occupied_spots,
    CAST(COUNT(CASE WHEN status = 'occupied' THEN 1 END) AS DOUBLE) / COUNT(*) * 100 as avg_occupancy_rate
FROM parking_data
GROUP BY day_of_week(from_iso8601_timestamp(timestamp))
ORDER BY day_of_week;

-- Get average duration of occupancy per spot
WITH status_changes AS (
    SELECT 
        spot_id,
        timestamp,
        status,
        LEAD(timestamp) OVER (PARTITION BY spot_id ORDER BY timestamp) as next_timestamp
    FROM parking_data
    WHERE status = 'occupied'
)
SELECT 
    spot_id,
    AVG(date_diff('minute', from_iso8601_timestamp(timestamp), from_iso8601_timestamp(next_timestamp))) as avg_occupancy_minutes
FROM status_changes
WHERE next_timestamp IS NOT NULL
GROUP BY spot_id
ORDER BY avg_occupancy_minutes DESC; 