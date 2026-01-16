#!/usr/bin/env python3
"""
Insurance Agent Factory - Manufacture Insurance AI Agents On Demand

Implements the factory system to create insurance AI agents with proper governance
and GCC generic assumptions.
"""

import os
import sys
import argparse
from pathlib import Path
import json
from datetime import datetime

class InsuranceAgentFactory:
    """
    Factory system to manufacture insurance AI agents on demand
    """
    
    def __init__(self):
        self.agents_dir = Path.cwd()
        self.factory_state_file = "factory_state.json"
        
    def create_agent(self, agent_name):
        """Create a new insurance agent repository"""
        print(f"🏭 Creating agent: {agent_name}")
        
        # Validate agent name
        agent_name_clean = agent_name.lower().replace(' ', '-').replace('_', '-')
        
        # Create directory
        agent_dir = self.agents_dir / agent_name_clean
        if agent_dir.exists():
            print(f"❌ Agent {agent_name_clean} already exists")
            return False
        
        agent_dir.mkdir(exist_ok=True)
        print(f"✓ Created directory: {agent_dir}")
        
        # Create subdirectories
        (agent_dir / "data").mkdir(exist_ok=True)
        (agent_dir / "models").mkdir(exist_ok=True)
        (agent_dir / "logs").mkdir(exist_ok=True)
        
        # Create app.py
        app_content = self._create_app_py(agent_name_clean)
        with open(agent_dir / "app.py", 'w') as f:
            f.write(app_content)
        print(f"✓ Created app.py")
        
        # Create requirements.txt
        requirements_content = self._create_requirements_txt()
        with open(agent_dir / "requirements.txt", 'w') as f:
            f.write(requirements_content)
        print(f"✓ Created requirements.txt")
        
        # Create README.md
        readme_content = self._create_readme_md(agent_name_clean)
        with open(agent_dir / "README.md", 'w') as f:
            f.write(readme_content)
        print(f"✓ Created README.md")
        
        # Create model_card.md
        model_card_content = self._create_model_card_md(agent_name_clean)
        with open(agent_dir / "model_card.md", 'w') as f:
            f.write(model_card_content)
        print(f"✓ Created model_card.md")
        
        # Create synthetic dataset if needed
        if self._needs_dataset(agent_name_clean):
            dataset_content = self._create_synthetic_dataset(agent_name_clean)
            with open(agent_dir / "data" / f"{agent_name_clean}_synthetic.csv", 'w') as f:
                f.write(dataset_content)
            print(f"✓ Created synthetic dataset")
        
        # Create deployment script
        deploy_script = self._create_deploy_script(agent_name_clean)
        with open(agent_dir / "deploy_to_hf.py", 'w') as f:
            f.write(deploy_script)
        print(f"✓ Created deployment script")
        
        # Create test script
        test_script = self._create_test_script(agent_name_clean)
        with open(agent_dir / "test_agent.py", 'w') as f:
            f.write(test_script)
        print(f"✓ Created test script")
        
        print(f"🎉 Agent {agent_name_clean} created successfully!")
        return True
    
    def _create_app_py(self, agent_name):
        """Create the main Gradio application"""
        title = agent_name.replace('-', ' ').title()
        
        # Different templates based on agent type
        if 'underwriting' in agent_name:
            template = '''import gradio as gr
import json
import random

def calculate_underwriting_score(industry_segment, applicant_risk_profile, prior_claim_count):
    """Calculate underwriting risk score based on inputs"""
    # Industry risk factors
    industry_factors = {
        'Manufacturing': 1.2,
        'Retail': 1.0,
        'Healthcare': 1.3,
        'Technology': 0.8,
        'Construction': 1.5
    }
    industry_factor = industry_factors.get(industry_segment, 1.0)
    
    # History factor: prior_claims * 0.15
    history_factor = prior_claim_count * 0.15
    
    # Profile bias
    profile_bias_map = {
        'Low': 0.0,
        'Medium': 1.0,
        'High': 2.0
    }
    profile_bias = profile_bias_map.get(applicant_risk_profile, 1.0)
    
    # Calculate composite score
    composite_score = (industry_factor + history_factor + profile_bias) / 3
    
    # Map to risk band
    if composite_score <= 1.0:
        risk_band = "Low Risk"
        color = "🟢"
        recommendation = "Approve with standard terms"
    elif composite_score <= 1.7:
        risk_band = "Medium Risk"
        color = "🟡"
        recommendation = "Approve with higher premium"
    else:
        risk_band = "High Risk"
        color = "🔴"
        recommendation = "Refer for manual review"
    
    # Factor breakdown
    factor_breakdown = {
        "Industry Factor": round(industry_factor, 2),
        "History Factor": round(history_factor, 2),
        "Profile Bias": round(profile_bias, 2),
        "Composite Score": round(composite_score, 2)
    }
    
    return risk_band, color, recommendation, json.dumps(factor_breakdown, indent=2)

agent_title = "Underwriting Score Agent"
with gr.Blocks(theme=gr.themes.Soft(), title=agent_title) as demo:
    gr.Markdown(f"""
    # {{agent_title}}
    
    **GCC Generic Underwriting Risk Assessment Tool**
    
    ## ⚠️ CRITICAL DISCLAIMER
    
    **This application demonstrates fictional insurance logic using synthetic data only.**
    
    - ❌ NOT for real underwriting decisions
    - ❌ NOT for production use
    - ✅ Educational and demonstration purposes ONLY
    - ✅ Synthetic data with no real-world application
    - ✅ Human review MANDATORY for all decisions
    
    **All outputs require human validation by qualified professionals.**
    """)
    
    with gr.Row():
        with gr.Column():
            industry_segment = gr.Dropdown(
                choices=['Manufacturing', 'Retail', 'Healthcare', 'Technology', 'Construction'],
                value='Technology',
                label="Industry Segment"
            )
            applicant_risk_profile = gr.Radio(
                choices=['Low', 'Medium', 'High'],
                value='Medium',
                label="Applicant Risk Profile"
            )
            prior_claim_count = gr.Number(value=0, label="Prior Claim Count")
            
            submit_btn = gr.Button("Calculate Risk Score", variant="primary")
        
        with gr.Column():
            risk_band_output = gr.Textbox(label="Risk Band", interactive=False)
            color_output = gr.Textbox(label="Indicator", interactive=False)
            recommendation_output = gr.Textbox(label="Recommendation", interactive=False)
            factor_breakdown = gr.Code(label="Factor Breakdown", language="json")
    
    submit_btn.click(
        fn=calculate_underwriting_score,
        inputs=[industry_segment, applicant_risk_profile, prior_claim_count],
        outputs=[risk_band_output, color_output, recommendation_output, factor_breakdown]
    )

if __name__ == "__main__":
    demo.launch()
'''
        elif 'fnol' in agent_name:
            template = '''import gradio as gr
import random

def screen_fnol_claim(claim_source, loss_severity, incident_category):
    """Screen FNOL claim and recommend routing"""
    # Routing logic
    if loss_severity <= 2 and claim_source in ['App', 'Call Center']:
        route = "Fast Track"
        route_color = "🟢"
        priority = "Low"
        estimated_resolution = "1-3 days"
        document_checklist = ["Claim form", "Initial photos"]
    elif loss_severity > 2 and incident_category in ['Auto Collision', 'Property']:
        route = "Standard Review"
        route_color = "🟡"
        priority = "Medium"
        estimated_resolution = "3-7 days"
        document_checklist = ["Claim form", "Photos", "Police report", "Estimates"]
    elif loss_severity >= 4:
        route = "Escalation"
        route_color = "🔴"
        priority = "High"
        estimated_resolution = "7+ days"
        document_checklist = ["Claim form", "Photos", "Police report", "Expert assessment", "Legal review"]
    else:
        route = "Standard Review"
        route_color = "🟡"
        priority = "Medium"
        estimated_resolution = "3-7 days"
        document_checklist = ["Claim form", "Photos", "Witness statements"]
    
    # Uncertainty score
    uncertainty_score = round(random.uniform(0.1, 0.9), 2)
    
    return route, route_color, priority, estimated_resolution, "\\n".join(document_checklist), uncertainty_score

with gr.Blocks(theme=gr.themes.Soft(), title="FNOL Fast Triage Agent") as demo:
    gr.Markdown("""
    # FNOL Fast Triage Agent
    
    **GCC Generic First Notice of Loss Screening Tool**
    
    ## ⚠️ CRITICAL DISCLAIMER
    
    **This application demonstrates fictional insurance logic using synthetic data only.**
    
    - ❌ NOT for real FNOL processing
    - ❌ NOT for production use
    - ✅ Educational and demonstration purposes ONLY
    - ✅ Synthetic data with no real-world application
    - ✅ Human review MANDATORY for all decisions
    
    **All outputs require human validation by qualified professionals.**
    """)
    
    with gr.Row():
        with gr.Column():
            claim_source = gr.Dropdown(
                choices=['App', 'Call Center', 'Agent', 'Direct'],
                value='App',
                label="Claim Source"
            )
            loss_severity = gr.Slider(minimum=1, maximum=5, value=2, step=1, label="Loss Severity (1-5)")
            incident_category = gr.Dropdown(
                choices=['Auto Collision', 'Property', 'Liability', 'Workers Comp', 'General'],
                value='Auto Collision',
                label="Incident Category"
            )
            
            submit_btn = gr.Button("Screen Claim", variant="primary")
        
        with gr.Column():
            route_output = gr.Textbox(label="Routing Recommendation", interactive=False)
            route_color_output = gr.Textbox(label="Priority Indicator", interactive=False)
            priority_output = gr.Textbox(label="Priority Level", interactive=False)
            resolution_output = gr.Textbox(label="Estimated Resolution Time", interactive=False)
            checklist_output = gr.Textbox(label="Required Documents", interactive=False)
            uncertainty_output = gr.Number(label="Uncertainty Score", interactive=False)
    
    submit_btn.click(
        fn=screen_fnol_claim,
        inputs=[claim_source, loss_severity, incident_category],
        outputs=[route_output, route_color_output, priority_output, resolution_output, checklist_output, uncertainty_output]
    )

if __name__ == "__main__":
    demo.launch()
'''
        elif 'claims' in agent_name:
            template = '''import gradio as gr
import random

def simulate_claims_journey(severity, doc_completeness):
    """Simulate claims journey timeline and identify bottlenecks"""
    # Base days per stage by severity
    base_days = {
        'Low': {'FNOL': 1, 'Assignment': 1, 'Investigation': 2, 'Decision': 2, 'Payment': 2},
        'Medium': {'FNOL': 2, 'Assignment': 2, 'Investigation': 5, 'Decision': 3, 'Payment': 3},
        'High': {'FNOL': 3, 'Assignment': 3, 'Investigation': 10, 'Decision': 5, 'Payment': 5}
    }
    
    # Adjust for document completeness (0.5 to 1.5 multiplier)
    doc_multiplier = 1.5 - (doc_completeness * 0.5)  # Higher completeness = lower time
    
    # Calculate timeline
    base_timeline = base_days.get(severity, base_days['Medium'])
    adjusted_timeline = {stage: max(1, int(days * doc_multiplier)) for stage, days in base_timeline.items()}
    
    # Total duration
    total_duration = sum(adjusted_timeline.values())
    
    # Identify bottlenecks (>3 days in stage)
    bottlenecks = [stage for stage, days in adjusted_timeline.items() if days > 3]
    
    # Touchpoint count (investigation and decision stages typically need more)
    touchpoint_count = adjusted_timeline['Investigation'] + adjusted_timeline['Decision']
    
    # Risk level based on severity and bottlenecks
    risk_level = "High" if severity == "High" or len(bottlenecks) > 1 else "Medium" if severity == "Medium" or bottlenecks else "Low"
    
    return (
        adjusted_timeline['FNOL'], adjusted_timeline['Assignment'], 
        adjusted_timeline['Investigation'], adjusted_timeline['Decision'], 
        adjusted_timeline['Payment'], total_duration, 
        "\\n".join(bottlenecks) if bottlenecks else "None",
        touchpoint_count, risk_level
    )

with gr.Blocks(theme=gr.themes.Soft(), title="Claims Journey Simulator") as demo:
    gr.Markdown("""
    # Claims Journey Simulator
    
    **GCC Generic Claims Lifecycle Simulation Tool**
    
    ## ⚠️ CRITICAL DISCLAIMER
    
    **This application demonstrates fictional insurance logic using synthetic data only.**
    
    - ❌ NOT for real claims processing
    - ❌ NOT for production use
    - ✅ Educational and demonstration purposes ONLY
    - ✅ Synthetic data with no real-world application
    - ✅ Human review MANDATORY for all decisions
    
    **All outputs require human validation by qualified professionals.**
    """)
    
    with gr.Row():
        with gr.Column():
            severity = gr.Radio(
                choices=['Low', 'Medium', 'High'],
                value='Medium',
                label="Claim Severity"
            )
            doc_completeness = gr.Slider(minimum=0.0, maximum=1.0, value=0.7, label="Document Completeness (0-1)")
            
            submit_btn = gr.Button("Simulate Journey", variant="primary")
        
        with gr.Column():
            fnol_output = gr.Number(label="FNOL Duration (days)", interactive=False)
            assignment_output = gr.Number(label="Assignment Duration (days)", interactive=False)
            investigation_output = gr.Number(label="Investigation Duration (days)", interactive=False)
            decision_output = gr.Number(label="Decision Duration (days)", interactive=False)
            payment_output = gr.Number(label="Payment Duration (days)", interactive=False)
            total_output = gr.Number(label="Total Duration (days)", interactive=False)
            bottlenecks_output = gr.Textbox(label="Bottlenecks", interactive=False)
            touchpoints_output = gr.Number(label="Adjuster Touchpoints", interactive=False)
            risk_output = gr.Textbox(label="Risk Level", interactive=False)
    
    submit_btn.click(
        fn=simulate_claims_journey,
        inputs=[severity, doc_completeness],
        outputs=[
            fnol_output, assignment_output, investigation_output, 
            decision_output, payment_output, total_output, 
            bottlenecks_output, touchpoints_output, risk_output
        ]
    )

if __name__ == "__main__":
    demo.launch()
'''
        elif 'reinsurance' in agent_name:
            template = '''import gradio as gr
import random

def mock_reinsurance_pricing(risk_group, frequency_tier, loss_severity):
    """Mock reinsurance pricing with indicative banding"""
    # Risk group multipliers
    risk_multipliers = {
        'Agricultural': 1.2,
        'Construction': 1.4,
        'Energy': 1.3,
        'Healthcare': 1.1,
        'Manufacturing': 1.3,
        'Technology': 0.9,
        'Transportation': 1.2
    }
    
    # Frequency tier multipliers
    freq_multipliers = {
        'Very Low': 0.8,
        'Low': 0.9,
        'Medium': 1.0,
        'High': 1.2,
        'Very High': 1.5
    }
    
    # Calculate composite risk score
    risk_mult = risk_multipliers.get(risk_group, 1.0)
    freq_mult = freq_multipliers.get(frequency_tier, 1.0)
    
    composite_score = (risk_mult * freq_mult * loss_severity) / 3
    
    # Assign indicative category
    if composite_score <= 1.0:
        category = "A"
        description = "Favorable risk profile, competitive pricing"
        capital_pressure = "Low"
    elif composite_score <= 1.5:
        category = "B"
        description = "Acceptable risk with standard terms"
        capital_pressure = "Moderate"
    else:
        category = "C"
        description = "Higher risk requiring careful monitoring"
        capital_pressure = "High"
    
    # Additional notes
    notes = f"Risk Group: {risk_group}, Frequency: {frequency_tier}, Severity: {loss_severity}"
    
    return category, description, capital_pressure, round(composite_score, 2), notes

with gr.Blocks(theme=gr.themes.Soft(), title="Reinsurance Pricing Mock") as demo:
    gr.Markdown("""
    # Reinsurance Pricing Mock
    
    **GCC Generic Reinsurance Appetite Assessment Tool**
    
    ## ⚠️ CRITICAL DISCLAIMER
    
    **This application demonstrates fictional insurance logic using synthetic data only.**
    
    - ❌ NOT for real reinsurance pricing
    - ❌ NOT for production use
    - ✅ Educational and demonstration purposes ONLY
    - ✅ Synthetic data with no real-world application
    - ✅ Human review MANDATORY for all decisions
    
    **All outputs require human validation by qualified professionals.**
    """)
    
    with gr.Row():
        with gr.Column():
            risk_group = gr.Dropdown(
                choices=['Agricultural', 'Construction', 'Energy', 'Healthcare', 'Manufacturing', 'Technology', 'Transportation'],
                value='Technology',
                label="Risk Group"
            )
            frequency_tier = gr.Dropdown(
                choices=['Very Low', 'Low', 'Medium', 'High', 'Very High'],
                value='Medium',
                label="Frequency Tier"
            )
            loss_severity = gr.Slider(minimum=1, maximum=5, value=2.5, step=0.1, label="Loss Severity (1-5)")
            
            submit_btn = gr.Button("Assess Appetite", variant="primary")
        
        with gr.Column():
            category_output = gr.Textbox(label="Indicative Category", interactive=False)
            description_output = gr.Textbox(label="Category Description", interactive=False)
            pressure_output = gr.Textbox(label="Capital Pressure", interactive=False)
            score_output = gr.Number(label="Composite Risk Score", interactive=False)
            notes_output = gr.Textbox(label="Additional Notes", interactive=False)
    
    submit_btn.click(
        fn=mock_reinsurance_pricing,
        inputs=[risk_group, frequency_tier, loss_severity],
        outputs=[category_output, description_output, pressure_output, score_output, notes_output]
    )

if __name__ == "__main__":
    demo.launch()
'''
        elif 'fraud' in agent_name:
            template = '''import gradio as gr
import json
import datetime

class FraudAuditLogger:
    def __init__(self, log_file="fraud_audit_log.jsonl"):
        self.log_file = log_file
    
    def log_fraud_assessment(self, case_id, assessment_result, confidence, analyst_notes):
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "case_id": case_id,
            "assessment_result": assessment_result,
            "confidence": confidence,
            "analyst_notes": analyst_notes,
            "entry_type": "fraud_assessment"
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\\n')
        
        return f"Entry logged: {case_id}"

logger = FraudAuditLogger()

def audit_fraud_case(case_id, signal_strength, evidence_quality, behavioral_indicators, transaction_patterns):
    """Audit fraud case and create immutable log entry"""
    # Calculate overall risk
    signal_weight = signal_strength * 0.3
    evidence_weight = evidence_quality * 0.3
    behavior_weight = behavioral_indicators * 0.2
    pattern_weight = transaction_patterns * 0.2
    
    overall_risk = signal_weight + evidence_weight + behavior_weight + pattern_weight
    
    # Determine risk level
    if overall_risk >= 0.7:
        risk_level = "High"
        recommendation = "Escalate to senior investigator"
        color = "🔴"
    elif overall_risk >= 0.4:
        risk_level = "Medium"
        recommendation = "Manual review required"
        color = "🟡"
    else:
        risk_level = "Low"
        recommendation = "Auto-approve with monitoring"
        color = "🟢"
    
    # Confidence score
    confidence = round(overall_risk, 2)
    
    # Generate case summary
    summary = f"""
    Case ID: {case_id}
    Risk Level: {risk_level}
    Overall Risk Score: {round(overall_risk, 2)}
    Signal Strength: {signal_strength}
    Evidence Quality: {evidence_quality}
    Behavioral Indicators: {behavioral_indicators}
    Transaction Patterns: {transaction_patterns}
    """
    
    return risk_level, color, recommendation, confidence, summary

with gr.Blocks(theme=gr.themes.Soft(), title="Automated Fraud Audit Log") as demo:
    gr.Markdown("""
    # Automated Fraud Audit Log
    
    **GCC Generic Fraud Detection Audit Trail System**
    
    ## ⚠️ CRITICAL DISCLAIMER
    
    **This application demonstrates fictional insurance logic using synthetic data only.**
    
    - ❌ NOT for real fraud detection
    - ❌ NOT for production use
    - ✅ Educational and demonstration purposes ONLY
    - ✅ Synthetic data with no real-world application
    - ✅ Human review MANDATORY for all decisions
    
    **All outputs require human validation by qualified professionals.**
    """)
    
    with gr.Row():
        with gr.Column():
            case_id = gr.Textbox(label="Case ID", value="FRAUD-2026-001")
            signal_strength = gr.Slider(minimum=0.0, maximum=1.0, value=0.5, label="Signal Strength (0-1)")
            evidence_quality = gr.Slider(minimum=0.0, maximum=1.0, value=0.6, label="Evidence Quality (0-1)")
            behavioral_indicators = gr.Slider(minimum=0.0, maximum=1.0, value=0.4, label="Behavioral Indicators (0-1)")
            transaction_patterns = gr.Slider(minimum=0.0, maximum=1.0, value=0.7, label="Transaction Patterns (0-1)")
            
            submit_btn = gr.Button("Audit Case", variant="primary")
        
        with gr.Column():
            risk_level_output = gr.Textbox(label="Risk Level", interactive=False)
            color_output = gr.Textbox(label="Indicator", interactive=False)
            recommendation_output = gr.Textbox(label="Recommendation", interactive=False)
            confidence_output = gr.Number(label="Confidence Score", interactive=False)
            summary_output = gr.Textbox(label="Case Summary", interactive=False)
    
    submit_btn.click(
        fn=audit_fraud_case,
        inputs=[case_id, signal_strength, evidence_quality, behavioral_indicators, transaction_patterns],
        outputs=[risk_level_output, color_output, recommendation_output, confidence_output, summary_output]
    )

if __name__ == "__main__":
    demo.launch()
'''
        else:
            # Generic template
            agent_title = agent_name.replace('-', ' ').title()
            template = f'''import gradio as gr

def process_input(input_param):
    """Generic processing function for {agent_name}"""
    result = f"Processed: {{input_param}} with {agent_name} logic"
    return result

with gr.Blocks(theme=gr.themes.Soft(), title="{agent_title}") as demo:
    gr.Markdown(f"""
    # {agent_title}
    
    **GCC Generic Insurance Agent**
    
    ## ⚠️ CRITICAL DISCLAIMER
    
    **This application demonstrates fictional insurance logic using synthetic data only.**
    
    - ❌ NOT for real insurance operations
    - ❌ NOT for production use
    - ✅ Educational and demonstration purposes ONLY
    - ✅ Synthetic data with no real-world application
    - ✅ Human review MANDATORY for all decisions
    
    **All outputs require human validation by qualified professionals.**
    """)
    
    with gr.Row():
        with gr.Column():
            input_field = gr.Textbox(label="Input", placeholder="Enter input...")
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
    
    def _create_requirements_txt(self):
        """Create requirements.txt file"""
        return "gradio==4.44.0\n"
    
    def _create_readme_md(self, agent_name):
        """Create README.md with governance requirements"""
        title = agent_name.replace('-', ' ').title()
        
        return f'''---
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

