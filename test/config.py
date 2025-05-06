# AWS Configuration
AWS_REGION = 'eu-west-1'
S3_BUCKET = 'parking-monitoring-data'  # Replace with your bucket name
LAMBDA_FUNCTION = 'dev-parking-processor'
GLUE_DATABASE = 'dev_parking_analytics'
ATHENA_WORKGROUP = 'dev-parking-analytics'

# MSK Configuration
MSK_BOOTSTRAP_SERVERS = 'b-2.parkingmonitoringclust.iky1uh.c3.kafka.eu-west-1.amazonaws.com:9092,b-1.parkingmonitoringclust.iky1uh.c3.kafka.eu-west-1.amazonaws.com:9092'
KAFKA_TOPIC = 'parking-events'

# Test Configuration
NUM_SPOTS = 10
SIMULATION_INTERVAL = 5  # seconds
SIMULATION_DURATION = 5  # minutes
VERIFICATION_WINDOW = 5  # minutes 