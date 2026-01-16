# Underwriting Score Sandbox

**Educational Underwriting Risk Assessment System**

## Overview

An interactive demonstration of rule-based underwriting risk scoring for insurance applicants. This sandbox calculates risk bands (Low/Medium/High) based on industry segment, applicant profile, and prior claim history.

## ⚠️ MANDATORY DISCLAIMER

**This application demonstrates fictional insurance logic using synthetic data only.**

- ✅ Educational and demonstration purposes only
- ✅ No outputs shall be used for real underwriting, pricing, or policy decisions
- ✅ All data is 100% synthetic and fabricated
- ✅ Underwriter review is MANDATORY for all assessments
- ✅ No real pricing, quoting, reserving, or binding occurs
- ✅ Human-in-the-loop required for all decisions

## Features

- **Rule-Based Scoring**: Transparent logic with weighted factors
- **Risk Band Classification**: Low / Medium / High risk categories
- **Factor Breakdown**: Detailed JSON output of scoring components
- **Explainable Results**: Clear explanation of risk assessment
- **Synthetic Data**: 200 fabricated risk profiles for reference

## Inputs

1. **Industry Segment** (dropdown)
   - Technology, Professional Services, Education, Retail, Healthcare, Hospitality, Manufacturing, Transportation, Construction
   
2. **Applicant Risk Profile** (radio)
   - Low, Medium, High

3. **Prior Claim Count** (slider)
   - 0-10 insurance claims in past 5 years

## Outputs

- **Risk Band**: Low / Medium / High
- **Aggregate Score**: 0.000 - 1.000
- **Factor Breakdown**: JSON with individual risk factors
- **Explanation**: Detailed risk assessment with recommendations
- **Underwriter Review Required**: Always true (mandatory)

## Scoring Logic

### Factor Weights
- Industry Segment: 40%
- Claim History: 35%
- Applicant Profile: 25%

### Risk Band Thresholds
- **Low**: 0.00 - 0.29
- **Medium**: 0.30 - 0.59
- **High**: 0.60 - 1.00

## Technical Details

- **Framework**: Gradio 4.44.0
- **Logic**: Rule-based scoring engine
- **Data**: 200 synthetic risk profiles (CSV)
- **Files**:
  - `app.py` - Gradio interface
  - `underwriting_rules.py` - Scoring logic
  - `risk_profiles_synthetic.csv` - Synthetic data
  - `requirements.txt` - Dependencies

## Usage

```bash
pip install -r requirements.txt
python3 app.py
```

## Governance & Safety

- ✅ No machine learning or predictive models
- ✅ Transparent rule-based logic
- ✅ Explainable scoring factors
- ✅ Mandatory underwriter review
- ✅ No automated underwriting decisions
- ✅ Advisory output only

## Use Cases

- Training insurance professionals
- Demonstrating underwriting concepts
- Prototyping risk assessment workflows
- Educational sandbox for GCC insurance markets

## Limitations

- Educational demonstration only
- Synthetic data with no real-world validation
- Simplified scoring model
- No integration with actual underwriting systems
- Not suitable for production use
- No real premium calculation or policy binding

## License

MIT License - Educational Use Only

---

**Built for GCC Insurance Intelligence Lab**

**Note**: This tool is not approved for actual underwriting decisions, premium pricing, or policy issuance. All outputs require human review and validation by qualified insurance underwriters.
