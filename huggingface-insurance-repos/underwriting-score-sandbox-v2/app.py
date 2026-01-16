import gradio as gr
import json

def calculate_underwriting_risk(industry_segment, applicant_risk_profile, prior_claim_count):
    """
    Calculate underwriting risk score based on rule-based logic
    
    Args:
        industry_segment: Industry category
        applicant_risk_profile: Risk profile (Low/Medium/High)
        prior_claim_count: Number of prior claims (0-10)
    
    Returns:
        Risk band, factor breakdown, and explanation
    """
    
    # 1. Industry risk factors
    industry_factors = {
        'Manufacturing': 1.2,
        'Retail': 1.0,
        'Healthcare': 1.3,
        'Technology': 0.8,
        'Construction': 1.5
    }
    industry_factor = industry_factors.get(industry_segment, 1.0)
    
    # 2. History factor: prior_claims * 0.15
    history_factor = prior_claim_count * 0.15
    
    # 3. Profile bias
    profile_bias_map = {
        'Low': 0.0,
        'Medium': 1.0,
        'High': 2.0
    }
    profile_bias = profile_bias_map.get(applicant_risk_profile, 1.0)
    
    # 4. Aggregate score = industry_factor + history_factor + profile_bias
    aggregate_score = industry_factor + history_factor + profile_bias
    
    # 5. Risk band determination
    if aggregate_score < 1.5:
        risk_band = "Low"
        risk_color = "🟢"
    elif aggregate_score <= 3.0:
        risk_band = "Medium"
        risk_color = "🟡"
    else:
        risk_band = "High"
        risk_color = "🔴"
    
    # Build factor breakdown
    factor_breakdown = {
        "industry_segment": industry_segment,
        "industry_factor": round(industry_factor, 2),
        "prior_claim_count": prior_claim_count,
        "history_factor": round(history_factor, 2),
        "applicant_risk_profile": applicant_risk_profile,
        "profile_bias": round(profile_bias, 2),
        "aggregate_score": round(aggregate_score, 2),
        "risk_band": risk_band
    }
    
    # Format factor breakdown as JSON
    factor_json = json.dumps(factor_breakdown, indent=2)
    
    # Build detailed explanation
    explanation = f"""# {risk_color} Underwriting Risk Assessment: {risk_band}

## Aggregate Risk Score: {aggregate_score:.2f}

### Factor Breakdown:

**1. Industry Factor ({industry_segment}):** {industry_factor:.2f}
- Manufacturing: 1.2
- Retail: 1.0
- Healthcare: 1.3
- Technology: 0.8
- Construction: 1.5

**2. History Factor ({prior_claim_count} prior claims):** {history_factor:.2f}
- Calculation: {prior_claim_count} × 0.15 = {history_factor:.2f}

**3. Profile Bias ({applicant_risk_profile}):** {profile_bias:.2f}
- Low: 0.0
- Medium: 1.0
- High: 2.0

**4. Aggregate Score:** {aggregate_score:.2f}
- Formula: {industry_factor:.2f} + {history_factor:.2f} + {profile_bias:.2f} = {aggregate_score:.2f}

**5. Risk Band:** {risk_band}
- Low: < 1.5
- Medium: 1.5 - 3.0
- High: > 3.0

---

## ⚠️ UNDERWRITER REVIEW REQUIRED

**This is an advisory assessment only. All underwriting decisions must be reviewed and approved by qualified underwriters before binding coverage.**

---

## 🚨 MANDATORY DISCLAIMER

**Synthetic data only - NOT for real underwriting decisions.**

This tool demonstrates fictional insurance logic using synthetic data only. No outputs shall be used for actual underwriting, pricing, reserving, or policy binding decisions. All data is fabricated for educational purposes.

**Human-in-the-loop is mandatory for all insurance decisions.**
"""
    
    # Summary output
    summary = f"""**Risk Band:** {risk_color} {risk_band}
**Aggregate Score:** {aggregate_score:.2f}
**Underwriter Review:** REQUIRED

**Factor Summary:**
- Industry Factor: {industry_factor:.2f}
- History Factor: {history_factor:.2f}
- Profile Bias: {profile_bias:.2f}"""
    
    return explanation, summary, factor_json, aggregate_score

