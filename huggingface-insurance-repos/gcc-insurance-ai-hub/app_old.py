"""
GCC Insurance AI Hub
Central hub linking all insurance AI demonstration repositories.
"""

import gradio as gr

# Repository information
REPOS = {
    "insurance-datasets-synthetic": {
        "title": "📊 Insurance Datasets (Synthetic)",
        "description": "Synthetic insurance datasets for claims, policies, and fraud indicators",
        "url": "https://huggingface.co/spaces/YOUR_USERNAME/insurance-datasets-synthetic",
        "features": [
            "3 synthetic CSV datasets",
            "Claims data with amounts and dates",
            "Policy information",
            "Fraud indicators",
            "Interactive data viewer",
            "Download capabilities"
        ],
        "use_cases": [
            "Testing and development",
            "Training and education",
            "Prototyping analytics",
            "Demo applications"
        ]
    },
    "fraud-triage-sandbox": {
        "title": "🔍 Fraud Triage Sandbox",
        "description": "Rule-based fraud detection and claim triage demonstration",
        "url": "https://huggingface.co/spaces/YOUR_USERNAME/fraud-triage-sandbox",
        "features": [
            "Interactive claim input",
            "Rule-based fraud detection",
            "Risk scoring system",
            "Triage recommendations",
            "Configurable thresholds",
            "Detailed explanations"
        ],
        "use_cases": [
            "Understanding fraud detection",
            "Testing triage logic",
            "Training claims adjusters",
            "Workflow prototyping"
        ]
    },
    "ifrs-claim-accrual-estimator": {
        "title": "📈 IFRS 17 Claim Accrual Estimator",
        "description": "Actuarial reserve estimation under IFRS 17 principles",
        "url": "https://huggingface.co/spaces/YOUR_USERNAME/ifrs-claim-accrual-estimator",
        "features": [
            "Chain ladder method",
            "Risk adjustment calculation",
            "Present value discounting",
            "Complete accrual breakdown",
            "Multiple claim types",
            "Interactive parameters"
        ],
        "use_cases": [
            "Learning IFRS 17 concepts",
            "Understanding actuarial methods",
            "Reserve estimation demos",
            "Accounting training"
        ]
    },
    "doc-rag-compliance-assistant": {
        "title": "📚 Document RAG Compliance Assistant",
        "description": "Retrieval-Augmented Generation for compliance Q&A",
        "url": "https://huggingface.co/spaces/YOUR_USERNAME/doc-rag-compliance-assistant",
        "features": [
            "Document retrieval",
            "Answer generation",
            "Source transparency",
            "Multiple compliance topics",
            "Natural language queries",
            "Relevance scoring"
        ],
        "use_cases": [
            "Compliance Q&A",
            "Policy guidance",
            "Training and education",
            "Knowledge management"
        ]
    }
}

