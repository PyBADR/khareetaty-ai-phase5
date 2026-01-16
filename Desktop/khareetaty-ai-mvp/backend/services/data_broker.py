"""
Data Broker Service for Khareetaty AI
Handles multi-agency data ingestion from various sources
Supports: MOI, Fire/EMS, Municipal, Traffic, Commercial feeds
"""

import redis
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from enum import Enum

logger = logging.getLogger(__name__)

class DataSource(Enum):
    """Enumeration of supported data sources"""
    MOI_INCIDENTS = "moi_incidents"
    FIRE_EMS = "fire_ems"
    MUNICIPAL = "municipal"
    TRAFFIC = "traffic"
    COMMERCIAL = "commercial"
    IOT_SENSORS = "iot_sensors"
    CCTV_METADATA = "cctv_metadata"

class DataBroker:
    """
    Central data broker using Redis Streams for real-time ingestion
    Acts as message bus for all incoming data from multiple agencies
    """
    
    def __init__(self, redis_host="redis", redis_port=6379):
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Connected to Redis data broker")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def publish_event(self, source: DataSource, data: Dict[str, Any]) -> bool:
        """
        Publish event to Redis stream
        
        Args:
            source: Data source type
            data: Event data dictionary
            
        Returns:
            bool: Success status
        """
        if not self.redis_client:
            logger.warning("Redis not available, event not published")
            return False
        
        try:
            # Add metadata
            event = {
                "source": source.value,
                "timestamp": datetime.utcnow().isoformat(),
                "data": json.dumps(data)
            }
            
            # Publish to stream
            stream_name = f"khareetaty:{source.value}"
            self.redis_client.xadd(stream_name, event, maxlen=10000)
            
            logger.info(f"Published event to {stream_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False
    
    def consume_events(self, source: DataSource, count: int = 10) -> List[Dict]:
        """
        Consume events from Redis stream
        
        Args:
            source: Data source to consume from
            count: Number of events to retrieve
            
        Returns:
            List of events
        """
        if not self.redis_client:
            return []
        
        try:
            stream_name = f"khareetaty:{source.value}"
            events = self.redis_client.xread(
                {stream_name: '0'},
                count=count
            )
            
            result = []
            for stream, messages in events:
                for msg_id, msg_data in messages:
                    result.append({
                        "id": msg_id,
                        "source": msg_data.get("source"),
                        "timestamp": msg_data.get("timestamp"),
                        "data": json.loads(msg_data.get("data", "{}"))
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to consume events: {e}")
            return []
    
    def get_stream_info(self, source: DataSource) -> Dict:
        """
        Get information about a stream
        
        Args:
            source: Data source
            
        Returns:
            Stream information dictionary
        """
        if not self.redis_client:
            return {}
        
        try:
            stream_name = f"khareetaty:{source.value}"
            info = self.redis_client.xinfo_stream(stream_name)
            return {
                "length": info.get("length", 0),
                "first_entry": info.get("first-entry"),
                "last_entry": info.get("last-entry")
            }
        except Exception as e:
            logger.error(f"Failed to get stream info: {e}")
            return {}


# Singleton instance
_broker_instance = None

def get_broker() -> DataBroker:
    """Get or create broker instance"""
    global _broker_instance
    if _broker_instance is None:
        _broker_instance = DataBroker()
    return _broker_instance
