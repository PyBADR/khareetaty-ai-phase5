# Hugging Face Push Instructions

All 5 Spaces are ready to be pushed to the `gcc-insurance-intelligence-lab` organization on Hugging Face. Each Space has been prepared with a dedicated push script.

## Authentication Required

Before pushing to Hugging Face, you need to authenticate. Run the following command:

```bash
huggingface-cli login
```

Then enter your Hugging Face access token when prompted.

## Push Commands for Each Space

### 1. underwriting-score-sandbox
```bash
cd /Users/bdr.ai/huggingface-insurance-repos/underwriting-score-sandbox-v2
python3 push_to_hf.py
```

### 2. fnol-fast-track-screener
```bash
cd /Users/bdr.ai/huggingface-insurance-repos/fnol-fast-track-screener
python3 push_to_hf.py
```

### 3. claims-journey-simulator
```bash
cd /Users/bdr.ai/huggingface-insurance-repos/claims-journey-simulator
python3 push_to_hf.py
```

### 4. reinsurance-pricing-mock
```bash
cd /Users/bdr.ai/huggingface-insurance-repos/reinsurance-pricing-mock
python3 push_to_hf.py
```

### 5. fraud-audit-log-engine
```bash
cd /Users/bdr.ai/huggingface-insurance-repos/fraud-audit-log-engine
python3 push_to_hf.py
```

## Space Details

### 1. underwriting-score-sandbox
- **Repository**: `gcc-insurance-intelligence-lab/underwriting-score-sandbox`
- **Function**: Rule-based underwriting risk scoring
- **Features**: Risk bands (Low/Medium/High), factor breakdown, human review enforcement

### 2. fnol-fast-track-screener
- **Repository**: `gcc-insurance-intelligence-lab/fnol-fast-track-screener`
- **Function**: FNOL screening with routing recommendations
- **Features**: Fast Track/Standard/Escalation routing, uncertainty scoring, document checklist

### 3. claims-journey-simulator
- **Repository**: `gcc-insurance-intelligence-lab/claims-journey-simulator`
- **Function**: Claims lifecycle simulation with duration estimates
- **Features**: 5-stage timeline simulation, bottleneck identification, adjuster touchpoints

### 4. reinsurance-pricing-mock
- **Repository**: `gcc-insurance-intelligence-lab/reinsurance-pricing-mock`
- **Function**: Conceptual reinsurance appetite assessment
- **Features**: Indicative categories (A/B/C), capital pressure notes, risk factor evaluation

### 5. fraud-audit-log-engine
- **Repository**: `gcc-insurance-intelligence-lab/fraud-audit-log-engine`
- **Function**: Audit trail system for fraud detection outcomes
- **Features**: Append-only logging, JSONL export, immutable audit trails

## Post-Push Verification

After pushing each Space, verify that it's running correctly by visiting:

- https://huggingface.co/spaces/gcc-insurance-intelligence-lab/underwriting-score-sandbox
- https://huggingface.co/spaces/gcc-insurance-intelligence-lab/fnol-fast-track-screener
- https://huggingface.co/spaces/gcc-insurance-intelligence-lab/claims-journey-simulator
- https://huggingface.co/spaces/gcc-insurance-intelligence-lab/reinsurance-pricing-mock
- https://huggingface.co/spaces/gcc-insurance-intelligence-lab/fraud-audit-log-engine

## Important Notes

- All Spaces use only synthetic data and are for educational purposes
- Each Space has proper disclaimers and human-in-the-loop requirements
- No real insurance data or production logic is used
- All Spaces are built with Gradio for easy web deployment
- Each Space includes comprehensive documentation (README.md and model_card.md)

## Troubleshooting

If you encounter permission errors, ensure that:
1. You have admin rights to the `gcc-insurance-intelligence-lab` organization
2. Your Hugging Face token has the correct scopes (write access)
3. The repository names don't conflict with existing repositories

If you encounter rate limiting, wait a few minutes between pushes to allow the Hugging Face servers to process each repository creation.