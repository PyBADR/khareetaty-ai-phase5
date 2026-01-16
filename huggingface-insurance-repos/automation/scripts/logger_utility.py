#!/usr/bin/env python3
"""
Logger Utility - Monitoring and logging for all applications
Part of gcc-insurance-intelligence-lab Platform Automation
"""

import json
import os
from datetime import datetime
from pathlib import Path
import traceback

class AppLogger:
    """Simple logger for tracking invocations and crashes"""
    
    def __init__(self, app_name, log_dir=None):
        self.app_name = app_name
        
        if log_dir is None:
            # Default to logs directory in app root
            self.log_dir = Path.cwd() / "logs"
        else:
            self.log_dir = Path(log_dir)
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.invocation_log = self.log_dir / f"{app_name}_invocations.jsonl"
        self.crash_log = self.log_dir / f"{app_name}_crashes.log"
        self.activity_log = self.log_dir / f"{app_name}_activity.jsonl"
    
    def log_invocation(self, function_name, action_type="call", metadata=None):
        """Log a function invocation"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "app": self.app_name,
                "function": function_name,
                "action": action_type,
                "metadata": metadata or {}
            }
            
            with open(self.invocation_log, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
            
            return True
        except Exception as e:
            print(f"Warning: Failed to log invocation: {e}")
            return False
    
    def log_crash(self, error, context=None):
        """Log a crash or error"""
        try:
            timestamp = datetime.now().isoformat()
            
            crash_entry = f"""
{'='*80}
CRASH REPORT
Timestamp: {timestamp}
App: {self.app_name}
Context: {context or 'N/A'}

Error: {str(error)}

Traceback:
{traceback.format_exc()}
{'='*80}

"""
            
            with open(self.crash_log, "a") as f:
                f.write(crash_entry)
            
            # Also log to activity
            self.log_activity("crash", {
                "error": str(error),
                "context": context
            })
            
            return True
        except Exception as e:
            print(f"Warning: Failed to log crash: {e}")
            return False
    
    def log_activity(self, activity_type, details=None):
        """Log general activity"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "app": self.app_name,
                "activity": activity_type,
                "details": details or {}
            }
            
            with open(self.activity_log, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
            
            return True
        except Exception as e:
            print(f"Warning: Failed to log activity: {e}")
            return False
    
    def get_invocation_count(self, function_name=None, since=None):
        """Get invocation count for a function or all functions"""
        try:
            if not self.invocation_log.exists():
                return 0
            
            count = 0
            with open(self.invocation_log, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        
                        # Filter by function name if specified
                        if function_name and entry.get("function") != function_name:
                            continue
                        
                        # Filter by timestamp if specified
                        if since:
                            entry_time = datetime.fromisoformat(entry["timestamp"])
                            if entry_time < since:
                                continue
                        
                        count += 1
                    except:
                        continue
            
            return count
        except Exception as e:
            print(f"Warning: Failed to get invocation count: {e}")
            return 0
    
    def get_recent_crashes(self, limit=10):
        """Get recent crash entries"""
        try:
            if not self.crash_log.exists():
                return []
            
            crashes = []
            with open(self.crash_log, "r") as f:
                content = f.read()
                crash_blocks = content.split("="*80)
                
                for block in crash_blocks:
                    if "CRASH REPORT" in block:
                        crashes.append(block.strip())
            
            return crashes[-limit:]
        except Exception as e:
            print(f"Warning: Failed to get recent crashes: {e}")
            return []
    
    def get_activity_summary(self, since=None):
        """Get summary of activity"""
        try:
            if not self.activity_log.exists():
                return {}
            
            summary = {}
            with open(self.activity_log, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        
                        # Filter by timestamp if specified
                        if since:
                            entry_time = datetime.fromisoformat(entry["timestamp"])
                            if entry_time < since:
                                continue
                        
                        activity = entry.get("activity", "unknown")
                        summary[activity] = summary.get(activity, 0) + 1
                    except:
                        continue
            
            return summary
        except Exception as e:
            print(f"Warning: Failed to get activity summary: {e}")
            return {}

class LogAggregator:
    """Aggregate logs from multiple applications"""
    
    def __init__(self, base_path="/Users/bdr.ai/huggingface-insurance-repos"):
        self.base_path = Path(base_path)
    
    def collect_all_logs(self):
        """Collect logs from all applications"""
        all_logs = {
            "invocations": [],
            "crashes": [],
            "activity": []
        }
        
        # Find all log directories
        for log_dir in self.base_path.rglob("logs"):
            if log_dir.is_dir():
                # Read invocation logs
                for inv_log in log_dir.glob("*_invocations.jsonl"):
                    try:
                        with open(inv_log, "r") as f:
                            for line in f:
                                try:
                                    all_logs["invocations"].append(json.loads(line))
                                except:
                                    continue
                    except:
                        continue
                
                # Read activity logs
                for act_log in log_dir.glob("*_activity.jsonl"):
                    try:
                        with open(act_log, "r") as f:
                            for line in f:
                                try:
                                    all_logs["activity"].append(json.loads(line))
                                except:
                                    continue
                    except:
                        continue
                
                # Read crash logs
                for crash_log in log_dir.glob("*_crashes.log"):
                    try:
                        with open(crash_log, "r") as f:
                            content = f.read()
                            crash_blocks = content.split("="*80)
                            for block in crash_blocks:
                                if "CRASH REPORT" in block:
                                    all_logs["crashes"].append(block.strip())
                    except:
                        continue
        
        return all_logs
    
    def generate_summary_report(self):
        """Generate a summary report of all activity"""
        logs = self.collect_all_logs()
        
        report = {
            "generated": datetime.now().isoformat(),
            "total_invocations": len(logs["invocations"]),
            "total_crashes": len(logs["crashes"]),
            "total_activity": len(logs["activity"]),
            "apps": {},
            "activity_types": {},
            "recent_crashes": logs["crashes"][-5:] if logs["crashes"] else []
        }
        
        # Count by app
        for inv in logs["invocations"]:
            app = inv.get("app", "unknown")
            if app not in report["apps"]:
                report["apps"][app] = {"invocations": 0, "crashes": 0}
            report["apps"][app]["invocations"] += 1
        
        # Count activity types
        for act in logs["activity"]:
            activity_type = act.get("activity", "unknown")
            report["activity_types"][activity_type] = report["activity_types"].get(activity_type, 0) + 1
        
        return report

if __name__ == "__main__":
    # Test the logger
    logger = AppLogger("test-app")
    
    print("Testing logger...")
    logger.log_invocation("test_function", "test_action")
    logger.log_activity("startup", {"version": "1.0"})
    
    print(f"Invocation count: {logger.get_invocation_count()}")
    print(f"Activity summary: {logger.get_activity_summary()}")
    
    print("\n✅ Logger utility test complete!")
