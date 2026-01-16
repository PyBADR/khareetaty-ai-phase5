import gradio as gr
import random
import pandas as pd

def simulate_claims_journey(severity, doc_completeness):
    """
    Simulate the claims lifecycle journey
    
    Args:
        severity: Low/Medium/High
        doc_completeness: Percentage of required documents (0-100)
    
    Returns:
        Timeline table, estimated total days, touchpoints
    """
    
    # Base days per stage by severity
    base_days = {
        'Low': {'FNOL': 1, 'Assignment': 1, 'Investigation': 2, 'Decision': 2, 'Payment': 2},
        'Medium': {'FNOL': 2, 'Assignment': 2, 'Investigation': 5, 'Decision': 3, 'Payment': 3},
        'High': {'FNOL': 3, 'Assignment': 3, 'Investigation': 10, 'Decision': 5, 'Payment': 5}
    }
    
    # Get base days for severity
    stage_base_days = base_days[severity]
    
    # Adjust for document completeness (incomplete docs add delays)
    doc_factor = 1.0 if doc_completeness >= 80 else 1.5 if doc_completeness >= 50 else 2.5
    
    # Calculate adjusted days with randomness
    stage_days = {}
    for stage, base_day in stage_base_days.items():
        # Add randomness and document factor
        adjusted = base_day * doc_factor
        random_factor = random.uniform(0.8, 1.2)
        stage_days[stage] = max(1, round(adjusted * random_factor))
    
    # Calculate total estimated days
    total_days = sum(stage_days.values())
    
    # Identify potential bottlenecks
    bottlenecks = []
    for stage, days in stage_days.items():
        if days > 5:  # Significant delay threshold
            bottlenecks.append(stage)
    
    # Generate touchpoints
    touchpoints = [
        "FNOL representative contact",
        "Adjuster assignment notification",
        "Document submission reminder",
        "Investigation status update",
        "Decision notification",
        "Payment processing confirmation"
    ]
    
    if severity == 'High':
        touchpoints.extend([
            "Senior adjuster review",
            "Specialist consultation"
        ])
    
    if doc_completeness < 80:
        touchpoints.append("Additional document request")
    
    # Create timeline table
    timeline_table = f"""
| Stage | Base Days | Adjusted Days | Touchpoints |
|-------|-----------|---------------|-------------|
| FNOL | {base_days[severity]['FNOL']} | {stage_days['FNOL']} | {stage_days['FNOL']} business days |
| Assignment | {base_days[severity]['Assignment']} | {stage_days['Assignment']} | {stage_days['Assignment']} business days |
| Investigation | {base_days[severity]['Investigation']} | {stage_days['Investigation']} | {stage_days['Investigation']} business days |
| Decision | {base_days[severity]['Decision']} | {stage_days['Decision']} | {stage_days['Decision']} business days |
| Payment | {base_days[severity]['Payment']} | {stage_days['Payment']} | {stage_days['Payment']} business days |
"""
    
    # Generate explanation
    explanation = f"""# Claims Journey Simulation

## Estimated Total Duration: {total_days} Business Days

### Stage-by-Stage Timeline:

{timeline_table}

### Key Factors:

**Severity Level:** {severity}
- Low: Minimal investigation required
- Medium: Standard investigation procedures
- High: Comprehensive investigation and review

**Document Completeness:** {doc_completeness}%
- ≥80%: Standard processing
- 50-79%: Moderate delays
- <50%: Significant delays

### Potential Bottlenecks:

"""
    
    if bottlenecks:
        explanation += "\n".join([f"- **{b}**: May require {stage_days[b]} business days" for b in bottlenecks])
    else:
        explanation += "- No significant bottlenecks expected"
    
    explanation += f"""

### Required Touchpoints:

{chr(10).join([f"- {t}" for t in touchpoints])}

---

## ⚠️ TOUCHPOINTS REQUIRING ADJUSTER ACTION

**This simulation demonstrates the typical claims journey flow.** All stages require active adjuster involvement and cannot be automated. The timeline is an estimate based on synthetic data and may vary significantly in real scenarios.

---

## 🚨 DISCLAIMER

**Synthetic journey simulation - NOT for actual claims processing.**

This tool demonstrates fictional claims lifecycle using synthetic logic. No outputs shall be used for actual claims processing, timing, or resource allocation. All scenarios are fabricated for educational purposes.

**Human adjuster involvement is mandatory at all stages.**
"""
    
    # Summary
    summary = f"""**Estimated Total Duration:** {total_days} business days
**Severity Level:** {severity}
**Document Completeness:** {doc_completeness}%

**Key Stages:**
- FNOL: {stage_days['FNOL']} days
- Investigation: {stage_days['Investigation']} days
- Decision: {stage_days['Decision']} days

**Touchpoints Required:** {len(touchpoints)} adjuster actions"""
    
    return explanation, summary, total_days, timeline_table

