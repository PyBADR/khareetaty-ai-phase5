"""
Sample synthetic data generator for Khareetaty AI MVP Crime Analytics System
Generates realistic crime data for testing and demonstration purposes
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from pathlib import Path

from src.config import KUWAIT_GOVERNORATES, CRIME_TYPE_MAPPING

def generate_synthetic_crime_data(num_records=1000, start_date=None, end_date=None):
    """
    Generate synthetic crime data for testing purposes
    
    Args:
        num_records (int): Number of records to generate
        start_date (datetime): Start date for generated data
        end_date (datetime): End date for generated data
    
    Returns:
        pandas.DataFrame: Generated crime data
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=90)  # Last 3 months
    if end_date is None:
        end_date = datetime.now()
    
    # Define possible crime types
    crime_types = [
        'THEFT', 'ASSAULT', 'BURGLARY', 'ROBBERY', 
        'FRAUD', 'DRUGS', 'VANDALISM', 'TRAFFIC_VIOLATION'
    ]
    
    # Governorate options with their geographical bounds
    governorates = list(KUWAIT_GOVERNORATES.keys())
    
    # Generate data
    data = {
        'timestamp': [],
        'crime_type': [],
        'latitude': [],
        'longitude': [],
        'description': []
    }
    
    for _ in range(num_records):
        # Random timestamp within the date range
        time_range = end_date - start_date
        random_seconds = random.randint(0, int(time_range.total_seconds()))
        timestamp = start_date + timedelta(seconds=random_seconds)
        data['timestamp'].append(timestamp)
        
        # Random crime type
        crime_type = random.choice(crime_types)
        data['crime_type'].append(crime_type)
        
        # Random governorate
        governorate = random.choice(governorates)
        bounds = KUWAIT_GOVERNORATES[governorate]['bounds']
        
        # Random coordinates within governorate bounds
        lat = round(random.uniform(bounds['min_lat'], bounds['max_lat']), 6)
        lon = round(random.uniform(bounds['min_lon'], bounds['max_lon']), 6)
        data['latitude'].append(lat)
        data['longitude'].append(lon)
        
        # Generate descriptive text
        descriptions = [
            f"Reported {crime_type.lower()} incident in {governorate}",
            f"Crime incident recorded: {crime_type} at {lat:.4f}, {lon:.4f}",
            f"Security breach - {crime_type} reported in {governorate} district",
            f"Suspicious activity: {crime_type} detected",
            f"Emergency response dispatched for {crime_type} case",
            f"Criminal activity logged: {crime_type} in {governorate} area"
        ]
        description = random.choice(descriptions)
        data['description'].append(description)
    
    df = pd.DataFrame(data)
    
    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    return df

def generate_varied_crime_data(num_records=1000):
    """
    Generate varied crime data with different patterns and distributions
    """
    # Split the records among different governorates with different crime patterns
    governorates = list(KUWAIT_GOVERNORATES.keys())
    
    records_per_gov = num_records // len(governates)
    remaining_records = num_records % len(governates)
    
    all_data = []
    
    for i, gov in enumerate(governates):
        # Adjust number of records for this governorate
        gov_records = records_per_gov
        if i < remaining_records:
            gov_records += 1
        
        # Define crime type weights for this governorate (some areas have more of certain crimes)
        if gov == 'Al Asimah':  # Capital area - more theft, fraud
            crime_weights = [0.25, 0.15, 0.20, 0.10, 0.20, 0.05, 0.03, 0.02]  # Higher theft/fraud
        elif gov == 'Ahmadi':  # Industrial area - more traffic violations
            crime_weights = [0.15, 0.10, 0.10, 0.05, 0.10, 0.10, 0.10, 0.30]  # Higher traffic violations
        elif gov == 'Hawalli':  # Residential area - more assaults, theft
            crime_weights = [0.20, 0.25, 0.10, 0.10, 0.10, 0.05, 0.15, 0.05]  # Higher assault
        else:  # Other areas - balanced distribution
            crime_weights = [0.18, 0.15, 0.12, 0.08, 0.12, 0.10, 0.12, 0.13]  # Balanced
        
        crime_types = [
            'THEFT', 'ASSAULT', 'BURGLARY', 'ROBBERY', 
            'FRAUD', 'DRUGS', 'VANDALISM', 'TRAFFIC_VIOLATION'
        ]
        
        # Generate data for this governorate
        bounds = KUWAIT_GOVERNORATES[gov]['bounds']
        
        for _ in range(gov_records):
            # Timestamp - last 90 days
            start_date = datetime.now() - timedelta(days=90)
            end_date = datetime.now()
            time_range = end_date - start_date
            random_seconds = random.randint(0, int(time_range.total_seconds()))
            timestamp = start_date + timedelta(seconds=random_seconds)
            
            # Crime type based on weighted probability
            crime_type = random.choices(crime_types, weights=crime_weights)[0]
            
            # Coordinates within governorate bounds
            lat = round(random.uniform(bounds['min_lat'], bounds['max_lat']), 6)
            lon = round(random.uniform(bounds['min_lon'], bounds['max_lon']), 6)
            
            # Description
            descriptions = [
                f"Reported {crime_type.lower()} incident in {gov}",
                f"Crime incident recorded: {crime_type} at {lat:.4f}, {lon:.4f}",
                f"Security breach - {crime_type} reported in {gov} district",
                f"Suspicious activity: {crime_type} detected",
                f"Emergency response dispatched for {crime_type} case",
                f"Criminal activity logged: {crime_type} in {gov} area"
            ]
            description = random.choice(descriptions)
            
            all_data.append({
                'timestamp': timestamp,
                'crime_type': crime_type,
                'latitude': lat,
                'longitude': lon,
                'description': description
            })
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    return df

