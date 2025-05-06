import json
import boto3
import time
from datetime import datetime
import random

# Initialize AWS clients
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
    print("\n1. Testing Lambda Function Directly")
    print("-----------------------------------")
    
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
    response = lambda_client.invoke(
        FunctionName='dev-parking-processor',
        Payload=json.dumps(test_event)
    )
    
    print(f"Lambda Response: {json.loads(response['Payload'].read())}")

def check_s3_data():
    """Check data in S3"""
    print("\n2. Checking S3 Data")
    print("------------------")
    
    # List objects in the bucket
    response = s3.list_objects_v2(
        Bucket='parking-monitoring-data',
        Prefix='parking-data/'
    )
    
    if 'Contents' in response:
        print("Found data in S3:")
        for obj in response['Contents'][:5]:  # Show first 5 objects
            print(f"- {obj['Key']}")
            # Get and print the content of each file
            content = s3.get_object(Bucket='parking-monitoring-data', Key=obj['Key'])
            data = json.loads(content['Body'].read().decode('utf-8'))
            print(f"  Content: {json.dumps(data, indent=2)}")
    else:
        print("No data found in S3")

def check_glue_catalog():
    """Check Glue Data Catalog"""
    print("\n3. Checking Glue Data Catalog")
    print("----------------------------")
    
    try:
        # Get database
        database = glue.get_database(Name='parking_analytics')
        print(f"Database: {database['Database']['Name']}")
        
        # Get tables
        tables = glue.get_tables(DatabaseName='parking_analytics')
        print("\nTables:")
        for table in tables['TableList']:
            print(f"- {table['Name']}")
            print(f"  Location: {table['StorageDescriptor']['Location']}")
            print(f"  Columns:")
            for column in table['StorageDescriptor']['Columns']:
                print(f"    - {column['Name']}: {column['Type']}")
    except Exception as e:
        print(f"Error checking Glue catalog: {str(e)}")

def repair_table_partitions():
    """Repair table partitions"""
    print("\n3.5 Repairing Table Partitions")
    print("-----------------------------")
    
    repair_query = "MSCK REPAIR TABLE parking_analytics.parking_events"
    
    try:
        # Start repair query
        response = athena.start_query_execution(
            QueryString=repair_query,
            QueryExecutionContext={
                'Database': 'parking_analytics'
            },
            ResultConfiguration={
                'OutputLocation': 's3://parking-monitoring-data/athena-results/'
            },
            WorkGroup='primary'
        )
        
        query_execution_id = response['QueryExecutionId']
        print(f"Started partition repair: {query_execution_id}")
        
        # Wait for repair to complete
        while True:
            query_status = athena.get_query_execution(QueryExecutionId=query_execution_id)
            state = query_status['QueryExecution']['Status']['State']
            
            if state == 'FAILED':
                error = query_status['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
                print(f"Repair failed: {error}")
                break
            elif state == 'CANCELLED':
                print("Repair was cancelled")
                break
            elif state == 'SUCCEEDED':
                print("Partition repair completed successfully")
                break
            
            print(f"Repair status: {state}")
            time.sleep(2)
            
    except Exception as e:
        print(f"Error repairing partitions: {str(e)}")

def run_athena_query():
    """Run Athena query"""
    print("\n4. Running Athena Query")
    print("----------------------")
    
    # Query to get current parking status
    query = """
    SELECT spot_id, status, timestamp,
           year, month, day, hour
    FROM parking_analytics.parking_events
    ORDER BY timestamp DESC
    LIMIT 5
    """
    
    try:
        # Start query execution
        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': 'parking_analytics'
            },
            ResultConfiguration={
                'OutputLocation': 's3://parking-monitoring-data/athena-results/'
            },
            WorkGroup='primary'  # Using the default workgroup
        )
        
        query_execution_id = response['QueryExecutionId']
        print(f"Started query execution: {query_execution_id}")
        
        # Wait for query to complete
        while True:
            query_status = athena.get_query_execution(QueryExecutionId=query_execution_id)
            state = query_status['QueryExecution']['Status']['State']
            
            if state == 'FAILED':
                error = query_status['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
                print(f"Query failed: {error}")
                break
            elif state == 'CANCELLED':
                print("Query was cancelled")
                break
            elif state == 'SUCCEEDED':
                # Get results
                results = athena.get_query_results(QueryExecutionId=query_execution_id)
                
                # Print results
                print("\nQuery Results:")
                if 'ResultSet' in results and 'Rows' in results['ResultSet']:
                    # Get header
                    header = [col['VarCharValue'] for col in results['ResultSet']['Rows'][0]['Data']]
                    print(f"Columns: {', '.join(header)}")
                    
                    # Print data rows
                    for row in results['ResultSet']['Rows'][1:]:
                        values = [col.get('VarCharValue', 'NULL') for col in row['Data']]
                        print(f"Row: {', '.join(values)}")
                else:
                    print("No results found")
                break
            
            print(f"Query status: {state}")
            time.sleep(2)
            
    except Exception as e:
        print(f"Error running Athena query: {str(e)}")
        print("Please check:")
        print("1. Athena workgroup 'primary' exists and is enabled")
        print("2. S3 output location is accessible")
        print("3. IAM permissions are correct")

def main():
    print("Parking Monitoring System - Complete Flow Demo")
    print("============================================")
    
    # 1. Test Lambda function
    test_lambda_direct()
    
    # Wait for data processing
    print("\nWaiting for data processing...")
    time.sleep(5)
    
    # 2. Check S3 data
    check_s3_data()
    
    # 3. Check Glue catalog
    check_glue_catalog()
    
    # 3.5 Repair table partitions
    repair_table_partitions()
    
    # 4. Run Athena query
    run_athena_query()

if __name__ == "__main__":
    main() 