# Create Gradio interface
with gr.Blocks(title="Claims Journey Simulator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🛣️ Claims Journey Simulator
    
    **Generic Insurance Claims Lifecycle Simulator**
    
    ## ⚠️ CRITICAL DISCLAIMER
    
    **This application demonstrates fictional claims lifecycle using synthetic data only.**
    
    - ❌ NOT for actual claims processing or timing
    - ❌ NOT for resource allocation or scheduling
    - ❌ NOT for policyholder communication
    - ✅ Educational and demonstration purposes ONLY
    - ✅ Synthetic data with no real-world application
    - ✅ Human adjuster involvement MANDATORY at all stages
    
    **All claims require active adjuster management and cannot be automated.**
    """)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Claim Information")
            
            severity = gr.Radio(
                choices=['Low', 'Medium', 'High'],
                label="Claim Severity",
                value="Medium",
                info="Overall severity of the claim"
            )
            
            doc_completeness = gr.Slider(
                minimum=0,
                maximum=100,
                step=5,
                label="Document Completeness %",
                value=80,
                info="Percentage of required documents submitted"
            )
            
            simulate_btn = gr.Button("🔄 Simulate Journey", variant="primary", size="lg")
        
        with gr.Column():
            gr.Markdown("### Simulation Results")
            
            summary_output = gr.Textbox(
                label="Quick Summary",
                lines=8,
                interactive=False
            )
            
            total_days_output = gr.Number(
                label="Estimated Total Days",
                interactive=False
            )
            
            timeline_table_output = gr.Markdown(
                label="Stage Timeline"
            )
    
    with gr.Row():
        detailed_explanation = gr.Markdown(label="Detailed Journey Analysis")
    
    simulate_btn.click(
        fn=simulate_claims_journey,
        inputs=[severity, doc_completeness],
        outputs=[detailed_explanation, summary_output, total_days_output, timeline_table_output]
    )
    
    with gr.Accordion("ℹ️ About This Tool", open=False):
        gr.Markdown("""
        ## How It Works
        
        This simulator demonstrates **generic claims lifecycle stages**:
        
        ### Lifecycle Stages
        
        **1. FNOL (First Notice of Loss)**
        - Initial claim reporting
        - Basic information gathering
        - Initial assignment
        
        **2. Assignment**
        - Adjuster assignment
        - Initial contact with claimant
        - Case setup
        
        **3. Investigation**
        - Evidence gathering
        - Witness interviews
        - Expert consultations
        
        **4. Decision**
        - Liability determination
        - Coverage verification
        - Settlement calculation
        
        **5. Payment**
        - Settlement processing
        - Payment authorization
        - File closure
        
        ### Factors Affecting Timeline
        
        - **Severity**: Higher severity = longer processing
        - **Document Completeness**: Incomplete docs cause delays
        - **Random Variation**: Simulates real-world uncertainty
        
        ---
        
        **Built for GCC Insurance Intelligence Lab**
        
        This tool is NOT approved for actual claims processing, timing, or resource allocation. All claims require active adjuster management.
        """)

if __name__ == "__main__":
    demo.launch()
