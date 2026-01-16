#!/usr/bin/env python3
"""
Repository Factory - Auto-generate folder structure and files for new use cases
Part of gcc-insurance-intelligence-lab Platform Automation
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Governance templates
DISCLAIMER = """
⚠️ **IMPORTANT DISCLAIMERS**

- **Synthetic Data Only**: This application uses only synthetic, artificially generated data
- **No Real Customer Data**: No personal, confidential, or real customer information is used
- **Human-in-Loop Required**: All outputs require human review and validation
- **No Pricing Authority**: This tool does not set prices, rates, or premiums
- **No Payout Authority**: This tool does not authorize claims payments or payouts
- **No Underwriting Authority**: This tool does not make underwriting decisions
- **Educational Purpose**: For demonstration and research purposes only
- **Not Production Ready**: Requires additional validation before production use
"""

class RepositoryFactory:
    def __init__(self, base_path="/Users/bdr.ai/huggingface-insurance-repos"):
        self.base_path = Path(base_path)
        self.templates_path = self.base_path / "automation" / "templates"
        
    def create_use_case(self, use_case_name, description="", include_dataset=True):
        """
        Create a new use case repository with complete structure
        """
        # Sanitize name
        repo_name = use_case_name.lower().replace(" ", "-").replace("_", "-")
        repo_path = self.base_path / repo_name
        
        print(f"🏭 Creating use case: {repo_name}")
        
        # Create directory structure
        directories = [
            repo_path,
            repo_path / "models",
            repo_path / "data",
            repo_path / "logs",
            repo_path / "tests",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created {directory.name}/")
        
        # Generate files
        self._create_app_py(repo_path, repo_name, description)
        self._create_readme(repo_path, repo_name, description)
        self._create_model_card(repo_path, repo_name, description)
        self._create_requirements(repo_path)
        self._create_gitignore(repo_path)
        self._create_smoke_test(repo_path, repo_name)
        
        if include_dataset:
            self._create_dataset_template(repo_path, repo_name)
        
        print(f"\n✅ Use case '{repo_name}' created successfully!")
        print(f"📁 Location: {repo_path}")
        
        return repo_path
    
    def _create_app_py(self, repo_path, repo_name, description):
        """Generate app.py with Streamlit/Gradio template"""
        title = repo_name.replace("-", " ").title()
        
        content = f'''#!/usr/bin/env python3
"""
{title}
{description}

Part of gcc-insurance-intelligence-lab
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

# Add logging
sys.path.append(str(Path(__file__).parent.parent / "automation" / "scripts"))
try:
    from logger_utility import AppLogger
    logger = AppLogger("{repo_name}")
except ImportError:
    logger = None

# Page config
st.set_page_config(
    page_title="{title}",
    page_icon="🏢",
    layout="wide"
)

# Header
st.title("🏢 {title}")
st.markdown("{description}")

# Disclaimers
with st.expander("⚠️ Important Disclaimers - READ BEFORE USE"):
    st.markdown("""{DISCLAIMER}""")

# Main application
st.header("Application")

tab1, tab2, tab3 = st.tabs(["Input", "Analysis", "Results"])

with tab1:
    st.subheader("Input Data")
    st.info("Upload or input your synthetic data here")
    
    # Example input
    uploaded_file = st.file_uploader("Upload CSV (Synthetic Data Only)", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())
        
        if logger:
            logger.log_invocation("{repo_name}", "file_upload")

with tab2:
    st.subheader("Analysis")
    st.info("Analysis logic goes here")
    
    if st.button("Run Analysis"):
        with st.spinner("Processing..."):
            # Placeholder for analysis logic
            st.success("Analysis complete!")
            
            if logger:
                logger.log_invocation("{repo_name}", "analysis_run")

with tab3:
    st.subheader("Results")
    st.info("Results will be displayed here")
    
    st.warning("⚠️ Human review required: All outputs must be validated by qualified personnel")

