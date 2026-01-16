"""
GCC Insurance AI Hub
Central landing page linking to insurance AI demonstration spaces.
"""

import gradio as gr

# Create Gradio interface
with gr.Blocks(title="GCC Insurance AI Hub", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🏢 GCC Insurance Intelligence Lab
    
    ## ⚠️ CRITICAL DISCLAIMER
    
    **All tools in this hub are for EDUCATIONAL and DEMONSTRATION purposes ONLY.**
    
    - **NOT for production use** in any insurance operations
    - **NOT a substitute** for qualified professionals (actuaries, compliance, legal)
    - **All data is 100% synthetic** - no real policies, claims, or customer information
    - **All outputs are advisory only** and require human expert validation
    - **No liability** for decisions based on these tools
    
    ### Compliance & Safety:
    
    - **No real insurer names** or product information
    - **No confidential rulebooks** or proprietary logic
    - **No pricing or reserving** for actual business use
    - **No KYC or personal identity** signals
    - **Human-in-the-loop enforced** for all outputs
    
    ---
    
    ## 📊 Available Spaces
    
    This hub provides access to four demonstration spaces:
    """)
    
    # Space 1: Fraud Triage Sandbox
    with gr.Row():
        with gr.Column():
            gr.Markdown("""
            ### 🔍 Fraud Triage Sandbox
            
            **Rule-based fraud detection system** for insurance claims triage.
            
            - Inputs: claim type, sector, evidence %, behavior pattern, claim history
            - Outputs: Low/Medium/High fraud likelihood with explanations
            - Includes uncertainty scoring and human review warnings
            
            **Use Case**: Educational demonstration of fraud detection logic
            
            [Open Fraud Triage Sandbox](https://huggingface.co/spaces/YOUR_USERNAME/fraud-triage-sandbox)
            """)
    
    # Space 2: IFRS Claim Accrual Estimator
    with gr.Row():
        with gr.Column():
            gr.Markdown("""
            ### 💰 IFRS Claim Accrual Estimator
            
            **Symbolic accrual bracket assignment** for insurance claims.
            
            - Inputs: claim stage, severity bracket, investigation duration, IBNR flag
            - Outputs: Accrual Band A-E (symbolic only, no monetary amounts)
            - Includes mandatory "consult finance" warnings
            
            **Use Case**: Educational demonstration of accrual estimation concepts
            
            [Open IFRS Accrual Estimator](https://huggingface.co/spaces/YOUR_USERNAME/ifrs-claim-accrual-estimator)
            """)
    
    # Space 3: Document RAG Compliance Assistant
    with gr.Row():
        with gr.Column():
            gr.Markdown("""
            ### 📚 Document RAG Compliance Assistant
            
            **Retrieval-Augmented Generation** for policy compliance questions.
            
            - Loads synthetic policy clauses from text file
            - Uses sentence transformers or TF-IDF for semantic search
            - Returns most relevant clause with similarity score
            - Includes out-of-scope guardrails and human review warnings
            
            **Use Case**: Educational demonstration of RAG systems for compliance
            
            [Open RAG Compliance Assistant](https://huggingface.co/spaces/YOUR_USERNAME/doc-rag-compliance-assistant)
            """)
    
    # Space 4: Insurance Datasets (Synthetic)
    with gr.Row():
        with gr.Column():
            gr.Markdown("""
            ### 📈 Insurance Datasets (Synthetic)
            
            **Synthetic datasets** for testing and development.
            
            - fraud_cases_synthetic.csv (250 rows)
            - claims_lifecycle_ifrs_synthetic.csv (251 rows)
            - policy_clauses_snippets.txt (12 clauses)
            - All data is 100% fabricated for demonstration
            
            **Use Case**: Synthetic data for testing insurance applications
            
            [Open Insurance Datasets](https://huggingface.co/spaces/YOUR_USERNAME/insurance-datasets-synthetic)
            """)
    
    gr.Markdown("""
    ---
    
    ## 🛡️ Mandatory Disclaimers
    
    ### For All Spaces:
    
    1. **Educational Purpose Only**: These tools demonstrate AI concepts, not production systems
    2. **Synthetic Data**: All datasets are fabricated - no real insurance information
    3. **No Business Decisions**: Never use for actual pricing, reserving, claims, or underwriting
    4. **Human Validation Required**: All outputs must be reviewed by qualified professionals
    5. **No Regulatory Compliance**: These tools do not ensure compliance with any regulations
    6. **No Liability**: Vercept and Qoder assume no liability for use of these tools
    
    ### Professional Guidance:
    
    For actual insurance operations, always consult:
    - **Actuaries** for reserving and pricing
    - **Compliance officers** for regulatory matters
    - **Legal counsel** for policy interpretation
    - **Finance teams** for accounting and reporting
    - **Underwriters** for risk assessment
    
    ### Privacy & Security:
    
    - No real customer data or PII
    - No confidential business information
    - No proprietary algorithms or formulas
    - No connection to production systems
    
    ---
    
    ## 📝 About This Hub
    
    The GCC Insurance Intelligence Lab is a collection of demonstration tools built by **Qoder for Vercept**.
    
    **Purpose**: Educational demonstrations of AI applications in insurance
    
    **Technology**: Gradio, Python, sentence transformers, scikit-learn
    
    **License**: MIT (for demonstration code only)
    
    **Version**: 1.0.0 | **Last Updated**: January 2026
    
    ---
    
    **⚠️ Remember**: These are demonstration tools only. Always consult qualified professionals for actual insurance operations.
    """)

if __name__ == "__main__":
    demo.launch()
