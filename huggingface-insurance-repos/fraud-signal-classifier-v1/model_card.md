---
license: mit
tags:
- fraud-detection
- insurance
- synthetic-data
- educational
- gcc-insurance
datasets:
- gcc-insurance-intelligence-lab/insurance-datasets-synthetic
language:
- en
library_name: scikit-learn
---

# Model Card: fraud-signal-classifier-v1

## Model Details

### Overview
**fraud-signal-classifier-v1** is a Random Forest-based fraud signal classifier for insurance claims, trained exclusively on synthetic data for educational purposes.

- **Developed by**: gcc-insurance-intelligence-lab
- **Model Type**: Multi-class Classification (Random Forest)
- **Language**: English
- **Framework**: scikit-learn
- **Version**: 1.0
- **License**: MIT (Educational Use Only)
- **Model Date**: January 2026

### Model Description

This model predicts fraud likelihood signals for insurance claims by analyzing claim characteristics including policy type, claimant risk profile, incident patterns, document quality, and anomaly indicators. It outputs probability scores and risk buckets to support fraud investigation workflows.

**Key Features**:
- 🎯 Multi-class classification into 4 fraud risk levels
- 📊 Probability scores for interpretable risk assessment
- 🔄 Bucket mapping (Low/Medium/High) for workflow routing
- 🎓 100% synthetic training data with no privacy concerns

## Intended Use

### Primary Use Cases
✅ **Educational Training**: Teaching AI concepts in insurance fraud detection  
✅ **Sandbox Testing**: Experimenting with fraud detection workflows  
✅ **Decision Support**: Advisory signals for human fraud investigators  
✅ **Research**: Developing hybrid ML + rule-based fraud systems  

### Out-of-Scope Use Cases
❌ **Underwriting Decisions**: Do not use for policy approval/denial  
❌ **Claim Rejection**: Not a basis for denying insurance claims  
❌ **Premium Pricing**: Not calibrated for actuarial pricing  
❌ **Production Systems**: Not validated for real-world deployment  
❌ **Automated Decisions**: Never use without human review  

## Training Data

### Data Source
- **Dataset**: fraud_cases_synthetic.csv
- **Records**: 236 synthetic insurance claims
- **Synthetic Status**: 100% fabricated data with **ZERO** production linkage
- **Generation Method**: Programmatically generated with controlled distributions

### Features
The model uses 5 input features:

| Feature | Type | Description | Values |
|---------|------|-------------|--------|
| policy_type | Categorical | Insurance policy type | Auto Collision, Auto Theft, Home Fire, Home Burglary, Home Water Damage, Property Damage, Liability, Workers Comp |
| claimant_profile_risk | Categorical | Claimant risk level | Low Risk, Medium Risk, High Risk, Very High Risk |
| incident_pattern | Categorical | Incident pattern observed | Normal, High Value, Holiday Filing, Suspicious Timing, Rapid Succession, Inconsistent Details, Multiple Claims |
| document_consistency_score | Numerical | Document quality score | 0.0 - 1.0 (float) |
| anomaly_score | Numerical | Anomaly detection score | 0.0 - 1.0 (float) |

### Target Variable
- **synthetic_flag_label**: Fraud risk classification
  - Clean
  - Under Review
  - Flagged
  - Confirmed Fraud

### Data Characteristics
- **No Protected Attributes**: No gender, race, nationality, or other protected features
- **No Personal Data**: No real names, addresses, or identifiable information
- **Balanced Sampling**: Class weights applied during training
- **No Real Claims**: Entirely synthetic with no connection to actual insurance claims

## Model Architecture

### Algorithm
Random Forest Classifier with the following hyperparameters:
- `n_estimators`: 100 (number of trees)
- `max_depth`: 10
- `min_samples_split`: 5
- `min_samples_leaf`: 2
- `class_weight`: 'balanced'
- `random_state`: 42

