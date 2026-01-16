import gradio as gr
import json

def mock_reinsurance_pricing(risk_group, frequency_tier, loss_severity):
    """
    Mock reinsurance pricing based on risk factors
    
    Args:
        risk_group: Risk category
        frequency_tier: Claim frequency (1-5)
        loss_severity: Severity category
    
    Returns:
        Indicative category, appetite indicator, capital pressure note
    """
    
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
    
    # Frequency multipliers
    freq_multipliers = {
        1: 0.8,  # Low frequency
        2: 0.9,  # Low-Med
        3: 1.0,  # Medium
        4: 1.2,  # Med-High
        5: 1.5   # High
    }
    
    # Severity multipliers
    severity_multipliers = {
        'Low': 0.8,
        'Medium': 1.0,
        'High': 1.4
    }
    
    # Calculate composite risk score
    risk_multiplier = risk_multipliers.get(risk_group, 1.0)
    freq_multiplier = freq_multipliers.get(frequency_tier, 1.0)
    severity_multiplier = severity_multipliers.get(loss_severity, 1.0)
    
    composite_score = risk_multiplier * freq_multiplier * severity_multiplier
    
    # Determine indicative category
    if composite_score < 1.0:
        category = "A"
        appetite = "Strong"
        pressure = "Low"
        color = "🟢"
    elif composite_score < 1.3:
        category = "B"
        appetite = "Moderate"
        pressure = "Moderate"
        color = "🟡"
    else:
        category = "C"
        appetite = "Cautious"
        pressure = "High"
        color = "🔴"
    
    # Capital pressure note
    if pressure == "High":
        pressure_note = "⚠️ Significant capital stress anticipated. Consider capacity limitations."
    elif pressure == "Moderate":
        pressure_note = "⚖️ Moderate capital impact. Monitor exposure concentrations."
    else:
        pressure_note = "✅ Minimal capital impact expected."
    
    # Build detailed explanation
    explanation = f"""# {color} Reinsurance Pricing Mock Analysis

## Indicative Category: {category}

**Composite Risk Score:** {composite_score:.2f}

### Factor Breakdown:

**Risk Group ({risk_group}):** {risk_multiplier:.2f}
- Agricultural: 1.2
- Construction: 1.4 (highest)
- Energy: 1.3
- Healthcare: 1.1
- Manufacturing: 1.3
- Technology: 0.9 (lowest)
- Transportation: 1.2

**Frequency Tier ({frequency_tier}/5):** {freq_multiplier:.2f}
- Tier 1 (Low): 0.8
- Tier 2 (Low-Med): 0.9
- Tier 3 (Medium): 1.0
- Tier 4 (Med-High): 1.2
- Tier 5 (High): 1.5

**Loss Severity ({loss_severity}):** {severity_multiplier:.2f}
- Low: 0.8
- Medium: 1.0
- High: 1.4

### Calculation:
Risk × Frequency × Severity = Composite Score
{risk_multiplier:.2f} × {freq_multiplier:.2f} × {severity_multiplier:.2f} = {composite_score:.2f}

### Category Determination:
- **A (< 1.0):** Strong appetite, favorable terms
- **B (1.0-1.3):** Moderate appetite, standard terms
- **C (> 1.3):** Cautious appetite, restrictive terms

### Reinsurance Appetite: {appetite}
### Capital Pressure: {pressure}

{pressure_note}

---

## 🚨 NO ACTUAL PRICING INFORMATION

**This is a conceptual demonstration only.** No actual premium calculations, treaty forms, or actuarial formulas are presented. This tool is for educational purposes only and does not constitute pricing advice.

---

## 🚨 DISCLAIMER

**Synthetic pricing mock - NOT for actual reinsurance decisions.**

This tool demonstrates fictional reinsurance concepts using synthetic logic. No outputs shall be used for actual pricing, treaty negotiation, or reinsurance decisions. All scenarios are fabricated for educational purposes.

**No actual premiums or financial obligations are calculated.**
"""
    
    # Summary
    summary = f"""**Indicative Category:** {color} {category}
**Reinsurance Appetite:** {appetite}
**Capital Pressure:** {pressure}
**Composite Score:** {composite_score:.2f}

**Factor Contributions:**
- Risk Group: {risk_multiplier:.2f}
- Frequency: {freq_multiplier:.2f}
- Severity: {severity_multiplier:.2f}"""
    
    return explanation, summary, composite_score, appetite

