import boto3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json

# Initialize clients
athena = boto3.client('athena')
s3 = boto3.client('s3')

def run_athena_query(query):
    """Run Athena query and return results as pandas DataFrame"""
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': 'parking_analytics'},
        ResultConfiguration={'OutputLocation': 's3://parking-monitoring-data/athena-results/'}
    )
    
    query_execution_id = response['QueryExecutionId']
    
    # Wait for query to complete
    while True:
        response = athena.get_query_execution(QueryExecutionId=query_execution_id)
        state = response['QueryExecution']['Status']['State']
        if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
    
    if state == 'SUCCEEDED':
        # Get results
        results = athena.get_query_results(QueryExecutionId=query_execution_id)
        
        # Convert to DataFrame
        columns = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
        rows = []
        for row in results['ResultSet']['Rows'][1:]:  # Skip header
            rows.append([field.get('VarCharValue', '') for field in row['Data']])
        
        return pd.DataFrame(rows, columns=columns)
    else:
        raise Exception(f"Query failed with state: {state}")

def plot_current_status(df):
    """Plot current parking status"""
    plt.figure(figsize=(12, 6))
    colors = ['red' if status == 'occupied' else 'green' for status in df['status']]
    plt.bar(df['spot_id'], [1] * len(df), color=colors)
    plt.title('Current Parking Status')
    plt.xlabel('Parking Spot')
    plt.ylabel('Status')
    plt.legend(['Red = Occupied, Green = Vacant'])
    plt.savefig('visualize/current_status.png')
    plt.close()

def plot_occupancy_rate(df):
    """Plot occupancy rate over time"""
    plt.figure(figsize=(15, 7))
    plt.plot(df['hour_slot'], df['occupancy_rate'].astype(float), marker='o')
    plt.title('Parking Occupancy Rate Over Time')
    plt.xlabel('Time')
    plt.ylabel('Occupancy Rate (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('visualize/occupancy_rate.png')
    plt.close()

def plot_spot_activity(df):
    """Plot parking spot activity"""
    plt.figure(figsize=(12, 6))
    df = df.sort_values('total_events', ascending=True)
    plt.barh(df['spot_id'], df['occupancy_rate'].astype(float))
    plt.title('Parking Spot Occupancy Rates')
    plt.xlabel('Occupancy Rate (%)')
    plt.ylabel('Parking Spot')
    plt.tight_layout()
    plt.savefig('visualize/spot_activity.png')
    plt.close()

def plot_daily_pattern(df):
    """Plot daily occupancy pattern"""
    # Convert occupied_spots to numeric
    df['occupied_spots'] = pd.to_numeric(df['occupied_spots'])
    
    pivot_df = df.pivot(index='hour', columns='date', values='occupied_spots')
    plt.figure(figsize=(15, 8))
    sns.heatmap(pivot_df, cmap='YlOrRd', annot=True, fmt='g')
    plt.title('Daily Occupancy Pattern')
    plt.xlabel('Date')
    plt.ylabel('Hour')
    plt.tight_layout()
    plt.savefig('visualize/daily_pattern.png')
    plt.close()

def main():
    print("Generating parking analytics visualizations...")
    
    # Create visualizations directory if it doesn't exist
    import os
    os.makedirs('visualize', exist_ok=True)
    
    # Run queries and create visualizations
    print("\n1. Current Parking Status")
    current_status = run_athena_query("""
        SELECT spot_id, status, timestamp
        FROM parking_analytics.parking_events
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    plot_current_status(current_status)
    
    print("\n2. Occupancy Rate Over Time")
    occupancy_rate = run_athena_query("""
        SELECT CONCAT(year, '-', month, '-', day, ' ', hour, ':00:00') as hour_slot,
               COUNT(CASE WHEN status = 'occupied' THEN 1 END) * 100.0 / COUNT(*) as occupancy_rate
        FROM parking_analytics.parking_events
        GROUP BY year, month, day, hour
        ORDER BY year, month, day, hour
    """)
    plot_occupancy_rate(occupancy_rate)
    
    print("\n3. Parking Spot Activity")
    spot_activity = run_athena_query("""
        SELECT spot_id,
               COUNT(*) as total_events,
               ROUND(COUNT(CASE WHEN status = 'occupied' THEN 1 END) * 100.0 / COUNT(*), 2) as occupancy_rate
        FROM parking_analytics.parking_events
        GROUP BY spot_id
        ORDER BY total_events DESC
    """)
    plot_spot_activity(spot_activity)
    
    print("\n4. Daily Occupancy Pattern")
    daily_pattern = run_athena_query("""
        SELECT CONCAT(year, '-', month, '-', day) as date,
               hour,
               COUNT(CASE WHEN status = 'occupied' THEN 1 END) as occupied_spots
        FROM parking_analytics.parking_events
        GROUP BY year, month, day, hour
        ORDER BY year, month, day, hour
    """)
    plot_daily_pattern(daily_pattern)
    
    print("\nVisualizations have been saved in the 'visualize' directory!")

if __name__ == "__main__":
    main() 