### Training Process
1. Load synthetic data from CSV
2. Encode categorical features using LabelEncoder
3. Split data (80% train, 20% test) with stratification
4. Train Random Forest on training set
5. Evaluate on held-out test set
6. Export model, encoders, and metadata

### Preprocessing
- **Categorical Encoding**: LabelEncoder for policy_type, claimant_profile_risk, incident_pattern
- **Numerical Features**: Used as-is (already normalized 0-1)
- **Missing Values**: Not applicable (synthetic data is complete)

## Performance

### Evaluation Metrics
Performance metrics are computed on a held-out test set (20% of data):

- **Accuracy**: Reported during training (typically 60-75% on synthetic data)
- **Classification Report**: Precision, recall, F1-score per class
- **Confusion Matrix**: Class-level prediction analysis
- **Feature Importance**: Random Forest feature importance scores

### Expected Performance Range
Given the synthetic nature and limited dataset size:
- **Baseline Accuracy**: 60-75%
- **Confidence Calibration**: Not calibrated for production
- **Generalization**: Limited to synthetic data distribution

### Limitations
⚠️ **Performance Caveats**:
- Small dataset (236 samples) limits generalization
- Synthetic data may not reflect real-world complexity
- No validation against real fraud patterns
- Class imbalance may affect minority class performance

## Ethical Considerations

### Bias & Fairness
✅ **No Protected Attributes**: Model does not use gender, race, nationality, or other protected characteristics  
✅ **Synthetic Data**: No real-world bias propagation from historical data  
✅ **Class Balancing**: Applied during training to mitigate class imbalance  
⚠️ **Not Audited**: Not validated against fairness metrics or regulatory standards  

### Privacy
✅ **Zero Privacy Risk**: 100% synthetic data with no personal information  
✅ **No GDPR Concerns**: No real individuals or protected data  
✅ **Public Dataset**: Can be shared without privacy restrictions  

### Transparency
✅ **Open Source**: Code, data, and model publicly available  
✅ **Explainability**: Feature importance scores provided  
⚠️ **Limited Interpretability**: Random Forest is less interpretable than linear models  
🔮 **Roadmap**: SHAP/LIME integration planned for future versions  

## Governance & Safety

### Human-in-the-Loop Requirements
🚨 **MANDATORY**: Every prediction MUST be reviewed by a qualified human expert before any action is taken.

**Review Protocol**:
1. Model generates fraud score and bucket
2. Human expert reviews claim details and model output
3. Expert makes final decision with full accountability
4. Decision and rationale are documented
5. Model output is treated as advisory only

### Risk Mitigation
- ⚠️ **No Automation**: Never auto-approve or auto-deny based on model alone
- 🔍 **Audit Trail**: Log all predictions and human decisions
- 📊 **Performance Monitoring**: Track prediction accuracy over time
- 🔄 **Model Updates**: Plan for periodic retraining and validation

### Regulatory Compliance
- 🎓 **Educational Use**: No regulatory approval required
- ⚖️ **Production Use**: Would require regulatory review and approval
- 🌍 **GCC Markets**: Organizations must comply with local insurance regulations
- 📜 **Documentation**: Maintain audit trail for compliance purposes

## Outputs & Interpretation

### Prediction Format
The model returns a dictionary with:
```python
{
    'fraud_score': 0.456,  # Continuous score 0-1
    'bucket': 'Medium',     # Risk category: Low, Medium, High
    'predicted_class': 'Under Review',  # Most likely class
    'confidence': 0.652,    # Model confidence
    'probabilities': {      # Full probability distribution
        'Clean': 0.234,
        'Under Review': 0.652,
        'Flagged': 0.089,
        'Confirmed Fraud': 0.025
    },
    'warning': '⚠️ HUMAN REVIEW REQUIRED - Educational model only'
}
```

### Bucket Mapping
Risk buckets guide workflow routing:

