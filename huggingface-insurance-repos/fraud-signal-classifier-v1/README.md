# fraud-signal-classifier-v1

🚨 **EDUCATIONAL USE ONLY** | 100% Synthetic Data | Human-in-the-Loop Required

## Overview

**fraud-signal-classifier-v1** is a baseline machine learning classifier that predicts fraud likelihood signals for generic insurance claims. This model is trained exclusively on synthetic data and is designed for educational purposes, AI experimentation, and decision support sandbox environments.

The model classifies insurance claims into risk buckets (Low, Medium, High) based on claim characteristics and provides probability scores to support fraud investigation workflows.

## 🎯 Purpose

This model serves as:
- ✅ An educational tool for understanding AI in GCC insurance contexts
- ✅ A demonstration of fraud signal detection capabilities
- ✅ A foundation for hybrid rule-based + ML fraud detection systems
- ✅ A sandbox environment for testing fraud workflows

## ⚠️ Critical Disclaimers

### NOT Intended For:
- ❌ **Underwriting decisions** - Do not use for policy approval/denial
- ❌ **Fraud denial or claims rejection** - Not a basis for claim denial
- ❌ **Premium pricing** - Not calibrated for actuarial pricing
- ❌ **Reserving or actuarial work** - Not designed for financial projections
- ❌ **Production environments** - Educational use only

### Mandatory Requirements:
- 🔍 **Human-in-the-loop review REQUIRED** for every prediction
- 📊 **Advisory signals only** - Outputs are suggestions, not decisions
- 🎓 **Educational context** - Training and demonstration purposes
- ⚖️ **No automated decisions** - Never use without human validation

## 🔧 Technical Details

### Model Architecture
- **Algorithm**: Random Forest Classifier
- **Features**: 5 input features (3 categorical, 2 numerical)
- **Output Classes**: 4 risk levels (Clean, Under Review, Flagged, Confirmed Fraud)
- **Framework**: scikit-learn

### Input Features
1. **policy_type** (categorical): Type of insurance policy
   - Auto Collision, Auto Theft, Home Fire, Home Burglary, Home Water Damage, Property Damage, Liability, Workers Comp

2. **claimant_profile_risk** (categorical): Risk level of the claimant
   - Low Risk, Medium Risk, High Risk, Very High Risk

3. **incident_pattern** (categorical): Pattern observed in the incident
   - Normal, High Value, Holiday Filing, Suspicious Timing, Rapid Succession, Inconsistent Details, Multiple Claims

4. **document_consistency_score** (numerical): Score indicating document quality (0.0 - 1.0)

5. **anomaly_score** (numerical): Anomaly detection score (0.0 - 1.0)

### Output
- **fraud_score**: Continuous score from 0.0 to 1.0 indicating fraud likelihood
- **bucket**: Risk category (Low, Medium, High)
- **predicted_class**: Most likely class (Clean, Under Review, Flagged, Confirmed Fraud)
- **confidence**: Model confidence in the prediction
- **probabilities**: Full probability distribution across all classes

### Bucket Mapping
- **Low**: fraud_score < 0.3 (Routine processing)
- **Medium**: 0.3 ≤ fraud_score < 0.6 (Enhanced review)
- **High**: fraud_score ≥ 0.6 (Priority investigation)

## 📊 Data Source

- **Dataset**: fraud_cases_synthetic.csv
- **Records**: 236 synthetic insurance claims
- **Synthetic Status**: 100% fabricated data with zero production linkage
- **Protected Features**: NONE - No gender, nationality, or protected attributes
- **Personal Data**: NONE - No real personal information

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Training the Model

```bash
python train_model.py
```

This will:
- Load synthetic data from `../insurance-datasets-synthetic/data/fraud_cases_synthetic.csv`
- Train a Random Forest classifier
- Evaluate performance on test set
- Export `model.pkl`, `label_encoders.pkl`, and `feature_names.json`

### Running Inference

```python
from inference import FraudSignalClassifier

# Initialize classifier
classifier = FraudSignalClassifier()

# Make prediction
result = classifier.get_fraud_score_and_bucket(
    policy_type='Auto Collision',
    claimant_profile_risk='Medium Risk',
    incident_pattern='Suspicious Timing',
    document_consistency_score=0.65,
    anomaly_score=0.45
)

print(f"Fraud Score: {result['fraud_score']}")
print(f"Bucket: {result['bucket']}")
print(f"Predicted Class: {result['predicted_class']}")
```

### Demo Inference

```bash
python inference.py
```

## 📦 Model Files

- `model.pkl` - Trained Random Forest classifier
- `label_encoders.pkl` - Label encoders for categorical features
- `feature_names.json` - Feature names and metadata
- `train_model.py` - Training script
- `inference.py` - Inference utilities
- `requirements.txt` - Python dependencies

## 🛡️ Governance & Safety

### Human-in-the-Loop Protocol
Every prediction from this model MUST be reviewed by a qualified human expert before any action is taken. The model provides advisory signals only.

### Bias Mitigation
- No protected attributes (gender, race, nationality) are used
- Synthetic data ensures no real-world bias propagation
- Class balancing applied during training
- Regular validation against fairness metrics recommended

### Audit Trail
Organizations using this model should maintain:
- Prediction logs with timestamps
- Human reviewer decisions and rationale
- Model version tracking
- Performance monitoring metrics

## 🗺️ Roadmap

### Planned Enhancements
- ✨ Add SHAP/LIME explainability for feature importance
- 📈 Expand synthetic dataset with more diverse scenarios
- 🌍 Enable multi-sector calibration (auto, property, health)
- 🌐 Multi-lingual input handling for GCC markets
- 🔄 Model retraining pipeline with versioning
- 📊 Enhanced uncertainty quantification

### Integration Opportunities
- Connect with fraud-triage-sandbox for hybrid ML + rule-based logic
- API endpoint for real-time inference
- Dashboard for batch prediction and monitoring

## 📄 License & Compliance

### Usage Rights
- ✅ Permitted for research and demonstration
- ✅ Educational training and workshops
- ✅ Internal sandbox testing
- ❌ NOT permitted for production use
- ❌ NOT permitted for commercial underwriting

### Compliance Notes
- Fully synthetic training data
- No GDPR/privacy concerns (no real personal data)
- No regulatory approval required for educational use
- Organizations must comply with local regulations if adapting for production

## 🤝 Contributing

This model is part of the **gcc-insurance-intelligence-lab** initiative to advance AI education in the GCC insurance sector.

For questions, improvements, or collaboration:
- Open issues for bugs or feature requests
- Submit pull requests for enhancements
- Contact: [Your organization contact]

## 🙏 Acknowledgments

- Synthetic dataset created for educational purposes
- Built with scikit-learn and Hugging Face tools
- Part of the GCC Insurance AI Hub ecosystem

## ⚡ Quick Links

- 🏠 [GCC Insurance AI Hub](https://huggingface.co/gcc-insurance-intelligence-lab)
- 🧪 [Fraud Triage Sandbox](https://huggingface.co/spaces/gcc-insurance-intelligence-lab/fraud-triage-sandbox)
- 📚 [Insurance Datasets Synthetic](https://huggingface.co/datasets/gcc-insurance-intelligence-lab/insurance-datasets-synthetic)

---

**Remember**: This is a synthetic educational model. Always use human judgment and comply with all applicable regulations when making insurance decisions.
