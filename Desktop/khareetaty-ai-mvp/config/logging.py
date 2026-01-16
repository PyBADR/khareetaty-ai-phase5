"""
Centralized logging configuration for Khareetaty AI
Provides consistent logging across all modules
"""
import logging
import logging.handlers
import os
from datetime import datetime
from config.settings import APP

def setup_logging():
    """Configure logging for the application"""
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, APP.LOG_LEVEL))
    console_handler.setFormatter(formatter)
    
    # Create file handler with rotation
    log_filename = os.path.join(log_dir, f"khareetaty_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_filename, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, APP.LOG_LEVEL))
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, APP.LOG_LEVEL))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Reduce noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.INFO)
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    return logging.getLogger(name)

# Initialize logging when module is imported
logger = setup_logging()

# Convenience function for getting module-specific loggers
def get_module_logger(module_name: str) -> logging.Logger:
    """Get logger for a specific module"""
    return get_logger(f"khareetaty.{module_name}")