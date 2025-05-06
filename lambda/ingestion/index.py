import os
import json
import boto3
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize S3 client
s3 = boto3.client('s3')
S3_BUCKET = os.environ['S3_BUCKET']

def handler(event, context):
    """
    Process parking events from MSK and store them in S3.
    Event format:
    {
        "spot_id": "A1",
        "status": "occupied",
        "timestamp": "2024-03-20T10:00:00Z"
    }
    """
    try:
        logger.info(f"Processing {len(event['records'])} records")
        
        for record in event['records']:
            # Decode and parse the message
            message = json.loads(record['value'])
            logger.info(f"Processing message: {message}")
            
            # Extract timestamp for partitioning
            timestamp = datetime.strptime(message['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
            partition_path = f"year={timestamp.year}/month={timestamp.month:02d}/day={timestamp.day:02d}/hour={timestamp.hour:02d}"
            
            # Generate S3 key
            s3_key = f"parking-data/{partition_path}/{record['topic']}-{record['partition']}-{record['offset']}.json"
            
            # Store the event in S3
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=s3_key,
                Body=json.dumps(message),
                ContentType='application/json'
            )
            
            logger.info(f"Stored event in S3: s3://{S3_BUCKET}/{s3_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully processed {len(event["records"])} records',
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing records: {str(e)}")
        raise 