"""
Utility functions for Streamlit Dashboard
Handles API calls to backend
"""

import requests
import os
from typing import Optional, Dict, List
import streamlit as st

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN", "")

def get_headers():
    """Get API request headers with authentication"""
    headers = {"Content-Type": "application/json"}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    return headers

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_geo_options():
    """Fetch geographic filter options from API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/geo/options",
            headers=get_headers(),
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            st.error(f"Failed to fetch geo options: {response.status_code}")
            return {}
    except Exception as e:
        st.error(f"Error fetching geo options: {e}")
        return {}

@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_live_status():
    """Fetch live system status"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/status/live",
            headers=get_headers(),
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"system": "error", "message": f"Status code: {response.status_code}"}
    except Exception as e:
        return {"system": "error", "message": str(e)}

def fetch_geojson_layer(layer: str):
    """Fetch GeoJSON data for a specific layer"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/geo/geojson/{layer}",
            headers=get_headers(),
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("data")
        else:
            st.error(f"Failed to fetch {layer} GeoJSON: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching {layer} GeoJSON: {e}")
        return None

def trigger_analytics():
    """Trigger analytics pipeline"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/analytics/run",
            headers=get_headers(),
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": f"Status code: {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def send_alert(message: str, phone: Optional[str] = None):
    """Send WhatsApp alert"""
    try:
        payload = {"message": message}
        if phone:
            payload["phone"] = phone
        
        response = requests.post(
            f"{API_BASE_URL}/alerts/send",
            headers=get_headers(),
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": f"Status code: {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def fetch_alert_history(limit: int = 50):
    """Fetch alert history"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/alerts/history?limit={limit}",
            headers=get_headers(),
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            return []
    except Exception as e:
        st.error(f"Error fetching alert history: {e}")
        return []

def fetch_alert_stats():
    """Fetch alert statistics"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/alerts/stats",
            headers=get_headers(),
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            return {}
    except Exception as e:
        return {}

# Database query functions (direct connection fallback)
def get_db_connection():
    """Get database connection"""
    import psycopg2
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
        dbname=os.getenv("DB_NAME", "khareetaty_ai"),
        user=os.getenv("DB_USER", "bdr.ai"),
        password=os.getenv("DB_PASSWORD", "secret123")
    )

@st.cache_data(ttl=60)
def fetch_incidents(governorate=None, district=None, police_zone=None, limit=1000):
    """Fetch incidents from database"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
            SELECT id, incident_type, lat, lon, timestamp, 
                   district, block, police_zone, governorate
            FROM incidents_clean
            WHERE 1=1
        """
        params = []
        
        if governorate:
            query += " AND governorate = %s"
            params.append(governorate)
        
        if district:
            query += " AND district = %s"
            params.append(district)
        
        if police_zone:
            query += " AND police_zone = %s"
            params.append(police_zone)
        
        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)
        
        cur.execute(query, params)
        rows = cur.fetchall()
        
        incidents = []
        for row in rows:
            incidents.append({
                "id": row[0],
                "incident_type": row[1],
                "lat": row[2],
                "lon": row[3],
                "timestamp": row[4],
                "district": row[5],
                "block": row[6],
                "police_zone": row[7],
                "governorate": row[8]
            })
        
        cur.close()
        conn.close()
        
        return incidents
    except Exception as e:
        st.error(f"Error fetching incidents: {e}")
        return []

@st.cache_data(ttl=60)
def fetch_hotspots(governorate=None, district=None, police_zone=None):
    """Fetch hotspots from database"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
            SELECT zone, governorate, district, police_zone, score, 
                   forecast, created_at, zone_type
            FROM zones_hotspots
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        """
        params = []
        
        if governorate:
            query += " AND governorate = %s"
            params.append(governorate)
        
        if district:
            query += " AND district = %s"
            params.append(district)
        
        if police_zone:
            query += " AND police_zone = %s"
            params.append(police_zone)
        
        query += " ORDER BY score DESC"
        
        cur.execute(query, params)
        rows = cur.fetchall()
        
        hotspots = []
        for row in rows:
            hotspots.append({
                "zone": row[0],
                "governorate": row[1],
                "district": row[2],
                "police_zone": row[3],
                "score": row[4],
                "forecast": row[5],
                "last_seen": row[6],
                "zone_type": row[7]
            })
        
        cur.close()
        conn.close()
        
        return hotspots
    except Exception as e:
        st.error(f"Error fetching hotspots: {e}")
        return []

@st.cache_data(ttl=300)
def fetch_trend_data(zone_type="district", days=30):
    """Fetch trend data for charts"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = f"""
            SELECT 
                DATE(timestamp) as date,
                {zone_type},
                COUNT(*) as incident_count
            FROM incidents_clean
            WHERE timestamp >= NOW() - INTERVAL '{days} days'
            AND {zone_type} IS NOT NULL
            GROUP BY DATE(timestamp), {zone_type}
            ORDER BY date, {zone_type}
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        
        trends = []
        for row in rows:
            trends.append({
                "date": row[0],
                "zone": row[1],
                "count": row[2]
            })
        
        cur.close()
        conn.close()
        
        return trends
    except Exception as e:
        st.error(f"Error fetching trend data: {e}")
        return []
