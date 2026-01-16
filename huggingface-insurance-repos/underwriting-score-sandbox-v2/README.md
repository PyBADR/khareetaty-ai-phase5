---
title: Underwriting Score Sandbox
emoji: 🏢
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# Underwriting Score Sandbox

**Educational Underwriting Risk Assessment System**

## Overview

An interactive demonstration of rule-based underwriting risk scoring for insurance applicants. This sandbox calculates risk bands (Low/Medium/High) based on industry segment, applicant risk profile, and prior claim history using transparent, explainable logic.

## Purpose

This tool demonstrates:
- Rule-based underwriting risk assessment
- Transparent scoring calculations
- Risk band classification
- Factor breakdown for auditability
- Human-in-the-loop enforcement

## Features

- **Rule-Based Scoring**: Transparent logic with no ML
- **Risk Band Classification**: Low / Medium / High categories
- **Factor Breakdown**: JSON output for audit trails
- **Explainable Results**: Clear explanation of calculations
- **Mandatory Review**: Underwriter approval required for all assessments

## Inputs

1. **Industry Segment** (dropdown)
   - Technology, Retail, Healthcare, Manufacturing, Construction

2. **Applicant Risk Profile** (dropdown)
   - Low, Medium, High

3. **Prior Claim Count** (slider)
   - 0-10 insurance claims in past 5 years

## Scoring Logic

### Formula
```
Aggregate Score = Industry Factor + History Factor + Profile Bias
```

### Factor Definitions

**Industry Risk Factors:**
- Technology: 0.8
- Retail: 1.0
- Manufacturing: 1.2
- Healthcare: 1.3
- Construction: 1.5

**History Factor:**
- Calculation: Prior Claim Count × 0.15

**Profile Bias:**
- Low: 0.0
- Medium: 1.0
- High: 2.0

### Risk Band Thresholds
- **Low**: < 1.5
- **Medium**: 1.5 - 3.0
- **High**: > 3.0

## Outputs

- **Risk Band**: Low / Medium / High with color indicators
- **Aggregate Score**: Numerical risk score
- **Factor Breakdown**: JSON with all calculation components
- **Detailed Explanation**: Step-by-step scoring breakdown
- **Underwriter Review Required**: Mandatory human review notice

## Data Sources

- **100% Synthetic**: All data and scenarios are fabricated
- **No Real Data**: No connection to actual insurance operations
- **Educational Only**: For demonstration and training purposes

## Technical Details

- **Framework**: Gradio 4.44.0
- **Language**: Python 3.9+
- **Logic**: Pure rule-based (no ML)
- **Dependencies**: gradio

## Usage

```bash
pip install -r requirements.txt
python3 app.py
```

## ⚠️ CRITICAL DISCLAIMER

**This application demonstrates fictional insurance logic using synthetic data only.**

### NOT Intended For:
- ❌ Real underwriting decisions
- ❌ Premium pricing or calculation
- ❌ Policy binding or issuance
- ❌ Actual risk assessment
- ❌ Production insurance operations

### Intended For:
- ✅ Educational training
- ✅ Logic demonstration
- ✅ Workflow prototyping
- ✅ Concept validation

**All outputs are advisory only and require qualified underwriter review. Human-in-the-loop is mandatory for all insurance decisions.**

## Governance & Safety

- ✅ No automated decisions
- ✅ Transparent logic
- ✅ Explainable factors
- ✅ JSON audit trails
- ✅ Mandatory human review
- ✅ Clear disclaimers

## Limitations

- Educational demonstration only
- Synthetic logic with no real-world validation
- Simplified scoring model
- No integration with actual systems
- Not suitable for production use

## License

MIT License - Educational Use Only

---

**Built for GCC Insurance Intelligence Lab**

This tool is not approved for actual underwriting decisions, premium pricing, or policy issuance. All outputs require human review and validation by qualified insurance underwriters.
