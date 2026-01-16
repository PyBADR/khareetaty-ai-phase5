import gradio as gr
import json
import random
import spaces

@spaces.GPU(duration=30)
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
