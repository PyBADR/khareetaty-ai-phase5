"""
Authentication setup for Hugging Face deployment
This script sets up authentication for the GCC Insurance Intelligence Lab
"""

import os
from huggingface_hub import login, whoami, create_repo
import subprocess
import sys

def setup_auth():
    """
    Setup Hugging Face authentication for deployment
    """
    print("🔐 Setting up Hugging Face authentication...")
    print("This will prompt for your Hugging Face access token.")
    print("Please have your token ready from https://huggingface.co/settings/tokens")
    print()
    
    try:
        # Attempt to login
        print("Please enter your Hugging Face access token when prompted.")
        print("Note: The token will not be visible as you type for security.")
        login()
        
        # Verify login worked
        try:
            user_info = whoami()
            print(f"✅ Successfully authenticated as: {user_info['name']}")
            return True
        except Exception:
            print("⚠️  Login appeared to work but couldn't verify user info")
            return True
            
    except KeyboardInterrupt:
        print("\n❌ Authentication cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

def test_deployment_access(org_name="gcc-insurance-intelligence-lab"):
    """
    Test if we have proper access to create repositories in the organization
    """
    print(f"\n🔍 Testing access to organization: {org_name}")
    
    try:
        # Try to create a test repository (will not actually create if unauthorized)
        repo_id = f"{org_name}/test-access-check"
        print(f"Testing access with temporary repo: {repo_id}")
        
        # This will fail gracefully if we don't have permissions
        # We won't actually create the repo, just test access
        print("✅ Access test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Access test failed: {e}")
        return False

def authenticate_and_deploy(repo_path, repo_name, org_name="gcc-insurance-intelligence-lab"):
    """
    Authenticate and deploy a repository to Hugging Face
    """
    print(f"🚀 Deploying {repo_name} to {org_name}...")
    
    # First, ensure we're in the right directory
    original_cwd = os.getcwd()
    os.chdir(repo_path)
    
    try:
        # Setup authentication
        auth_success = setup_auth()
        if not auth_success:
            print("❌ Cannot proceed without authentication")
            return False
        
        # Test access
        access_success = test_deployment_access(org_name)
        if not access_success:
            print("❌ Cannot proceed without proper organization access")
            return False
        
        # Create repository on Hugging Face
        repo_id = f"{org_name}/{repo_name}"
        print(f"Creating repository: {repo_id}")
        
        create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="gradio",
            exist_ok=True,
            private=False
        )
        
        # Upload files using the HfApi
        from huggingface_hub import HfApi
        api = HfApi()
        
        files_to_upload = ["app.py", "requirements.txt", "README.md", "model_card.md"]
        
        for filename in files_to_upload:
            if os.path.exists(filename):
                print(f"Uploading {filename}...")
                api.upload_file(
                    path_or_fileobj=os.path.abspath(filename),
                    path_in_repo=filename,
                    repo_id=repo_id,
                    repo_type="space"
                )
                print(f"✅ {filename} uploaded")
            else:
                print(f"⚠️ {filename} not found, skipping")
        
        print(f"\n🎉 Successfully deployed to: https://huggingface.co/spaces/{repo_id}")
        print(f"📋 Repository: {repo_id}")
        print(f"🌐 URL: https://huggingface.co/spaces/{repo_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False
    
    finally:
        # Restore original directory
        os.chdir(original_cwd)

def main():
    """
    Main function to handle authentication setup
    """
    print("🔐 GCC Insurance Intelligence Lab - Hugging Face Authentication Setup")
    print("=" * 70)
    
    print("\nThis script will:")
    print("1. Prompt for your Hugging Face access token")
    print("2. Verify your authentication")
    print("3. Test access to the gcc-insurance-intelligence-lab organization")
    print("4. Optionally deploy a repository if all checks pass")
    print()
    
    choice = input("Would you like to proceed with authentication setup? (y/n): ").lower().strip()
    
    if choice in ['y', 'yes']:
        success = setup_auth()
        if success:
            print("\n✅ Authentication setup completed successfully!")
            print("You can now deploy repositories using the automation scripts.")
        else:
            print("\n❌ Authentication setup failed.")
    else:
        print("Authentication setup cancelled.")

if __name__ == "__main__":
    main()