import boto3
import time

# Initialize Glue client
glue = boto3.client('glue')

def create_database():
    """Create Glue database"""
    try:
        glue.create_database(
            DatabaseInput={
                'Name': 'parking_analytics',
                'Description': 'Database for parking monitoring analytics'
            }
        )
        print("Created database: parking_analytics")
    except glue.exceptions.AlreadyExistsException:
        print("Database already exists")

def delete_table_if_exists():
    """Delete table if it exists"""
    try:
        glue.delete_table(
            DatabaseName='parking_analytics',
            Name='parking_events'
        )
        print("Deleted existing table")
        time.sleep(5)  # Wait for deletion to complete
    except glue.exceptions.EntityNotFoundException:
        print("Table does not exist")

def create_table():
    """Create Glue table"""
    try:
        glue.create_table(
            DatabaseName='parking_analytics',
            TableInput={
                'Name': 'parking_events',
                'Description': 'Parking events data',
                'TableType': 'EXTERNAL_TABLE',
                'Parameters': {
                    'classification': 'json',
                    'typeOfData': 'file',
                    'EXTERNAL': 'TRUE'
                },
                'StorageDescriptor': {
                    'Columns': [
                        {'Name': 'spot_id', 'Type': 'string'},
                        {'Name': 'status', 'Type': 'string'},
                        {'Name': 'timestamp', 'Type': 'string'}
                    ],
                    'Location': 's3://parking-monitoring-data/parking-data',
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.openx.data.jsonserde.JsonSerDe',
                        'Parameters': {
                            'serialization.format': '1',
                            'paths': 'spot_id,status,timestamp'
                        }
                    },
                    'Compressed': False
                },
                'PartitionKeys': [
                    {'Name': 'year', 'Type': 'string'},
                    {'Name': 'month', 'Type': 'string'},
                    {'Name': 'day', 'Type': 'string'},
                    {'Name': 'hour', 'Type': 'string'}
                ]
            }
        )
        print("Created table: parking_events")
    except Exception as e:
        print(f"Error creating table: {str(e)}")

def update_partitions():
    """Update table partitions using Athena"""
    athena = boto3.client('athena')
    
    try:
        # Run MSCK REPAIR TABLE
        query = "MSCK REPAIR TABLE parking_analytics.parking_events"
        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': 'parking_analytics'
            },
            ResultConfiguration={
                'OutputLocation': 's3://parking-monitoring-data/athena-results/'
            }
        )
        
        # Wait for query to complete
        query_execution_id = response['QueryExecutionId']
        print(f"Started partition update: {query_execution_id}")
        
        while True:
            query_status = athena.get_query_execution(QueryExecutionId=query_execution_id)
            state = query_status['QueryExecution']['Status']['State']
            
            if state == 'SUCCEEDED':
                print("Successfully updated partitions")
                break
            elif state in ['FAILED', 'CANCELLED']:
                print(f"Failed to update partitions: {state}")
                break
            
            print(f"Partition update status: {state}")
            time.sleep(2)
            
    except Exception as e:
        print(f"Error updating partitions: {str(e)}")

def main():
    print("Setting up Glue Catalog...")
    
    # Create database
    create_database()
    
    # Delete existing table if any
    delete_table_if_exists()
    
    # Create table
    create_table()
    
    # Update partitions
    print("\nUpdating partitions...")
    update_partitions()
    
    print("\nGlue Catalog setup complete!")

if __name__ == "__main__":
    main() 