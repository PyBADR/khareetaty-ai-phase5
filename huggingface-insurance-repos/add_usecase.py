#!/usr/bin/env python3
"""
Insurance AI Factory - Single Command Use Case Generator

Implements the /add-usecase command that creates complete repositories
with governance, synthetic data, and CI/CD automation.
"""

import os
import sys
import argparse
from pathlib import Path
import shutil
import json
from datetime import datetime

def create_app_py(usecase_name, title=None, subtitle=None, input_label=None):
    """Create the main Gradio application file"""
    if not title:
        title = usecase_name.replace('-', ' ').title()
    if not subtitle:
        subtitle = f"Rule-based {usecase_name.replace('-', ' ')} system"
    if not input_label:
        input_label = "Input Parameter"
    
    template = f'''import gradio as gr

def process_input(input_param):
    """Rule-based processing function"""
    # Rule-based logic goes here - implement based on use case
    result = f"Processed: {{input_param}} with rule-based logic"
    return result

with gr.Blocks(title="{title}", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # {title}
    
    **{subtitle}**
    
    ## ⚠️ CRITICAL DISCLAIMER
    
    **This application demonstrates fictional insurance logic using synthetic data only.**
    
    - ❌ NOT for real insurance operations
    - ❌ NOT for production decisions
    - ✅ Educational and demonstration purposes ONLY
    - ✅ Synthetic data with no real-world application
    - ✅ Human review MANDATORY for all decisions
    
    **All outputs require human validation by qualified professionals.**
    """)
    
    with gr.Row():
        with gr.Column():
            input_field = gr.Textbox(label="{input_label}", placeholder="Enter input...")
            submit_btn = gr.Button("Process", variant="primary")
        
        with gr.Column():
            output_field = gr.Textbox(label="Result", interactive=False)
    
    submit_btn.click(
        fn=process_input,
        inputs=input_field,
        outputs=output_field
    )

if __name__ == "__main__":
    demo.launch()
'''
    return template

def create_requirements_txt():
    """Create requirements.txt file"""
    return "gradio==4.44.0\n"

def create_readme_md(usecase_name, title=None):
    """Create README.md with governance requirements"""
    if not title:
        title = usecase_name.replace('-', ' ').title()
    
    template = f'''---
title: {title}
emoji: 🤖
colorFrom: blue
colorTo: red
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# {title}

**Rule-based insurance logic demonstration**

## Overview

This application demonstrates fictional insurance logic using synthetic data only. No outputs shall be used for actual underwriting, pricing, reserving, claim approval, or policy issuance.

## Purpose

Educational demonstration of {usecase_name.replace('-', ' ')} concepts for training insurance professionals and prototyping insurance workflows.

## Features

- Rule-based processing engine
- Synthetic data only
- Human-in-the-loop enforcement
- Educational purpose only
- Transparent logic

## Inputs

Input parameters for the {usecase_name.replace('-', ' ')} system.

## Outputs

Educational outputs for demonstration purposes only.

## Data Sources

- **100% Synthetic**: All data and scenarios are fabricated
- **No Real Data**: No connection to actual insurance operations
- **Educational Only**: For demonstration and training purposes

## Technical Details

- **Framework**: Gradio 4.44.0
- **Language**: Python 3.9+
- **Logic**: Rule-based (no ML)
- **Dependencies**: gradio

## Usage

```bash
pip install -r requirements.txt
python3 app.py
```

## ⚠️ CRITICAL DISCLAIMER

**This application demonstrates fictional insurance logic using synthetic data only.**

### NOT Intended For:
- ❌ Real insurance operations
- ❌ Production decisions
- ❌ Actual underwriting or pricing
- ❌ Production operations
- ❌ Automated decisions

### Intended For:
- ✅ Educational training
- ✅ Logic demonstration
- ✅ Workflow prototyping
- ✅ Concept validation

**All outputs are advisory only and require qualified professional review. Human-in-the-loop is mandatory for all decisions.**

## Governance & Safety

- ✅ No automated decisions
- ✅ Transparent logic
- ✅ Explainable outputs
- ✅ Mandatory human review
- ✅ Clear disclaimers

## Limitations

- Educational demonstration only
- Synthetic logic with no real-world validation
- Simplified model
- No integration with actual systems
- Not suitable for production use

## License

MIT License - Educational Use Only

---

**Built for GCC Insurance Intelligence Lab**

This tool is not approved for actual insurance operations. All outputs require human review and validation by qualified professionals.
'''
    return template

