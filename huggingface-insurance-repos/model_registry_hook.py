"""
Model Registry Hook System
Automatically detects trained models in /models folder and pushes them to HF Model Hub
"""

import os
import json
from pathlib import Path
import tempfile
from datetime import datetime

class ModelRegistryHook:
    """
    Auto-detects trained models in /models folder and pushes them to HF Model Hub
    """
    
    def __init__(self, models_dir="models", hf_org="gcc-insurance-intelligence-lab"):
        self.models_dir = Path(models_dir)
        self.hf_org = hf_org
        self.models_dir.mkdir(exist_ok=True)
    
    def scan_for_new_models(self):
        """Scan for new model files that need to be registered"""
        model_extensions = ['.pkl', '.joblib', '.bin', '.pt', '.h5', '.onnx', '.model']
        new_models = []
        
        for file_path in self.models_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in model_extensions:
                # Check if model is already registered
                model_name = file_path.stem
                metadata_file = file_path.with_name(f"{model_name}_metadata.json")
                
                if not metadata_file.exists():
                    new_models.append(file_path)
        
        return new_models
    
    def create_model_card(self, model_path, model_name):
        """Create a model card for the given model"""
        model_card_content = f"""# Model Card: {model_name}

## Model Details

### Description

Insurance risk assessment model trained on synthetic data for educational purposes only. This model is not intended for production use.

- **Developed by:** GCC Insurance Intelligence Lab
- **Model Type:** {model_path.suffix.upper()[1:]} model
- **Version:** 1.0
- **Framework:** Trained with synthetic data
- **License:** MIT (Educational Use Only)

## Intended Use

### Primary Use Cases

✅ **Educational Training**: Training insurance professionals  
✅ **Logic Demonstration**: Demonstrating insurance concepts  
✅ **Workflow Prototyping**: Prototyping insurance workflows  
✅ **Concept Validation**: Validating insurance concepts  

### Out-of-Scope Use

❌ **Real Operations**: Not for actual insurance operations  
❌ **Production Decisions**: Not for production decisions  
❌ **Production Systems**: Not validated for live operations  

## Training Data

**100% Synthetic**: All training data is fabricated for educational purposes. No real insurance data was used in training.

### Synthetic Data Context

- 100% fabricated scenarios
- No real insurance data used
- Educational examples only
- No connection to actual operations

## Factors & Metrics

Model trained on synthetic features for educational demonstration.

## Ethical Considerations

### Bias & Fairness

As a synthetic model, bias is limited to the synthetic data generation process. All logic is transparent and auditable.

### Mitigation Strategies

✅ **Transparency**: All logic is explicit and auditable  
✅ **Explainability**: Clear reasoning provided for all decisions  
✅ **Human Review**: Mandatory validation by professionals  
✅ **No Automation**: No automated decisions  

## Limitations

### Known Limitations

- Educational demonstration only
- No real-world validation
- Simplified model
- Not suitable for production use

### Technical Constraints

- Requires compatible runtime environment
- Local execution only

## Recommendations

### For Users

- Use only for educational purposes
- Always implement human review
- Do not use for production decisions
- Validate outputs with qualified professionals

### For Organizations

- Do not deploy for production use
- Implement appropriate governance
- Maintain professional oversight
- Document all decisions appropriately

## Governance

### Mandatory Requirements

- Human-in-the-loop for all decisions
- Clear disclaimers in all interfaces
- Synthetic data only
- Educational use only

### Compliance Notes

This model is designed for educational use only and must not be used for actual insurance operations.

## Technical Specifications

### Architecture

Trained model with synthetic parameters.

### Compute Requirements

- Compatible runtime environment
- Minimal memory requirements
- Local execution

## Disclaimer

⚠️ **CRITICAL NOTICE**

{model_name} demonstrates fictional insurance logic using synthetic data only. No outputs shall be used for actual insurance operations. All data and scenarios are fabricated for educational purposes.

**Human-in-the-loop is mandatory for all decisions.**

Organizations using this tool must:
- Comply with all applicable laws and regulations
- Implement appropriate governance and oversight
- Maintain professional standards
- Document all decisions with qualified professional approval
- Never rely on this system for actual insurance operations

## Contact

For questions or feedback about this educational tool, contact the GCC Insurance Intelligence Lab.

---

**Version**: 1.0  
**Last Updated**: {datetime.now().strftime('%B %Y')}  
**Status**: Educational Demonstration
"""
        return model_card_content
    
    def register_model(self, model_path):
        """Register a model to Hugging Face Hub"""
        model_name = model_path.stem
        print(f"Registering model: {model_name}")
        
        # Create model card if it doesn't exist
        model_card_path = model_path.with_name(f"{model_name}_card.md")
        if not model_card_path.exists():
            model_card_content = self.create_model_card(model_path, model_name)
            with open(model_card_path, 'w') as f:
                f.write(model_card_content)
            print(f"✓ Created model card: {model_card_path.name}")
        
        # Create metadata to track registration
        metadata = {
            "model_name": model_name,
            "file_path": str(model_path),
            "registered_at": datetime.now().isoformat(),
            "hf_org": self.hf_org,
            "status": "pending_upload"
        }
        
        metadata_file = model_path.with_name(f"{model_name}_metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Created metadata: {metadata_file.name}")
        
        # Note: Actual upload to HF Hub requires authentication
        # This would be handled by the CI/CD system
        print(f"ℹ️  Model {model_name} prepared for upload to {self.hf_org}/{model_name}")
        print(f"ℹ️  Upload requires HF credentials and would be handled by CI/CD")
        
        return str(metadata_file)
    
    def process_all_new_models(self):
        """Process all new models in the models directory"""
        new_models = self.scan_for_new_models()
        
        if not new_models:
            print("No new models found to register")
            return []
        
        registered_models = []
        for model_path in new_models:
            try:
                metadata_file = self.register_model(model_path)
                registered_models.append(metadata_file)
            except Exception as e:
                print(f"❌ Error registering {model_path.name}: {e}")
        
        return registered_models

# Example usage
def run_model_registry_hook():
    """Run the model registry hook to detect and register new models"""
    hook = ModelRegistryHook()
    registered_models = hook.process_all_new_models()
    
    if registered_models:
        print(f"\n✅ Registered {len(registered_models)} models:")
        for model in registered_models:
            print(f"  - {os.path.basename(model)}")
    else:
        print("No new models to register")

if __name__ == "__main__":
    run_model_registry_hook()