| Bucket | Fraud Score Range | Recommended Action |
|--------|-------------------|-------------------|
| **Low** | 0.0 - 0.3 | Routine processing, standard review |
| **Medium** | 0.3 - 0.6 | Enhanced review, secondary checks |
| **High** | 0.6 - 1.0 | Priority investigation, expert review |

**Important**: Buckets are advisory suggestions, not automatic decisions.

### Fraud Score Calculation
The fraud_score is a weighted average:
- Clean = 0.0
- Under Review = 0.33
- Flagged = 0.66
- Confirmed Fraud = 1.0

Weighted by class probabilities to produce a continuous 0-1 score.

## Usage Example

```python
from inference import FraudSignalClassifier

# Load model
classifier = FraudSignalClassifier(
    model_path='model.pkl',
    encoder_path='label_encoders.pkl'
)

# Make prediction
result = classifier.get_fraud_score_and_bucket(
    policy_type='Auto Collision',
    claimant_profile_risk='High Risk',
    incident_pattern='Multiple Claims',
    document_consistency_score=0.35,
    anomaly_score=0.95
)

# Interpret results
print(f"Fraud Score: {result['fraud_score']:.3f}")
print(f"Risk Bucket: {result['bucket']}")
print(f"Predicted Class: {result['predicted_class']}")
print(f"Confidence: {result['confidence']:.3f}")

# ⚠️ CRITICAL: Human review required before any action
```

## Roadmap & Future Work

### Planned Enhancements
- ✨ **Explainability**: Integrate SHAP/LIME for feature contribution analysis
- 📈 **Dataset Expansion**: Grow synthetic dataset to 1000+ samples
- 🎯 **Calibration**: Improve probability calibration for confidence scores
- 🌍 **Multi-Sector**: Add domain-specific models for auto, property, health
- 🌐 **Multi-Lingual**: Support Arabic and other GCC languages
- 🔄 **Retraining Pipeline**: Automated model versioning and retraining
- 📊 **Uncertainty Quantification**: Better uncertainty estimates
- 🔗 **API**: REST API for inference

### Integration Plans
- **fraud-triage-sandbox**: Hybrid ML + rule-based fraud detection
- **Dashboard**: Batch prediction and performance monitoring
- **Workflow Tools**: Integration with case management systems

## Model Files

The model repository includes:
- `model.pkl` - Trained Random Forest classifier (scikit-learn)
- `label_encoders.pkl` - Feature and target encoders
- `feature_names.json` - Feature metadata
- `train_model.py` - Training script
- `inference.py` - Inference utilities
- `requirements.txt` - Python dependencies

## Citation

If you use this model in your research or projects, please cite:

```bibtex
@model{gcc-fraud-classifier-v1,
  title={Fraud Signal Classifier v1},
  author={GCC Insurance Intelligence Lab},
  year={2026},
  publisher={Hugging Face},
  howpublished={\url{https://huggingface.co/gcc-insurance-intelligence-lab/fraud-signal-classifier-v1}},
  note={Educational model trained on 100% synthetic data}
}
```

## Contact & Support

- **Organization**: gcc-insurance-intelligence-lab
- **Repository**: https://huggingface.co/gcc-insurance-intelligence-lab/fraud-signal-classifier-v1
- **Issues**: Please open GitHub issues for bugs or questions
- **Contributions**: Pull requests welcome for improvements

## Disclaimer

⚠️ **IMPORTANT LEGAL DISCLAIMER**

This model is provided "as-is" for educational and research purposes only. The developers and publishers:

- Make NO warranties about accuracy, reliability, or fitness for any purpose
- Accept NO liability for decisions made based on model outputs
- Require human review for ALL predictions
- Prohibit use for actual underwriting, claim denial, or pricing decisions
- Disclaim responsibility for any damages from model use

Organizations using this model must:
- Comply with all applicable laws and regulations
- Implement appropriate governance and oversight
- Maintain human accountability for all decisions
- Document model limitations and use cases
- Obtain necessary regulatory approvals for production use

**This model is NOT approved for production insurance operations.**

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Status**: Educational / Experimental
