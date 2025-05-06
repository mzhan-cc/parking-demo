import boto3
import time
import logging
from datetime import datetime
from config import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AthenaQueryTester:
    def __init__(self, database=GLUE_DATABASE, workgroup=ATHENA_WORKGROUP, output_location=f's3://{S3_BUCKET}/athena-results/'):
        self.athena = boto3.client('athena')
        self.database = database
        self.workgroup = workgroup
        self.output_location = output_location

    def run_query(self, query):
        """Execute an Athena query and wait for results."""
        try:
            # Start query execution
            response = self.athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': self.database},
                ResultConfiguration={'OutputLocation': self.output_location},
                WorkGroup=self.workgroup
            )
            
            query_execution_id = response['QueryExecutionId']
            logger.info(f"Started query execution: {query_execution_id}")
            
            # Wait for query to complete
            while True:
                response = self.athena.get_query_execution(QueryExecutionId=query_execution_id)
                state = response['QueryExecution']['Status']['State']
                
                if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                    break
                    
                time.sleep(1)
            
            if state == 'SUCCEEDED':
                # Get results
                results = self.athena.get_query_results(QueryExecutionId=query_execution_id)
                
                # Print column names
                columns = [col['Label'] for col in results['ResultSet']['Rows'][0]['Data']]
                logger.info("Columns: " + " | ".join(columns))
                
                # Print data rows
                for row in results['ResultSet']['Rows'][1:]:
                    values = [field.get('VarCharValue', '') for field in row['Data']]
                    logger.info(" | ".join(values))
                
                return True
            else:
                logger.error(f"Query failed with state: {state}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return False

def test_queries():
    """Run a series of test queries."""
    tester = AthenaQueryTester()
    
    queries = [
        # Hourly occupancy rates
        """
        SELECT 
            date_trunc('hour', timestamp) as hour,
            count(*) as total_events,
            sum(case when status = 'occupied' then 1 else 0 end) as occupied_spots,
            round(sum(case when status = 'occupied' then 1 else 0 end)::decimal / count(*) * 100, 2) as occupancy_rate
        FROM parking_events
        GROUP BY date_trunc('hour', timestamp)
        ORDER BY hour DESC
        LIMIT 24
        """,
        
        # Peak hours
        """
        SELECT 
            date_trunc('hour', timestamp) as hour,
            count(*) as total_events,
            sum(case when status = 'occupied' then 1 else 0 end) as occupied_spots,
            round(sum(case when status = 'occupied' then 1 else 0 end)::decimal / count(*) * 100, 2) as occupancy_rate
        FROM parking_events
        GROUP BY date_trunc('hour', timestamp)
        ORDER BY occupancy_rate DESC
        LIMIT 10
        """,
        
        # Day of week analysis
        """
        SELECT 
            day_of_week(timestamp) as day,
            count(*) as total_events,
            sum(case when status = 'occupied' then 1 else 0 end) as occupied_spots,
            round(sum(case when status = 'occupied' then 1 else 0 end)::decimal / count(*) * 100, 2) as occupancy_rate
        FROM parking_events
        GROUP BY day_of_week(timestamp)
        ORDER BY day
        """
    ]
    
    for i, query in enumerate(queries, 1):
        logger.info(f"\nExecuting query {i}...")
        success = tester.run_query(query)
        if success:
            logger.info(f"✅ Query {i} completed successfully")
        else:
            logger.error(f"❌ Query {i} failed")

if __name__ == "__main__":
    test_queries() 