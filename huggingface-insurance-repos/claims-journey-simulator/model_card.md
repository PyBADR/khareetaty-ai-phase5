# Model Card: Claims Journey Simulator

## Model Details

### Description

This is a **rule-based claims lifecycle simulation system** that estimates duration for each stage of the insurance claims process. The system simulates the journey from FNOL through Payment based on claim severity and document completeness.

- **Developed by:** GCC Insurance Intelligence Lab
- **Model Type:** Rule-based simulation engine
- **Version:** 1.0
- **Framework:** Pure Python logic (no ML)
- **License:** MIT (Educational Use Only)

## Intended Use

### Primary Use Cases

✅ **Educational Training**: Teaching claims lifecycle concepts  
✅ **Process Demonstration**: Showing claims handling stages  
✅ **Workflow Prototyping**: Testing claims process designs  
✅ **Timeline Estimation**: Demonstrating duration factors  

### Out-of-Scope Use

❌ **Actual Processing**: Not for real claims processing  
❌ **Timing Decisions**: Not for actual timeline commitments  
❌ **Resource Allocation**: Not for staffing or scheduling  
❌ **Production Systems**: Not validated for live operations  

## Training Data

**N/A** - This is a rule-based system with no training data. The simulation logic is defined by explicit rules, not learned from data.

### Synthetic Data Context

- 100% fabricated scenarios
- No real insurance data used
- Educational examples only
- No connection to actual operations

## Factors & Metrics

### Input Factors

1. **Claim Severity**
   - Low: Minimal investigation required
   - Medium: Standard investigation procedures
   - High: Comprehensive investigation and review

2. **Document Completeness**
   - Range: 0-100% of required documents
   - ≥80%: Standard processing (1.0x factor)
   - 50-79%: Moderate delays (1.5x factor)
   - <50%: Significant delays (2.5x factor)

### Simulation Logic

**Base Stage Durations by Severity:**

Low Severity:
- FNOL: 1 day
- Assignment: 1 day
- Investigation: 2 days
- Decision: 2 days
- Payment: 2 days

Medium Severity:
- FNOL: 2 days
- Assignment: 2 days
- Investigation: 5 days
- Decision: 3 days
- Payment: 3 days

High Severity:
- FNOL: 3 days
- Assignment: 3 days
- Investigation: 10 days
- Decision: 5 days
- Payment: 5 days

### Duration Calculation

- Base days adjusted by document completeness factor
- ±20% random variation added for realism
- Minimum 1 day per stage enforced

### Bottleneck Identification

- Stages requiring >5 days flagged as potential bottlenecks
- High severity claims more likely to have bottlenecks
- Incomplete documentation increases bottleneck risk

## Ethical Considerations

### Bias & Fairness

⚠️ **Severity Simplification**: Complex claims reduced to simple categories  
⚠️ **Document Threshold**: Arbitrary 80% threshold may not reflect reality  
⚠️ **Time Estimation**: Estimates may not match real-world processing times  

### Mitigation Strategies

✅ **Transparency**: All calculation logic is explicit and auditable  
✅ **Explainability**: Clear reasoning provided for all estimates  
✅ **Human Review**: All claims require adjuster involvement  
✅ **No Automation**: No automated processing or timing commitments  

## Limitations

### Known Limitations

1. **Simplified Model**: Real claims involve many more variables
2. **No ML**: Cannot learn or adapt from new data
3. **Static Rules**: Fixed logic that doesn't evolve
4. **No Context**: Cannot consider unique circumstances
5. **Educational Only**: Not validated against real-world outcomes

### Technical Constraints

- No integration with actual claims systems
- No access to external data sources
- No claim verification or validation
- No regulatory compliance checks
- No fraud detection integration

## Recommendations

### For Users

- **Understand Limitations**: This is a demonstration tool only
- **Never Use in Production**: Not suitable for real claims processing
- **Require Human Management**: Always involve qualified adjusters
- **Consider Context**: Rules don't replace professional judgment
- **Document Processes**: Maintain audit trail of all estimations

### For Organizations

- Consult with claims professionals before any real-world application
- Ensure compliance with local insurance regulations
- Implement proper governance and oversight
- Validate against actual claims handling standards
- Consider fairness and bias implications

## Governance

### Mandatory Requirements

🚨 **Human-in-the-Loop**: Every claim requires active adjuster management  
🚨 **No Automation**: System provides advisory estimates only  
🚨 **No Timing Commitments**: Estimates are not guarantees  
🚨 **Clear Disclaimers**: Users must acknowledge educational-only status  

### Compliance Notes

- Not approved by any insurance regulatory body
- No validation against actual claims processing times
- No guarantee of accuracy or reliability
- Organizations responsible for compliance if adapted
- Professional claims standards must be maintained

## Technical Specifications

### Architecture

**Type**: Rule-based simulation engine  
**Components**:
- Input validation
- Duration calculation
- Bottleneck identification
- Touchpoint tracking
- Explanation generation

### Compute Requirements

- Minimal: Runs on CPU
- No GPU required
- No external API calls
- Local execution only

### Dependencies

```
gradio==4.44.0
pandas==2.1.4
```

## Disclaimer

⚠️ **CRITICAL NOTICE**

This tool demonstrates fictional claims lifecycle using synthetic data only. No outputs shall be used for actual claims processing, timing, resource allocation, or policyholder communication. All data and scenarios are fabricated for educational purposes.

**Human adjuster involvement is mandatory at all stages.**

Organizations using this tool must:
- Comply with all applicable laws and regulations
- Implement appropriate governance and oversight
- Maintain professional claims handling standards
- Document all processes with qualified adjuster involvement
- Never rely on this system for actual claims processing authority

## Contact

For questions or feedback about this educational tool, contact the GCC Insurance Intelligence Lab.

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Status**: Educational Demonstration
