"""
Interoperability Manager
Handles secure communication with external government systems
"""

import logging
import hashlib
import hmac
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import psycopg2

logger = logging.getLogger(__name__)

DB_CONN = {
    "host": "postgres",
    "dbname": "khareetaty_ai",
    "user": "bader",
    "password": "secret123"
}

class InteroperabilityManager:
    """
    Manages interoperability with external systems:
    - API key management
    - Service account authentication
    - Webhook delivery
    - Data format standardization
    - Rate limiting
    """
    
    def __init__(self):
        self.conn = None
    
    def _get_connection(self):
        """Get database connection"""
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(**DB_CONN)
        return self.conn
    
    def generate_api_key(self, service_name: str, permissions: str = "read") -> str:
        """
        Generate API key for external service
        
        Args:
            service_name: Name of the external service
            permissions: Permission level (read, write, admin)
            
        Returns:
            Generated API key
        """
        try:
            # Generate secure API key
            timestamp = datetime.now().isoformat()
            raw_key = f"{service_name}:{timestamp}:{permissions}"
            api_key = hashlib.sha256(raw_key.encode()).hexdigest()
            
            # Store in database
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO api_keys (service_name, api_key, permissions, active)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (service_name) DO UPDATE
                SET api_key = EXCLUDED.api_key,
                    permissions = EXCLUDED.permissions,
                    updated_at = NOW()
            """, (service_name, api_key, permissions, True))
            
            conn.commit()
            
            logger.info(f"Generated API key for {service_name}")
            return api_key
            
        except Exception as e:
            logger.error(f"Failed to generate API key: {e}")
            return ""
    
    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """
        Validate API key and return service info
        
        Args:
            api_key: API key to validate
            
        Returns:
            Service information if valid, None otherwise
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT service_name, permissions, active
                FROM api_keys
                WHERE api_key = %s AND active = true
            """, (api_key,))
            
            result = cur.fetchone()
            
            if result:
                return {
                    "service_name": result[0],
                    "permissions": result[1],
                    "active": result[2]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to validate API key: {e}")
            return None
    
    def revoke_api_key(self, service_name: str) -> bool:
        """
        Revoke API key for a service
        
        Args:
            service_name: Name of the service
            
        Returns:
            Success status
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE api_keys
                SET active = false, updated_at = NOW()
                WHERE service_name = %s
            """, (service_name,))
            
            conn.commit()
            
            logger.info(f"Revoked API key for {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke API key: {e}")
            return False
    
    def log_api_request(self, service_name: str, endpoint: str, method: str, status: int):
        """
        Log API request for monitoring and rate limiting
        
        Args:
            service_name: Name of the service
            endpoint: API endpoint accessed
            method: HTTP method
            status: Response status code
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO api_request_log 
                (service_name, endpoint, method, status, timestamp)
                VALUES (%s, %s, %s, %s, NOW())
            """, (service_name, endpoint, method, status))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Failed to log API request: {e}")
    
    def check_rate_limit(self, service_name: str, limit: int = 100, window_minutes: int = 60) -> bool:
        """
        Check if service has exceeded rate limit
        
        Args:
            service_name: Name of the service
            limit: Maximum requests allowed
            window_minutes: Time window in minutes
            
        Returns:
            True if within limit, False if exceeded
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT COUNT(*) FROM api_request_log
                WHERE service_name = %s
                AND timestamp > NOW() - INTERVAL '%s minutes'
            """, (service_name, window_minutes))
            
            count = cur.fetchone()[0]
            
            if count >= limit:
                logger.warning(f"Rate limit exceeded for {service_name}: {count}/{limit}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            return True  # Allow on error
    
    def standardize_incident_format(self, data: Dict, source_format: str) -> Dict:
        """
        Standardize incident data from different sources
        
        Args:
            data: Raw incident data
            source_format: Source system format (moi, fire, municipal, etc.)
            
        Returns:
            Standardized incident data
        """
        # Standard format
        standard = {
            "incident_type": "",
            "governorate": "unknown",
            "zone": "unknown",
            "lat": 0.0,
            "lon": 0.0,
            "timestamp": datetime.now().isoformat(),
            "severity": "medium",
            "source": source_format
        }
        
        # Map different formats to standard
        if source_format == "moi":
            standard.update({
                "incident_type": data.get("type", data.get("incident_type", "unknown")),
                "governorate": data.get("governorate", "unknown"),
                "zone": data.get("zone", "unknown"),
                "lat": float(data.get("latitude", data.get("lat", 0))),
                "lon": float(data.get("longitude", data.get("lon", 0))),
                "timestamp": data.get("timestamp", data.get("time", datetime.now().isoformat())),
                "severity": data.get("severity", "medium")
            })
        
        elif source_format == "fire":
            standard.update({
                "incident_type": "fire",
                "governorate": data.get("location", "unknown"),
                "zone": data.get("location", "unknown"),
                "lat": float(data.get("lat", 0)),
                "lon": float(data.get("lon", 0)),
                "timestamp": data.get("timestamp", datetime.now().isoformat()),
                "severity": data.get("severity", "high")
            })
        
        elif source_format == "traffic":
            standard.update({
                "incident_type": "traffic_accident",
                "governorate": data.get("location", "unknown"),
                "zone": data.get("location", "unknown"),
                "lat": float(data.get("lat", 0)),
                "lon": float(data.get("lon", 0)),
                "timestamp": data.get("timestamp", datetime.now().isoformat()),
                "severity": data.get("severity", "medium")
            })
        
        return standard
    
    def prepare_webhook_payload(self, event_type: str, data: Dict) -> Dict:
        """
        Prepare standardized webhook payload
        
        Args:
            event_type: Type of event (incident, alert, hotspot)
            data: Event data
            
        Returns:
            Standardized webhook payload
        """
        return {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "source": "khareetaty_ai",
            "version": "1.0",
            "data": data
        }
    
    def sign_webhook_payload(self, payload: Dict, secret: str) -> str:
        """
        Sign webhook payload for verification
        
        Args:
            payload: Webhook payload
            secret: Shared secret
            
        Returns:
            HMAC signature
        """
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def get_service_statistics(self, service_name: str, days: int = 7) -> Dict:
        """
        Get API usage statistics for a service
        
        Args:
            service_name: Name of the service
            days: Number of days to analyze
            
        Returns:
            Usage statistics
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            # Total requests
            cur.execute("""
                SELECT COUNT(*) FROM api_request_log
                WHERE service_name = %s
                AND timestamp > NOW() - INTERVAL '%s days'
            """, (service_name, days))
            
            total_requests = cur.fetchone()[0]
            
            # Requests by status
            cur.execute("""
                SELECT status, COUNT(*) FROM api_request_log
                WHERE service_name = %s
                AND timestamp > NOW() - INTERVAL '%s days'
                GROUP BY status
            """, (service_name, days))
            
            status_breakdown = {row[0]: row[1] for row in cur.fetchall()}
            
            # Most accessed endpoints
            cur.execute("""
                SELECT endpoint, COUNT(*) as count FROM api_request_log
                WHERE service_name = %s
                AND timestamp > NOW() - INTERVAL '%s days'
                GROUP BY endpoint
                ORDER BY count DESC
                LIMIT 5
            """, (service_name, days))
            
            top_endpoints = [{
                "endpoint": row[0],
                "count": row[1]
            } for row in cur.fetchall()]
            
            return {
                "service_name": service_name,
                "days_analyzed": days,
                "total_requests": total_requests,
                "status_breakdown": status_breakdown,
                "top_endpoints": top_endpoints,
                "avg_requests_per_day": round(total_requests / days, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get service statistics: {e}")
            return {}


if __name__ == "__main__":
    manager = InteroperabilityManager()
    
    # Generate API keys for different services
    moi_key = manager.generate_api_key("MOI_System", "write")
    fire_key = manager.generate_api_key("Fire_Department", "write")
    
    print(f"MOI API Key: {moi_key}")
    print(f"Fire API Key: {fire_key}")
