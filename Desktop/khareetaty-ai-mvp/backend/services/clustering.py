"""Clustering service for hotspot computation"""
import psycopg2
import os
from datetime import datetime, timedelta

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "khareetaty_ai"),
        user=os.getenv("DB_USER", "bdr.ai"),
        password=os.getenv("DB_PASSWORD", "secret123"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )

def compute_hotspots():
    """Compute crime hotspots from incidents data"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get incidents from last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # Compute hotspots by zone
        query = """
        INSERT INTO zones_hotspots (zone_id, incident_count, severity_score, last_updated)
        SELECT 
            zone_id,
            COUNT(*) as incident_count,
            AVG(CASE 
                WHEN severity = 'high' THEN 3
                WHEN severity = 'medium' THEN 2
                ELSE 1
            END) as severity_score,
            NOW() as last_updated
        FROM incidents_clean
        WHERE created_at >= %s
        GROUP BY zone_id
        ON CONFLICT (zone_id) DO UPDATE
        SET incident_count = EXCLUDED.incident_count,
            severity_score = EXCLUDED.severity_score,
            last_updated = EXCLUDED.last_updated;
        """
        
        cur.execute(query, (thirty_days_ago,))
        conn.commit()
        
        print(f"Hotspots computed successfully at {datetime.now()}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error computing hotspots: {e}")
