-- Current parking status for all spots
SELECT spot_id, 
       status,
       timestamp,
       CONCAT(year, '-', month, '-', day, ' ', hour, ':00:00') as event_time
FROM parking_analytics.parking_events
ORDER BY timestamp DESC
LIMIT 10;

-- Occupancy rate by hour
SELECT CONCAT(year, '-', month, '-', day, ' ', hour, ':00:00') as hour_slot,
       COUNT(CASE WHEN status = 'occupied' THEN 1 END) * 100.0 / COUNT(*) as occupancy_rate,
       COUNT(*) as total_events
FROM parking_analytics.parking_events
GROUP BY year, month, day, hour
ORDER BY year, month, day, hour DESC;

-- Most active parking spots
SELECT spot_id,
       COUNT(*) as total_events,
       COUNT(CASE WHEN status = 'occupied' THEN 1 END) as times_occupied,
       COUNT(CASE WHEN status = 'vacant' THEN 1 END) as times_vacant,
       ROUND(COUNT(CASE WHEN status = 'occupied' THEN 1 END) * 100.0 / COUNT(*), 2) as occupancy_rate
FROM parking_analytics.parking_events
GROUP BY spot_id
ORDER BY total_events DESC;

-- Daily occupancy patterns
SELECT CONCAT(year, '-', month, '-', day) as date,
       hour,
       COUNT(CASE WHEN status = 'occupied' THEN 1 END) as occupied_spots,
       COUNT(CASE WHEN status = 'vacant' THEN 1 END) as vacant_spots
FROM parking_analytics.parking_events
GROUP BY year, month, day, hour
ORDER BY year, month, day, hour; 