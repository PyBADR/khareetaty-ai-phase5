"""
Data loader module for Khareetaty AI MVP Crime Analytics System
Handles CSV data loading, validation, and initial processing
"""
import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re
from pathlib import Path

from src.config import Config
from src.database import db_manager

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self):
        self.required_columns = Config.REQUIRED_COLUMNS
        self.allowed_crime_types = Config.ALLOWED_CRIME_TYPES
        self.kuwait_bounds = Config.KUWAIT_BOUNDS
        
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV file into pandas DataFrame"""
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            logger.info(f"Loaded {len(df)} rows from {file_path}")
            return df
        except Exception as e:
            logger.error(f"Failed to load CSV file {file_path}: {e}")
            raise
            
    def validate_schema(self, df: pd.DataFrame) -> bool:
        """Validate that required columns exist in DataFrame"""
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
            
        logger.info("Schema validation passed")
        return True
        
    def validate_gps_coordinates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate GPS coordinates are within Kuwait bounds"""
        # Check if coordinates are within Kuwait bounds
        lat_valid = (df['latitude'] >= self.kuwait_bounds['min_lat']) & \
                   (df['latitude'] <= self.kuwait_bounds['max_lat'])
        lon_valid = (df['longitude'] >= self.kuwait_bounds['min_lon']) & \
                   (df['longitude'] <= self.kuwait_bounds['max_lon'])
        
        # Count invalid coordinates
        invalid_coords = (~lat_valid | ~lon_valid)
        invalid_count = invalid_coords.sum()
        
        if invalid_count > 0:
            logger.warning(f"Found {invalid_count} records with invalid GPS coordinates")
            logger.info(f"Removing invalid coordinates...")
            df = df[~invalid_coords]
            
        logger.info(f"GPS coordinate validation completed. Valid records: {len(df)}")
        return df
        
    def validate_timestamps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and parse timestamps"""
        # Ensure timestamp column exists
        if 'timestamp' not in df.columns:
            raise ValueError("Timestamp column is required")
            
        # Convert to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            
        # Remove rows with invalid timestamps
        invalid_timestamps = df['timestamp'].isna()
        invalid_count = invalid_timestamps.sum()
        
        if invalid_count > 0:
            logger.warning(f"Removed {invalid_count} records with invalid timestamps")
            df = df[~invalid_timestamps]
            
        # Sort by timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        logger.info(f"Timestamp validation completed. Valid records: {len(df)}")
        return df
        
    def validate_crime_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate crime types against allowed list"""
        # Convert to uppercase for comparison
        df['crime_type'] = df['crime_type'].str.upper().str.replace(' ', '_')
        
        # Filter out invalid crime types
        valid_crimes = df['crime_type'].isin(self.allowed_crime_types)
        invalid_count = (~valid_crimes).sum()
        
        if invalid_count > 0:
            logger.warning(f"Removed {invalid_count} records with invalid crime types")
            df = df[valid_crimes].reset_index(drop=True)
            
        logger.info(f"Crime type validation completed. Valid records: {len(df)}")
        return df
        
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all cleaning functions to the DataFrame"""
        logger.info("Starting data cleaning process...")
        
        # Validate schema first
        if not self.validate_schema(df):
            raise ValueError("Schema validation failed")
            
        # Apply validations in sequence
        df = self.validate_gps_coordinates(df)
        df = self.validate_timestamps(df)
        df = self.validate_crime_types(df)
        
        # Handle missing values
        if 'description' in df.columns:
            df['description'] = df['description'].fillna('')
        else:
            df['description'] = ''
            
        logger.info(f"Data cleaning completed. Final record count: {len(df)}")
        return df
        
    def load_and_validate_data(self, file_path: str) -> pd.DataFrame:
        """Complete workflow: Load, validate, and clean data"""
        logger.info(f"Starting load and validation for {file_path}")
        
        # Load data
        df = self.load_csv(file_path)
        
        # Clean and validate
        df = self.clean_data(df)
        
        # Add ingestion timestamp
        df['ingestion_timestamp'] = datetime.now()
        df['source_file'] = os.path.basename(file_path)
        
        logger.info(f"Load and validation completed for {file_path}. Records: {len(df)}")
        return df
        
    def load_multiple_files(self, directory_path: str) -> pd.DataFrame:
        """Load and combine multiple CSV files from a directory"""
        csv_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.csv')]
        
        if not csv_files:
            logger.warning(f"No CSV files found in {directory_path}")
            return pd.DataFrame()
            
        combined_df_list = []
        
        for file in csv_files:
            file_path = os.path.join(directory_path, file)
            try:
                df = self.load_and_validate_data(file_path)
                if not df.empty:
                    combined_df_list.append(df)
            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {e}")
                
        if combined_df_list:
            combined_df = pd.concat(combined_df_list, ignore_index=True)
            logger.info(f"Combined {len(combined_df_list)} files into {len(combined_df)} total records")
            return combined_df
        else:
            logger.warning("No valid data loaded from any files")
            return pd.DataFrame()
            
    def save_to_database(self, df: pd.DataFrame, table_name: str = 'incidents_raw'):
        """Save cleaned data to database"""
        if df.empty:
            logger.warning("Empty DataFrame, nothing to save to database")
            return 0
            
        # Prepare data for database insertion
        required_cols = ['timestamp', 'crime_type', 'latitude', 'longitude']
        optional_cols = ['description'] if 'description' in df.columns else []
        meta_cols = ['ingestion_timestamp', 'source_file']
        
        all_cols = required_cols + optional_cols + meta_cols
        
        # Select only columns that exist in the dataframe
        cols_to_save = [col for col in all_cols if col in df.columns]
        df_to_save = df[cols_to_save].copy()
        
        # Insert into database
        rows_inserted = db_manager.insert_dataframe(df_to_save, table_name)
        logger.info(f"Saved {rows_inserted} records to {table_name}")
        
        return rows_inserted
        
    def archive_processed_file(self, original_path: str):
        """Move processed file to archive directory"""
        try:
            filename = os.path.basename(original_path)
            archive_path = os.path.join(Config.ARCHIVE_DIR, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
            os.rename(original_path, archive_path)
            logger.info(f"Archived {original_path} to {archive_path}")
        except Exception as e:
            logger.error(f"Failed to archive file {original_path}: {e}")
            
    def validate_and_load_directory(self, directory_path: str = None):
        """Main method to validate and load data from staging directory"""
        if directory_path is None:
            directory_path = Config.STAGING_DIR
            
        logger.info(f"Starting validation and loading from {directory_path}")
        
        # Load and process data
        df = self.load_multiple_files(directory_path)
        
        if not df.empty:
            # Save to database
            rows_saved = self.save_to_database(df)
            
            # Archive processed files
            for filename in os.listdir(directory_path):
                if filename.lower().endswith('.csv'):
                    original_path = os.path.join(directory_path, filename)
                    self.archive_processed_file(original_path)
                    
            logger.info(f"Completed loading process. Total records saved: {rows_saved}")
            return rows_saved
        else:
            logger.info("No valid data found to process")
            return 0
            
    def validate_single_record(self, record: Dict) -> Tuple[bool, List[str]]:
        """Validate a single incident record"""
        errors = []
        
        # Check required fields
        for col in self.required_columns:
            if col not in record or pd.isna(record[col]):
                errors.append(f"Missing required field: {col}")
                
        # Validate GPS coordinates
        if 'latitude' in record and 'longitude' in record:
            lat = float(record['latitude'])
            lon = float(record['longitude'])
            
            if not (self.kuwait_bounds['min_lat'] <= lat <= self.kuwait_bounds['max_lat']):
                errors.append(f"Latitude {lat} out of bounds for Kuwait")
                
            if not (self.kuwait_bounds['min_lon'] <= lon <= self.kuwait_bounds['max_lon']):
                errors.append(f"Longitude {lon} out of bounds for Kuwait")
                
        # Validate timestamp
        if 'timestamp' in record:
            try:
                pd.to_datetime(record['timestamp'])
            except:
                errors.append(f"Invalid timestamp: {record['timestamp']}")
                
        # Validate crime type
        if 'crime_type' in record:
            crime_type = str(record['crime_type']).upper().replace(' ', '_')
            if crime_type not in self.allowed_crime_types:
                errors.append(f"Invalid crime type: {crime_type}")
                
        is_valid = len(errors) == 0
        return is_valid, errors