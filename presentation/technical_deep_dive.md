# Smart Parking System - Technical Deep Dive

## Architecture Components

### 1. MSK (Managed Streaming for Kafka)
- Cluster Configuration
  - VPC: vpc-048923e3e5fd693de
  - Subnets: subnet-0868010d2e66bb7f6, subnet-0e34a279cd23754d4
  - Security Group: sg-0f53d3c7192ba3194
  - Bootstrap Servers: Configured for VPC access

- Event Format
  ```json
  {
    "spot_id": "A1",
    "status": "occupied",
    "timestamp": "2024-03-20T10:00:00Z"
  }
  ```

### 2. Lambda Function
- Runtime: Python 3.9
- Memory: 256MB
- Timeout: 30 seconds
- VPC Configuration
  - Security Group: sg-085abaf11ad63f400
  - Subnets: Same as MSK
  - VPC Endpoints: S3, CloudWatch Logs

- IAM Role: ParkingDataIngestionRole
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "s3:PutObject",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource": "*"
      }
    ]
  }
  ```

### 3. S3 Storage
- Bucket: parking-monitoring-data
- Partitioning Structure:
  ```
  parking-data/
  ├── year=2024/
  │   └── month=03/
  │       └── day=20/
  │           └── hour=10/
  └── year=2025/
      └── month=05/
          └── day=06/
              └── hour=18/
  ```

### 4. Glue Data Catalog
- Database: parking_analytics
- Table: parking_events
- Schema:
  ```sql
  CREATE EXTERNAL TABLE parking_analytics.parking_events (
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
  STORED AS JSON
  LOCATION 's3://parking-monitoring-data/parking-data/'
  ```

### 5. Athena Queries
- Workgroup: primary
- Query Result Location: s3://parking-monitoring-data/athena-results/
- Common Queries:
  - Current status
  - Occupancy rates
  - Spot utilization
  - Daily patterns

## Best Practices

### 1. VPC Configuration
- Use private subnets
- Configure security groups properly
- Set up VPC endpoints
- Monitor network performance

### 2. Security
- Least privilege IAM roles
- Encrypt data at rest
- Use VPC for network isolation
- Regular security audits

### 3. Performance
- Optimize Lambda memory
- Use appropriate batch sizes
- Partition data effectively
- Monitor query performance

### 4. Cost Optimization
- Right-size Lambda resources
- Use appropriate storage classes
- Monitor data transfer costs
- Clean up old data

## Monitoring and Maintenance

### 1. CloudWatch Metrics
- Lambda execution time
- MSK broker metrics
- S3 storage usage
- Athena query performance

### 2. Logging
- Lambda function logs
- MSK broker logs
- S3 access logs
- Athena query logs

### 3. Alerts
- Lambda errors
- MSK broker health
- S3 storage thresholds
- Query performance

## Scaling Considerations

### 1. Horizontal Scaling
- MSK broker scaling
- Lambda concurrency
- S3 partition limits
- Athena query concurrency

### 2. Vertical Scaling
- Lambda memory
- MSK broker size
- S3 storage class
- Query optimization

### 3. Cost Scaling
- Monitor usage patterns
- Optimize resource allocation
- Use appropriate storage classes
- Clean up unused resources 