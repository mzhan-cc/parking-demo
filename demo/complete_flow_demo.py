import json
import time
import random
import boto3
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# AWS clients
s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')
glue = boto3.client('glue')
athena = boto3.client('athena')

def generate_parking_event():
    """Generate a sample parking event"""
    return {
        "spot_id": f"A{random.randint(1, 10)}",
        "status": random.choice(["occupied", "vacant"]),
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }

def test_lambda_direct():
    """Test Lambda function directly"""
    logger.info("\n1. Testing Lambda Function Directly")
    logger.info("-----------------------------------")
    
    # Create test event
    test_event = {
        "records": [
            {
                "topic": "parking-events",
                "partition": 0,
                "offset": 0,
                "value": json.dumps(generate_parking_event())
            }
        ]
    }
    
    # Invoke Lambda
    try:
        response = lambda_client.invoke(
            FunctionName='dev-parking-processor',
            Payload=json.dumps(test_event)
        )
        logger.info(f"Lambda Response: {json.loads(response['Payload'].read())}")
        return True
    except Exception as e:
        logger.error(f"Error invoking Lambda: {str(e)}")
        return False

def check_s3_data():
    """Check data in S3"""
    logger.info("\n2. Checking S3 Data")
    logger.info("------------------")
    
    try:
        response = s3.list_objects_v2(
            Bucket='parking-monitoring-data',
            Prefix='parking-data/'
        )
        
        if 'Contents' in response:
            logger.info("Found data in S3:")
            for obj in response['Contents'][:5]:
                logger.info(f"- {obj['Key']}")
                content = s3.get_object(Bucket='parking-monitoring-data', Key=obj['Key'])
                data = json.loads(content['Body'].read().decode('utf-8'))
                logger.info(f"  Content: {json.dumps(data, indent=2)}")
        else:
            logger.info("No data found in S3")
    except Exception as e:
        logger.error(f"Error checking S3 data: {str(e)}")

def run_athena_query():
    """Run Athena query to verify data"""
    logger.info("\n3. Running Athena Query")
    logger.info("----------------------")
    
    query = """
    SELECT spot_id, status, timestamp,
           year, month, day, hour
    FROM parking_analytics.parking_events
    ORDER BY timestamp DESC
    LIMIT 5
    """
    
    try:
        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': 'parking_analytics'},
            ResultConfiguration={
                'OutputLocation': 's3://parking-monitoring-data/athena-results/'
            },
            WorkGroup='primary'
        )
        
        query_execution_id = response['QueryExecutionId']
        logger.info(f"Started query execution: {query_execution_id}")
        
        while True:
            query_status = athena.get_query_execution(QueryExecutionId=query_execution_id)
            state = query_status['QueryExecution']['Status']['State']
            
            if state == 'SUCCEEDED':
                results = athena.get_query_results(QueryExecutionId=query_execution_id)
                logger.info("\nQuery Results:")
                if 'ResultSet' in results and 'Rows' in results['ResultSet']:
                    header = [col['VarCharValue'] for col in results['ResultSet']['Rows'][0]['Data']]
                    logger.info(f"Columns: {', '.join(header)}")
                    
                    for row in results['ResultSet']['Rows'][1:]:
                        values = [col.get('VarCharValue', 'NULL') for col in row['Data']]
                        logger.info(f"Row: {', '.join(values)}")
                break
            elif state in ['FAILED', 'CANCELLED']:
                logger.error(f"Query {state.lower()}")
                break
            
            time.sleep(2)
    except Exception as e:
        logger.error(f"Error running Athena query: {str(e)}")

def main():
    logger.info("Starting Complete Flow Demo")
    logger.info("==========================")
    
    try:
        # 1. Test Lambda function with multiple events
        logger.info("\n1. Testing Lambda Function with Multiple Events")
        for _ in range(5):
            if test_lambda_direct():
                logger.info("Event processed successfully")
            else:
                logger.error("Failed to process event")
            time.sleep(1)  # Small delay between events
        
        # 2. Wait for processing
        logger.info("\n2. Waiting for data processing...")
        time.sleep(10)  # Give Lambda time to process
        
        # 3. Check S3 data
        check_s3_data()
        
        # 4. Run Athena query
        run_athena_query()
        
        logger.info("\nDemo completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")

if __name__ == "__main__":
    main() 