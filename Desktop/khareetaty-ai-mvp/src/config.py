"""
Configuration settings for Khareetaty AI MVP Crime Analytics System
"""
import os
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
# Get the project root directory (parent of src/)
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'khareetaty_db')
    DB_USER = os.getenv('DB_USER', 'insurance_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'insurance_pass')
    DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Data Paths
    STAGING_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'staging')
    ARCHIVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'archive')
    
    # Data Validation Settings
    REQUIRED_COLUMNS = ['timestamp', 'crime_type', 'latitude', 'longitude']
    ALLOWED_CRIME_TYPES = [
        'THEFT', 'ASSAULT', 'BURGLARY', 'ROBBERY', 
        'FRAUD', 'DRUGS', 'VANDALISM', 'TRAFFIC_VIOLATION'
    ]
    
    # GPS Bounds for Kuwait (approximate)
    KUWAIT_BOUNDS = {
        'min_lat': 28.5,
        'max_lat': 30.1,
        'min_lon': 46.5,
        'max_lon': 48.5
    }
    
    # Processing Settings
    BATCH_SIZE = 1000
    DUPLICATE_THRESHOLD_MINUTES = 5
    
    # Analytics Settings
    TIMEZONE = 'Asia/Kuwait'
    DEFAULT_FORECAST_PERIODS = 30  # days
    
    # Alert Thresholds
    HIGH_INCIDENT_THRESHOLD = 10  # incidents per day
    MEDIUM_INCIDENT_THRESHOLD = 5  # incidents per day
    ALERT_COOLDOWN_HOURS = 24
    
    # Hotspot Detection
    CLUSTER_EPSILON_KM = 0.5  # DBSCAN epsilon in kilometers
    MIN_SAMPLES_CLUSTER = 3   # Minimum samples for DBSCAN
    
    # Retention Policy (days)
    RAW_DATA_RETENTION_DAYS = 90
    CLEAN_DATA_RETENTION_DAYS = 365
    ANALYTICS_RETENTION_DAYS = 730
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'khareetaty.log'
    
    # Notification Settings
    ENABLE_EMAIL_ALERTS = False
    ENABLE_SMS_ALERTS = False
    ENABLE_WHATSAPP_ALERTS = False
    
    # Email Configuration (if enabled)
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    EMAIL_USER = os.getenv('EMAIL_USER', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    
    # Admin Recipients
    ADMIN_EMAILS = os.getenv('ADMIN_EMAILS', '').split(',') if os.getenv('ADMIN_EMAILS') else []
    ADMIN_PHONES = os.getenv('ADMIN_PHONES', '').split(',') if os.getenv('ADMIN_PHONES') else []

# Governorate and District mappings for Kuwait
KUWAIT_GOVERNORATES = {
    'Al Asimah': {
        'bounds': {'min_lat': 29.3, 'max_lat': 29.4, 'min_lon': 47.9, 'max_lon': 48.0},
        'districts': ['Capital', 'Sulaibikhat', 'Qortuba', 'Kaifan']
    },
    'Hawalli': {
        'bounds': {'min_lat': 29.3, 'max_lat': 29.35, 'min_lon': 48.0, 'max_lon': 48.1},
        'districts': ['Hawalli', 'Salmiya', 'Bayan', 'Rumaithiya']
    },
    'Farwaniya': {
        'bounds': {'min_lat': 29.25, 'max_lat': 29.35, 'min_lon': 47.9, 'max_lon': 48.0},
        'districts': ['Farwaniya', 'Khaitan', 'Jeleeb Al-Shuyoukh', 'Rehab']
    },
    'Mubarak Al-Kabeer': {
        'bounds': {'min_lat': 29.15, 'max_lat': 29.25, 'min_lon': 48.0, 'max_lon': 48.2},
        'districts': ['Mubarak Al-Kabeer', 'Abdullah Al-Mubarak', 'Al-Qusour']
    },
    'Ahmadi': {
        'bounds': {'min_lat': 29.0, 'max_lat': 29.2, 'min_lon': 48.0, 'max_lon': 48.2},
        'districts': ['Ahmadi', 'Fahaheel', 'Al-Zour', 'Sabah Al-Ahmad']
    },
    'Al Jahra': {
        'bounds': {'min_lat': 29.3, 'max_lat': 29.5, 'min_lon': 47.5, 'max_lon': 47.9},
        'districts': ['Al Jahra', 'Nassef', 'Saad Al-Abdullah', 'Oyoun']
    }
}

# Crime Type Normalization Mapping
CRIME_TYPE_MAPPING = {
    # Theft related
    'theft': 'THEFT',
    'robbery': 'ROBBERY',
    'burglary': 'BURGLARY',
    'shoplifting': 'THEFT',
    'pickpocketing': 'THEFT',
    
    # Violence related
    'assault': 'ASSAULT',
    'battery': 'ASSAULT',
    'fighting': 'ASSAULT',
    'domestic violence': 'ASSAULT',
    
    # Property damage
    'vandalism': 'VANDALISM',
    'arson': 'VANDALISM',
    'damage to property': 'VANDALISM',
    
    # Traffic related
    'traffic violation': 'TRAFFIC_VIOLATION',
    'speeding': 'TRAFFIC_VIOLATION',
    'accident': 'TRAFFIC_VIOLATION',
    'driving under influence': 'TRAFFIC_VIOLATION',
    
    # Other crimes
    'fraud': 'FRAUD',
    'scam': 'FRAUD',
    'embezzlement': 'FRAUD',
    'drug possession': 'DRUGS',
    'drug trafficking': 'DRUGS',
}