**GCC Generic Insurance Agent**

## Overview

This application demonstrates fictional insurance logic using synthetic data only. No outputs shall be used for actual underwriting, pricing, reserving, claim approval, or policy issuance.

## Purpose

Educational demonstration of {agent_name.replace('-', ' ')} concepts for training insurance professionals and prototyping insurance workflows.

## Features

- Rule-based processing engine
- Synthetic data only
- Human-in-the-loop enforcement
- Educational purpose only
- Transparent logic

## Inputs

Input parameters for the {agent_name.replace('-', ' ')} system.

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
    
    def _create_model_card_md(self, agent_name):
        """Create model_card.md with governance requirements"""
        title = agent_name.replace('-', ' ').title()
        
        return f'''# Model Card: {title}

## Model Details

### Description

Rule-based processing system for {agent_name.replace('-', ' ')} demonstration. This is not a machine learning model but a rule-based system for educational purposes.

- **Developed by:** GCC Insurance Intelligence Lab
- **Model Type:** Rule-based processing engine
- **Version:** 1.0
- **Framework:** Pure Python logic (no ML)
- **License:** MIT (Educational Use Only)

## Intended Use

### Primary Use Cases

✅ **Educational Training**: Training insurance professionals on {agent_name.replace('-', ' ')} concepts  
✅ **Logic Demonstration**: Demonstrating {agent_name.replace('-', ' ')} logic  
✅ **Workflow Prototyping**: Prototyping {agent_name.replace('-', ' ')} workflows  
✅ **Concept Validation**: Validating {agent_name.replace('-', ' ')} concepts  

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
    
    def _needs_dataset(self, agent_name):
        """Determine if agent needs a synthetic dataset"""
        return any(keyword in agent_name for keyword in ['underwriting', 'claims', 'fraud', 'pricing'])
    
    def _create_synthetic_dataset(self, agent_name):
        """Create a basic synthetic dataset"""
        if 'underwriting' in agent_name:
            return """id,industry,prior_claims,risk_score,approved
1,Technology,0,0.3,True
2,Construction,3,0.8,False
3,Retail,1,0.5,True
4,Healthcare,0,0.2,True
5,Manufacturing,2,0.7,False
"""
        elif 'fnol' in agent_name:
            return """claim_id,severity,source,category,resolution_time,days
FNOL-001,2,App,Auto Collision,2,2
FNOL-002,4,Agent,Property,10,10
FNOL-003,1,Call Center,General,1,1
FNOL-004,3,Direct,Liability,5,5
FNOL-005,2,App,Workers Comp,3,3
"""
        elif 'claims' in agent_name:
            return """claim_id,severity,doc_completeness,total_days,bottlenecks
CLAIM-001,Low,0.9,5,None
CLAIM-002,High,0.3,25,Investigation
CLAIM-003,Medium,0.7,12,None
CLAIM-004,Low,0.8,4,None
CLAIM-005,High,0.6,18,Decision
"""
        elif 'fraud' in agent_name:
            return """case_id,signal_strength,evidence_quality,risk_level
FRAUD-001,0.8,0.7,High
FRAUD-002,0.2,0.9,Low
FRAUD-003,0.6,0.4,Medium
FRAUD-004,0.9,0.8,High
FRAUD-005,0.3,0.5,Low
"""
        else:
            return """id,param1,param2,result
1,0.5,0.3,processed
2,0.8,0.7,processed
3,0.2,0.1,processed
4,0.9,0.4,processed
5,0.6,0.8,processed
"""
    
    def _create_deploy_script(self, agent_name):
        """Create deployment script for Hugging Face"""
        return f'''"""
Deploy {agent_name} to Hugging Face
This script deploys the {agent_name} to Hugging Face Spaces
"""

