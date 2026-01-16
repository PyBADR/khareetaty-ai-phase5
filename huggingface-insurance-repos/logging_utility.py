"""
Logging utility for Insurance AI Factory applications
Provides consistent logging across all apps with invocation tracking
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

class InsuranceAILogger:
    """
    A simple logger utility for tracking invocations and errors in insurance AI apps.
    All logs are stored locally only - no external services.
    """
    
    def __init__(self, app_name="insurance_app", log_dir="logs"):
        self.app_name = app_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize invocation counter
        self.counter_file = self.log_dir / f"{app_name}_counter.json"
        self._init_counter()
    
    def _init_counter(self):
        """Initialize the invocation counter"""
        if not self.counter_file.exists():
            with open(self.counter_file, 'w') as f:
                json.dump({"count": 0, "last_updated": datetime.now().isoformat()}, f)
    
    def get_invocation_count(self):
        """Get the current invocation count"""
        if self.counter_file.exists():
            with open(self.counter_file, 'r') as f:
                data = json.load(f)
                return data.get("count", 0)
        return 0
    
    def increment_invocation(self):
        """Increment the invocation counter"""
        if self.counter_file.exists():
            with open(self.counter_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"count": 0}
        
        data["count"] += 1
        data["last_updated"] = datetime.now().isoformat()
        
        with open(self.counter_file, 'w') as f:
            json.dump(data, f)
        
        return data["count"]
    
    def log_invocation(self, inputs, outputs, user_id=None, session_id=None):
        """Log an invocation with inputs and outputs"""
        invocation_count = self.increment_invocation()
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "invocation_number": invocation_count,
            "app_name": self.app_name,
            "inputs": inputs,
            "outputs": outputs,
            "user_id": user_id,
            "session_id": session_id,
            "log_type": "invocation"
        }
        
        # Write to invocation log
        log_file = self.log_dir / f"{self.app_name}_invocations.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        return invocation_count
    
    def log_error(self, error_msg, inputs=None, user_id=None, session_id=None):
        """Log an error"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "app_name": self.app_name,
            "error": str(error_msg),
            "inputs": inputs,
            "user_id": user_id,
            "session_id": session_id,
            "log_type": "error"
        }
        
        # Write to error log
        log_file = self.log_dir / f"{self.app_name}_errors.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def log_warning(self, warning_msg, inputs=None, user_id=None, session_id=None):
        """Log a warning"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "app_name": self.app_name,
            "warning": str(warning_msg),
            "inputs": inputs,
            "user_id": user_id,
            "session_id": session_id,
            "log_type": "warning"
        }
        
        # Write to warning log
        log_file = self.log_dir / f"{self.app_name}_warnings.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

# Example usage function
def add_logging_to_gradio_app(app, logger):
    """
    Utility function to add logging to a Gradio app
    This is a decorator-style function to wrap Gradio interfaces
    """
    def logged_function(*args, **kwargs):
        try:
            # Log the invocation
            inputs = {"args": args, "kwargs": kwargs}
            result = app(*args, **kwargs)  # Execute the original function
            outputs = {"result": result}
            
            # Log successful invocation
            invocation_count = logger.log_invocation(inputs, outputs)
            
            return result
        except Exception as e:
            # Log the error
            logger.log_error(str(e), inputs={"args": args, "kwargs": kwargs})
            raise  # Re-raise the exception
    
    return logged_function

# Example implementation for Gradio apps
def setup_logging_for_app(app_name):
    """
    Set up logging for a Gradio app
    Returns a logger instance
    """
    logger = InsuranceAILogger(app_name=app_name)
    
    # Print status
    invocation_count = logger.get_invocation_count()
    print(f"📊 {app_name} has been invoked {invocation_count} times")
    
    return logger

# Example usage in an app:
"""
# In your app.py:
from logging_utility import setup_logging_for_app

logger = setup_logging_for_app("premium-lapse-monitor")

# Then wrap your processing function:
def process_with_logging(input_param):
    try:
        # Your processing logic here
        result = f"Processed: {input_param}"
        
        # Log the invocation
        logger.log_invocation({"input": input_param}, {"result": result})
        
        return result
    except Exception as e:
        logger.log_error(str(e), inputs={"input": input_param})
        raise
"""