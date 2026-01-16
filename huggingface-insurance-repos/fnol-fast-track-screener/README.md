---
title: FNOL Fast Track Screener
emoji: 📋
colorFrom: orange
colorTo: red
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# FNOL Fast Track Screener

**First Notice of Loss Screening System**

## Overview

An interactive demonstration of automated FNOL (First Notice of Loss) screening for routing claims to appropriate handling channels. The system evaluates claim source, loss severity, and incident category to recommend routing decisions with uncertainty quantification.

## Purpose

This tool demonstrates:
- Automated FNOL screening logic
- Claim routing recommendations
- Uncertainty quantification
- Document checklist generation
- Human validation requirements

## Features

- **Routing Recommendations**: Fast Track / Standard / Escalation
- **Uncertainty Scoring**: Confidence measure for each decision
- **Document Checklist**: Required documents based on incident type
- **Explainable Logic**: Clear reasoning for routing decisions
- **Human Validation**: Mandatory review for all routing decisions

## Inputs

1. **Claim Source** (dropdown)
   - Call Center, App, Web, Agent, Email

2. **Loss Severity** (slider)
   - 1 (Minor) to 5 (Catastrophic)

3. **Incident Category** (dropdown)
   - Auto Collision, Auto Theft, Property, Fire, Water Damage, Theft, Liability

## Routing Logic

### Fast Track (🟢)
- Loss severity ≤ 2
- Verified source (App/Call Center)
- Standard incident categories
- Expected resolution: 3-5 business days

### Standard Review (🟡)
- Loss severity = 3
- Sensitive incident categories
- Web/Agent submissions
- Expected resolution: 7-14 business days

### Escalation (🔴)
- Loss severity ≥ 4
- High-value claims
- Complex incidents
- Expected resolution: 14-30 business days

## Uncertainty Scoring

- Base uncertainty based on claim complexity
- Random variation for demonstration
- Higher uncertainty = more manual review needed

## Outputs

- **Routing Recommendation**: Fast Track / Standard Review / Escalation
- **Uncertainty Score**: 0.00 - 1.00
- **Required Documents Checklist**: Tailored to incident type
- **Detailed Explanation**: Reasoning for routing decision
- **Human Validation Required**: Mandatory review notice

## Data Sources

- **100% Synthetic**: All scenarios are fabricated
- **No Real Data**: No connection to actual claims
- **Educational Only**: For demonstration and training purposes

## Technical Details

- **Framework**: Gradio 4.44.0
- **Language**: Python 3.9+
- **Logic**: Rule-based screening
- **Dependencies**: gradio

## Usage

```bash
pip install -r requirements.txt
python3 app.py
```

## ⚠️ CRITICAL DISCLAIMER

**This application demonstrates fictional FNOL screening logic using synthetic data only.**

### NOT Intended For:
- ❌ Actual claim routing or processing
- ❌ Claims handling decisions
- ❌ Resource allocation
- ❌ Production claims operations
- ❌ Automated approval or denial

### Intended For:
- ✅ Educational training
- ✅ Logic demonstration
- ✅ Workflow prototyping
- ✅ Process validation

**All routing decisions require validation by qualified claims professionals. Human-in-the-loop is mandatory for all claims decisions.**

## Governance & Safety

- ✅ No automated routing
- ✅ Transparent logic
- ✅ Uncertainty quantification
- ✅ Mandatory human review
- ✅ Clear disclaimers

## Limitations

- Educational demonstration only
- Synthetic logic with no real-world validation
- Simplified routing model
- No integration with actual systems
- Not suitable for production use

## License

MIT License - Educational Use Only

---

**Built for GCC Insurance Intelligence Lab**

This tool is not approved for actual FNOL routing, claims processing, or resource allocation. All decisions require validation by qualified claims professionals.
