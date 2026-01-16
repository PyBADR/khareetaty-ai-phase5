# Model Card: Underwriting Score Sandbox

## Model Details

### Description

This is a **rule-based underwriting risk assessment system** that calculates risk bands for insurance applicants. The system evaluates industry segment, applicant risk profile, and prior claim history to assign risk classifications with transparent factor breakdowns.

- **Developed by:** GCC Insurance Intelligence Lab
- **Model Type:** Rule-based scoring engine
- **Version:** 1.0
- **Framework:** Pure Python logic (no ML)
- **License:** MIT (Educational Use Only)

## Intended Use

### Primary Use Cases

✅ **Educational Training**: Teaching underwriting risk assessment concepts  
✅ **Logic Demonstration**: Showing rule-based scoring methodology  
✅ **Workflow Prototyping**: Testing underwriting processes  
✅ **Process Validation**: Demonstrating risk classification systems  

### Out-of-Scope Use

❌ **Actual Underwriting**: Not for real underwriting decisions  
❌ **Premium Pricing**: Not for calculating actual premiums  
❌ **Policy Issuance**: Not for binding coverage  
❌ **Production Systems**: Not validated for live operations  

## Training Data

**N/A** - This is a rule-based system with no training data. The scoring logic is defined by explicit rules, not learned from data.

### Synthetic Data Context

- 200 fabricated risk profiles (risk_profiles_synthetic.csv)
- No real insurance data used
- Educational examples only
- No connection to actual applicants or policies

## Factors & Metrics

### Input Factors

1. **Industry Segment**
   - Technology: Lower risk (0.8x multiplier)
   - Professional Services: Lower risk (0.9x)
   - Retail: Standard risk (1.0x)
   - Healthcare: Standard risk (1.0x)
   - Hospitality: Moderate risk (1.1x)
   - Manufacturing: Higher risk (1.3x)
   - Construction: Higher risk (1.4x)

2. **Applicant Risk Profile**
   - Low: Base score adjustment -10
   - Medium: Base score adjustment 0
   - High: Base score adjustment +15

3. **Prior Claim Count**
   - 0 claims: No penalty
   - 1-2 claims: +5 points per claim
   - 3-5 claims: +8 points per claim
   - 6+ claims: +12 points per claim

### Scoring Logic

**Aggregate Score Calculation:**
```
aggregate_score = (industry_factor × 100) + applicant_adjustment + (claim_count × claim_penalty)
```

**Risk Band Assignment:**
- **Low Risk (🟢):** aggregate_score < 100
- **Medium Risk (🟡):** 100 ≤ aggregate_score < 130
- **High Risk (🔴):** aggregate_score ≥ 130

### Output Components

1. **Risk Band**: Low / Medium / High classification
2. **Aggregate Score**: Numerical score (0-200+ range)
3. **Factor Breakdown**: JSON with individual component scores
4. **Underwriter Review Warning**: Mandatory human validation message

## Ethical Considerations

### Bias & Fairness

⚠️ **Industry Bias**: This system applies different risk factors to different industries. In real-world applications, such factors must be:
- Actuarially justified
- Regularly validated
- Compliant with anti-discrimination laws
- Transparent to applicants

⚠️ **Prior Claims Penalty**: Heavy weighting on claim history may disadvantage applicants unfairly. Real systems must consider:
- Claim circumstances
- Time since claims
- Claim severity vs. frequency
- Industry norms

### Transparency

✅ **Explainable**: All scoring factors are transparent and documented  
✅ **Auditable**: Factor breakdown provided for every assessment  
✅ **Human Review**: Mandatory underwriter validation required  

## Limitations

1. **Simplified Logic**: Real underwriting involves 50+ factors
2. **No Context**: Doesn't consider business size, revenue, location, etc.
3. **Static Rules**: No adaptation to changing risk landscapes
4. **No Validation**: Not validated against actual loss data
5. **Educational Only**: Not suitable for production use

## Governance

### Human-in-the-Loop

🔴 **MANDATORY**: All risk assessments require human underwriter review and approval. This system provides decision support only, not final decisions.

### Compliance Requirements

- **Regulatory Approval**: Not approved by any insurance regulator
- **Actuarial Validation**: Not validated by qualified actuaries
- **Fair Lending**: Not tested for discriminatory impact
- **Data Privacy**: Uses only synthetic data

### Audit Trail

- All inputs and outputs are logged
- Factor breakdowns enable audit review
- Transparent scoring methodology
- Version controlled rules

## Disclaimers

⚠️ **CRITICAL DISCLAIMER**

**This application demonstrates fictional insurance logic using synthetic data only.**

- ✅ Educational and demonstration purposes only
- ✅ No outputs shall be used for real underwriting, pricing, or policy decisions
- ✅ All data is 100% synthetic and fabricated
- ✅ Underwriter review is MANDATORY for all assessments
- ✅ No real pricing, quoting, reserving, or binding occurs
- ✅ Human-in-the-loop required for all decisions

**This tool is not approved for actual underwriting decisions, premium pricing, or policy issuance. All outputs require human review and validation by qualified insurance underwriters.**

## Technical Specifications

### Dependencies

```
gradio>=4.0.0
pandas>=2.0.0
numpy>=1.24.0
```

### System Requirements

- Python 3.8+
- No GPU required
- Minimal compute resources
- Local execution supported

### API Interface

**Gradio Interface:**
- Input: 3 fields (industry, risk profile, claim count)
- Output: Risk band, score, factor breakdown, warnings
- Response time: <100ms

## Roadmap

### Potential Enhancements (Educational Context Only)

- [ ] Add more industry segments
- [ ] Include business size factors
- [ ] Add geographic risk factors
- [ ] Implement confidence intervals
- [ ] Add comparative benchmarking
- [ ] Enhanced visualization of factor contributions

### Not Planned

❌ Real actuarial models  
❌ Production deployment  
❌ Real data integration  
❌ Automated decision-making  

## Contact & Support

**Organization:** GCC Insurance Intelligence Lab  
**Purpose:** Educational demonstration only  
**Support:** Community-driven (no SLA)  

## Version History

- **v1.0** (2026-01-08): Initial release with rule-based scoring

## License

MIT License - Educational Use Only

This software is provided for educational and demonstration purposes. It is not licensed, approved, or validated for production insurance underwriting operations.