def generate_hotspot_areas_data(num_records=1500):
    """
    Generate data with intentional hotspots (areas with higher incident density)
    """
    # Define some hotspots with higher incident density
    hotspots = [
        {'center': (29.375859, 47.977405), 'radius': 0.01, 'weight': 3},  # Downtown Kuwait City
        {'center': (29.368993, 48.002730), 'radius': 0.01, 'weight': 2.5},  # Salmiya
        {'center': (29.1176, 48.1465), 'radius': 0.01, 'weight': 2},  # Airport area
    ]
    
    all_data = []
    
    for _ in range(num_records):
        # Decide if this record should be in a hotspot (weighted probability)
        if random.random() < 0.6:  # 60% chance to be in a hotspot
            # Choose a hotspot
            hotspot = random.choice(hotspots)
            center_lat, center_lon = hotspot['center']
            radius = hotspot['radius']
            
            # Generate coordinates near the hotspot center
            lat = center_lat + random.uniform(-radius, radius)
            lon = center_lon + random.uniform(-radius, radius)
            
            # Ensure coordinates are within Kuwait bounds
            lat = max(28.5, min(30.1, lat))
            lon = max(46.5, min(48.5, lon))
        else:
            # Random location anywhere in Kuwait
            lat = round(random.uniform(29.0, 29.5), 6)
            lon = round(random.uniform(47.5, 48.0), 6)
        
        # Timestamp - last 90 days
        start_date = datetime.now() - timedelta(days=90)
        end_date = datetime.now()
        time_range = end_date - start_date
        random_seconds = random.randint(0, int(time_range.total_seconds()))
        timestamp = start_date + timedelta(seconds=random_seconds)
        
        # Crime type
        crime_types = ['THEFT', 'ASSAULT', 'BURGLARY', 'ROBBERY', 'FRAUD', 'DRUGS', 'VANDALISM', 'TRAFFIC_VIOLATION']
        crime_type = random.choice(crime_types)
        
        # Description
        descriptions = [
            f"Reported {crime_type.lower()} incident in high-density area",
            f"Crime incident recorded: {crime_type} at {lat:.4f}, {lon:.4f}",
            f"Security breach - {crime_type} reported in commercial district",
            f"Suspicious activity: {crime_type} detected",
            f"Emergency response dispatched for {crime_type} case",
            f"Criminal activity logged: {crime_type} in business area"
        ]
        description = random.choice(descriptions)
        
        all_data.append({
            'timestamp': timestamp,
            'crime_type': crime_type,
            'latitude': lat,
            'longitude': lon,
            'description': description
        })
    
    df = pd.DataFrame(all_data)
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    return df

def save_sample_data(filename='sample_crime_data.csv', num_records=2000, data_type='varied'):
    """
    Generate and save sample crime data to CSV file
    
    Args:
        filename (str): Output filename
        num_records (int): Number of records to generate
        data_type (str): Type of data to generate ('basic', 'varied', 'hotspots')
    """
    # Create staging directory if it doesn't exist
    staging_dir = Path('data/staging')
    staging_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate data based on type
    if data_type == 'basic':
        df = generate_synthetic_crime_data(num_records)
    elif data_type == 'varied':
        df = generate_varied_crime_data(num_records)
    elif data_type == 'hotspots':
        df = generate_hotspot_areas_data(num_records)
    else:
        df = generate_varied_crime_data(num_records)
    
    # Save to CSV
    filepath = staging_dir / filename
    df.to_csv(filepath, index=False)
    
    print(f"Generated {len(df)} crime records and saved to {filepath}")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"Crime type distribution:\n{df['crime_type'].value_counts()}")
    
    return filepath

if __name__ == "__main__":
    print("Generating sample crime data for Khareetaty AI system...")
    
    # Generate different types of sample data
    save_sample_data('sample_crime_data_basic.csv', num_records=500, data_type='basic')
    save_sample_data('sample_crime_data_varied.csv', num_records=1000, data_type='varied')
    save_sample_data('sample_crime_data_hotspots.csv', num_records=1000, data_type='hotspots')
    
    print("Sample data generation completed!")