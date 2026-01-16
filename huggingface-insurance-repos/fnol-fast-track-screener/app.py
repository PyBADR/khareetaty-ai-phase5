import gradio as gr
import random

def screen_fnol_claim(claim_source, loss_severity, incident_category):
    """
    Screen FNOL (First Notice of Loss) for routing decision
    
    Args:
        claim_source: Source of claim submission
        loss_severity: Severity rating (1-5)
        incident_category: Type of incident
    
    Returns:
        Routing decision, uncertainty, required documents checklist
    """
    
    # Routing logic
    if loss_severity <= 2 and claim_source in ['App', 'Call Center']:
        route = "Fast Track"
        route_color = "🟢"
        priority = "Low"
    elif loss_severity > 2 and incident_category in ['Auto Collision', 'Property']:
        route = "Standard Review"
        route_color = "🟡"
        priority = "Medium"
    elif loss_severity >= 4:
        route = "Escalation"
        route_color = "🔴"
        priority = "High"
    else:
        route = "Standard Review"
        route_color = "🟡"
        priority = "Medium"
    
    # Calculate uncertainty (random ±0.1 for demonstration)
    base_uncertainty = 0.15 if loss_severity <= 2 else 0.25 if loss_severity <= 3 else 0.40
    uncertainty = round(base_uncertainty + random.uniform(-0.1, 0.1), 2)
    uncertainty = max(0.0, min(1.0, uncertainty))
    
    # Required documents checklist
    required_docs = [
        "✓ Police report (if applicable)",
        "✓ Photos of damage/incident",
        "✓ Witness statements",
        "✓ Medical records (if injury involved)"
    ]
    
    if loss_severity >= 3:
        required_docs.append("✓ Expert assessment required")
    
    if incident_category in ['Fire', 'Theft']:
        required_docs.append("✓ Fire marshal/police investigation report")
    
    docs_checklist = "\n".join(required_docs)
    
    # Build detailed explanation
    explanation = f"""# {route_color} FNOL Screening Result: {route}

## Routing Decision

**Route:** {route}  
**Priority:** {priority}  
**Uncertainty:** {uncertainty:.2f}

### Decision Factors:

**Claim Source:** {claim_source}
- App / Call Center → Fast Track eligible
- Web / Agent → Standard routing
- Email → Manual review

**Loss Severity:** {loss_severity} / 5
- Level 1-2: Fast Track eligible
- Level 3: Standard Review
- Level 4-5: Escalation required

**Incident Category:** {incident_category}
- Sensitive categories require enhanced review

### Routing Explanation:

"""
    
    if route == "Fast Track":
        explanation += """**Fast Track**: Low severity claim from verified source.
- Streamlined processing
- Automated documentation review
- Expected resolution: 3-5 business days
"""
    elif route == "Standard Review":
        explanation += """**Standard Review**: Moderate complexity requiring adjuster review.
- Standard investigation procedures
- Document verification required
- Expected resolution: 7-14 business days
"""
    else:
        explanation += """**Escalation**: High severity requiring immediate attention.
- Senior adjuster assignment
- Comprehensive investigation
- Enhanced documentation requirements
- Expected resolution: 14-30 business days
"""
    
    explanation += f"""
---

## Required Documents Checklist

{docs_checklist}

---

## ⚠️ HUMAN VALIDATION NOTE

**This is an automated screening recommendation only.** All routing decisions must be validated by claims personnel. The system cannot make final determinations on claim routing or handling.

---

## 🚨 DISCLAIMER

**Synthetic screening logic - NOT for actual FNOL routing.**

This tool demonstrates fictional claims screening using synthetic logic. No outputs shall be used for actual claim routing, processing, or handling decisions. All scenarios are fabricated for educational purposes.

**Human claims professional review is mandatory.**
"""
    
    # Summary
    summary = f"""**Route:** {route_color} {route}
**Priority:** {priority}
**Uncertainty:** {uncertainty:.2f}
**Human Validation:** REQUIRED

**Next Steps:**
- Review required documents
- Assign to appropriate team
- Validate routing decision"""
    
    return explanation, summary, uncertainty, docs_checklist

# Create Gradio interface
with gr.Blocks(title="FNOL Fast Track Screener", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 📋 FNOL Fast Track Screener
    
    **First Notice of Loss Screening System**
    
    ## ⚠️ CRITICAL DISCLAIMER
    
    **This application demonstrates fictional FNOL screening logic using synthetic data only.**
    
    - ❌ NOT for actual claim routing or processing
    - ❌ NOT for claims handling decisions
    - ❌ NOT for resource allocation
    - ✅ Educational and demonstration purposes ONLY
    - ✅ Synthetic logic with no real-world application
    - ✅ Human claims professional review MANDATORY
    
    **All routing decisions require validation by qualified claims personnel.**
    """)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Claim Information")
            
            claim_source = gr.Dropdown(
                choices=['Call Center', 'App', 'Web', 'Agent', 'Email'],
                label="Claim Source",
                value="App",
                info="How was the claim submitted?"
            )
            
            loss_severity = gr.Slider(
                minimum=1,
                maximum=5,
                step=1,
                label="Loss Severity",
                value=2,
                info="1=Minor, 5=Catastrophic"
            )
            
            incident_category = gr.Dropdown(
                choices=['Auto Collision', 'Auto Theft', 'Property', 'Fire', 'Water Damage', 'Theft', 'Liability'],
                label="Incident Category",
                value="Auto Collision",
                info="Type of loss/incident"
            )
            
            screen_btn = gr.Button("🔍 Screen FNOL", variant="primary", size="lg")
        
        with gr.Column():
            gr.Markdown("### Screening Results")
            
            summary_output = gr.Textbox(
                label="Quick Summary",
                lines=10,
                interactive=False
            )
            
            uncertainty_output = gr.Number(
                label="Uncertainty Score (0-1)",
                interactive=False,
                precision=2
            )
            
            checklist_output = gr.Textbox(
                label="Required Documents Checklist",
                lines=8,
                interactive=False
            )
    
    with gr.Row():
        detailed_explanation = gr.Markdown(label="Detailed Screening Analysis")
    
    screen_btn.click(
        fn=screen_fnol_claim,
        inputs=[claim_source, loss_severity, incident_category],
        outputs=[detailed_explanation, summary_output, uncertainty_output, checklist_output]
    )
    
    with gr.Accordion("ℹ️ About This Tool", open=False):
        gr.Markdown("""
        ## How It Works
        
        This screener demonstrates **automated FNOL routing logic**:
        
        ### Routing Rules
        
        **Fast Track (🟢)**
        - Loss severity ≤ 2
        - Verified source (App/Call Center)
        - Standard incident categories
        
        **Standard Review (🟡)**
        - Loss severity = 3
        - Sensitive incident categories
        - Web/Agent submissions
        
        **Escalation (🔴)**
        - Loss severity ≥ 4
        - High-value claims
        - Complex incidents
        
        ### Uncertainty Scoring
        
        - Based on claim complexity
        - Random variation ±0.1 (for demonstration)
        - Higher uncertainty = more manual review needed
        
        ### Document Checklist
        
        Automatically generated based on:
        - Incident category
        - Loss severity
        - Regulatory requirements
        
        ---
        
        **Built for GCC Insurance Intelligence Lab**
        
        This tool is NOT approved for actual FNOL routing or claims handling. All decisions require validation by qualified claims professionals.
        """)

if __name__ == "__main__":
    demo.launch()
