"""
Script to push underwriting-score-sandbox to Hugging Face Hub
"""

from huggingface_hub import HfApi, create_repo
import os

def push_space():
    api = HfApi()
    
    # Repository details
    repo_id = "gcc-insurance-intelligence-lab/underwriting-score-sandbox"
    repo_type = "space"
    space_sdk = "gradio"
    
    print(f"Creating/updating repository: {repo_id}")
    
    # Create the repository
    create_repo(
        repo_id=repo_id,
        repo_type=repo_type,
        space_sdk=space_sdk,
        exist_ok=True,
        private=False
    )
    
    # Upload all files
    files_to_upload = [
        "app.py",
        "requirements.txt", 
        "README.md",
        "model_card.md",
        "underwriting_rules.py",
        "risk_profiles_synthetic.csv"
    ]
    
    for filename in files_to_upload:
        if os.path.exists(filename):
            print(f"Uploading {filename}...")
            api.upload_file(
                path_or_fileobj=f"./{filename}",
                path_in_repo=filename,
                repo_id=repo_id,
                repo_type=repo_type
            )
            print(f"✓ {filename} uploaded")
        else:
            print(f"⚠️ {filename} not found")
    
    print(f"\n✅ Repository {repo_id} has been updated on Hugging Face Hub!")
    print(f"URL: https://huggingface.co/spaces/{repo_id}")

if __name__ == "__main__":
    push_space()
