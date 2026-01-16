# Model Card: FNOL Fast Track Screener

## Model Details

### Description

This is a **rule-based FNOL (First Notice of Loss) screening system** that recommends routing decisions for insurance claims. The system evaluates claim source, loss severity, and incident category to suggest appropriate handling channels with uncertainty quantification.

- **Developed by:** GCC Insurance Intelligence Lab
- **Model Type:** Rule-based screening engine
- **Version:** 1.0
- **Framework:** Pure Python logic (no ML)
- **License:** MIT (Educational Use Only)

## Intended Use

### Primary Use Cases

✅ **Educational Training**: Teaching FNOL screening concepts  
✅ **Logic Demonstration**: Showing automated routing logic  
✅ **Workflow Prototyping**: Testing claims handling processes  
✅ **Process Validation**: Demonstrating claim routing systems  

### Out-of-Scope Use

❌ **Actual Routing**: Not for real claim routing decisions  
❌ **Claims Processing**: Not for actual claims handling  
❌ **Resource Allocation**: Not for assigning staff/resources  
❌ **Production Systems**: Not validated for live operations  

## Training Data

**N/A** - This is a rule-based system with no training data. The screening logic is defined by explicit rules, not learned from data.

### Synthetic Data Context

- 100% fabricated scenarios
- No real insurance data used
- Educational examples only
- No connection to actual operations

## Factors & Metrics

### Input Factors

1. **Claim Source**
   - Call Center: Fast Track eligible
   - App: Fast Track eligible
   - Web: Standard routing
   - Agent: Standard routing
   - Email: Manual review

2. **Loss Severity**
   - Range: 1 (Minor) - 5 (Catastrophic)
   - 1-2: Fast Track eligible
   - 3: Standard Review
   - 4-5: Escalation required

3. **Incident Category**
   - Standard: Auto Collision, Property
   - Sensitive: Fire, Theft, Water Damage
   - Complex: Liability

### Routing Logic

**Fast Track (🟢):**
- Loss severity ≤ 2 AND verified source
- Expected resolution: 3-5 business days

**Standard Review (🟡):**
- Loss severity = 3 OR sensitive category
- Expected resolution: 7-14 business days

**Escalation (🔴):**
- Loss severity ≥ 4 OR complex category
- Expected resolution: 14-30 business days

### Uncertainty Calculation

- Base uncertainty based on claim complexity
- Random variation ±0.1 for demonstration
- Higher uncertainty = more manual review needed

## Ethical Considerations

### Bias & Fairness

⚠️ **Source Bias**: Different claim sources receive different routing treatment  
⚠️ **Severity Subjectivity**: Severity ratings may be inconsistent  
⚠️ **Category Simplification**: Complex incidents reduced to simple categories  

### Mitigation Strategies

✅ **Transparency**: All routing logic is explicit and auditable  
✅ **Explainability**: Clear reasoning provided for all decisions  
✅ **Human Review**: Mandatory validation by claims professionals  
✅ **No Automation**: No automated routing or processing  

## Limitations

### Known Limitations

1. **Simplified Model**: Real claims involve many more factors
2. **No ML**: Cannot learn or adapt from new data
3. **Static Rules**: Fixed routing logic that doesn't evolve
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
- **Never Use in Production**: Not suitable for real claims routing
- **Require Human Review**: Always involve qualified claims professionals
- **Consider Context**: Rules don't replace professional judgment
- **Document Decisions**: Maintain audit trail of all routing decisions

### For Organizations

- Consult with claims professionals before any real-world application
- Ensure compliance with local insurance regulations
- Implement proper governance and oversight
- Validate against actual claims handling standards
- Consider fairness and bias implications

## Governance

### Mandatory Requirements

🚨 **Human-in-the-Loop**: Every routing decision must be validated by a qualified claims professional  
🚨 **No Automation**: System provides advisory output only  
🚨 **Audit Trail**: All decisions logged with reasoning  
🚨 **Clear Disclaimers**: Users must acknowledge educational-only status  

### Compliance Notes

- Not approved by any insurance regulatory body
- No validation against actual claims handling standards
- No guarantee of accuracy or reliability
- Organizations responsible for compliance if adapted
- Professional claims standards must be maintained

## Technical Specifications

### Architecture

**Type**: Rule-based screening engine  
**Components**:
- Input validation
- Routing logic
- Uncertainty calculation
- Document checklist generation
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

This tool demonstrates fictional FNOL screening logic using synthetic data only. No outputs shall be used for actual claim routing, processing, handling, or resource allocation decisions. All data and scenarios are fabricated for educational purposes.

**Human-in-the-loop is mandatory for all claims decisions.**

Organizations using this tool must:
- Comply with all applicable laws and regulations
- Implement appropriate governance and oversight
- Maintain professional claims handling standards
- Document all decisions with qualified claims professional approval
- Never rely on this system for actual claims routing authority

## Contact

For questions or feedback about this educational tool, contact the GCC Insurance Intelligence Lab.

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Status**: Educational Demonstration
