# Smart Parking Monitoring System

A real-time parking monitoring system built with AWS services that tracks parking spot availability, provides analytics, and offers real-time updates.

## Architecture

The system uses the following AWS services:

- **Amazon MSK (Managed Streaming for Kafka)**
  - 2 kafka.t3.small brokers
  - Handles real-time event streaming
  - Processes parking events (entry/exit)

- **AWS Lambda**
  - Ingestion function (256MB, 500ms)
  - Processes events from MSK
  - Stores data in S3

- **Amazon S3**
  - Stores parking event data
  - Organized by date/hour
  - Optimized for Athena queries

- **Amazon Athena**
  - SQL queries for analytics
  - Predefined queries for common metrics
  - Cost-effective querying

- **Amazon CloudWatch**
  - Monitors system health
  - Tracks metrics and logs
  - Alerts for issues

## Project Structure

```
parking-demo/
├── lambda/              # Lambda functions
│   ├── ingestion/      # Event ingestion
│   └── analytics/      # Analytics processing
├── terraform/          # Infrastructure as Code
│   ├── modules/        # Reusable modules
│   └── environments/   # Environment configs
├── glue/              # ETL and analytics
│   └── analytics_queries.sql
├── test/              # Test scripts
│   ├── parking_simulator.py
│   └── test_complete_flow.py
└── demo/              # Demo scripts
    └── run_demo.py
```

## Getting Started

### Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform installed
- Python 3.8+
- Docker (for local testing)

### Setup

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd parking-demo
   ```

2. **Install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scriptsctivate` on Windows
   pip install -r requirements.txt
   ```

3. **Deploy infrastructure**
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

4. **Run tests**
   ```bash
   python -m pytest test/
   ```

5. **Run demo**
   ```bash
   python demo/run_demo.py
   ```

## Cost Estimates

Monthly costs (US East region):

- **MSK**: .00
  - 2 kafka.t3.small brokers (.00 each)
  - Data ingestion: /bin/zsh.25 (2.5GB)
  - Storage: /bin/zsh.01 (0.1GB)

- **Lambda**: .40
  - Compute: .40 (864,000 invocations)
  - Request: /bin/zsh.17 (864,000 requests)

- **S3**: .68
  - Storage: /bin/zsh.01 (0.2GB)
  - PUT requests: .32 (864,000 requests)
  - GET requests: /bin/zsh.35 (864,000 requests)

- **Athena**: /bin/zsh.03
  - Data scanned: /bin/zsh.03 (5GB)

- **CloudWatch**: /bin/zsh.50
  - Log storage: /bin/zsh.50 (2GB)

**Total Estimated Monthly Cost**: .19

## Monitoring and Analytics

The system provides:

1. **Real-time Monitoring**
   - Current parking spot availability
   - System health metrics
   - Error tracking

2. **Analytics**
   - Occupancy rates
   - Peak usage times
   - Historical trends
   - Revenue analysis

3. **Alerts**
   - System issues
   - Capacity warnings
   - Performance metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the maintainers.