def create_model_card_md(usecase_name, title=None):
    """Create model_card.md with governance requirements"""
    if not title:
        title = usecase_name.replace('-', ' ').title()
    
    template = f'''# Model Card: {title}

## Model Details

### Description

Rule-based processing system for {usecase_name.replace('-', ' ')} demonstration. This is not a machine learning model but a rule-based system for educational purposes.

- **Developed by:** GCC Insurance Intelligence Lab
- **Model Type:** Rule-based processing engine
- **Version:** 1.0
- **Framework:** Pure Python logic (no ML)
- **License:** MIT (Educational Use Only)

## Intended Use

### Primary Use Cases

✅ **Educational Training**: Training insurance professionals on {usecase_name.replace('-', ' ')} concepts  
✅ **Logic Demonstration**: Demonstrating {usecase_name.replace('-', ' ')} logic  
✅ **Workflow Prototyping**: Prototyping {usecase_name.replace('-', ' ')} workflows  
✅ **Concept Validation**: Validating {usecase_name.replace('-', ' ')} concepts  

### Out-of-Scope Use

❌ **Real Operations**: Not for actual insurance operations  
❌ **Production Decisions**: Not for production decisions  
❌ **Production Systems**: Not validated for live operations  

## Training Data

**N/A** - This is a rule-based system with no training data. The logic is defined by explicit rules, not learned from data.

### Synthetic Data Context

- 100% fabricated scenarios
- No real insurance data used
- Educational examples only
- No connection to actual operations

## Factors & Metrics

Rule-based system with configurable parameters for educational demonstration.

## Ethical Considerations

### Bias & Fairness

As a rule-based system, bias is limited to the rules defined. All logic is transparent and auditable.

### Mitigation Strategies

✅ **Transparency**: All logic is explicit and auditable  
✅ **Explainability**: Clear reasoning provided for all decisions  
✅ **Human Review**: Mandatory validation by professionals  
✅ **No Automation**: No automated decisions  

## Limitations

### Known Limitations

- Educational demonstration only
- No real-world validation
- Simplified model
- Not suitable for production use

### Technical Constraints

- Requires Python 3.9+
- Requires Gradio framework
- Local execution only

## Recommendations

### For Users

- Use only for educational purposes
- Always implement human review
- Do not use for production decisions
- Validate outputs with qualified professionals

### For Organizations

- Do not deploy for production use
- Implement appropriate governance
- Maintain professional oversight
- Document all decisions appropriately

## Governance

### Mandatory Requirements

- Human-in-the-loop for all decisions
- Clear disclaimers in all interfaces
- Synthetic data only
- Educational use only

### Compliance Notes

This system is designed for educational use only and must not be used for actual insurance operations.

## Technical Specifications

### Architecture

Rule-based processing engine with Gradio interface.

### Compute Requirements

- Python 3.9+
- Minimal memory requirements
- Local execution

### Dependencies

```
gradio==4.44.0
```

## Disclaimer

⚠️ **CRITICAL NOTICE**

{title} demonstrates fictional insurance logic using synthetic data only. No outputs shall be used for actual insurance operations. All data and scenarios are fabricated for educational purposes.

**Human-in-the-loop is mandatory for all decisions.**

Organizations using this tool must:
- Comply with all applicable laws and regulations
- Implement appropriate governance and oversight
- Maintain professional standards
- Document all decisions with qualified professional approval
- Never rely on this system for actual insurance operations

## Contact

For questions or feedback about this educational tool, contact the GCC Insurance Intelligence Lab.

---

**Version**: 1.0  
**Last Updated**: {datetime.now().strftime('%B %Y')}  
**Status**: Educational Demonstration
'''
    return template

def create_test_smoke_py(usecase_name):
    """Create basic smoke test"""
    template = f'''"""
Smoke test for {usecase_name} application
"""
import sys
import os

def test_app_loads():
    """Test that the main app can be imported without errors"""
    try:
        # Import the app module
        import app  # Replace with your app filename
        print("✓ App loads successfully")
        return True
    except ImportError as e:
        print(f"✗ App failed to load: {{e}}")
        return False
    except Exception as e:
        print(f"✗ App error: {{e}}")
        return False

def test_governance_requirements():
    """Test that governance requirements are met"""
    try:
        # Check if required files exist
        required_files = ["README.md", "model_card.md", "requirements.txt"]
        for file in required_files:
            if not os.path.exists(file):
                print(f"✗ Missing required file: {{file}}")
                return False
        print("✓ All required governance files present")
        return True
    except Exception as e:
        print(f"✗ Governance test error: {{e}}")
        return False

if __name__ == "__main__":
    print(f"Running smoke tests for {usecase_name}...")
    
    tests = [
        test_app_loads,
        test_governance_requirements
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    if all(results):
        print("\\n✓ All smoke tests passed!")
        sys.exit(0)
    else:
        print("\\n✗ Some tests failed!")
        sys.exit(1)
'''
    return template

