import sys
import time
import subprocess
import os

def print_header(message):
    print("\n" + "=" * 80)
    print(message)
    print("=" * 80)

def run_command(command, description):
    print_header(description)
    print(f"Running: {command}")
    result = subprocess.run(command.split(), capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

def main():
    print_header("Smart Parking System Demo")
    
    # Step 1: Setup Glue Catalog
    print("\nStep 1: Setting up Glue Catalog")
    if not run_command("python glue/setup_catalog.py", "Setting up Glue Catalog"):
        print("Failed to setup Glue Catalog")
        return
    
    # Step 2: Generate and Process Events
    print("\nStep 2: Testing Data Flow")
    if not run_command("python test/test_complete_flow.py", "Testing Complete Flow"):
        print("Failed to test complete flow")
        return
    
    # Step 3: Run Analytics
    print("\nStep 3: Running Analytics Queries")
    print("Check glue/analytics_queries.sql for the complete set of analytics queries")
    
    # Step 4: Generate Visualizations
    print("\nStep 4: Generating Visualizations")
    if not run_command("python visualize/parking_analytics.py", "Creating Analytics Visualizations"):
        print("Failed to generate visualizations")
        return
    
    print_header("Demo Complete!")
    print("""
Demo Results:
1. Data Flow:
   - Events processed through MSK
   - Lambda function executed
   - Data stored in S3
   - Glue catalog updated
   - Athena queries working

2. Analytics Available:
   - Current parking status
   - Occupancy rates
   - Spot utilization
   - Daily patterns

3. Visualizations Created:
   - Current status chart
   - Occupancy rate trends
   - Spot activity analysis
   - Daily pattern heatmap

Check the 'visualize' directory for the generated charts!
""")

if __name__ == "__main__":
    main() 