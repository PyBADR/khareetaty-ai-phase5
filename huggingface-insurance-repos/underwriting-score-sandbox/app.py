import gradio as gr
import pandas as pd
import json
from underwriting_rules import UnderwritingScorer

# Initialize the underwriting scorer
scorer = UnderwritingScorer()

# Load synthetic data for reference
try:
    df_profiles = pd.read_csv("risk_profiles_synthetic.csv")
    print(f"✓ Loaded {len(df_profiles)} synthetic risk profiles")
except:
    df_profiles = None
    print("⚠️ Could not load risk profiles data")

def score_underwriting_risk(industry_segment, applicant_risk_profile, prior_claim_count):
    """Score underwriting risk based on inputs"""
    
    try:
        # Score the applicant
        result = scorer.score_applicant(
            industry_segment=industry_segment,
            applicant_risk_profile=applicant_risk_profile,
            prior_claim_count=int(prior_claim_count)
        )
        
        # Format output
        risk_band = result['risk_band']
        aggregate_score = result['aggregate_score']
        factor_breakdown = result['factor_breakdown']
        explanation = result['explanation']
        
        # Create factor breakdown JSON display
        factor_json = json.dumps(factor_breakdown, indent=2)
        
        # Summary
        summary = f"""**Risk Band:** {risk_band}
**Aggregate Score:** {aggregate_score:.3f}
**Underwriter Review:** Required

**Factor Breakdown:**
{factor_json}"""
        
        return explanation, summary, aggregate_score, factor_json
        
    except Exception as e:
        error_msg = f"Error processing underwriting score: {str(e)}"
        return error_msg, error_msg, 0.0, "{}"

# Create Gradio interface
with gr.Blocks(title="Underwriting Score Sandbox", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🏢 Underwriting Score Sandbox
    
    **Educational Underwriting Risk Scoring System**
    
    This sandbox demonstrates rule-based underwriting risk assessment for insurance applicants.
    
    ## ⚠️ MANDATORY DISCLAIMER
    
    **This application demonstrates fictional insurance logic using synthetic data only.**
    
    - ✅ Educational and demonstration purposes only
    - ✅ No outputs shall be used for real underwriting decisions
    - ✅ All data is 100% synthetic and fabricated
    - ✅ Underwriter review is MANDATORY for all assessments
    - ✅ No real pricing, quoting, or policy binding occurs here
    - ✅ Human-in-the-loop required for all decisions
    
    **This tool provides advisory risk bands only. Final underwriting decisions must be made by qualified insurance underwriters.**
    """)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Applicant Information")
            
            industry_segment = gr.Dropdown(
                choices=[
                    'Technology',
                    'Professional Services',
                    'Education',
                    'Retail',
                    'Healthcare',
                    'Hospitality',
                    'Manufacturing',
                    'Transportation',
                    'Construction'
                ],
                label="Industry Segment",
                value="Technology",
                info="Primary business industry"
            )
            
            applicant_risk_profile = gr.Radio(
                choices=['Low', 'Medium', 'High'],
                label="Applicant Risk Profile",
                value="Low",
                info="Initial risk assessment from application"
            )
            
            prior_claim_count = gr.Slider(
                minimum=0,
                maximum=10,
                step=1,
                label="Prior Claim Count",
                value=0,
                info="Number of insurance claims in past 5 years"
            )
            
            score_btn = gr.Button("🎯 Calculate Risk Score", variant="primary", size="lg")
        
        with gr.Column():
            gr.Markdown("### Risk Assessment Results")
            
            summary_output = gr.Textbox(
                label="Quick Summary",
                lines=10,
                interactive=False
            )
            
            aggregate_score_output = gr.Number(
                label="Aggregate Risk Score (0-1)",
                interactive=False
            )
            
            factor_breakdown_output = gr.Textbox(
                label="Factor Breakdown (JSON)",
                lines=8,
                interactive=False
            )
    
    with gr.Row():
        detailed_output = gr.Markdown(label="Detailed Risk Explanation")
    
    score_btn.click(
        fn=score_underwriting_risk,
        inputs=[industry_segment, applicant_risk_profile, prior_claim_count],
        outputs=[detailed_output, summary_output, aggregate_score_output, factor_breakdown_output]
    )
    
    with gr.Accordion("ℹ️ About This Tool", open=False):
        gr.Markdown("""
        ## How It Works
        
        This underwriting risk scorer uses **rule-based logic** to assess insurance applicant risk:
        
        ### Input Factors
        
        1. **Industry Segment** (Weight: 40%)
           - Different industries have varying inherent risk levels
           - Range: Technology (lowest) to Construction (highest)
        
        2. **Prior Claim History** (Weight: 35%)
           - Number of insurance claims filed in past 5 years
           - 0 claims = excellent, 7+ claims = high risk
        
        3. **Applicant Risk Profile** (Weight: 25%)
           - Initial risk assessment from application review
           - Low / Medium / High categories
        
        ### Risk Bands
        
        - **Low (0.00 - 0.29)**: Standard underwriting, minimal documentation
        - **Medium (0.30 - 0.59)**: Enhanced review, additional documentation required
        - **High (0.60 - 1.00)**: Detailed assessment, risk controls recommended
        
        ### Calculation Method
        
        ```
        Aggregate Score = (Industry × 0.40) + (History × 0.35) + (Profile × 0.25)
        Risk Band = Map score to Low/Medium/High thresholds
        ```
        
        ### Governance & Safety
        
        - ✅ Rule-based (no machine learning)
        - ✅ Transparent scoring logic
        - ✅ Explainable factors
        - ✅ Mandatory underwriter review
        - ✅ No automated decisions
        - ✅ Advisory output only
        
        ### Use Cases
        
        - **Training**: Teach underwriting concepts
        - **Process Design**: Test risk assessment workflows
        - **Education**: Demonstrate insurance risk scoring
        - **Prototyping**: Validate underwriting logic
        
        ### Technical Details
        
        - **Framework**: Gradio
        - **Logic**: Rule-based scoring engine
        - **Data**: 200 synthetic risk profiles
        - **Dependencies**: gradio, pandas, numpy
        
        ### Limitations
        
        - Educational demonstration only
        - Synthetic data with no real-world validation
        - Simplified scoring model
        - No integration with actual underwriting systems
        - Not suitable for production use
        
        **Built for GCC Insurance Intelligence Lab**
        """
        )

if __name__ == "__main__":
    demo.launch()
