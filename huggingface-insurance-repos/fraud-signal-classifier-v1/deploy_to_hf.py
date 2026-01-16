#!/usr/bin/env python3
"""
Deploy fraud-signal-classifier-v1 to Hugging Face Hub
"""

from huggingface_hub import HfApi, create_repo, upload_file, upload_folder
import os

# Configuration
REPO_ID = "gcc-insurance-intelligence-lab/fraud-signal-classifier-v1"
REPO_TYPE = "model"

# Files to upload
FILES_TO_UPLOAD = [
    "model.pkl",
    "label_encoders.pkl",
    "feature_names.json",
    "train_model.py",
    "inference.py",
    "requirements.txt",
    "README.md",
    "model_card.md"
]

def deploy_model():
    """
    Deploy model to Hugging Face Hub
    """
    print("="*60)
    print("DEPLOYING fraud-signal-classifier-v1 TO HUGGING FACE")
    print("="*60)
    
    # Initialize API
    api = HfApi()
    
    # Create repository if it doesn't exist
    print(f"\n1. Creating repository: {REPO_ID}")
    try:
        create_repo(
            repo_id=REPO_ID,
            repo_type=REPO_TYPE,
            exist_ok=True,
            private=False
        )
        print(f"   ✓ Repository created/verified: {REPO_ID}")
    except Exception as e:
        print(f"   ⚠️  Repository may already exist: {e}")
    
    # Upload files
    print(f"\n2. Uploading model artifacts...")
    for filename in FILES_TO_UPLOAD:
        if os.path.exists(filename):
            try:
                print(f"   Uploading {filename}...")
                upload_file(
                    path_or_fileobj=filename,
                    path_in_repo=filename,
                    repo_id=REPO_ID,
                    repo_type=REPO_TYPE
                )
                print(f"   ✓ {filename} uploaded")
            except Exception as e:
                print(f"   ✗ Failed to upload {filename}: {e}")
        else:
            print(f"   ⚠️  {filename} not found, skipping")
    
    # Print success message
    print("\n" + "="*60)
    print("✅ DEPLOYMENT COMPLETE")
    print("="*60)
    print(f"\n🎉 fraud-signal-classifier-v1 published successfully")
    print(f"\n📦 Model URL: https://huggingface.co/{REPO_ID}")
    print("\n⚠️  Remember: This is a synthetic educational model")
    print("   Human-in-the-loop validation required for all predictions")
    print("\n" + "="*60)
    print("\n🔗 NEXT STEP: Connect to fraud-triage-sandbox")
    print("   to enable hybrid logic (ML + rule-based)")
    print("="*60)

if __name__ == "__main__":
    deploy_model()