# Footer
st.markdown("---")
st.markdown("Part of **gcc-insurance-intelligence-lab** | Synthetic Data Only | Human-in-Loop Required")
'''
        
        file_path = repo_path / "app.py"
        file_path.write_text(content)
        print(f"  ✓ Created app.py")
    
    def _create_readme(self, repo_path, repo_name, description):
        """Generate README.md"""
        title = repo_name.replace("-", " ").title()
        
        content = f'''# {title}

{description}

## 🎯 Purpose

This application is part of the **gcc-insurance-intelligence-lab** and demonstrates {repo_name} capabilities using synthetic data.

## ⚠️ Important Disclaimers

{DISCLAIMER}

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Hugging Face Space

This Space is automatically deployed via CI/CD pipeline.

## 📊 Features

- Synthetic data processing
- Interactive analysis
- Human-in-loop validation
- Governance compliance

## 🏗️ Architecture

```
{repo_name}/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── model_card.md      # Model documentation
├── data/              # Synthetic datasets
├── models/            # Trained models
├── tests/             # Test suite
└── logs/              # Application logs
```

## 🧪 Testing

```bash
python -m pytest tests/test_smoke.py
```

## 📝 Governance

- ✅ Synthetic data only
- ✅ Human-in-loop required
- ✅ No pricing authority
- ✅ No payout authority
- ✅ No underwriting authority
- ✅ No PII/confidential data

## 🔗 Links