import os
from huggingface_hub import HfApi, create_repo

def deploy_to_hf():
    """Deploy to Hugging Face"""
    api = HfApi()
    
    # Repository details
    repo_id = f"gcc-insurance-intelligence-lab/{agent_name}"
    repo_type = "space"
    space_sdk = "gradio"
    
    print(f"Creating/updating repository: {{repo_id}}")
    
    # Create the repository
    create_repo(
        repo_id=repo_id,
        repo_type=repo_type,
        space_sdk=space_sdk,
        exist_ok=True,
        private=False
    )
    
    # Upload all files
    files_to_upload = [
        "app.py",
        "requirements.txt", 
        "README.md",
        "model_card.md"
    ]
    
    for filename in files_to_upload:
        if os.path.exists(filename):
            print(f"Uploading {{filename}}...")
            api.upload_file(
                path_or_fileobj=f"./{{filename}}",
                path_in_repo=filename,
                repo_id=repo_id,
                repo_type=repo_type
            )
            print(f"✓ {{filename}} uploaded")
        else:
            print(f"⚠️ {{filename}} not found")
    
    print(f"\\n✅ Repository {{repo_id}} has been updated on Hugging Face Hub!")
    print(f"URL: https://huggingface.co/spaces/{{repo_id}}")

if __name__ == "__main__":
    deploy_to_hf()
