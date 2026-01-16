"""
Health Check Service
Continuously monitors all system components and sends alerts on failures
"""

import requests
import time
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 60))  # seconds
ALERT_WEBHOOK = os.getenv('ALERT_WEBHOOK', '')

# Services to monitor
SERVICES = [
    {'name': 'Backend-1', 'url': 'http://backend-1:8000/health', 'critical': True},
    {'name': 'Backend-2', 'url': 'http://backend-2:8000/health', 'critical': True},
    {'name': 'Backend-3', 'url': 'http://backend-3:8000/health', 'critical': True},
    {'name': 'Postgres-Primary', 'url': 'http://postgres-primary:5432', 'critical': True},
    {'name': 'Redis-Primary', 'url': 'http://redis-primary:6379', 'critical': True},
]

def check_service(service):
    """Check if a service is healthy"""
    try:
        response = requests.get(service['url'], timeout=5)
        if response.status_code == 200:
            return True, 'healthy'
        else:
            return False, f'status_code: {response.status_code}'
    except requests.exceptions.ConnectionError:
        return False, 'connection_refused'
    except requests.exceptions.Timeout:
        return False, 'timeout'
    except Exception as e:
        return False, str(e)

def send_alert(service_name, status, reason):
    """Send alert notification"""
    message = f"🚨 ALERT: {service_name} is {status}\nReason: {reason}\nTime: {datetime.now().isoformat()}"
    
    logger.error(message)
    
    if ALERT_WEBHOOK:
        try:
            requests.post(ALERT_WEBHOOK, json={'text': message}, timeout=5)
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")

def monitor_services():
    """Main monitoring loop"""
    logger.info("Health check service started")
    logger.info(f"Monitoring {len(SERVICES)} services every {CHECK_INTERVAL} seconds")
    
    service_status = {s['name']: True for s in SERVICES}
    
    while True:
        try:
            for service in SERVICES:
                healthy, reason = check_service(service)
                
                # Status changed from healthy to unhealthy
                if not healthy and service_status[service['name']]:
                    send_alert(service['name'], 'DOWN', reason)
                    service_status[service['name']] = False
                
                # Status changed from unhealthy to healthy
                elif healthy and not service_status[service['name']]:
                    logger.info(f"✅ {service['name']} is back online")
                    service_status[service['name']] = True
                
                # Log current status
                status_emoji = '✅' if healthy else '❌'
                logger.info(f"{status_emoji} {service['name']}: {reason}")
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Health check service stopped")
            break
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    monitor_services()