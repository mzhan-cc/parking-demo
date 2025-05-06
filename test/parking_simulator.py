import json
import time
import random
from datetime import datetime, timedelta
from kafka import KafkaProducer
import logging
import socket
from config import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_msk_connectivity():
    """Check if MSK bootstrap servers are reachable."""
    for server in MSK_BOOTSTRAP_SERVERS.split(','):
        host, port = server.split(':')
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, int(port)))
            if result == 0:
                logger.info(f"Successfully connected to {server}")
            else:
                logger.error(f"Failed to connect to {server}")
            sock.close()
        except Exception as e:
            logger.error(f"Error checking connectivity to {server}: {str(e)}")

def create_producer():
    """Create a Kafka producer with SSL configuration."""
    try:
        logger.info(f"Attempting to connect to MSK cluster at {MSK_BOOTSTRAP_SERVERS}")
        producer = KafkaProducer(
            bootstrap_servers=MSK_BOOTSTRAP_SERVERS,
            security_protocol='SSL',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            request_timeout_ms=10000,  # 10 seconds timeout
            api_version_auto_timeout_ms=10000
        )
        logger.info("Successfully created Kafka producer")
        return producer
    except Exception as e:
        logger.error(f"Failed to create Kafka producer: {str(e)}")
        raise

def generate_parking_event(spot_id):
    """Generate a random parking event."""
    status = random.choice(['occupied', 'vacant'])
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    return {
        'spot_id': spot_id,
        'status': status,
        'timestamp': timestamp
    }

def simulate_parking_sensors(num_spots=NUM_SPOTS, interval=SIMULATION_INTERVAL, duration_minutes=SIMULATION_DURATION):
    """Simulate multiple parking sensors sending events."""
    logger.info("Checking MSK connectivity...")
    check_msk_connectivity()
    
    try:
        producer = create_producer()
    except Exception as e:
        logger.error("Failed to create producer, aborting simulation")
        return
    
    end_time = datetime.now() + timedelta(minutes=duration_minutes)
    
    try:
        logger.info(f"Starting simulation with {num_spots} parking spots")
        while datetime.now() < end_time:
            for spot_id in range(1, num_spots + 1):
                event = generate_parking_event(f'A{spot_id}')
                try:
                    future = producer.send(KAFKA_TOPIC, value=event)
                    # Wait for the message to be delivered
                    record_metadata = future.get(timeout=10)
                    logger.info(f"Sent event: {event} to partition {record_metadata.partition}")
                except Exception as e:
                    logger.error(f"Failed to send event: {str(e)}")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("Simulation stopped by user")
    except Exception as e:
        logger.error(f"Error during simulation: {str(e)}")
    finally:
        producer.close()
        logger.info("Simulation completed")

if __name__ == "__main__":
    simulate_parking_sensors() 