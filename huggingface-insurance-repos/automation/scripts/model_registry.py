#!/usr/bin/env python3
"""
Model Registry - Automated Model Detection and HuggingFace Hub Integration

This script:
- Detects trained models in /models folders across repos
- Packages models for HuggingFace Model Hub
- Auto-generates model_card.md if missing
- Tags model versions (v1, v2, etc.)
- Manages synthetic dataset versions
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_utils import run_command, get_all_repos, validate_governance


class ModelRegistry:
    """Manages model detection, packaging, and HuggingFace Hub integration"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.hf_org = "gcc-insurance-intelligence-lab"
        
    def detect_models(self, repo_path: Path) -> List[Dict]:
        """Detect all models in a repository's /models folder"""
        models_dir = repo_path / "models"
        detected_models = []
        
        if not models_dir.exists():
            return detected_models
            
        print(f"\n🔍 Scanning {models_dir} for models...")
        
        # Common model file extensions
        model_extensions = [
            '.pkl', '.joblib', '.h5', '.pt', '.pth', 
            '.onnx', '.pb', '.safetensors', '.bin'
        ]
        
        for item in models_dir.rglob('*'):
            if item.is_file() and item.suffix in model_extensions:
                model_info = {
                    'path': item,
                    'name': item.stem,
                    'extension': item.suffix,
                    'size': item.stat().st_size,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime),
                    'repo': repo_path.name
                }
                detected_models.append(model_info)
                print(f"  ✓ Found: {item.name} ({model_info['size'] / 1024:.2f} KB)")
                
        return detected_models
    
    def get_model_version(self, repo_path: Path, model_name: str) -> str:
        """Determine next version number for a model"""
        versions_file = repo_path / "models" / ".versions.json"
        
        if versions_file.exists():
            with open(versions_file, 'r') as f:
                versions = json.load(f)
        else:
            versions = {}
            
        current_version = versions.get(model_name, 0)
        next_version = current_version + 1
        
        # Update versions file
        versions[model_name] = next_version
        versions_file.parent.mkdir(parents=True, exist_ok=True)
        with open(versions_file, 'w') as f:
            json.dump(versions, f, indent=2)
            
        return f"v{next_version}"
    
    def generate_model_card(self, model_info: Dict, repo_path: Path) -> Path:
        """Generate model_card.md for a model if it doesn't exist"""
        model_card_path = repo_path / "models" / f"{model_info['name']}_model_card.md"
        
        if model_card_path.exists():
            print(f"  ℹ️  Model card already exists: {model_card_path.name}")
            return model_card_path
            
        version = self.get_model_version(repo_path, model_info['name'])
        
        model_card_content = f"""---
license: apache-2.0
tags:
- insurance
- synthetic-data
- {repo_path.name}
library_name: scikit-learn
---

# {model_info['name'].replace('_', ' ').title()}

## Model Description

This model is part of the GCC Insurance Intelligence Lab and was trained on **synthetic data only**.

**Version:** {version}
**Repository:** {repo_path.name}
**Model Type:** {model_info['extension'][1:].upper()}
**Size:** {model_info['size'] / 1024:.2f} KB
**Last Modified:** {model_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}

## Intended Use

🎯 **Educational and Research Purposes Only**

This model is designed for:
- Learning and experimentation
- Proof-of-concept demonstrations
- Research and development
- Testing and validation

## Training Data

✅ **100% Synthetic Data**

All training data is synthetically generated and contains:
- No real customer information
- No personally identifiable information (PII)
- No confidential business data
- No actual insurance claims or policies

## Limitations and Disclaimers

⚠️ **IMPORTANT DISCLAIMERS**

- **NOT FOR PRODUCTION USE**: This model is not validated for production deployment
- **NO UNDERWRITING AUTHORITY**: Cannot be used for actual insurance underwriting decisions
- **NO PRICING AUTHORITY**: Cannot be used to set insurance premiums or rates
- **NO PAYOUT DECISIONS**: Cannot be used to approve or deny insurance claims
- **HUMAN-IN-LOOP REQUIRED**: All outputs must be reviewed by qualified professionals
- **SYNTHETIC DATA ONLY**: Trained exclusively on synthetic data

## Governance

This model adheres to the GCC Insurance Intelligence Lab governance framework:

1. **Synthetic Data Only**: No real customer or business data used
2. **Human Oversight**: All predictions require human review
3. **Educational Purpose**: For learning and demonstration only
4. **No Authority**: No decision-making authority in production systems
5. **Transparency**: Full disclosure of limitations and intended use

## Model Performance

*Performance metrics should be added here after evaluation*

## Usage Example

```python
import joblib

# Load model
model = joblib.load('{model_info['name']}{model_info['extension']}')

# Make prediction (synthetic data only)
# prediction = model.predict(X_test)

# ⚠️ ALWAYS review predictions with domain experts
```

## Citation

```bibtex
@misc{{{model_info['name']},
  title={{{model_info['name'].replace('_', ' ').title()}}},
  author={{GCC Insurance Intelligence Lab}},
  year={{{datetime.now().year}}},
  publisher={{HuggingFace}},
  howpublished={{\\url{{https://huggingface.co/{self.hf_org}/{repo_path.name}}}}}
}}
```

## Contact

For questions or issues, please refer to the main repository documentation.

---

**Created:** {datetime.now().strftime('%Y-%m-%d')}
**Version:** {version}
**Status:** Development
"""
        
        with open(model_card_path, 'w') as f:
            f.write(model_card_content)
            
        print(f"  ✓ Generated model card: {model_card_path.name}")
        return model_card_path
    
    def package_model(self, model_info: Dict, repo_path: Path) -> Path:
        """Package model with metadata for HuggingFace Hub"""
        version = self.get_model_version(repo_path, model_info['name'])
        package_dir = repo_path / "models" / f"{model_info['name']}_{version}"
        package_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📦 Packaging model: {model_info['name']} ({version})")
        
        # Copy model file
        model_dest = package_dir / f"model{model_info['extension']}"
        shutil.copy2(model_info['path'], model_dest)
        print(f"  ✓ Copied model file")
        
        # Generate/copy model card
        model_card = self.generate_model_card(model_info, repo_path)
        shutil.copy2(model_card, package_dir / "README.md")
        print(f"  ✓ Added model card")
        
        # Create config.json
        config = {
            "model_name": model_info['name'],
            "version": version,
            "repository": repo_path.name,
            "organization": self.hf_org,
            "created_date": datetime.now().isoformat(),
            "model_type": model_info['extension'][1:],
            "size_bytes": model_info['size'],
            "governance": {
                "synthetic_data_only": True,
                "human_in_loop_required": True,
                "production_ready": False,
                "underwriting_authority": False,
                "pricing_authority": False,
                "payout_authority": False
            }
        }
        
        with open(package_dir / "config.json", 'w') as f:
            json.dump(config, f, indent=2)
        print(f"  ✓ Created config.json")
        
        return package_dir
    
    def push_to_hf_hub(self, package_dir: Path, repo_name: str) -> bool:
        """Push packaged model to HuggingFace Model Hub"""
        print(f"\n🚀 Pushing to HuggingFace Model Hub...")
        
        # Check if huggingface_hub is installed
        try:
            import huggingface_hub
        except ImportError:
            print("  ⚠️  huggingface_hub not installed. Install with: pip install huggingface_hub")
            return False
            
        try:
            # This would use HF_TOKEN environment variable
            # In practice, this requires authentication
            model_id = f"{self.hf_org}/{repo_name}"
            print(f"  📍 Target: {model_id}")
            print(f"  ℹ️  Note: Requires HF_TOKEN environment variable for authentication")
            
            # Placeholder for actual push
            # api = huggingface_hub.HfApi()
            # api.upload_folder(
            #     folder_path=package_dir,
            #     repo_id=model_id,
            #     repo_type="model"
            # )
            
            print(f"  ✓ Model package ready for upload")
            print(f"  💡 To upload manually: huggingface-cli upload {model_id} {package_dir}")
            return True
            
        except Exception as e:
            print(f"  ❌ Error preparing upload: {e}")
            return False
    
    def manage_dataset_versions(self, repo_path: Path) -> List[str]:
        """Manage synthetic dataset versions in repository"""
        data_dir = repo_path / "data"
        if not data_dir.exists():
            return []
            
        print(f"\n📊 Managing dataset versions in {repo_path.name}...")
        
        versions = []
        dataset_files = list(data_dir.glob('*.csv')) + list(data_dir.glob('*.json'))
        
        for dataset_file in dataset_files:
            # Check if it's a versioned dataset
            if '_v' in dataset_file.stem or 'dataset' in dataset_file.stem.lower():
                versions.append(dataset_file.name)
                print(f"  ✓ Found dataset: {dataset_file.name}")
                
        # Create dataset registry
        registry_file = data_dir / ".dataset_registry.json"
        registry = {
            "repository": repo_path.name,
            "datasets": [],
            "last_updated": datetime.now().isoformat()
        }
        
        for version in versions:
            dataset_path = data_dir / version
            registry["datasets"].append({
                "filename": version,
                "size_bytes": dataset_path.stat().st_size if dataset_path.exists() else 0,
                "modified": datetime.fromtimestamp(dataset_path.stat().st_mtime).isoformat() if dataset_path.exists() else None,
                "synthetic": True,
                "governance_compliant": True
            })
            
        with open(registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
            
        print(f"  ✓ Created dataset registry with {len(versions)} datasets")
        return versions
    
    def process_repository(self, repo_path: Path) -> Dict:
        """Process a single repository for models and datasets"""
        print(f"\n{'='*60}")
        print(f"Processing: {repo_path.name}")
        print(f"{'='*60}")
        
        results = {
            "repository": repo_path.name,
            "models_detected": 0,
            "models_packaged": 0,
            "datasets_managed": 0,
            "status": "success"
        }
        
        try:
            # Detect models
            models = self.detect_models(repo_path)
            results["models_detected"] = len(models)
            
            # Package each model
            for model_info in models:
                try:
                    package_dir = self.package_model(model_info, repo_path)
                    results["models_packaged"] += 1
                except Exception as e:
                    print(f"  ⚠️  Error packaging {model_info['name']}: {e}")
                    
            # Manage dataset versions
            datasets = self.manage_dataset_versions(repo_path)
            results["datasets_managed"] = len(datasets)
            
        except Exception as e:
            print(f"  ❌ Error processing repository: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            
        return results
    
    def process_all_repositories(self) -> Dict:
        """Process all repositories in the lab"""
        print("\n" + "="*60)
        print("🏭 MODEL REGISTRY - Processing All Repositories")
        print("="*60)
        
        repos = get_all_repos(self.base_path)
        summary = {
            "total_repos": len(repos),
            "repos_processed": 0,
            "total_models": 0,
            "total_datasets": 0,
            "results": []
        }
        
        for repo in repos:
            result = self.process_repository(repo)
            summary["results"].append(result)
            summary["repos_processed"] += 1
            summary["total_models"] += result["models_detected"]
            summary["total_datasets"] += result["datasets_managed"]
            
        # Print summary
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        print(f"Repositories Processed: {summary['repos_processed']}/{summary['total_repos']}")
        print(f"Total Models Detected: {summary['total_models']}")
        print(f"Total Datasets Managed: {summary['total_datasets']}")
        
        # Save summary
        summary_file = self.base_path / "automation" / "model_registry_summary.json"
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"\n✓ Summary saved to: {summary_file}")
        
        return summary


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Model Registry - Automated model detection and HuggingFace Hub integration"
    )
    parser.add_argument(
        '--repo',
        help='Process specific repository (default: all repos)'
    )
    parser.add_argument(
        '--base-path',
        default=os.getcwd(),
        help='Base path for repositories'
    )
    
    args = parser.parse_args()
    
    registry = ModelRegistry(args.base_path)
    
    if args.repo:
        repo_path = Path(args.base_path) / args.repo
        if repo_path.exists():
            registry.process_repository(repo_path)
        else:
            print(f"❌ Repository not found: {repo_path}")
            sys.exit(1)
    else:
        registry.process_all_repositories()
    
    print("\n✅ Model registry processing complete!")


if __name__ == "__main__":
    main()
