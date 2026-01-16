# Model Card: Underwriting Score Sandbox

## Model Details

### Description

This is a **rule-based underwriting risk assessment system** that calculates risk scores for insurance applicants using transparent, explainable logic. The system is purely algorithmic with no machine learning components.

- **Developed by:** GCC Insurance Intelligence Lab
- **Model Type:** Rule-based scoring engine
- **Version:** 1.0
- **Framework:** Pure Python logic (no ML)
- **License:** MIT (Educational Use Only)

## Intended Use

### Primary Use Cases

✅ **Educational Training**: Teaching underwriting risk assessment concepts  
✅ **Logic Demonstration**: Showcasing transparent scoring calculations  
✅ **Workflow Prototyping**: Testing underwriting process designs  
✅ **Concept Validation**: Demonstrating risk band classification  

### Out-of-Scope Use

❌ **Real Underwriting**: Not for actual insurance underwriting decisions  
❌ **Premium Pricing**: Not for calculating actual premiums  
❌ **Policy Binding**: Not for issuing or binding insurance policies  
❌ **Production Systems**: Not validated for real-world operations  

## Training Data

**N/A** - This is a rule-based system with no training data. The scoring logic is defined by explicit rules, not learned from data.

### Synthetic Data Context

- 100% fabricated scenarios
- No real insurance data used
- Educational examples only
- No connection to actual operations

## Factors & Metrics

### Input Factors

1. **Industry Segment**
   - Technology: 0.8 (lowest risk)
   - Retail: 1.0
   - Manufacturing: 1.2
   - Healthcare: 1.3
   - Construction: 1.5 (highest risk)

2. **Prior Claim Count**
   - Range: 0-10 claims
   - Multiplier: 0.15 per claim
   - Formula: claims × 0.15

3. **Applicant Risk Profile**
   - Low: 0.0 (no bias)
   - Medium: 1.0
   - High: 2.0

### Scoring Formula

```
Aggregate Score = Industry Factor + History Factor + Profile Bias
```

### Risk Band Classification

- **Low**: Aggregate Score < 1.5
- **Medium**: Aggregate Score 1.5 - 3.0
- **High**: Aggregate Score > 3.0

### Example Calculations

**Case 1: Low Risk**
- Industry: Technology (0.8)
- Claims: 0 (0.0)
- Profile: Low (0.0)
- **Score**: 0.8 → Low Risk

**Case 2: Medium Risk**
- Industry: Retail (1.0)
- Claims: 3 (0.45)
- Profile: Medium (1.0)
- **Score**: 2.45 → Medium Risk

**Case 3: High Risk**
- Industry: Construction (1.5)
- Claims: 5 (0.75)
- Profile: High (2.0)
- **Score**: 4.25 → High Risk

## Ethical Considerations

### Bias & Fairness

⚠️ **Industry Bias**: Different industries receive different risk scores based on predefined factors. This is a simplification and may not reflect real-world risk distributions.

⚠️ **Historical Claims Bias**: Applicants with more claims receive higher risk scores, which could disadvantage those with legitimate claim histories.

⚠️ **Profile Subjectivity**: Initial risk profile assessment could introduce subjective bias.

### Mitigation Strategies

✅ **Transparency**: All scoring logic is explicit and auditable  
✅ **Explainability**: Factor breakdown provided for every assessment  
✅ **Human Review**: Mandatory underwriter review for all decisions  
✅ **No Automation**: No automated approvals or denials  

## Limitations

### Known Limitations

1. **Simplified Model**: Real underwriting involves many more factors
2. **No ML**: Cannot learn or adapt from new data
3. **Static Rules**: Fixed scoring logic that doesn't evolve
4. **No Context**: Cannot consider unique circumstances or nuances
5. **Educational Only**: Not validated against real-world outcomes

### Technical Constraints

- No integration with actual underwriting systems
- No access to external data sources
- No claim verification or validation
- No regulatory compliance checks
- No actuarial foundation

## Recommendations

### For Users

- **Understand Limitations**: This is a demonstration tool only
- **Never Use in Production**: Not suitable for real underwriting
- **Require Human Review**: Always involve qualified underwriters
- **Consider Context**: Rules don't replace professional judgment
- **Document Decisions**: Maintain audit trail of all assessments

### For Organizations

- Consult with actuaries and underwriters before any real-world application
- Ensure compliance with local insurance regulations
- Implement proper governance and oversight
- Validate against actual underwriting standards
- Consider fairness and bias implications

## Governance

### Mandatory Requirements

🚨 **Human-in-the-Loop**: Every assessment must be reviewed by a qualified underwriter  
🚨 **No Automation**: System provides advisory output only  
🚨 **Audit Trail**: All calculations logged in JSON format  
🚨 **Clear Disclaimers**: Users must acknowledge educational-only status  

### Compliance Notes

- Not approved by any insurance regulatory body
- No actuarial validation or certification
- No guarantee of accuracy or reliability
- Organizations responsible for compliance if adapted
- Professional underwriting standards must be maintained

## Technical Specifications

### Architecture

**Type**: Rule-based scoring engine  
**Components**:
- Input validation
- Factor calculation
- Score aggregation
- Risk band classification
- Explanation generation

### Compute Requirements

- Minimal: Runs on CPU
- No GPU required
- No external API calls
- Local execution only

### Dependencies

```
gradio==4.44.0
```

## Disclaimer

⚠️ **CRITICAL NOTICE**

This tool demonstrates fictional insurance logic using synthetic data only. No outputs shall be used for actual underwriting, pricing, reserving, claim approval, or policy issuance. All data and scenarios are fabricated for educational purposes.

**Human-in-the-loop is mandatory for all insurance decisions.**

Organizations using this tool must:
- Comply with all applicable laws and regulations
- Implement appropriate governance and oversight
- Maintain professional underwriting standards
- Document all decisions with qualified underwriter approval
- Never rely on this system for actual underwriting authority

## Contact

For questions or feedback about this educational tool, contact the GCC Insurance Intelligence Lab.

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Status**: Educational Demonstration
