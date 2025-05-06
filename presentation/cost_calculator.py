from dataclasses import dataclass
from typing import Dict, List
import math

@dataclass
class CostConfig:
    """Configuration for cost calculation"""
    # MSK Configuration
    msk_broker_count: int = 2
    msk_broker_type: str = "kafka.t3.small"  # $36/month per broker
    msk_data_ingestion_gb: float = 2.5  # Estimated monthly data ingestion
    msk_data_storage_gb: float = 0.1    # Estimated monthly data storage
    
    # Lambda Configuration
    lambda_memory_mb: int = 256
    lambda_duration_ms: int = 500
    lambda_invocations: int = 864000    # 100 spots * 12 events/hour * 24 hours * 30 days
    
    # S3 Configuration
    s3_storage_gb: float = 0.2          # Estimated monthly storage
    s3_put_requests: int = 864000       # Same as Lambda invocations
    s3_get_requests: int = 1000         # Estimated monthly queries
    
    # Athena Configuration
    athena_data_scanned_gb: float = 5.0  # Estimated monthly data scanned
    
    # CloudWatch Configuration
    cloudwatch_logs_gb: float = 2.0      # Estimated monthly log volume
    cloudwatch_storage_gb: float = 2.0   # Estimated monthly log storage

class AWSCostCalculator:
    """AWS Cost Calculator for Smart Parking System"""
    
    def __init__(self, config: CostConfig):
        self.config = config
        self.pricing = {
            'msk': {
                'broker': {
                    'kafka.t3.small': 36.00  # $36/month per broker
                },
                'data_ingestion': 0.10,      # $0.10/GB
                'data_storage': 0.10         # $0.10/GB
            },
            'lambda': {
                'compute': 0.0000166667,     # $0.0000166667 per 100ms
                'request': 0.0000002         # $0.0000002 per request
            },
            's3': {
                'storage': 0.023,            # $0.023/GB/month
                'put_request': 0.000005,     # $0.000005 per request
                'get_request': 0.0000004     # $0.0000004 per request
            },
            'athena': {
                'data_scanned': 5.00         # $5.00 per TB
            },
            'cloudwatch': {
                'logs_ingestion': 0.50,      # $0.50/GB
                'logs_storage': 0.03         # $0.03/GB/month
            }
        }
    
    def calculate_msk_cost(self) -> Dict[str, float]:
        """Calculate MSK costs"""
        broker_cost = self.config.msk_broker_count * self.pricing['msk']['broker'][self.config.msk_broker_type]
        ingestion_cost = self.config.msk_data_ingestion_gb * self.pricing['msk']['data_ingestion']
        storage_cost = self.config.msk_data_storage_gb * self.pricing['msk']['data_storage']
        
        return {
            'broker_cost': broker_cost,
            'ingestion_cost': ingestion_cost,
            'storage_cost': storage_cost,
            'total': broker_cost + ingestion_cost + storage_cost
        }
    
    def calculate_lambda_cost(self) -> Dict[str, float]:
        """Calculate Lambda costs"""
        compute_cost = (
            self.config.lambda_memory_mb / 1024 *  # Convert to GB
            self.config.lambda_duration_ms / 100 *  # Convert to 100ms units
            self.pricing['lambda']['compute'] *
            self.config.lambda_invocations
        )
        
        request_cost = (
            self.config.lambda_invocations *
            self.pricing['lambda']['request']
        )
        
        return {
            'compute_cost': compute_cost,
            'request_cost': request_cost,
            'total': compute_cost + request_cost
        }
    
    def calculate_s3_cost(self) -> Dict[str, float]:
        """Calculate S3 costs"""
        storage_cost = self.config.s3_storage_gb * self.pricing['s3']['storage']
        put_cost = self.config.s3_put_requests * self.pricing['s3']['put_request']
        get_cost = self.config.s3_get_requests * self.pricing['s3']['get_request']
        
        return {
            'storage_cost': storage_cost,
            'put_cost': put_cost,
            'get_cost': get_cost,
            'total': storage_cost + put_cost + get_cost
        }
    
    def calculate_athena_cost(self) -> Dict[str, float]:
        """Calculate Athena costs"""
        data_scanned_tb = self.config.athena_data_scanned_gb / 1024
        cost = data_scanned_tb * self.pricing['athena']['data_scanned']
        
        return {
            'data_scanned_cost': cost,
            'total': cost
        }
    
    def calculate_cloudwatch_cost(self) -> Dict[str, float]:
        """Calculate CloudWatch costs"""
        ingestion_cost = self.config.cloudwatch_logs_gb * self.pricing['cloudwatch']['logs_ingestion']
        storage_cost = self.config.cloudwatch_storage_gb * self.pricing['cloudwatch']['logs_storage']
        
        return {
            'ingestion_cost': ingestion_cost,
            'storage_cost': storage_cost,
            'total': ingestion_cost + storage_cost
        }
    
    def calculate_total_cost(self) -> Dict[str, Dict[str, float]]:
        """Calculate total costs for all services"""
        return {
            'msk': self.calculate_msk_cost(),
            'lambda': self.calculate_lambda_cost(),
            's3': self.calculate_s3_cost(),
            'athena': self.calculate_athena_cost(),
            'cloudwatch': self.calculate_cloudwatch_cost()
        }
    
    def generate_cost_report(self) -> str:
        """Generate a formatted cost report"""
        costs = self.calculate_total_cost()
        total_monthly = sum(service['total'] for service in costs.values())
        
        report = [
            "Smart Parking System - Monthly Cost Analysis",
            "===========================================",
            "",
            f"Total Monthly Cost: ${total_monthly:.2f}",
            "",
            "Breakdown by Service:",
            "-------------------"
        ]
        
        for service, cost_breakdown in costs.items():
            report.append(f"\n{service.upper()}:")
            for cost_type, amount in cost_breakdown.items():
                if cost_type != 'total':
                    report.append(f"  {cost_type}: ${amount:.2f}")
            report.append(f"  Total: ${cost_breakdown['total']:.2f}")
        
        return "\n".join(report)

def main():
    # Default configuration for 100 parking spots
    config = CostConfig()
    
    # Create calculator and generate report
    calculator = AWSCostCalculator(config)
    report = calculator.generate_cost_report()
    
    print(report)
    
    # Example of scaling analysis
    print("\nScaling Analysis:")
    print("================")
    
    spot_counts = [50, 200, 500]
    for spots in spot_counts:
        # Adjust invocations based on spot count
        config.lambda_invocations = int(864000 * (spots / 100))
        config.s3_put_requests = config.lambda_invocations
        
        calculator = AWSCostCalculator(config)
        costs = calculator.calculate_total_cost()
        total = sum(service['total'] for service in costs.values())
        
        print(f"\n{spots} Parking Spots:")
        print(f"Total Monthly Cost: ${total:.2f}")

if __name__ == "__main__":
    main() 