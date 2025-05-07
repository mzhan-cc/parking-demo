import json
import time
import random
from datetime import datetime
import logging
from collections import deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simulated Kafka topic
KAFKA_TOPIC = 'parking-events'
kafka_messages = deque()

def print_step(step, total, message):
    """Print a formatted step message"""
    logger.info(f"\nStep {step}/{total}: {message}")
    logger.info("-" * 80)

def generate_parking_event():
    """Generate a sample parking event"""
    return {
        "spot_id": f"A{random.randint(1, 10)}",
        "status": random.choice(["occupied", "vacant"]),
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }

def simulate_kafka_producer(event):
    """Simulate sending event to Kafka"""
    try:
        # Simulate network delay
        time.sleep(0.5)
        kafka_messages.append(event)
        logger.info(f"Event sent to Kafka: {event}")
        logger.info(f"Topic: {KAFKA_TOPIC}")
        logger.info(f"Partition: 0")
        logger.info(f"Offset: {len(kafka_messages) - 1}")
        return True
    except Exception as e:
        logger.error(f"Failed to send event to Kafka: {str(e)}")
        return False

def simulate_kafka_consumer():
    """Simulate consuming events from Kafka"""
    logger.info("Starting to consume events from Kafka...")
    events = []
    
    while kafka_messages:
        event = kafka_messages.popleft()
        events.append(event)
        logger.info(f"Received event: {event}")
        # Simulate processing time
        time.sleep(0.5)
    
    return events

def simulate_lambda_processing(events):
    """Simulate Lambda processing events"""
    logger.info("\nSimulating Lambda processing...")
    processed_events = []
    
    for event in events:
        # Simulate Lambda processing
        time.sleep(0.5)
        processed_event = {
            **event,
            "processed_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "year": datetime.utcnow().year,
            "month": datetime.utcnow().month,
            "day": datetime.utcnow().day,
            "hour": datetime.utcnow().hour
        }
        processed_events.append(processed_event)
        logger.info(f"Lambda processed event: {processed_event}")
    
    return processed_events

def simulate_s3_storage(events):
    """Simulate storing events in S3"""
    logger.info("\nSimulating S3 storage...")
    
    # Group events by partition
    partitions = {}
    for event in events:
        partition = f"year={event['year']}/month={event['month']}/day={event['day']}/hour={event['hour']}"
        if partition not in partitions:
            partitions[partition] = []
        partitions[partition].append(event)
    
    # Simulate storing in S3
    for partition, partition_events in partitions.items():
        logger.info(f"\nStoring in S3 partition: {partition}")
        for event in partition_events:
            logger.info(f"  Stored event: {event}")

def simulate_athena_query(events):
    """Simulate Athena query"""
    logger.info("\nSimulating Athena query...")
    
    # Sort events by timestamp
    sorted_events = sorted(events, key=lambda x: x['timestamp'], reverse=True)
    
    # Print results in table format
    logger.info("\nQuery Results:")
    logger.info("spot_id | status  | timestamp           | year | month | day | hour")
    logger.info("-" * 80)
    
    for event in sorted_events[:5]:  # Show only 5 most recent events
        logger.info(f"{event['spot_id']:7} | {event['status']:7} | {event['timestamp']} | {event['year']} | {event['month']:5} | {event['day']:3} | {event['hour']:4}")

def main():
    logger.info("Starting Simulated Flow Demo")
    logger.info("==========================")
    
    try:
        # Step 1: Generate events
        print_step(1, 5, "Generating parking events")
        events = [generate_parking_event() for _ in range(5)]
        for event in events:
            logger.info(f"Generated event: {event}")
        
        # Step 2: Send to Kafka
        print_step(2, 5, "Sending events to Kafka")
        for event in events:
            simulate_kafka_producer(event)
            time.sleep(0.5)  # Small delay between events
        
        # Step 3: Consume from Kafka
        print_step(3, 5, "Consuming events from Kafka")
        consumed_events = simulate_kafka_consumer()
        logger.info(f"Consumed {len(consumed_events)} events")
        
        # Step 4: Process with Lambda and store in S3
        print_step(4, 5, "Processing events with Lambda and storing in S3")
        processed_events = simulate_lambda_processing(consumed_events)
        simulate_s3_storage(processed_events)
        
        # Step 5: Query with Athena
        print_step(5, 5, "Querying data with Athena")
        simulate_athena_query(processed_events)
        
        logger.info("\nDemo completed successfully!")
        logger.info("\nFlow Summary:")
        logger.info("1. Events generated and sent to Kafka")
        logger.info("2. Events consumed from Kafka")
        logger.info("3. Lambda processed events and stored in S3")
        logger.info("4. Data verified through Athena query")
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")

if __name__ == "__main__":
    main() 