- [gcc-insurance-ai-hub](https://huggingface.co/spaces/gcc-ai-lab/gcc-insurance-ai-hub)
- [Lab Repository](https://github.com/gcc-ai-lab/insurance-intelligence-lab)

## 📄 License

For educational and research purposes only.

---

**Created**: {datetime.now().strftime("%Y-%m-%d")}
**Part of**: gcc-insurance-intelligence-lab
**Automation**: Repository Factory v1.0
'''
        
        file_path = repo_path / "README.md"
        file_path.write_text(content)
        print(f"  ✓ Created README.md")
    
    def _create_model_card(self, repo_path, repo_name, description):
        """Generate model_card.md"""
        title = repo_name.replace("-", " ").title()
        
        content = f'''---
title: {title}
emoji: 🏢
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.32.0
app_file: app.py
pinned: false
license: mit
---

# Model Card: {title}

## Model Details

- **Model Name**: {repo_name}
- **Model Type**: Insurance AI Application
- **Organization**: gcc-insurance-intelligence-lab
- **Created**: {datetime.now().strftime("%Y-%m-%d")}
- **Version**: 1.0.0

## Intended Use

### Primary Use Cases

{description}

### Intended Users

- Insurance professionals (educational purposes)
- Researchers
- Data scientists
- Actuaries

### Out-of-Scope Uses

❌ **NOT for production underwriting decisions**
❌ **NOT for pricing or rating**
❌ **NOT for claims payment authorization**
❌ **NOT with real customer data**

## Training Data

- **Data Type**: 100% Synthetic
- **Data Source**: Artificially generated
- **No Real Data**: No personal or confidential information used

## Evaluation

- Human-in-loop validation required
- Smoke tests automated
- Governance checks enforced

## Ethical Considerations

### Governance

{DISCLAIMER}

### Bias and Fairness

- Synthetic data designed to avoid real-world biases
- Regular audits recommended
- Human oversight mandatory

## Limitations

- Educational/research tool only
- Requires validation before any production use
- Synthetic data may not reflect real-world complexity
- Not a substitute for professional judgment

## Additional Information

- **Repository**: [gcc-insurance-intelligence-lab](https://github.com/gcc-ai-lab/insurance-intelligence-lab)
- **Hub**: [gcc-insurance-ai-hub](https://huggingface.co/spaces/gcc-ai-lab/gcc-insurance-ai-hub)
- **Contact**: gcc-ai-lab team

---

**Automated Generation**: Repository Factory v1.0
'''
        
        file_path = repo_path / "model_card.md"
        file_path.write_text(content)
        print(f"  ✓ Created model_card.md")
    
    def _create_requirements(self, repo_path):
        """Generate requirements.txt"""
        content = '''# Core dependencies
streamlit>=1.32.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0

# Visualization
plotly>=5.18.0
matplotlib>=3.7.0
seaborn>=0.12.0

# Utilities
python-dateutil>=2.8.0
pytz>=2023.3

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Code quality
black>=23.0.0
flake8>=6.0.0
isort>=5.12.0
'''
        
        file_path = repo_path / "requirements.txt"
        file_path.write_text(content)
        print(f"  ✓ Created requirements.txt")
    
    def _create_gitignore(self, repo_path):
        """Generate .gitignore"""
        content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
logs/
*.log

# Data
*.csv
*.xlsx
*.parquet

# Models
models/*.pkl
models/*.joblib
models/*.h5

# OS
.DS_Store
Thumbs.db

# Secrets
.env
.env.local
secrets.toml
'''
        
        file_path = repo_path / ".gitignore"
        file_path.write_text(content)
        print(f"  ✓ Created .gitignore")
    
    def _create_smoke_test(self, repo_path, repo_name):
        """Generate test_smoke.py"""
        content = f'''#!/usr/bin/env python3
"""
Smoke tests for {repo_name}
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
        pytest.fail(f"Import failed: {{e}}")

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
        assert term in content, f"Missing governance term: {{term}}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
        
        file_path = repo_path / "tests" / "test_smoke.py"
        file_path.write_text(content)
        print(f"  ✓ Created tests/test_smoke.py")
    
    def _create_dataset_template(self, repo_path, repo_name):
        """Generate synthetic dataset template"""
        content = f'''#!/usr/bin/env python3
"""
Synthetic Dataset Generator for {repo_name}
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_synthetic_data(n_records=1000, version="v1"):
    """
    Generate synthetic insurance data
    
    Args:
        n_records: Number of records to generate
        version: Dataset version (v1, v2, etc.)
    
    Returns:
        pandas.DataFrame with synthetic data
    """
    np.random.seed(42 if version == "v1" else 43)
    
    data = {{
        "record_id": [f"REC-{{i:06d}}" for i in range(n_records)],
        "timestamp": [datetime.now() - timedelta(days=random.randint(0, 365)) for _ in range(n_records)],
        "value": np.random.normal(1000, 200, n_records),
        "category": np.random.choice(["A", "B", "C", "D"], n_records),
        "score": np.random.uniform(0, 100, n_records),
        "flag": np.random.choice([True, False], n_records),
    }}
    
    df = pd.DataFrame(data)
    
    # Add version metadata
    df.attrs["version"] = version
    df.attrs["generated"] = datetime.now().isoformat()
    df.attrs["synthetic"] = True
    
    return df

if __name__ == "__main__":
    # Generate v1
    df_v1 = generate_synthetic_data(1000, "v1")
    df_v1.to_csv("data/dataset_v1.csv", index=False)
    print(f"✓ Generated dataset_v1.csv ({{len(df_v1)}} records)")
    
    # Generate v2
    df_v2 = generate_synthetic_data(1500, "v2")
    df_v2.to_csv("data/dataset_v2.csv", index=False)
    print(f"✓ Generated dataset_v2.csv ({{len(df_v2)}} records)")
    
    print("\n✅ Synthetic datasets created successfully!")
    print("⚠️  Remember: These are 100% synthetic - no real data used")
'''
        
        file_path = repo_path / "data" / "generate_dataset.py"
        file_path.write_text(content)
        print(f"  ✓ Created data/generate_dataset.py")

if __name__ == "__main__":
    factory = RepoFactory()
    
    # Example usage
    if len(sys.argv) > 1:
        use_case_name = sys.argv[1]
        description = sys.argv[2] if len(sys.argv) > 2 else ""
        factory.create_use_case(use_case_name, description)
    else:
        print("Usage: python repo_factory.py <use_case_name> [description]")
        print("Example: python repo_factory.py 'Premium Lapse Monitor' 'Monitor policy lapses'")
