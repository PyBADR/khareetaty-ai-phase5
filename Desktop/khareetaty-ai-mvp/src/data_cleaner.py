"""
Data cleaner module for Khareetaty AI MVP Crime Analytics System
Handles duplicate removal, geo-tagging, and crime type normalization
"""
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Tuple
import re
from collections import defaultdict

from src.config import Config, KUWAIT_GOVERNORATES, CRIME_TYPE_MAPPING
from src.database import db_manager

logger = logging.getLogger(__name__)

class DataCleaner:
    def __init__(self):
        self.duplicate_threshold_minutes = Config.DUPLICATE_THRESHOLD_MINUTES
        self.crime_mapping = CRIME_TYPE_MAPPING
        
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate incidents based on timestamp and location proximity"""
        logger.info("Starting duplicate removal process...")
        
        if df.empty:
            return df
            
        # Sort by timestamp to process chronologically
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Calculate time differences between consecutive records
        df['prev_timestamp'] = df['timestamp'].shift(1)
        df['time_diff_minutes'] = (df['timestamp'] - df['prev_timestamp']).dt.total_seconds() / 60
        
        # Calculate distance between consecutive records
        df['prev_latitude'] = df['latitude'].shift(1)
        df['prev_longitude'] = df['longitude'].shift(1)
        
        # Calculate distances using geopy
        distances = []
        for i, row in df.iterrows():
            if i == 0:
                distances.append(float('inf'))  # First record, no previous
            else:
                prev_point = (row['prev_latitude'], row['prev_longitude'])
                curr_point = (row['latitude'], row['longitude'])
                dist = geodesic(prev_point, curr_point).kilometers
                distances.append(dist)
                
        df['distance_km'] = distances
        
        # Identify duplicates: same location (within 0.1km) and close in time (within threshold)
        is_duplicate = (df['distance_km'] <= 0.1) & (df['time_diff_minutes'] <= self.duplicate_threshold_minutes)
        
        # Mark duplicates for removal
        df['is_duplicate'] = is_duplicate
        duplicates_count = is_duplicate.sum()
        
        # Remove duplicates
        df_cleaned = df[~is_duplicate].drop(['prev_timestamp', 'time_diff_minutes', 'prev_latitude', 'prev_longitude', 'distance_km', 'is_duplicate'], axis=1, errors='ignore')
        
        logger.info(f"Removed {duplicates_count} duplicate records. Remaining: {len(df_cleaned)}")
        return df_cleaned.reset_index(drop=True)
        
    def geotag_location(self, latitude: float, longitude: float) -> Tuple[str, str]:
        """Determine governorate and district for given coordinates"""
        point = (latitude, longitude)
        
        for gov_name, gov_info in KUWAIT_GOVERNORATES.items():
            bounds = gov_info['bounds']
            
            if (bounds['min_lat'] <= latitude <= bounds['max_lat'] and 
                bounds['min_lon'] <= longitude <= bounds['max_lon']):
                
                # Simple assignment to first district in the governorate
                # In a real system, you might use more sophisticated geofencing
                district = gov_info['districts'][0] if gov_info['districts'] else 'Unknown'
                return gov_name, district
                
        return 'Unknown', 'Unknown'
        
    def geotag_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add governorate and district information to DataFrame"""
        logger.info("Starting geotagging process...")
        
        if df.empty:
            return df
            
        df = df.copy()
        
        # Create columns for governorate and district
        df['governorate'] = ''
        df['district'] = ''
        
        # Apply geotagging to each row
        for idx, row in df.iterrows():
            gov, dist = self.geotag_location(row['latitude'], row['longitude'])
            df.at[idx, 'governorate'] = gov
            df.at[idx, 'district'] = dist
            
        logger.info("Geotagging completed")
        return df
        
    def normalize_crime_type(self, crime_type: str) -> str:
        """Normalize crime type using mapping dictionary"""
        if pd.isna(crime_type):
            return 'UNKNOWN'
            
        crime_lower = str(crime_type).lower().strip()
        
        # Check if the crime type is in our mapping
        if crime_lower in self.crime_mapping:
            return self.crime_mapping[crime_lower]
        else:
            # If not mapped, return original if it's in allowed types, else UNKNOWN
            original_upper = crime_lower.upper().replace(' ', '_')
            if original_upper in Config.ALLOWED_CRIME_TYPES:
                return original_upper
            else:
                return 'OTHER'
                
    def normalize_crime_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize all crime types in the DataFrame"""
        logger.info("Starting crime type normalization...")
        
        if df.empty:
            return df
            
        df = df.copy()
        
        # Normalize crime types
        df['normalized_type'] = df['crime_type'].apply(self.normalize_crime_type)
        
        # Count normalized types
        type_counts = df['normalized_type'].value_counts()
        logger.info(f"Normalized crime types: {dict(type_counts)}")
        
        return df
        
    def clean_incidents_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Complete cleaning workflow: deduplication, geotagging, normalization"""
        logger.info("Starting complete data cleaning workflow...")
        
        if df.empty:
            logger.info("Empty DataFrame, skipping cleaning")
            return df
            
        # Remove duplicates
        df = self.remove_duplicates(df)
        
        # Geotag locations
        df = self.geotag_dataframe(df)
        
        # Normalize crime types
        df = self.normalize_crime_types(df)
        
        # Add reference to raw incident IDs if not present
        if 'raw_incident_id' not in df.columns:
            df['raw_incident_id'] = None  # Will be populated later when linking to raw data
            
        logger.info(f"Data cleaning completed. Final record count: {len(df)}")
        return df
        
    def calculate_location_hash(self, latitude: float, longitude: float, precision: int = 4) -> str:
        """Calculate a hash for a location to group nearby incidents"""
        lat_rounded = round(latitude, precision)
        lon_rounded = round(longitude, precision)
        return f"{lat_rounded}_{lon_rounded}"
        
    def detect_clusters_by_location(self, df: pd.DataFrame, precision: int = 4) -> pd.DataFrame:
        """Group incidents by location clusters"""
        if df.empty:
            return df
            
        df = df.copy()
        
        # Create location clusters
        df['location_cluster'] = df.apply(
            lambda row: self.calculate_location_hash(row['latitude'], row['longitude'], precision), 
            axis=1
        )
        
        # Count incidents per cluster
        cluster_counts = df['location_cluster'].value_counts()
        df['cluster_incident_count'] = df['location_cluster'].map(cluster_counts)
        
        return df
        
    def enrich_with_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add statistical enrichments to the data"""
        if df.empty:
            return df
            
        df = df.copy()
        
        # Add hour of day
        df['hour_of_day'] = df['timestamp'].dt.hour
        
        # Add day of week
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        # Add month
        df['month'] = df['timestamp'].dt.month
        
        # Add incident density indicators
        # Group by location cluster and time window
        df['date'] = df['timestamp'].dt.date
        df['time_window'] = df['hour_of_day'].apply(lambda x: f"{x//6}_early_morning" if x < 6 
                                                   else f"{x//6}_morning" if x < 12 
                                                   else f"{x//6}_afternoon" if x < 18 
                                                   else f"{x//6}_evening")
        
        # Calculate incident counts by location and time
        location_time_groups = df.groupby(['location_cluster', 'time_window']).size().reset_index(name='time_location_count')
        df = df.merge(location_time_groups, on=['location_cluster', 'time_window'], how='left')
        
        return df
        
    def save_clean_data_to_db(self, df: pd.DataFrame) -> int:
        """Save cleaned data to incidents_clean table"""
        if df.empty:
            logger.warning("Empty DataFrame, nothing to save to clean table")
            return 0
            
        # Prepare columns for clean table
        required_cols = [
            'timestamp', 'crime_type', 'latitude', 'longitude', 
            'governorate', 'district', 'normalized_type'
        ]
        
        # Add optional columns if they exist
        optional_cols = ['description', 'raw_incident_id']
        
        all_cols = required_cols + [col for col in optional_cols if col in df.columns]
        
        # Select only existing columns
        cols_to_save = [col for col in all_cols if col in df.columns]
        df_to_save = df[cols_to_save].copy()
        
        # Insert into database
        rows_inserted = db_manager.insert_dataframe(df_to_save, 'incidents_clean')
        logger.info(f"Saved {rows_inserted} cleaned records to incidents_clean table")
        
        return rows_inserted
        
    def process_raw_data_batch(self, batch_size: int = Config.BATCH_SIZE) -> int:
        """Process raw data in batches and move to clean table"""
        logger.info("Starting batch processing of raw data...")
        
        # Get raw incidents that haven't been processed yet
        query = """
            SELECT ir.id, ir.timestamp, ir.crime_type, ir.latitude, ir.longitude, 
                   ir.description, ir.ingestion_timestamp
            FROM incidents_raw ir
            LEFT JOIN incidents_clean ic ON ir.id = ic.raw_incident_id
            WHERE ic.raw_incident_id IS NULL
            ORDER BY ir.timestamp
            LIMIT %s
        """
        
        raw_incidents = db_manager.execute_query(query, (batch_size,))
        
        if not raw_incidents:
            logger.info("No unprocessed raw incidents found")
            return 0
            
        # Convert to DataFrame
        df_raw = pd.DataFrame(raw_incidents)
        
        if df_raw.empty:
            logger.info("No raw incidents to process")
            return 0
            
        # Clean the data
        df_cleaned = self.clean_incidents_data(df_raw)
        
        if df_cleaned.empty:
            logger.warning("No cleaned data to save after processing")
            return 0
            
        # Link to raw data by adding raw_incident_id
        df_cleaned['raw_incident_id'] = df_cleaned['id']
        df_cleaned = df_cleaned.drop(columns=['id'])  # Remove raw id to let clean table auto-increment
        
        # Save to clean table
        rows_saved = self.save_clean_data_to_db(df_cleaned)
        
        logger.info(f"Batch processing completed. Saved {rows_saved} records.")
        return rows_saved
        
    def run_full_cleaning_pipeline(self):
        """Run the complete data cleaning pipeline"""
        logger.info("Starting full data cleaning pipeline...")
        
        # Process raw data in batches until all is processed
        total_processed = 0
        while True:
            batch_processed = self.process_raw_data_batch()
            total_processed += batch_processed
            
            if batch_processed == 0:
                break  # No more data to process
                
        logger.info(f"Full cleaning pipeline completed. Total records processed: {total_processed}")
        return total_processed