# Create Gradio interface
with gr.Blocks(title="Underwriting Score Sandbox", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🏢 Underwriting Score Sandbox
    
    **Educational Underwriting Risk Assessment System**
    
    ## ⚠️ CRITICAL DISCLAIMER
    
    **This application demonstrates fictional insurance logic using synthetic data only.**
    
    - ❌ NOT for real underwriting decisions
    - ❌ NOT for pricing or premium calculation
    - ❌ NOT for policy binding or issuance
    - ✅ Educational and demonstration purposes ONLY
    - ✅ Synthetic data with no real-world application
    - ✅ Human-in-the-loop MANDATORY for all decisions
    
    **All outputs are advisory only and require qualified underwriter review.**
    """)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Applicant Information")
            
            industry_segment = gr.Dropdown(
                choices=['Manufacturing', 'Retail', 'Healthcare', 'Technology', 'Construction'],
                label="Industry Segment",
                value="Technology",
                info="Select primary business industry"
            )
            
            applicant_risk_profile = gr.Dropdown(
                choices=['Low', 'Medium', 'High'],
                label="Applicant Risk Profile",
                value="Low",
                info="Initial risk assessment from application review"
            )
            
            prior_claim_count = gr.Slider(
                minimum=0,
                maximum=10,
                step=1,
                label="Prior Claim Count",
                value=0,
                info="Number of insurance claims in past 5 years"
            )
            
            calculate_btn = gr.Button("🎯 Calculate Risk Score", variant="primary", size="lg")
        
        with gr.Column():
            gr.Markdown("### Assessment Results")
            
            summary_output = gr.Textbox(
                label="Quick Summary",
                lines=8,
                interactive=False
            )
            
            aggregate_score_output = gr.Number(
                label="Aggregate Risk Score",
                interactive=False,
                precision=2
            )
            
            factor_breakdown_output = gr.Textbox(
                label="Factor Breakdown (JSON)",
                lines=10,
                interactive=False
            )
    
    with gr.Row():
        detailed_explanation = gr.Markdown(label="Detailed Risk Assessment")
    
    # Connect button to function
    calculate_btn.click(
        fn=calculate_underwriting_risk,
        inputs=[industry_segment, applicant_risk_profile, prior_claim_count],
        outputs=[detailed_explanation, summary_output, factor_breakdown_output, aggregate_score_output]
    )
    
    with gr.Accordion("ℹ️ About This Tool", open=False):
        gr.Markdown("""
        ## How It Works
        
        This sandbox demonstrates **rule-based underwriting risk scoring** using transparent logic:
        
        ### Scoring Formula
        
        ```
        Aggregate Score = Industry Factor + History Factor + Profile Bias
        ```
        
        ### Factor Definitions
        
        **1. Industry Risk Factors:**
        - Technology: 0.8 (lowest risk)
        - Retail: 1.0
        - Manufacturing: 1.2
        - Healthcare: 1.3
        - Construction: 1.5 (highest risk)
        
        **2. History Factor:**
        - Calculation: Prior Claim Count × 0.15
        - Example: 5 claims × 0.15 = 0.75
        
        **3. Profile Bias:**
        - Low: 0.0 (no additional risk)
        - Medium: 1.0
        - High: 2.0 (significant risk)
        
        ### Risk Band Thresholds
        
        - **Low**: Aggregate Score < 1.5
        - **Medium**: Aggregate Score 1.5 - 3.0
        - **High**: Aggregate Score > 3.0
        
        ### Example Calculation
        
        **Inputs:**
        - Industry: Construction (1.5)
        - Prior Claims: 4 (0.60)
        - Profile: Medium (1.0)
        
        **Calculation:**
        - 1.5 + 0.60 + 1.0 = 3.1
        - Risk Band: High (> 3.0)
        
        ### Governance & Safety
        
        - ✅ Rule-based logic (no ML)
        - ✅ Transparent calculations
        - ✅ JSON output for auditability
        - ✅ Mandatory underwriter review
        - ✅ No automated decisions
        - ✅ Human-in-the-loop enforced
        
        ### Use Cases
        
        - Training insurance professionals
        - Demonstrating risk assessment logic
        - Prototyping underwriting workflows
        - Educational sandbox for GCC markets
        
        ### Limitations
        
        - Educational demonstration only
        - Synthetic logic with no real-world validation
        - Simplified scoring model
        - Not suitable for production use
        - No actual underwriting authority
        
        ---
        
        **Built for GCC Insurance Intelligence Lab**
        
        **CRITICAL**: This tool is NOT approved for actual underwriting decisions, premium pricing, policy binding, or any real insurance operations. All outputs require human review by qualified underwriters.
        """)

if __name__ == "__main__":
    demo.launch()
