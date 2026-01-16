"""
Database module for Khareetaty AI MVP Crime Analytics System
Handles PostgreSQL connection, table creation, and data operations
"""
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime
import json

from src.config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
        
    def connect(self):
        """Establish connection to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            )
            self.connection.autocommit = True
            logger.info("Successfully connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
            
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
            
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query and return results"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
            
    def execute_command(self, query: str, params: tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE command and return affected rows"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise
            
    def create_tables(self):
        """Create all required tables"""
        tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS incidents_raw (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                crime_type VARCHAR(50) NOT NULL,
                latitude DECIMAL(10, 8) NOT NULL,
                longitude DECIMAL(11, 8) NOT NULL,
                description TEXT,
                ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_file VARCHAR(255)
            );
            """,
            
            """
            CREATE TABLE IF NOT EXISTS incidents_clean (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                crime_type VARCHAR(50) NOT NULL,
                latitude DECIMAL(10, 8) NOT NULL,
                longitude DECIMAL(11, 8) NOT NULL,
                governorate VARCHAR(50),
                district VARCHAR(50),
                normalized_type VARCHAR(50) NOT NULL,
                description TEXT,
                ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                raw_incident_id INTEGER REFERENCES incidents_raw(id)
            );
            """,
            
            """
            CREATE TABLE IF NOT EXISTS zones_hotspots (
                id SERIAL PRIMARY KEY,
                zone_name VARCHAR(100) NOT NULL,
                latitude DECIMAL(10, 8) NOT NULL,
                longitude DECIMAL(11, 8) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                prediction_date DATE NOT NULL,
                cluster_id INTEGER,
                incident_count INTEGER DEFAULT 0,
                risk_score DECIMAL(5, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            """
            CREATE TABLE IF NOT EXISTS analytics_summary (
                id SERIAL PRIMARY KEY,
                period_type VARCHAR(20) NOT NULL, -- HOURLY, DAILY, WEEKLY, MONTHLY
                period_value VARCHAR(50) NOT NULL, -- e.g., '2024-01-15 14:00', '2024-01-15'
                zone VARCHAR(100),
                crime_type VARCHAR(50),
                incident_count INTEGER NOT NULL,
                average_severity DECIMAL(3, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            """
            CREATE TABLE IF NOT EXISTS alerts_log (
                id SERIAL PRIMARY KEY,
                alert_type VARCHAR(50) NOT NULL, -- THRESHOLD, HOTSPOT, TREND
                severity VARCHAR(20) NOT NULL, -- LOW, MEDIUM, HIGH, CRITICAL
                message TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                recipients TEXT,
                status VARCHAR(20) DEFAULT 'SENT', -- SENT, FAILED, ACKNOWLEDGED
                related_incidents JSONB
            );
            """,
            
            """
            CREATE INDEX IF NOT EXISTS idx_incidents_raw_timestamp ON incidents_raw(timestamp);
            CREATE INDEX IF NOT EXISTS idx_incidents_raw_location ON incidents_raw(latitude, longitude);
            CREATE INDEX IF NOT EXISTS idx_incidents_clean_timestamp ON incidents_clean(timestamp);
            CREATE INDEX IF NOT EXISTS idx_incidents_clean_zone ON incidents_clean(governorate, district);
            CREATE INDEX IF NOT EXISTS idx_analytics_period ON analytics_summary(period_type, period_value);
            CREATE INDEX IF NOT EXISTS idx_hotspots_prediction_date ON zones_hotspots(prediction_date);
            """
        ]
        
        try:
            for sql in tables_sql:
                self.execute_command(sql)
            logger.info("All tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
            
    def insert_dataframe(self, df: pd.DataFrame, table_name: str) -> int:
        """Insert pandas DataFrame into database table"""
        try:
            # Convert DataFrame to list of tuples
            records = [tuple(row) for row in df.values]
            
            # Get column names
            columns = list(df.columns)
            
            # Create INSERT query
            placeholders = ', '.join(['%s'] * len(columns))
            column_names = ', '.join(columns)
            query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
            
            # Execute batch insert
            with self.connection.cursor() as cursor:
                cursor.executemany(query, records)
                rows_inserted = cursor.rowcount
                
            logger.info(f"Inserted {rows_inserted} records into {table_name}")
            return rows_inserted
            
        except Exception as e:
            logger.error(f"Failed to insert DataFrame into {table_name}: {e}")
            raise
            
    def bulk_insert_incidents_raw(self, incidents_data: List[Dict]) -> int:
        """Bulk insert raw incidents data"""
        try:
            query = """
                INSERT INTO incidents_raw 
                (timestamp, crime_type, latitude, longitude, description, source_file)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            with self.connection.cursor() as cursor:
                cursor.executemany(query, [
                    (
                        incident['timestamp'],
                        incident['crime_type'],
                        incident['latitude'],
                        incident['longitude'],
                        incident.get('description', ''),
                        incident.get('source_file', '')
                    ) for incident in incidents_data
                ])
                rows_inserted = cursor.rowcount
                
            logger.info(f"Bulk inserted {rows_inserted} raw incidents")
            return rows_inserted
            
        except Exception as e:
            logger.error(f"Failed to bulk insert raw incidents: {e}")
            raise
            
    def get_incidents_by_date_range(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Retrieve incidents within date range"""
        query = """
            SELECT * FROM incidents_clean 
            WHERE timestamp BETWEEN %s AND %s
            ORDER BY timestamp
        """
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (start_date, end_date))
                results = cursor.fetchall()
                
                if results:
                    df = pd.DataFrame([dict(row) for row in results])
                    return df
                else:
                    return pd.DataFrame()
                    
        except Exception as e:
            logger.error(f"Failed to retrieve incidents by date range: {e}")
            raise
            
    def get_incidents_by_zone(self, governorate: str = None, district: str = None) -> pd.DataFrame:
        """Retrieve incidents by geographic zone"""
        base_query = "SELECT * FROM incidents_clean WHERE 1=1"
        params = []
        
        if governorate:
            base_query += " AND governorate = %s"
            params.append(governorate)
            
        if district:
            base_query += " AND district = %s"
            params.append(district)
            
        base_query += " ORDER BY timestamp"
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(base_query, params)
                results = cursor.fetchall()
                
                if results:
                    df = pd.DataFrame([dict(row) for row in results])
                    return df
                else:
                    return pd.DataFrame()
                    
        except Exception as e:
            logger.error(f"Failed to retrieve incidents by zone: {e}")
            raise
            
    def log_alert(self, alert_type: str, severity: str, message: str, 
                  recipients: List[str], related_incidents: List[int] = None) -> int:
        """Log alert to alerts_log table"""
        query = """
            INSERT INTO alerts_log 
            (alert_type, severity, message, recipients, related_incidents)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (
                    alert_type,
                    severity,
                    message,
                    ','.join(recipients) if recipients else '',
                    json.dumps(related_incidents) if related_incidents else None
                ))
                alert_id = cursor.fetchone()[0]
                logger.info(f"Alert logged with ID: {alert_id}")
                return alert_id
                
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")
            raise
            
    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Get recent alerts from the last N hours"""
        query = """
            SELECT * FROM alerts_log 
            WHERE sent_at >= NOW() - INTERVAL '%s hours'
            ORDER BY sent_at DESC
        """
        
        try:
            return self.execute_query(query, (hours,))
        except Exception as e:
            logger.error(f"Failed to retrieve recent alerts: {e}")
            raise
            
    def cleanup_old_data(self):
        """Clean up old data based on retention policies"""
        cleanup_queries = [
            # Clean raw data
            f"""
            DELETE FROM incidents_raw 
            WHERE ingestion_timestamp < NOW() - INTERVAL '{Config.RAW_DATA_RETENTION_DAYS} days'
            """,
            
            # Clean analytics data
            f"""
            DELETE FROM analytics_summary 
            WHERE created_at < NOW() - INTERVAL '{Config.ANALYTICS_RETENTION_DAYS} days'
            """
        ]
        
        try:
            for query in cleanup_queries:
                rows_deleted = self.execute_command(query)
                logger.info(f"Cleaned up {rows_deleted} old records")
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            raise

# Singleton instance
db_manager = DatabaseManager()