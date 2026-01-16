#!/usr/bin/env python3
"""
Full pipeline runner for Khareetaty AI system
Executes all components in the correct order
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {description}")
    print(f"Command: {cmd}")
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            if result.stdout.strip():
                print(result.stdout)
        else:
            print("❌ FAILED")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🚀 Khareetaty AI - Full Pipeline Runner")
    print("="*50)
    
    # Check if we're in the right directory
    if not os.path.exists("backend/main.py"):
        print("❌ Error: Not in the project root directory")
        print("Please run this script from the khareetaty-ai-mvp directory")
        return 1
    
    # Steps to run
    steps = [
        ("python3 backend/db/migrations.py", "Setting up database tables"),
        ("python3 src/sample_data_generator.py", "Generating sample data"),
        ("python3 automation/etl_job.py", "Running ETL pipeline"),
        ("python3 services/clustering.py", "Computing crime hotspots"),
        ("python3 services/modeling.py", "Running forecasting models"),
        ("python3 automation/trigger_alerts.py", "Checking for alerts"),
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for cmd, desc in steps:
        if run_command(cmd, desc):
            success_count += 1
        print("-" * 30)
    
    print(f"\n📊 Pipeline Summary:")
    print(f"Total steps: {total_steps}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_steps - success_count}")
    
    if success_count == total_steps:
        print("\n🎉 All pipeline steps completed successfully!")
        print("\nNext steps:")
        print("- Start the API server: python3 backend/main.py")
        print("- Or with uvicorn: uvicorn backend.main:app --reload")
        print("- Access the API at: http://localhost:8000")
        print("- Dashboard: streamlit run src/dashboard.py")
        return 0
    else:
        print(f"\n⚠️  {total_steps - success_count} steps failed. Check logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())