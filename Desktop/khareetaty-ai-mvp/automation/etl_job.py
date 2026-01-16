import pandas as pd
import psycopg2
from datetime import datetime
import os
import logging
import glob
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.services.geo_lookup import resolve_zone
    GEO_LOOKUP_AVAILABLE = True
except ImportError:
    GEO_LOOKUP_AVAILABLE = False
    logging.warning("Geo lookup service not available. Geographic resolution will be skipped.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DB_CONN = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME", "khareetaty_ai"),
    "user": os.getenv("DB_USER", "bdr.ai"),
    "password": os.getenv("DB_PASSWORD", "")
}

RAW_TABLE = "incidents_raw"
CLEAN_TABLE = "incidents_clean"

# Valid incident types for validation
VALID_INCIDENT_TYPES = [
    'theft', 'assault', 'vandalism', 'burglary', 'robbery',
    'vehicle_theft', 'fraud', 'drug_offense', 'traffic_accident',
    'domestic_violence', 'public_disturbance', 'other'
]

# Kuwait governorates
VALID_GOVERNORATES = [
    'Capital', 'Hawalli', 'Farwaniya', 'Mubarak Al-Kabeer',
    'Ahmadi', 'Jahra', 'unknown'
]

def validate_incident_data(df):
    """Validate incident data before loading"""
    errors = []
    
    # Check required columns
    required_cols = ['incident_type', 'lat', 'lon', 'timestamp']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")
        return False, errors
    
    # Validate latitude/longitude ranges (Kuwait bounds)
    if not df['lat'].between(28.5, 30.1).all():
        errors.append("Some latitude values are outside Kuwait bounds (28.5-30.1)")
    
    if not df['lon'].between(46.5, 48.5).all():
        errors.append("Some longitude values are outside Kuwait bounds (46.5-48.5)")
    
    # Check for null values in required fields
    null_counts = df[required_cols].isnull().sum()
    if null_counts.any():
        errors.append(f"Null values found: {null_counts[null_counts > 0].to_dict()}")
    
    if errors:
        return False, errors
    return True, []

def load_csv_to_raw(csv_path="./data/staging/incidents.csv"):
    """Load CSV data into raw incidents table with validation"""
    if not os.path.exists(csv_path):
        logger.warning(f"CSV file not found: {csv_path}")
        return 0
    
    try:
        logger.info(f"Loading CSV from {csv_path}")
        df = pd.read_csv(csv_path)
        
        if df.empty:
            logger.warning(f"CSV file is empty: {csv_path}")
            return 0
        
        # Validate data
        is_valid, errors = validate_incident_data(df)
        if not is_valid:
            logger.error(f"Data validation failed: {errors}")
            return 0
        
        conn = psycopg2.connect(**DB_CONN)
        cur = conn.cursor()
        
        loaded_count = 0
        failed_count = 0
        
        # Batch insert for better performance
        for _, row in df.iterrows():
            try:
                # Normalize incident type
                incident_type = str(row["incident_type"]).lower().strip()
                
                # Parse timestamp
                if isinstance(row["timestamp"], str):
                    timestamp = datetime.fromisoformat(row["timestamp"])
                else:
                    timestamp = pd.to_datetime(row["timestamp"])
                
                cur.execute(f"""
                    INSERT INTO {RAW_TABLE} (incident_type, governorate, zone, lat, lon, timestamp, description)
                    VALUES (%s,%s,%s,%s,%s,%s,%s);
                    """,
                    (
                        incident_type,
                        row.get("governorate", "unknown"),
                        row.get("zone", "unknown"),
                        float(row["lat"]),
                        float(row["lon"]),
                        timestamp,
                        row.get("description", "")
                    )
                )
                loaded_count += 1
            except Exception as e:
                logger.error(f"Failed to load row: {e}")
                failed_count += 1
                continue
        
        conn.commit()
        conn.close()
        
        logger.info(f"Loaded {loaded_count} records from {csv_path} into {RAW_TABLE}")
        if failed_count > 0:
            logger.warning(f"Failed to load {failed_count} records")
        
        # Archive processed file
        archive_processed_file(csv_path)
        
        return loaded_count
        
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        return 0

