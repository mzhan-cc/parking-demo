CREATE EXTERNAL TABLE IF NOT EXISTS parking_analytics.parking_events (
    spot_id string,
    status string,
    timestamp string
)
PARTITIONED BY (
    year string,
    month string,
    day string,
    hour string
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://parking-monitoring-data/parking-data/'
TBLPROPERTIES ('has_encrypted_data'='false'); 