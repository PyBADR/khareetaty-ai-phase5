#!/usr/bin/env python3
"""
GCC Insurance Agent Factory Orchestrator
Creates and manages insurance AI agent repositories
"""

import os
import json
from pathlib import Path
from datetime import datetime

class AgentFactory:
    """Factory for creating insurance AI agent repositories"""
    
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.factory_state = {
            "created_at": datetime.now().isoformat(),
            "agents": [],
            "gcc_compliance": True,
            "human_in_loop": True
        }
    
    def add_agent(self, name, description, use_case_type):
        """Create a new agent repository"""
        agent_path = self.base_path / name
        agent_path.mkdir(exist_ok=True)
        
        print(f"\n🏭 Creating agent: {name}")
        
        # Create app.py
        self._create_app_py(agent_path, name, description, use_case_type)
        
        # Create README.md
        self._create_readme(agent_path, name, description, use_case_type)
        
        # Create model_card.md
        self._create_model_card(agent_path, name, description, use_case_type)
        
        # Create requirements.txt
        self._create_requirements(agent_path, use_case_type)
        
        # Create deploy_to_hf.py
        self._create_deploy_script(agent_path, name)
        
        # Create synthetic dataset if needed
        if use_case_type in ["underwriting", "fraud", "claims", "reinsurance"]:
            self._create_synthetic_data(agent_path, use_case_type)
        
        # Update factory state
        self.factory_state["agents"].append({
            "name": name,
            "description": description,
            "type": use_case_type,
            "created_at": datetime.now().isoformat()
        })
        
        print(f"✅ Agent {name} created successfully")
        return agent_path
    
    def _create_app_py(self, path, name, description, use_case_type):
        """Generate Gradio app.py for the agent"""
        app_content = f'''import gradio as gr
import pandas as pd
import json
from datetime import datetime

# GCC Insurance Agent: {name}
# {description}
# Human-in-loop: ALWAYS ENFORCED

def process_request(input_data):
    """
    Process insurance request with human-in-loop validation
    """
    result = {{
        "agent": "{name}",
        "timestamp": datetime.now().isoformat(),
        "input": input_data,
        "status": "pending_human_review",
        "gcc_compliant": True,
        "recommendation": "Awaiting human approval"
    }}
    return json.dumps(result, indent=2)

def load_sample_data():
    """Load synthetic sample data"""
    try:
        df = pd.read_csv("synthetic_data.csv")
        return df.head(10).to_html()
    except:
        return "No sample data available"

# Gradio Interface
with gr.Blocks(title="{name}") as demo:
    gr.Markdown(f"# {name}")
    gr.Markdown(f"## {description}")
    gr.Markdown("### ⚠️ Human-in-Loop: All decisions require human approval")
    
    with gr.Tab("Agent Interface"):
        input_text = gr.Textbox(
            label="Input Data (JSON format)",
            placeholder='{{"policy_id": "12345", "data": "..."}}')
        output_text = gr.Textbox(label="Agent Response", lines=10)
        submit_btn = gr.Button("Process Request")
        submit_btn.click(process_request, inputs=input_text, outputs=output_text)
    
    with gr.Tab("Sample Data"):
        gr.Markdown("### Synthetic Dataset Sample")
        sample_output = gr.HTML()
        load_btn = gr.Button("Load Sample Data")
        load_btn.click(load_sample_data, outputs=sample_output)
    
    with gr.Tab("About"):
        gr.Markdown(f"""
        ### Agent Information
        - **Name**: {name}
        - **Type**: {use_case_type}
        - **GCC Compliant**: Yes
        - **Human-in-Loop**: Enforced
        - **Proprietary Logic**: None (Generic assumptions only)
        
        ### Factory Rules
        ✅ Generic GCC assumptions only  
        ✅ Human approval required  
        ✅ No proprietary insurer logic  
        ✅ Synthetic data for testing  
        """)

if __name__ == "__main__":
    demo.launch()
'''
        (path / "app.py").write_text(app_content)
    
    def _create_readme(self, path, name, description, use_case_type):
        """Generate README.md"""
        readme_content = f'''# {name}

## Description
{description}

## Agent Type
{use_case_type}

## GCC Insurance Agent Factory

This agent is part of the GCC Insurance Agent Factory - a system for manufacturing insurance AI agents on demand.

### Factory Rules Compliance
✅ **Human-in-Loop**: All decisions require human approval  
✅ **GCC Generic Assumptions**: No proprietary insurer logic  
✅ **Synthetic Data**: Uses generated test data  
✅ **Auto-Generated**: Complete repository structure  

## Usage

```bash
python app.py
```

Or deploy to Hugging Face:

```bash
python deploy_to_hf.py
```

## Files

- `app.py` - Gradio interface
- `model_card.md` - Model documentation
- `requirements.txt` - Dependencies
- `synthetic_data.csv` - Sample dataset
- `deploy_to_hf.py` - Deployment script

## License

MIT License - Generic GCC Insurance Use Case

## Disclaimer

This agent uses generic insurance assumptions and requires human validation for all decisions.
'''
        (path / "README.md").write_text(readme_content)
    
    def _create_model_card(self, path, name, description, use_case_type):
        """Generate model_card.md"""
        model_card = f'''---
title: {name}
emoji: 🏢
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
---

# Model Card: {name}

## Model Description

{description}

## Intended Use

**Primary Use Case**: {use_case_type}

**Users**: Insurance professionals, underwriters, claims adjusters, risk analysts

**Out-of-Scope**: This model should NOT be used for:
- Final decision-making without human review
- Proprietary insurer-specific workflows
- Production use without proper validation

## Training Data

This agent uses synthetic data generated for GCC (Generic Commercial Coverage) insurance scenarios.

## Ethical Considerations

- **Human-in-Loop**: MANDATORY - All outputs require human validation
- **Bias Mitigation**: Generic assumptions to avoid insurer-specific bias
- **Transparency**: All logic is explainable and auditable
- **Privacy**: No real customer data used

## Limitations

- Generic assumptions may not fit all insurance contexts
- Requires domain expert validation
- Not a replacement for human judgment
- Synthetic data may not capture all real-world scenarios

## Factory Compliance

✅ GCC Generic Assumptions Only  
✅ Human-in-Loop Enforced  
✅ No Proprietary Logic  
✅ Synthetic Data Only  

## Contact

Generated by GCC Insurance Agent Factory
'''
        (path / "model_card.md").write_text(model_card)
    
    def _create_requirements(self, path, use_case_type):
        """Generate requirements.txt"""
        requirements = '''gradio>=4.0.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
'''
        (path / "requirements.txt").write_text(requirements)
    
    def _create_deploy_script(self, path, name):
        """Generate deploy_to_hf.py"""
        deploy_script = f'''#!/usr/bin/env python3
"""
Deploy {name} to Hugging Face
"""

import os
import subprocess
import sys

def deploy():
    print("\n🚀 Deploying {name} to Hugging Face...")
    
    # Check if huggingface-cli is installed
    try:
        subprocess.run(["huggingface-cli", "--version"], check=True, capture_output=True)
    except:
        print("❌ Error: huggingface-cli not found. Install with: pip install huggingface_hub")
        sys.exit(1)
    
    # Check authentication
    print("\n🔑 Checking Hugging Face authentication...")
    result = subprocess.run(["huggingface-cli", "whoami"], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Not logged in to Hugging Face")
        print("Please run: huggingface-cli login")
        sys.exit(1)
    
    print(f"✅ Authenticated as: {{result.stdout.strip()}}")
    
    # Create space
    space_name = "{name}"
    org_name = "gcc-insurance-intelligence-lab"  # Update with your org
    
    print(f"\n🏭 Creating Hugging Face Space: {{org_name}}/{{space_name}}")
    
    # Note: Actual deployment would use huggingface_hub API
    print("⚠️  Manual deployment required:")
    print(f"   1. Create space at: https://huggingface.co/new-space")
    print(f"   2. Name: {{space_name}}")
    print(f"   3. Upload files from this directory")
    print(f"   4. Or use: huggingface-cli upload {{org_name}}/{{space_name}} . --repo-type=space")
    
    print("\n✅ Deployment instructions provided")

if __name__ == "__main__":
    deploy()
'''
        (path / "deploy_to_hf.py").write_text(deploy_script)
        os.chmod(path / "deploy_to_hf.py", 0o755)
    
    def _create_synthetic_data(self, path, use_case_type):
        """Generate synthetic dataset"""
        import pandas as pd
        import numpy as np
        
        np.random.seed(42)
        
        if use_case_type == "underwriting":
            data = {
                "policy_id": [f"POL{i:06d}" for i in range(1, 101)],
                "applicant_age": np.random.randint(25, 70, 100),
                "coverage_amount": np.random.randint(100000, 1000000, 100),
                "risk_score": np.random.uniform(0.1, 0.9, 100),
                "premium_estimate": np.random.randint(500, 5000, 100)
            }
        elif use_case_type == "fraud":
            data = {
                "claim_id": [f"CLM{i:06d}" for i in range(1, 101)],
                "claim_amount": np.random.randint(1000, 100000, 100),
                "fraud_score": np.random.uniform(0.0, 1.0, 100),
                "red_flags": np.random.randint(0, 5, 100),
                "investigation_priority": np.random.choice(["low", "medium", "high"], 100)
            }
        elif use_case_type == "claims":
            data = {
                "claim_id": [f"CLM{i:06d}" for i in range(1, 101)],
                "loss_type": np.random.choice(["property", "liability", "auto"], 100),
                "claim_amount": np.random.randint(5000, 50000, 100),
                "processing_time_days": np.random.randint(1, 30, 100),
                "status": np.random.choice(["pending", "approved", "denied"], 100)
            }
        elif use_case_type == "reinsurance":
            data = {
                "treaty_id": [f"TRT{i:06d}" for i in range(1, 101)],
                "exposure_amount": np.random.randint(1000000, 10000000, 100),
                "retention_rate": np.random.uniform(0.1, 0.5, 100),
                "premium_rate": np.random.uniform(0.01, 0.1, 100),
                "risk_category": np.random.choice(["cat", "casualty", "specialty"], 100)
            }
        else:
            data = {
                "id": range(1, 101),
                "value": np.random.uniform(0, 100, 100)
            }
        
        df = pd.DataFrame(data)
        df.to_csv(path / "synthetic_data.csv", index=False)
    
    def status(self):
        """Print factory status"""
        print("\n" + "="*60)
        print("GCC Insurance Agent Factory - Status")
        print("="*60)
        print(f"Created: {self.factory_state['created_at']}")
        print(f"GCC Compliance: {self.factory_state['gcc_compliance']}")
        print(f"Human-in-Loop: {self.factory_state['human_in_loop']}")
        print(f"\nAgents Created: {len(self.factory_state['agents'])}")
        for agent in self.factory_state['agents']:
            print(f"  ✅ {agent['name']} ({agent['type']})")
        print("="*60)

if __name__ == "__main__":
    print("GCC Insurance Agent Factory Orchestrator")
    print("Use this module to create insurance AI agents programmatically")