def archive_processed_file(csv_path):
    """Move processed CSV to archive directory"""
    try:
        archive_dir = "./data/archive"
        os.makedirs(archive_dir, exist_ok=True)
        
        filename = os.path.basename(csv_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = os.path.join(archive_dir, f"{timestamp}_{filename}")
        
        os.rename(csv_path, archive_path)
        logger.info(f"Archived processed file to {archive_path}")
    except Exception as e:
        logger.error(f"Failed to archive file: {e}")

def clean_raw_to_clean():
    """Process raw incidents to clean incidents table with derived fields and geo resolution"""
    try:
        conn = psycopg2.connect(**DB_CONN)
        cur = conn.cursor()

        # Get raw records that haven't been processed yet
        cur.execute(f"""
            SELECT id, incident_type, governorate, zone, lat, lon, timestamp 
            FROM {RAW_TABLE} 
            WHERE id NOT IN (SELECT raw_incident_id FROM {CLEAN_TABLE} WHERE raw_incident_id IS NOT NULL)
        """)
        rows = cur.fetchall()
        
        if not rows:
            logger.info("No new raw records to process")
            conn.close()
            return 0

        processed_count = 0
        failed_count = 0
        geo_resolved_count = 0
        geo_failed_count = 0
        
        for r in rows:
            try:
                incident_id, inc_type, gov, zone, lat, lon, ts = r
                
                # Derive temporal features
                hour = ts.hour
                day = ts.strftime('%A')
                week = int(ts.strftime('%V'))
                
                # Geographic resolution
                district = None
                block = None
                police_zone = None
                
                if GEO_LOOKUP_AVAILABLE:
                    try:
                        geo_result = resolve_zone(lat, lon)
                        if geo_result['resolved']:
                            district = geo_result.get('district')
                            block = geo_result.get('block')
                            police_zone = geo_result.get('police_zone')
                            # Update governorate from geo lookup if more accurate
                            if geo_result.get('governorate'):
                                gov = geo_result['governorate']
                            geo_resolved_count += 1
                            logger.debug(f"Resolved incident {incident_id} to district: {district}")
                        else:
                            geo_failed_count += 1
                            # Log to geo_resolution_log
                            try:
                                cur.execute("""
                                    INSERT INTO geo_resolution_log (lat, lon, resolved, error_message, timestamp)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (lat, lon, False, 'Point not in any district polygon', ts))
                            except Exception:
                                pass  # Table might not exist yet
                    except Exception as e:
                        logger.warning(f"Geo resolution failed for incident {incident_id}: {e}")
                        geo_failed_count += 1
                
                # Insert into clean table with geo fields
                cur.execute(f"""
                    INSERT INTO {CLEAN_TABLE}
                    (raw_incident_id, incident_type, governorate, zone, lat, lon, 
                     district, block, police_zone, hour, day, week, timestamp)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    incident_id,
                    inc_type,
                    gov,
                    zone,
                    lat,
                    lon,
                    district,
                    block,
                    police_zone,
                    hour,
                    day,
                    week,
                    ts
                ))
                processed_count += 1
            except Exception as e:
                logger.error(f"Failed to process record {incident_id}: {e}")
                failed_count += 1
                continue
            
        conn.commit()
        conn.close()
        
        logger.info(f"Processed {processed_count} records from {RAW_TABLE} to {CLEAN_TABLE}")
        if GEO_LOOKUP_AVAILABLE:
            logger.info(f"Geographic resolution: {geo_resolved_count} resolved, {geo_failed_count} failed")
        if failed_count > 0:
            logger.warning(f"Failed to process {failed_count} records")
        
        return processed_count
        
    except Exception as e:
        logger.error(f"Error in clean_raw_to_clean: {e}")
        return 0

def load_all_staging_files():
    """Load all CSV files from staging directory"""
    staging_dir = "./data/staging"
    csv_files = glob.glob(os.path.join(staging_dir, "*.csv"))
    
    if not csv_files:
        logger.info("No CSV files found in staging directory")
        return 0
    
    total_loaded = 0
    for csv_file in csv_files:
        logger.info(f"Processing file: {csv_file}")
        loaded = load_csv_to_raw(csv_file)
        total_loaded += loaded
    
    return total_loaded

def run_full_etl():
    """Run complete ETL pipeline"""
    logger.info("Starting ETL pipeline...")
    
    # Step 1: Load all staging files
    loaded = load_all_staging_files()
    logger.info(f"Total records loaded: {loaded}")
    
    # Step 2: Clean and process raw data
    processed = clean_raw_to_clean()
    logger.info(f"Total records processed: {processed}")
    
    logger.info("ETL pipeline complete")
    return {"loaded": loaded, "processed": processed}

if __name__ == "__main__":
    result = run_full_etl()
    print(f"ETL complete. Results: {result}")