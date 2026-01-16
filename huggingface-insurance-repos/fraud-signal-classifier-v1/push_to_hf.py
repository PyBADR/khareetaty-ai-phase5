"""
Push fraud-signal-classifier-v1 to Hugging Face Hub

This script uploads the trained model and all artifacts to Hugging Face
under the gcc-insurance-intelligence-lab organization.
"""

from huggingface_hub import HfApi, create_repo, upload_file, upload_folder
import os

# Configuration
REPO_ID = "gcc-insurance-intelligence-lab/fraud-signal-classifier-v1"
REPO_TYPE = "model"
LOCAL_DIR = "."

def push_to_huggingface():
    """Push model artifacts to Hugging Face Hub"""
    print("=" * 70)
    print("🚀 PUSHING MODEL TO HUGGING FACE HUB")
    print("=" * 70)
    print(f"\n📦 Repository: {REPO_ID}")
    
    # Initialize API
    api = HfApi()
    
    # Check if files exist
    required_files = [
        'model.pkl',
        'label_encoders.pkl',
        'feature_names.json',
        'train_model.py',
        'inference.py',
        'requirements.txt',
        'README.md',
        'model_card.md'
    ]
    
    print("\n✅ Checking files...")
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ ERROR: Missing files: {missing_files}")
        return False
    
    try:
        # Create repository if it doesn't exist
        print(f"\n🔧 Creating repository (if not exists)...")
        create_repo(
            repo_id=REPO_ID,
            repo_type=REPO_TYPE,
            exist_ok=True,
            private=False
        )
        print(f"✓ Repository ready: {REPO_ID}")
        
        # Upload files
        print(f"\n📤 Uploading files to Hugging Face...")
        
        for file in required_files:
            print(f"  Uploading {file}...")
            upload_file(
                path_or_fileobj=file,
                path_in_repo=file,
                repo_id=REPO_ID,
                repo_type=REPO_TYPE,
            )
            print(f"  ✓ {file} uploaded")
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS: fraud-signal-classifier-v1 published successfully")
        print("=" * 70)
        print(f"\n🔗 Model URL:")
        print(f"   https://huggingface.co/{REPO_ID}")
        print(f"\n📊 Next Steps:")
        print(f"   1. Verify model on Hugging Face")
        print(f"   2. Test inference from Hub")
        print(f"   3. Integrate with fraud-triage-sandbox")
        print(f"\n⚠️  Remember: Educational use only - Human review required")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to push to Hugging Face")
        print(f"   {str(e)}")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Check you're logged in: huggingface-cli login")
        print(f"   2. Verify organization access: {REPO_ID.split('/')[0]}")
        print(f"   3. Check internet connection")
        return False

if __name__ == "__main__":
    success = push_to_huggingface()
    
    if success:
        print("\n" + "=" * 70)
        print("🎉 DEPLOYMENT COMPLETE")
        print("=" * 70)
        print("\n📍 Model ready. Connect to fraud-triage-sandbox to enable hybrid logic.")
        print(f"   https://huggingface.co/{REPO_ID}")
    else:
        print("\n❌ Deployment failed. Please check errors above.")
