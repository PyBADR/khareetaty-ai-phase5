"""
Basic test script for fnol-fast-triage-agent
Tests basic functionality and imports
"""

def test_imports():
    """Test that required modules can be imported"""
    try:
        import gradio as gr
        print("✓ Gradio import successful")
    except ImportError:
        print("✗ Gradio import failed")
        return False
    
    try:
        import app
        print("✓ App module import successful")
    except ImportError as e:
        print(f"✗ App module import failed: {e}")
        return False
    
    return True

def test_app_structure():
    """Test that app has required structure"""
    try:
        import app
        # Check if demo exists
        if hasattr(app, 'demo'):
            print("✓ App has demo object")
            return True
        else:
            print("✗ App does not have demo object")
            return False
    except Exception as e:
        print(f"✗ App structure test failed: {e}")
        return False

def run_tests():
    """Run all tests"""
    print(f"Running tests for fnol-fast-triage-agent...")
    
    tests = [
        test_imports,
        test_app_structure
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    if all(results):
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n✗ Some tests failed!")
        return False

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
