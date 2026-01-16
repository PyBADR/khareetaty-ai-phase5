import psycopg2
import pandas as pd
from sklearn.cluster import DBSCAN
from datetime import datetime
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

DB_CONN = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME", "khareetaty_ai"),
    "user": os.getenv("DB_USER", "bdr.ai"),
    "password": os.getenv("DB_PASSWORD", "")
}

def compute_hotspots_per_zone():
    """
    Compute crime hotspots per district using DBSCAN clustering
    This provides zone-aware hotspot detection
    """
    try:
        conn = psycopg2.connect(**DB_CONN)
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        raise

    cur = conn.cursor()
    
    # Get unique districts with incidents
    districts_df = pd.read_sql("""
        SELECT DISTINCT district 
        FROM incidents_clean 
        WHERE district IS NOT NULL 
        AND timestamp >= NOW() - INTERVAL '30 days'
    """, conn)
    
    if districts_df.empty:
        logger.warning("No districts found with recent incidents.")
        conn.close()
        return
    
    districts = districts_df['district'].tolist()
    logger.info(f"Processing {len(districts)} districts for hotspot detection")
    
    total_hotspots = 0
    
    for district in districts:
        try:
            # Get incidents for this district
            df = pd.read_sql("""
                SELECT lat, lon, incident_type, police_zone, governorate
                FROM incidents_clean 
                WHERE district = %s 
                AND timestamp >= NOW() - INTERVAL '30 days'
            """, conn, params=(district,))
            
            if len(df) < 3:
                logger.debug(f"District {district}: Too few incidents ({len(df)}) for clustering")
                continue
            
            coords = df[["lat", "lon"]].values
            
            # Tighter clustering for district-level (smaller eps)
            model = DBSCAN(eps=0.01, min_samples=3, metric='euclidean')  # ~1.1km radius
            labels = model.fit_predict(coords)
            
            df["cluster"] = labels
            
            # Get cluster statistics
            clusters = df[df["cluster"] != -1].groupby("cluster").agg({
                "lat": ["mean", "count"],
                "lon": "mean",
                "incident_type": lambda x: x.mode()[0] if len(x) > 0 else None,
                "police_zone": lambda x: x.mode()[0] if len(x) > 0 else None,
                "governorate": lambda x: x.mode()[0] if len(x) > 0 else None
            })
            
            if clusters.empty:
                continue
            
            # Insert hotspots for this district
            for cluster_id in clusters.index:
                count = int(clusters.loc[cluster_id, ("lat", "count")])
                center_lat = float(clusters.loc[cluster_id, ("lat", "mean")])
                center_lon = float(clusters.loc[cluster_id, ("lon", "mean")])
                police_zone = clusters.loc[cluster_id, ("police_zone", "<lambda>")]
                
                zone_key = f"{district}_cluster_{cluster_id}"
                score = float(count)
                
                cur.execute("""
                    INSERT INTO zones_hotspots 
                    (zone, score, predicted, zone_type, district, police_zone, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (zone, predicted) DO UPDATE SET
                        score = EXCLUDED.score,
                        district = EXCLUDED.district,
                        police_zone = EXCLUDED.police_zone,
                        created_at = EXCLUDED.created_at
                """, (
                    zone_key, 
                    score, 
                    False, 
                    'district_cluster',
                    district,
                    police_zone,
                    datetime.now()
                ))
                
                total_hotspots += 1
                logger.debug(f"District {district}: Cluster {cluster_id} with {count} incidents")
        
        except Exception as e:
            logger.error(f"Error processing district {district}: {e}")
            continue
    
    conn.commit()
    conn.close()
    logger.info(f"Zone-aware clustering complete. Found {total_hotspots} hotspots across {len(districts)} districts.")
    return total_hotspots

def compute_hotspots():
    """
    Legacy function - now calls zone-aware clustering
    Maintained for backward compatibility
    """
    return compute_hotspots_per_zone()

def compute_hotspots_by_police_zone():
    """
    Compute hotspots aggregated by police zone
    Useful for police resource allocation
    """
    try:
        conn = psycopg2.connect(**DB_CONN)
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        raise
    
    cur = conn.cursor()
    
    # Aggregate incidents by police zone
    police_zones_df = pd.read_sql("""
        SELECT 
            police_zone,
            COUNT(*) as incident_count,
            COUNT(DISTINCT district) as district_count,
            COUNT(DISTINCT incident_type) as incident_types
        FROM incidents_clean
        WHERE police_zone IS NOT NULL
        AND timestamp >= NOW() - INTERVAL '30 days'
        GROUP BY police_zone
    """, conn)
    
    if police_zones_df.empty:
        logger.warning("No police zones found with incidents")
        conn.close()
        return
    
    for _, row in police_zones_df.iterrows():
        police_zone = row['police_zone']
        score = float(row['incident_count'])
        
        cur.execute("""
            INSERT INTO zones_hotspots 
            (zone, score, predicted, zone_type, police_zone, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (zone, predicted) DO UPDATE SET
                score = EXCLUDED.score,
                created_at = EXCLUDED.created_at
        """, (
            f"pz_{police_zone}",
            score,
            False,
            'police_zone',
            police_zone,
            datetime.now()
        ))
    
    conn.commit()
    conn.close()
    logger.info(f"Police zone aggregation complete. Processed {len(police_zones_df)} zones.")


if __name__ == "__main__":
    compute_hotspots()