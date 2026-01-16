#!/usr/bin/env python3
"""
Smoke tests for premium-lapse-monitor
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all required imports work"""
    try:
        import streamlit
        import pandas
        import numpy
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_app_file_exists():
    """Test that app.py exists"""
    app_path = Path(__file__).parent.parent / "app.py"
    assert app_path.exists(), "app.py not found"

def test_readme_exists():
    """Test that README.md exists"""
    readme_path = Path(__file__).parent.parent / "README.md"
    assert readme_path.exists(), "README.md not found"

def test_model_card_exists():
    """Test that model_card.md exists"""
    model_card_path = Path(__file__).parent.parent / "model_card.md"
    assert model_card_path.exists(), "model_card.md not found"

def test_requirements_exists():
    """Test that requirements.txt exists"""
    req_path = Path(__file__).parent.parent / "requirements.txt"
    assert req_path.exists(), "requirements.txt not found"

def test_governance_disclaimers():
    """Test that governance disclaimers are present"""
    readme_path = Path(__file__).parent.parent / "README.md"
    content = readme_path.read_text()
    
    required_terms = [
        "Synthetic Data Only",
        "Human-in-Loop",
        "No Pricing Authority",
        "No Payout Authority",
        "No Underwriting Authority"
    ]
    
    for term in required_terms:
        assert term in content, f"Missing governance term: {term}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