def create_synthetic_dataset(usecase_name):
    """Create a basic synthetic dataset"""
    # This is a placeholder - actual implementation would depend on use case
    return f"""# Synthetic dataset for {usecase_name}
# This is fabricated data for educational purposes only

id,value,category,status
1,100,A,active
2,200,B,inactive
3,150,A,active
4,300,C,active
5,250,B,inactive
"""

def link_to_hub(usecase_name, hub_path="../gcc-insurance-ai-hub"):
    """Add the new use case to the main hub"""
    try:
        hub_readme_path = os.path.join(hub_path, "README.md")
        if os.path.exists(hub_readme_path):
            with open(hub_readme_path, "r") as f:
                content = f.read()
            
            # Check if the use case is already listed
            if usecase_name not in content:
                # Find a good place to insert the link (after the main heading)
                insert_pos = content.find("\n", content.find("#")) + 1
                new_content = (content[:insert_pos] + 
                              f"\n- [{usecase_name.title()}](https://huggingface.co/spaces/gcc-insurance-intelligence-lab/{usecase_name}) - {usecase_name.replace('-', ' ')} system\n" + 
                              content[insert_pos:])
                
                with open(hub_readme_path, "w") as f:
                    f.write(new_content)
                print(f"✓ Added {usecase_name} to hub index")
            else:
                print(f"- {usecase_name} already in hub index")
        else:
            print(f"! Hub README not found at {hub_readme_path}, skipping linking")
    except Exception as e:
        print(f"! Could not link to hub: {e}")

def main():
    parser = argparse.ArgumentParser(description='Add new use case to GCC Insurance Intelligence Lab')
    parser.add_argument('name', help='Name of the new use case (e.g., premium-lapse-monitor)')
    parser.add_argument('--datasets', nargs='*', help='Optional synthetic datasets to create')
    
    args = parser.parse_args()
    
    usecase_name = args.name.lower().replace(' ', '-')
    
    # Validate name format
    if not usecase_name.replace('-', '').replace('_', '').isalnum():
        print("❌ Error: Use case name can only contain letters, numbers, hyphens, and underscores")
        sys.exit(1)
    
    # Create directory
    if os.path.exists(usecase_name):
        print(f"❌ Error: Directory {usecase_name} already exists")
        sys.exit(1)
    
    os.makedirs(usecase_name)
    print(f"✓ Created directory: {usecase_name}")
    
    # Create subdirectories
    os.makedirs(os.path.join(usecase_name, "logs"), exist_ok=True)
    print("✓ Created logs directory")
    
    # Create files
    files_to_create = [
        ("app.py", create_app_py(usecase_name)),
        ("requirements.txt", create_requirements_txt()),
        ("README.md", create_readme_md(usecase_name)),
        ("model_card.md", create_model_card_md(usecase_name)),
        ("test_smoke.py", create_test_smoke_py(usecase_name))
    ]
    
    for filename, content in files_to_create:
        filepath = os.path.join(usecase_name, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✓ Created: {filename}")
    
    # Create synthetic dataset if requested
    if args.datasets:
        for dataset_name in args.datasets:
            dataset_content = create_synthetic_dataset(dataset_name)
            dataset_path = os.path.join(usecase_name, f"{dataset_name}.csv")
            with open(dataset_path, 'w') as f:
                f.write(dataset_content)
            print(f"✓ Created synthetic dataset: {dataset_name}.csv")
    
    # Copy CI/CD template
    ci_template_path = ".github/workflows/lab-ci-template.yml"
    if os.path.exists(ci_template_path):
        dest_ci_path = os.path.join(usecase_name, ".github", "workflows")
        os.makedirs(dest_ci_path, exist_ok=True)
        shutil.copy(ci_template_path, os.path.join(dest_ci_path, "deploy.yml"))
        print("✓ Copied CI/CD template")
    else:
        print("! CI/CD template not found")
    
    # Link to hub
    link_to_hub(usecase_name)
    
    print(f"\n🎉 Success! New use case '{usecase_name}' created with:")
    print("- Gradio application with rule-based logic")
    print("- Complete documentation with governance")
    print("- Synthetic data (if specified)")
    print("- Smoke tests")
    print("- CI/CD automation")
    print("- Hub linking")
    print("\n🚀 To deploy: cd {usecase_name} && python3 app.py")

if __name__ == "__main__":
    main()