#!/usr/bin/env python3
"""
Deploy premium-lapse-monitor to Hugging Face
This script handles the authentication and deployment of the premium-lapse-monitor space
"""

import os
from huggingface_hub import login, whoami, create_repo
from huggingface_hub import HfApi
import sys
import argparse

def deploy_premium_lapse_monitor():
    """
    Deploy the premium-lapse-monitor space to Hugging Face
    """
    print("🚀 Deploying premium-lapse-monitor to Hugging Face...")
    print("Organization: gcc-insurance-intelligence-lab")
    print()
    
    # Change to the premium-lapse-monitor directory
    repo_path = "premium-lapse-monitor"
    if not os.path.exists(repo_path):
        print(f"❌ Directory {repo_path} does not exist")
        return False
    
    original_cwd = os.getcwd()
    os.chdir(repo_path)
    
    try:
        # Check if we have the required files
        required_files = ["app.py", "requirements.txt", "README.md", "model_card.md"]
        missing_files = []
        
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing required files: {missing_files}")
            return False
        
        print("✅ All required files present")
        
        # Attempt authentication
        print("\n🔐 Authenticating with Hugging Face...")
        print("Please enter your Hugging Face access token when prompted.")
        print("Note: The token will not be visible as you type for security.")
        
        try:
            login()
            
            # Verify authentication
            user_info = whoami()
            print(f"✅ Successfully authenticated as: {user_info['name']}")
            
        except KeyboardInterrupt:
            print("\n❌ Authentication cancelled by user")
            return False
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
        
        # Create repository on Hugging Face
        repo_id = "gcc-insurance-intelligence-lab/premium-lapse-monitor"
        print(f"\n📦 Creating repository: {repo_id}")
        
        create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="gradio",
            exist_ok=True,
            private=False
        )
        
        # Upload files using the HfApi
        api = HfApi()
        
        files_to_upload = ["app.py", "requirements.txt", "README.md", "model_card.md"]
        
        print("\n📤 Uploading files...")
        for filename in files_to_upload:
            if os.path.exists(filename):
                print(f"  Uploading {filename}...")
                api.upload_file(
                    path_or_fileobj=os.path.abspath(filename),
                    path_in_repo=filename,
                    repo_id=repo_id,
                    repo_type="space"
                )
                print(f"  ✅ {filename} uploaded")
            else:
                print(f"  ⚠️ {filename} not found, skipping")
        
        print(f"\n🎉 Successfully deployed to: https://huggingface.co/spaces/{repo_id}")
        print(f"📋 Repository: {repo_id}")
        print(f"🌐 URL: https://huggingface.co/spaces/{repo_id}")
        print()
        print("💡 The Space may take a few minutes to fully initialize and become available.")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Restore original directory
        os.chdir(original_cwd)

def main():
    """
    Main function to handle the deployment
    """
    parser = argparse.ArgumentParser(description='Deploy premium-lapse-monitor to Hugging Face')
    parser.add_argument('--skip-auth', action='store_true', help='Skip authentication step (for testing)')
    
    args = parser.parse_args()
    
    print("🔐 GCC Insurance Intelligence Lab - Deploy Premium Lapse Monitor")
    print("=" * 70)
    
    if args.skip_auth:
        print("⚠️  Skipping authentication (testing mode)")
        # In testing mode, we'd use an API key from environment
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            print("❌ HF_TOKEN environment variable not set")
            return False
    else:
        success = deploy_premium_lapse_monitor()
        if success:
            print("\n✅ Deployment completed successfully!")
        else:
            print("\n❌ Deployment failed.")
            sys.exit(1)

if __name__ == "__main__":
    main()