# Create Gradio interface
with gr.Blocks(title="GCC Insurance AI Hub", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🏢 GCC Insurance AI Hub
    
    Welcome to the **GCC Insurance AI Demonstration Hub** - your central access point for insurance AI tools and datasets.
    
    ## 🎯 Purpose
    
    This hub provides access to a collection of **demonstration tools** for insurance operations, including:
    - Synthetic datasets for testing
    - Fraud detection systems
    - Actuarial calculations
    - Compliance assistance
    
    ⚠️ **Important**: All tools use **synthetic data** and are for **demonstration purposes only**.
    
    ---
    """)
    
    # Repository 1: Datasets
    with gr.Accordion("📊 Insurance Datasets (Synthetic)", open=True):
        gr.Markdown(f"""
        ### {REPOS['insurance-datasets-synthetic']['title']}
        
        {REPOS['insurance-datasets-synthetic']['description']}
        
        **Features:**
        {chr(10).join(['- ' + f for f in REPOS['insurance-datasets-synthetic']['features']])}
        
        **Use Cases:**
        {chr(10).join(['- ' + u for u in REPOS['insurance-datasets-synthetic']['use_cases']])}
        
        **Access:** [Open Repository]({REPOS['insurance-datasets-synthetic']['url']})
        """)
    
    # Repository 2: Fraud Triage
    with gr.Accordion("🔍 Fraud Triage Sandbox", open=False):
        gr.Markdown(f"""
        ### {REPOS['fraud-triage-sandbox']['title']}
        
        {REPOS['fraud-triage-sandbox']['description']}
        
        **Features:**
        {chr(10).join(['- ' + f for f in REPOS['fraud-triage-sandbox']['features']])}
        
        **Use Cases:**
        {chr(10).join(['- ' + u for u in REPOS['fraud-triage-sandbox']['use_cases']])}
        
        **Access:** [Open Repository]({REPOS['fraud-triage-sandbox']['url']})
        """)
    
    # Repository 3: IFRS Estimator
    with gr.Accordion("📈 IFRS 17 Claim Accrual Estimator", open=False):
        gr.Markdown(f"""
        ### {REPOS['ifrs-claim-accrual-estimator']['title']}
        
        {REPOS['ifrs-claim-accrual-estimator']['description']}
        
        **Features:**
        {chr(10).join(['- ' + f for f in REPOS['ifrs-claim-accrual-estimator']['features']])}
        
        **Use Cases:**
        {chr(10).join(['- ' + u for u in REPOS['ifrs-claim-accrual-estimator']['use_cases']])}
        
        **Access:** [Open Repository]({REPOS['ifrs-claim-accrual-estimator']['url']})
        """)
    
    # Repository 4: RAG Assistant
    with gr.Accordion("📚 Document RAG Compliance Assistant", open=False):
        gr.Markdown(f"""
        ### {REPOS['doc-rag-compliance-assistant']['title']}
        
        {REPOS['doc-rag-compliance-assistant']['description']}
        
        **Features:**
        {chr(10).join(['- ' + f for f in REPOS['doc-rag-compliance-assistant']['features']])}
        
        **Use Cases:**
        {chr(10).join(['- ' + u for u in REPOS['doc-rag-compliance-assistant']['use_cases']])}
        
        **Access:** [Open Repository]({REPOS['doc-rag-compliance-assistant']['url']})
        """)
    
    gr.Markdown("""
    ---
    
    ## 🛠️ Technology Stack
    
    All repositories are built with:
    - **Framework**: Gradio for interactive interfaces
    - **Language**: Python 3.9+
    - **Libraries**: pandas, numpy for data processing
    - **Deployment**: Hugging Face Spaces
    
    ## 📋 Repository Overview
    
    | Repository | Type | Primary Function |
    |------------|------|------------------|
    | **Insurance Datasets** | Data | Synthetic datasets for testing |
    | **Fraud Triage Sandbox** | Application | Rule-based fraud detection |
    | **IFRS Accrual Estimator** | Calculator | Actuarial reserve estimation |
    | **RAG Compliance Assistant** | Q&A System | Document-based compliance guidance |
    
    ## ⚠️ Important Disclaimers
    
    ### Synthetic Data Only
    - All datasets are **100% synthetic**
    - No real customer, policy, or claim data
    - Generated for demonstration purposes only
    
    ### Advisory Only
    - All outputs are **advisory and illustrative**
    - Not suitable for production use
    - Not intended for actual business decisions
    
    ### No Real Business Logic
    - No real insurer names or policies
    - No actuarial formulas from real companies
    - No KYC fields or sensitive data
    - No pricing or quoting functionality
    
    ### Professional Guidance Required
    - Consult qualified professionals for real implementations
    - Verify all information with authoritative sources
    - Follow regulatory requirements and standards
    
    ## 🎓 Educational Use
    
    These tools are designed for:
    - **Learning**: Understanding insurance AI concepts
    - **Training**: Teaching insurance operations
    - **Prototyping**: Testing workflows and ideas
    - **Demonstration**: Showcasing capabilities
    
    ## 🔒 Compliance & Safety
    
    All repositories follow these principles:
    - **Privacy**: No real personal data
    - **Security**: No sensitive information
    - **Transparency**: Clear disclaimers and limitations
    - **Ethics**: Fair and unbiased demonstrations
    
    ## 📖 Documentation
    
    Each repository includes:
    - **README.md**: Overview and usage instructions
    - **model_card.md**: Detailed technical documentation
    - **requirements.txt**: Python dependencies
    - **Utility files**: Supporting code and functions
    
    ## 🚀 Getting Started
    
    1. **Browse** the repositories above
    2. **Click** on the repository links to access
    3. **Explore** the interactive demos
    4. **Learn** from the examples and documentation
    
    ## 💡 Use Case Examples
    
    ### For Developers
    - Test insurance applications with synthetic data
    - Prototype fraud detection workflows
    - Learn actuarial calculation methods
    - Implement RAG systems for compliance
    
    ### For Business Analysts
    - Understand fraud triage processes
    - Learn IFRS 17 measurement principles
    - Explore compliance documentation approaches
    - Analyze synthetic insurance data
    
    ### For Students & Educators
    - Study insurance operations
    - Learn AI/ML applications in insurance
    - Practice with realistic (but synthetic) scenarios
    - Understand regulatory frameworks
    
    ## 🔄 Updates & Maintenance
    
    These repositories are demonstration tools and may be updated periodically with:
    - Bug fixes and improvements
    - Additional features
    - Enhanced documentation
    - New examples and use cases
    
    ## 📞 Contact & Feedback
    
    For questions, feedback, or suggestions:
    - Visit individual repository pages
    - Review documentation and model cards
    - Contact Vercept for more information
    
    ---
    
    ## 🏗️ Architecture Overview
    
    ```
    GCC Insurance AI Hub (This Page)
            |
            ├── Insurance Datasets (Synthetic)
            |   └── Claims, Policies, Fraud Indicators
            |
            ├── Fraud Triage Sandbox
            |   └── Rule-based Detection & Triage
            |
            ├── IFRS 17 Accrual Estimator
            |   └── Chain Ladder & Reserve Calculation
            |
            └── RAG Compliance Assistant
                └── Document Retrieval & Q&A
    ```
    
    ## 🎯 Future Enhancements
    
    Potential additions to this hub:
    - Additional datasets (underwriting, claims processing)
    - More specialized calculators
    - Advanced ML models (with synthetic data)
    - Integration examples
    - API documentation
    
    ---
    
    **Built by Qoder for Vercept** | All data synthetic | Advisory only
    
    **Version**: 1.0.0 | **Last Updated**: January 2026
    """)

if __name__ == "__main__":
    demo.launch()
