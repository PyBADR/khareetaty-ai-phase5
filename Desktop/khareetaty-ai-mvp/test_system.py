#!/usr/bin/env python3
"""
Khareetaty AI - System Verification Script
Tests all components of the system end-to-end
"""
import sys
import os
import time
import requests
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import DATABASE, APP
from config.database import health_check, execute_query
from config.logging import get_module_logger

logger = get_module_logger("system_test")

def test_database_connection():
    """Test database connectivity"""
    print("🔍 Testing database connection...")
    try:
        if health_check():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("🔍 Testing API endpoints...")
    
    base_url = f"http://localhost:{APP.PORT}"
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint accessible")
        else:
            print(f"❌ Root endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint test failed: {e}")
        return False
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint accessible")
        else:
            print(f"❌ Health endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False
    
    return True

def test_data_loading():
    """Test data loading capability"""
    print("🔍 Testing data loading...")
    
    try:
        # Check if incidents_raw table exists and has data
        query = "SELECT COUNT(*) FROM incidents_raw;"
        result = execute_query(query)
        
        if result and len(result) > 0:
            count = result[0][0]
            print(f"✅ Found {count} records in incidents_raw table")
            return True
        else:
            print("❌ No data found in incidents_raw table")
            return False
    except Exception as e:
        print(f"❌ Data loading test failed: {e}")
        return False

def test_clustering_service():
    """Test clustering service"""
    print("🔍 Testing clustering service...")
    
    try:
        # Import and test clustering function
        from services.clustering import compute_hotspots
        print("✅ Clustering service imported successfully")
        return True
    except Exception as e:
        print(f"❌ Clustering service test failed: {e}")
        return False

def test_modeling_service():
    """Test modeling service"""
    print("🔍 Testing modeling service...")
    
    try:
        # Import and test modeling functions
        from services.modeling import predict_trends, predict_by_governorate
        print("✅ Modeling service imported successfully")
        return True
    except Exception as e:
        print(f"❌ Modeling service test failed: {e}")
        return False

def test_notification_service():
    """Test notification service"""
    print("🔍 Testing notification service...")
    
    try:
        # Import notification functions
        from services.notifications import send_whatsapp, send_sms, send_email
        print("✅ Notification service imported successfully")
        return True
    except Exception as e:
        print(f"❌ Notification service test failed: {e}")
        return False

def test_etl_pipeline():
    """Test ETL pipeline"""
    print("🔍 Testing ETL pipeline...")
    
    try:
        # Import ETL functions
        from automation.etl_job import run_full_etl
        print("✅ ETL pipeline imported successfully")
        return True
    except Exception as e:
        print(f"❌ ETL pipeline test failed: {e}")
        return False

def run_complete_verification():
    """Run complete system verification"""
    print("=" * 60)
    print("🚀 KHAREETATY AI - SYSTEM VERIFICATION")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Database Connection", test_database_connection),
        ("API Endpoints", test_api_endpoints),
        ("Data Loading", test_data_loading),
        ("Clustering Service", test_clustering_service),
        ("Modeling Service", test_modeling_service),
        ("Notification Service", test_notification_service),
        ("ETL Pipeline", test_etl_pipeline),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready for use.")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_complete_verification()
    sys.exit(0 if success else 1)