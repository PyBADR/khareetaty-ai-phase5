#!/usr/bin/env python3
"""
Deploy claims-journey-simulator to Hugging Face
"""

import os
import subprocess
import sys

def deploy():
    print("\n🚀 Deploying claims-journey-simulator to Hugging Face...")
    
    # Check if huggingface-cli is installed
    try:
        subprocess.run(["huggingface-cli", "--version"], check=True, capture_output=True)
    except:
        print("❌ Error: huggingface-cli not found. Install with: pip install huggingface_hub")
        sys.exit(1)
    
    # Check authentication
    print("\n🔑 Checking Hugging Face authentication...")
    result = subprocess.run(["huggingface-cli", "whoami"], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Not logged in to Hugging Face")
        print("Please run: huggingface-cli login")
        sys.exit(1)
    
    print(f"✅ Authenticated as: {result.stdout.strip()}")
    
    # Create space
    space_name = "claims-journey-simulator"
    org_name = "gcc-insurance-intelligence-lab"  # Update with your org
    
    print(f"\n🏭 Creating Hugging Face Space: {org_name}/{space_name}")
    
    # Note: Actual deployment would use huggingface_hub API
    print("⚠️  Manual deployment required:")
    print(f"   1. Create space at: https://huggingface.co/new-space")
    print(f"   2. Name: {space_name}")
    print(f"   3. Upload files from this directory")
    print(f"   4. Or use: huggingface-cli upload {org_name}/{space_name} . --repo-type=space")
    
    print("\n✅ Deployment instructions provided")

if __name__ == "__main__":
    deploy()
