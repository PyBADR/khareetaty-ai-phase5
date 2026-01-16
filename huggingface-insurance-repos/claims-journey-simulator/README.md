---
title: Claims Journey Simulator
emoji: 🛣️
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# Claims Journey Simulator

**Generic Insurance Claims Lifecycle Simulator**

## Overview

An interactive demonstration of generic insurance claims lifecycle simulation. The system estimates duration for each stage of the claims process (FNOL → Assignment → Investigation → Decision → Payment) based on claim severity and document completeness.

## Purpose

This tool demonstrates:
- Generic claims lifecycle stages
- Duration estimation based on factors
- Bottleneck identification
- Adjuster touchpoint requirements
- Human involvement necessity

## Features

- **Lifecycle Simulation**: FNOL → Assignment → Investigation → Decision → Payment
- **Duration Estimation**: Estimated days per stage and total
- **Bottleneck Identification**: Potential delay points
- **Touchpoint Tracking**: Required adjuster actions
- **Explainable Logic**: Clear reasoning for estimates

## Inputs

1. **Claim Severity** (radio buttons)
   - Low, Medium, High

2. **Document Completeness** (slider)
   - 0% - 100% of required documents submitted

## Simulation Logic

### Stage Durations by Severity

**Low Severity:**
- FNOL: 1 day base
- Assignment: 1 day base
- Investigation: 2 days base
- Decision: 2 days base
- Payment: 2 days base

**Medium Severity:**
- FNOL: 2 days base
- Assignment: 2 days base
- Investigation: 5 days base
- Decision: 3 days base
- Payment: 3 days base

**High Severity:**
- FNOL: 3 days base
- Assignment: 3 days base
- Investigation: 10 days base
- Decision: 5 days base
- Payment: 5 days base

### Document Completeness Adjustment

- ≥80%: Standard processing (1.0x factor)
- 50-79%: Moderate delays (1.5x factor)
- <50%: Significant delays (2.5x factor)

### Random Variation

- ±20% random variation applied to simulate real-world uncertainty

## Outputs

- **Stage Timeline Table**: Days per stage with adjustments
- **Estimated Total Duration**: Sum of all stage days
- **Potential Bottlenecks**: Stages with significant delays
- **Required Touchpoints**: Adjuster actions needed
- **Detailed Analysis**: Explanation of factors affecting timeline

## Data Sources

- **100% Synthetic**: All scenarios are fabricated
- **No Real Data**: No connection to actual claims
- **Educational Only**: For demonstration and training purposes

## Technical Details

- **Framework**: Gradio 4.44.0
- **Language**: Python 3.9+
- **Logic**: Rule-based simulation
- **Dependencies**: gradio, pandas

## Usage

```bash
pip install -r requirements.txt
python3 app.py
```

## ⚠️ CRITICAL DISCLAIMER

**This application demonstrates fictional claims lifecycle using synthetic data only.**

### NOT Intended For:
- ❌ Actual claims processing or timing
- ❌ Resource allocation or scheduling
- ❌ Policyholder communication
- ❌ Production claims operations
- ❌ Automated claims handling

### Intended For:
- ✅ Educational training
- ✅ Process demonstration
- ✅ Workflow prototyping
- ✅ Timeline estimation concepts

**All claims require active adjuster management and cannot be automated. Human adjuster involvement is mandatory at all stages.**

## Governance & Safety

- ✅ No automated processing
- ✅ Transparent logic
- ✅ Human involvement requirement
- ✅ Clear disclaimers
- ✅ Mandatory adjuster action tracking

## Limitations

- Educational demonstration only
- Synthetic logic with no real-world validation
- Simplified lifecycle model
- No integration with actual systems
- Not suitable for production use

## License

MIT License - Educational Use Only

---

**Built for GCC Insurance Intelligence Lab**

This tool is not approved for actual claims processing, timing, or resource allocation. All claims require active adjuster management.
