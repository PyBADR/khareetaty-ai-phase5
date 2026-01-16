# Model Card: Insurance Synthetic Datasets

## Model Details

**Model Type:** Dataset Repository  
**Version:** 1.0  
**Date:** January 2026  
**License:** MIT  

## Intended Use

### Primary Use Cases
- Training and testing insurance AI/ML models
- Developing claims processing systems
- Educational purposes for insurance data science
- Prototyping insurance technology solutions
- Fraud detection algorithm development

### Out-of-Scope Uses
- Real insurance underwriting or pricing
- Actual claims processing or settlement
- Production insurance operations
- Any use requiring real customer data

## Dataset Composition

### Fraud Cases Synthetic
- **Size:** 250 synthetic records
- **Features:** 6 columns including policy type, risk profiles, and fraud labels
- **Coverage:** Fraud detection training data for insurance claims triage
- **File:** `data/fraud_cases_synthetic.csv`

### Claims Lifecycle IFRS Synthetic
- **Size:** 251 synthetic records
- **Features:** 6 columns including claim stages, severity, IBNR flags, and accrual factors
- **Coverage:** IFRS 17 compliant claims lifecycle and accrual estimation data
- **File:** `data/claims_lifecycle_ifrs_synthetic.csv`

### Policy Clauses Snippets
- **Size:** 12 fabricated paragraphs
- **Content:** Synthetic policy clause text for compliance and RAG testing
- **Coverage:** Various insurance policy topics (no real-world product text)
- **File:** `data/policy_clauses_snippets.txt`

## Data Generation Process

All data in this repository is **100% synthetically generated** using the following principles:

1. **Realistic Patterns:** Data follows realistic insurance industry patterns
2. **No Real Data:** No actual insurance policies or claims were used
3. **Privacy-Safe:** No real personal information included
4. **Diverse Scenarios:** Covers multiple claim types and risk levels
5. **Balanced Distribution:** Mix of settled/pending claims, various severities

## Limitations

- **Sample Size:** 200+ records per CSV dataset (for demonstration and testing)
- **Simplified Schema:** Real insurance data has more complex relationships
- **No Temporal Patterns:** Does not model seasonal or trend effects
- **Limited Geography:** No geographic or regional variations
- **Simplified Risk Models:** Risk scores are illustrative, not actuarially sound

## Ethical Considerations

### Privacy
- ✅ No real personal data
- ✅ All names are synthetic
- ✅ No actual policy numbers or claims

### Bias
- Dataset is intentionally simplified and may not reflect real-world distributions
- Age and risk distributions are illustrative only
- Should not be used to train production models without validation

### Compliance
- ✅ No real insurer names or proprietary information
- ✅ No actuarial formulas or pricing models
- ✅ No KYC or sensitive personal fields
- ✅ All outputs marked as advisory only

## Recommendations

### For Developers
- Use this dataset for prototyping and testing only
- Validate any models with real data before production use
- Understand the limitations of synthetic data

### For Researchers
- Good for educational purposes and concept validation
- Not suitable for academic research requiring real-world data
- Can be used to demonstrate data structures and workflows

### For Students
- Excellent for learning insurance data analysis
- Safe to use without privacy concerns
- Good for practicing data manipulation and visualization

## Technical Specifications

**Format:** CSV  
**Encoding:** UTF-8  
**Delimiter:** Comma  
**Missing Values:** None  
**Data Types:** Mixed (strings, floats, dates)  

## Contact & Support

For questions or issues, please open an issue in the repository.

## Changelog

### Version 1.0 (January 2026)
- Initial release
- 3 synthetic datasets (fraud cases, IFRS claims lifecycle, policy clauses)
- Interactive Gradio explorer app
- Complete documentation with mandatory disclaimers
