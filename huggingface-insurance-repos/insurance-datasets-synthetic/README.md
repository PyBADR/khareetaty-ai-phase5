---
title: Insurance Datasets Synthetic
emoji: 📈
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
---

# 📈 Insurance Synthetic Datasets

## Overview

This repository provides **synthetic insurance datasets** for testing, development, and educational purposes. All data is completely synthetic and does not contain any real insurance policies, claims, or personal information.

## 📊 Datasets Included

### 1. Fraud Cases Synthetic (`data/fraud_cases_synthetic.csv`)
Synthetic fraud detection training data for insurance claims triage.

**Columns:**
- `policy_type`: Type of insurance policy
- `claimant_profile_risk`: Risk profile of claimant
- `incident_pattern`: Pattern of incident occurrence
- `document_consistency_score`: Score for document consistency (0-100)
- `anomaly_score`: Anomaly detection score (0-100)
- `synthetic_flag_label`: Fraud flag label (Low/Medium/High)

**Sample Size:** 250 records

### 2. Claims Lifecycle IFRS Synthetic (`data/claims_lifecycle_ifrs_synthetic.csv`)
Synthetic claims data for IFRS 17 accrual estimation and lifecycle analysis.

**Columns:**
- `claim_stage`: Current stage of claim processing
- `expected_severity`: Expected severity level
- `incurred_but_not_reported_flag`: IBNR indicator (Yes/No)
- `accrual_factor`: Accrual multiplier factor
- `expected_loss_amount`: Expected loss amount in USD
- `uncertainty_score`: Uncertainty score (0-100)

**Sample Size:** 251 records

### 3. Policy Clauses Snippets (`data/policy_clauses_snippets.txt`)
Synthetic policy clause text snippets for compliance and RAG testing.

**Content:** 12 fabricated policy clause paragraphs covering various insurance topics

**Sample Size:** 12 paragraphs

## 🚀 Usage

### Interactive Explorer
Use the Gradio app to explore the datasets interactively:
- View dataset statistics
- Preview fraud cases data
- Explore IFRS claims lifecycle data
- Read policy clause snippets

### Download & Use
Download the files from the `data/` directory for use in your projects:

```python
import pandas as pd

# Load fraud cases data
fraud_df = pd.read_csv('data/fraud_cases_synthetic.csv')

# Load IFRS claims data
claims_df = pd.read_csv('data/claims_lifecycle_ifrs_synthetic.csv')

# Load policy clauses
with open('data/policy_clauses_snippets.txt', 'r') as f:
    clauses = f.read()
```

## ⚠️ Disclaimer

This project models generic insurance concepts common in GCC markets. All datasets are synthetic and made-up for demonstration and research purposes. No proprietary pricing, underwriting rules, policy wording, or confidential logic was used. Outputs are illustrative only and require human review. Not to be used for any pricing, reserving, claim approval, or policy issuance.

## Human-In-The-Loop

No AI component here issues approvals, denials, or financial outcomes. All outputs require human verification and decision-making.

## ⚠️ Compliance & Safety

- ✅ **100% Synthetic Data**: All data is artificially generated
- ✅ **No Real Information**: No actual insurance policies or personal data
- ✅ **No Real Insurers**: No real insurance company names used
- ✅ **No Actuarial Formulas**: No proprietary pricing or risk models
- ✅ **Advisory Only**: All outputs are for demonstration purposes
- ✅ **No KYC Fields**: No sensitive personal identification data

## 🎯 Use Cases

- **AI/ML Model Training**: Train fraud detection or claims prediction models
- **System Testing**: Test insurance claims processing systems
- **Educational Projects**: Learn about insurance data structures
- **Prototype Development**: Build insurance tech prototypes
- **Data Analysis Practice**: Practice data analysis on realistic datasets

## 📝 License

MIT License - Free to use for any purpose

## 🔗 Related Repositories

Check out other insurance AI tools:
- fraud-triage-sandbox
- ifrs-claim-accrual-estimator
- doc-rag-compliance-assistant

## Technical Details

- **Format**: CSV files
- **License**: MIT
- **Data Source**: Fully synthetic, programmatically generated
- **Size**: Sample datasets (200+ records for CSV files, 12 clauses for text file)
- **Purpose**: Educational and testing only

---

**Built by Qoder for Vercept**
