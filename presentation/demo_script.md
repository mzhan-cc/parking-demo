# Smart Parking System Demo Script

## Prerequisites
1. AWS Console open
2. Terminal with demo code ready
3. Visualizations generated
4. Test data prepared

## Demo Flow

### 1. Architecture Overview (2 minutes)
- Show architecture diagram
- Explain each component
- Highlight serverless nature
- Point out data flow

### 2. AWS Console Tour (3 minutes)
- MSK Cluster
  - Show bootstrap servers
  - Explain VPC configuration
  - Point out security groups

- Lambda Function
  - Show function code
  - Explain event source mapping
  - Show IAM roles

- S3 Bucket
  - Show partitioned data
  - Explain folder structure
  - Show JSON format

### 3. Live Demo (5 minutes)
1. Generate Test Events
   ```bash
   python test/test_complete_flow.py
   ```
   - Watch Lambda logs
   - Check S3 for new files
   - Verify partitioning

2. Show Analytics
   - Run Athena queries
   - Display results
   - Explain partitioning benefits

3. Display Visualizations
   - Current status
   - Occupancy rates
   - Spot utilization
   - Daily patterns

### 4. Technical Highlights (3 minutes)
- Event-driven architecture
- Serverless benefits
- Cost optimization
- Scaling capabilities

### 5. Q&A Preparation
Common questions to expect:
1. How does it scale?
2. What's the cost?
3. How to handle failures?
4. Production deployment?

## Demo Tips
1. Keep AWS Console and terminal side by side
2. Have backup test data ready
3. Prepare for common errors
4. Keep timing in mind
5. Have visualizations pre-generated

## Success Metrics
- Real-time processing
- Data accuracy
- Query performance
- Visualization quality 