# Create Gradio interface
with gr.Blocks(title="Reinsurance Pricing Mock", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🔄 Reinsurance Pricing Mock
    
    **Conceptual Reinsurance Appetite and Category Assessment**
    
    ## ⚠️ CRITICAL DISCLAIMER
    
    **This application demonstrates fictional reinsurance concepts using synthetic data only.**
    
    - ❌ NOT for actual pricing or treaty negotiation
    - ❌ NOT for premium calculation or financial modeling
    - ❌ NOT for actuarial analysis or risk assessment
    - ✅ Educational and demonstration purposes ONLY
    - ✅ Synthetic logic with no real-world application
    - ✅ No actual financial calculations performed
    
    **No actual premiums, treaties, or financial obligations are calculated. This is a conceptual demonstration only.**
    """)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Risk Information")
            
            risk_group = gr.Dropdown(
                choices=['Agricultural', 'Construction', 'Energy', 'Healthcare', 'Manufacturing', 'Technology', 'Transportation'],
                label="Risk Group",
                value="Technology",
                info="Primary risk category"
            )
            
            frequency_tier = gr.Slider(
                minimum=1,
                maximum=5,
                step=1,
                label="Frequency Tier",
                value=3,
                info="1=Low, 5=High claim frequency"
            )
            
            loss_severity = gr.Radio(
                choices=['Low', 'Medium', 'High'],
                label="Loss Severity",
                value="Medium",
                info="Expected severity level"
            )
            
            assess_btn = gr.Button("📊 Assess Appetite", variant="primary", size="lg")
        
        with gr.Column():
            gr.Markdown("### Assessment Results")
            
            summary_output = gr.Textbox(
                label="Quick Summary",
                lines=8,
                interactive=False
            )
            
            composite_score_output = gr.Number(
                label="Composite Risk Score",
                interactive=False,
                precision=2
            )
            
            appetite_output = gr.Textbox(
                label="Reinsurance Appetite",
                lines=2,
                interactive=False
            )
    
    with gr.Row():
        detailed_explanation = gr.Markdown(label="Detailed Analysis")
    
    assess_btn.click(
        fn=mock_reinsurance_pricing,
        inputs=[risk_group, frequency_tier, loss_severity],
        outputs=[detailed_explanation, summary_output, composite_score_output, appetite_output]
    )
    
    with gr.Accordion("ℹ️ About This Tool", open=False):
        gr.Markdown("""
        ## How It Works
        
        This mock demonstrates **conceptual reinsurance appetite assessment**:
        
        ### Risk Factors
        
        **Risk Group Multiplier:**
        - Technology: 0.9 (lowest)
        - Healthcare: 1.1
        - Agricultural: 1.2
        - Transportation: 1.2
        - Manufacturing: 1.3
        - Energy: 1.3
        - Construction: 1.4 (highest)
        
        **Frequency Tier Multiplier:**
        - Tier 1 (Low): 0.8
        - Tier 2 (Low-Med): 0.9
        - Tier 3 (Medium): 1.0
        - Tier 4 (Med-High): 1.2
        - Tier 5 (High): 1.5
        
        **Loss Severity Multiplier:**
        - Low: 0.8
        - Medium: 1.0
        - High: 1.4
        
        ### Composite Calculation
        
        Risk × Frequency × Severity = Composite Score
        
        ### Indicative Categories
        
        - **Category A (< 1.0):** Strong appetite
        - **Category B (1.0-1.3):** Moderate appetite
        - **Category C (> 1.3):** Cautious appetite
        
        ---
        
        **Built for GCC Insurance Intelligence Lab**
        
        This tool is NOT approved for actual reinsurance pricing, treaty negotiation, or financial modeling. No actual premiums are calculated.
        """)

if __name__ == "__main__":
    demo.launch()