'''
    
    def _create_test_script(self, agent_name):
        """Create basic test script"""
        return f'''"""
Basic test script for {agent_name}
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
        print(f"✗ App module import failed: {{e}}")
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
        print(f"✗ App structure test failed: {{e}}")
        return False

def run_tests():
    """Run all tests"""
    print(f"Running tests for {agent_name}...")
    
    tests = [
        test_imports,
        test_app_structure
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    if all(results):
        print("\\n✅ All tests passed!")
        return True
    else:
        print("\\n✗ Some tests failed!")
        return False

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
'''

    def generate_synthetic_data(self, domain):
        """Generate synthetic data for a specific domain"""
        print(f"🎲 Generating synthetic data for domain: {domain}")
        
        # This would contain more sophisticated data generation logic
        # For now, we'll just create a placeholder
        data_dir = self.agents_dir / "synthetic_data"
        data_dir.mkdir(exist_ok=True)
        
        filename = f"{domain}_synthetic_data.csv"
        filepath = data_dir / filename
        
        # Placeholder data - in a real implementation this would be more sophisticated
        with open(filepath, 'w') as f:
            f.write(f"# Synthetic data for {domain}\\n")
            f.write("id,data,value,status\\n")
            f.write("1,example1,100,active\\n")
            f.write("2,example2,200,inactive\\n")
            f.write("3,example3,150,active\\n")
        
        print(f"✓ Created synthetic data file: {filename}")
        return str(filepath)
    
    def link_model(self, agent_name, model_repo):
        """Link a model repo to an agent"""
        print(f"🔗 Linking model {model_repo} to agent {agent_name}")
        
        agent_dir = self.agents_dir / agent_name
        if not agent_dir.exists():
            print(f"❌ Agent {agent_name} does not exist")
            return False
        
        # In a real implementation, this would create a connection between repos
        # For now, we'll just record the linkage in a file
        link_file = agent_dir / "linked_models.json"
        
        if link_file.exists():
            import json
            with open(link_file, 'r') as f:
                links = json.load(f)
        else:
            links = []
        
        if model_repo not in links:
            links.append(model_repo)
            with open(link_file, 'w') as f:
                json.dump(links, f, indent=2)
            print(f"✓ Linked {model_repo} to {agent_name}")
        else:
            print(f"- {model_repo} already linked to {agent_name}")
        
        return True
    
    def publish_agent(self, agent_name):
        """Publish agent to Hugging Face"""
        print(f"🚀 Publishing agent: {agent_name}")
        
        agent_dir = self.agents_dir / agent_name
        if not agent_dir.exists():
            print(f"❌ Agent {agent_name} does not exist")
            return False
        
        deploy_script = agent_dir / "deploy_to_hf.py"
        if not deploy_script.exists():
            print(f"❌ Deployment script not found for {agent_name}")
            return False
        
        # Execute the deployment script
        import subprocess
        result = subprocess.run([
            "python", str(deploy_script)
        ], cwd=agent_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Agent {agent_name} published successfully!")
            print(result.stdout)
            return True
        else:
            print(f"❌ Agent {agent_name} publication failed:")
            print(result.stderr)
            return False
    
    def test_agent(self, agent_name):
        """Test agent functionality"""
        print(f"🧪 Testing agent: {agent_name}")
        
        agent_dir = self.agents_dir / agent_name
        if not agent_dir.exists():
            print(f"❌ Agent {agent_name} does not exist")
            return False
        
        test_script = agent_dir / "test_agent.py"
        if not test_script.exists():
            print(f"❌ Test script not found for {agent_name}")
            return False
        
        # Execute the test script
        import subprocess
        result = subprocess.run([
            "python", str(test_script)
        ], cwd=agent_dir, capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ Agent {agent_name} tests passed!")
            return True
        else:
            print(f"❌ Agent {agent_name} tests failed!")
            return False
    
    def get_status(self):
        """Get current factory status"""
        print("🏭 Insurance Agent Factory Status")
        print("=" * 50)
        
        # Count agents
        agent_dirs = [d for d in self.agents_dir.iterdir() if d.is_dir() and 
                     (d / "app.py").exists() and 
                     (d / "README.md").exists() and 
                     (d / "model_card.md").exists()]
        
        print(f"Active agents: {len(agent_dirs)}")
        for agent_dir in agent_dirs:
            print(f"  - {agent_dir.name}")
        
        # Check factory state
        state_file = self.agents_dir / self.factory_state_file
        if state_file.exists():
            import json
            with open(state_file, 'r') as f:
                state = json.load(f)
            print(f"Factory state loaded from {self.factory_state_file}")
        else:
            print("No factory state file found")
        
        print(f"Factory location: {self.agents_dir}")
        print("Ready to manufacture new agents on demand!")
        
        return {
            "agent_count": len(agent_dirs),
            "agents": [str(d.name) for d in agent_dirs],
            "location": str(self.agents_dir)
        }

def main():
    parser = argparse.ArgumentParser(description='Insurance Agent Factory')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add agent command
    add_parser = subparsers.add_parser('add-agent', help='Add a new agent')
    add_parser.add_argument('name', help='Name of the new agent')
    
    # Generate synthetic data command
    gen_parser = subparsers.add_parser('gen-synthetic', help='Generate synthetic data')
    gen_parser.add_argument('domain', help='Domain for synthetic data')
    
    # Link model command
    link_parser = subparsers.add_parser('link-model', help='Link model to agent')
    link_parser.add_argument('agent', help='Agent name')
    link_parser.add_argument('model', help='Model repository name')
    
    # Publish command
    pub_parser = subparsers.add_parser('publish', help='Publish agent to Hugging Face')
    pub_parser.add_argument('agent', help='Agent name')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test agent functionality')
    test_parser.add_argument('agent', help='Agent name')
    
    # Status command
    subparsers.add_parser('status', help='Show factory status')
    
    args = parser.parse_args()
    
    factory = InsuranceAgentFactory()
    
    if args.command == 'add-agent':
        factory.create_agent(args.name)
    elif args.command == 'gen-synthetic':
        factory.generate_synthetic_data(args.domain)
    elif args.command == 'link-model':
        factory.link_model(args.agent, args.model)
    elif args.command == 'publish':
        factory.publish_agent(args.agent)
    elif args.command == 'test':
        factory.test_agent(args.agent)
    elif args.command == 'status':
        factory.get_status()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()