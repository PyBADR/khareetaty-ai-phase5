#!/usr/bin/env python3
"""
Insurance AI Factory - Complete Automation System

Enables platform automation for gcc-insurance-intelligence-lab so new use cases can be:
✔ Generated
✔ Validated  
✔ Published
✔ Linked
without manual effort.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import json
from datetime import datetime

# Import our automation components
from add_usecase import main as add_usecase_main
from model_registry_hook import run_model_registry_hook
from hub_orchestrator import run_hub_sync
from logging_utility import InsuranceAILogger


class InsuranceAIPlatformFactory:
    """
    Complete automation system for the GCC Insurance Intelligence Lab
    """
    
    def __init__(self):
        self.logger = InsuranceAILogger(app_name="platform-factory")
        self.base_path = Path.cwd()
        
    def initialize_factory(self):
        """Initialize the complete automation infrastructure"""
        print("🏭 Initializing Insurance AI Factory...")
        
        # Ensure required directories exist
        dirs_to_create = [
            ".github/workflows",
            "models",
            "datasets",
            "logs"
        ]
        
        for dir_path in dirs_to_create:
            full_path = self.base_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {full_path}")
        
        # Copy workflow template if not exists
        workflow_path = self.base_path / ".github/workflows/lab-ci-template.yml"
        if not workflow_path.exists():
            print("⚠️  Workflow template not found in expected location")
        else:
            print("✓ Workflow template verified")
        
        print("✅ Insurance AI Factory initialized")
    
    def generate_repository(self, usecase_name, datasets=None):
        """Generate a new repository using the add-usecase system"""
        print(f"🏗️  Generating repository: {usecase_name}")
        
        # Prepare arguments for add_usecase
        args = [usecase_name]
        if datasets:
            args.extend(["--datasets"] + datasets)
        
        # Call the add-usecase functionality directly
        import sys
        original_argv = sys.argv
        sys.argv = ["add_usecase"] + args
        
        try:
            # Import and run the add_usecase main function
            import importlib.util
            spec = importlib.util.spec_from_file_location("add_usecase_module", "add_usecase.py")
            add_usecase_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(add_usecase_module)
            
            # Create argument namespace
            from argparse import Namespace
            args_namespace = Namespace(name=usecase_name, datasets=datasets)
            
            # Run the creation process
            add_usecase_module.usecase_name = usecase_name
            add_usecase_module.main = lambda: None  # Override main to avoid arg parsing
            
            # Actually create the files
            usecase_dir = Path(usecase_name)
            if usecase_dir.exists():
                print(f"⚠️  Directory {usecase_name} already exists, skipping creation")
            else:
                # Execute the creation process
                os.system(f"python add_usecase.py {usecase_name} {' '.join(['--datasets'] + datasets) if datasets else ''}")
                
            print(f"✅ Repository {usecase_name} generated")
            return True
            
        except Exception as e:
            print(f"❌ Error generating repository: {e}")
            return False
        finally:
            sys.argv = original_argv
    
    def validate_repository(self, repo_path):
        """Validate a repository meets all requirements"""
        print(f"🔍 Validating repository: {repo_path}")
        
        repo_path = Path(repo_path)
        if not repo_path.exists():
            print(f"❌ Repository {repo_path} does not exist")
            return False
        
        # Check required files
        required_files = ["app.py", "requirements.txt", "README.md", "model_card.md"]
        missing_files = []
        
        for file in required_files:
            if not (repo_path / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing required files: {missing_files}")
            return False
        
        # Run smoke tests if they exist
        test_file = repo_path / "test_smoke.py"
        if test_file.exists():
            print("🧪 Running smoke tests...")
            result = subprocess.run([
                sys.executable, str(test_file)
            ], cwd=repo_path, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Smoke tests failed: {result.stderr}")
                return False
            else:
                print("✅ Smoke tests passed")
        
        # Check governance requirements
        readme_content = (repo_path / "README.md").read_text()
        model_card_content = (repo_path / "model_card.md").read_text()
        
        governance_keywords = [
            "synthetic", "educational", "human-in-the-loop", "disclaimer"
        ]
        
        for keyword in governance_keywords:
            if keyword.lower() not in readme_content.lower():
                print(f"⚠️  Governance keyword '{keyword}' not found in README")
            if keyword.lower() not in model_card_content.lower():
                print(f"⚠️  Governance keyword '{keyword}' not found in model_card")
        
        print(f"✅ Repository {repo_path} validated")
        return True
    
    def publish_to_hf(self, repo_path, hf_token=None, hf_username="gcc-insurance-intelligence-lab"):
        """Publish repository to Hugging Face (requires credentials)"""
        print(f"🚀 Publishing {repo_path} to Hugging Face...")
        
        repo_path = Path(repo_path)
        repo_name = repo_path.name
        
        # Check if huggingface_hub is available
        try:
            from huggingface_hub import HfApi, create_repo
        except ImportError:
            print("⚠️  huggingface_hub not installed, skipping publication")
            print("💡 Install with: pip install huggingface_hub")
            return False
        
        if not hf_token:
            print("⚠️  No HF token provided, skipping publication")
            print("💡 Set HF_TOKEN environment variable to enable publication")
            return False
        
        try:
            api = HfApi()
            
            # Create/update space
            repo_id = f"{hf_username}/{repo_name}"
            print(f"Creating/updating repository: {repo_id}")
            
            create_repo(
                repo_id=repo_id,
                repo_type='space',
                space_sdk='gradio',
                exist_ok=True,
                private=False
            )
            
            # Upload files
            files_to_upload = ["app.py", "requirements.txt", "README.md", "model_card.md"]
            
            for file in files_to_upload:
                file_path = repo_path / file
                if file_path.exists():
                    api.upload_file(
                        path_or_fileobj=str(file_path),
                        path_in_repo=file,
                        repo_id=repo_id,
                        repo_type='space'
                    )
                    print(f"✓ Uploaded {file}")
            
            print(f"✅ Published to https://huggingface.co/spaces/{repo_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error publishing to Hugging Face: {e}")
            return False
    
    def link_to_hub(self, repo_name):
        """Link the new repository to the main hub"""
        print(f"🔗 Linking {repo_name} to main hub...")
        
        try:
            # Run the hub orchestrator to update the main index
            run_hub_sync()
            print(f"✅ {repo_name} linked to hub")
            return True
        except Exception as e:
            print(f"❌ Error linking to hub: {e}")
            return False
    
    def run_complete_pipeline(self, usecase_name, datasets=None, hf_token=None):
        """Run the complete pipeline: generate, validate, publish, link"""
        print(f"🚀 Starting complete pipeline for: {usecase_name}")
        
        # Step 1: Generate repository
        if not self.generate_repository(usecase_name, datasets):
            print("❌ Pipeline failed at generation step")
            return False
        
        # Step 2: Validate repository
        if not self.validate_repository(usecase_name):
            print("❌ Pipeline failed at validation step")
            return False
        
        # Step 3: Publish to Hugging Face (if token provided)
        if hf_token:
            if not self.publish_to_hf(usecase_name, hf_token):
                print("⚠️  Publication failed, but continuing with linking")
        else:
            print("⚠️  No HF token provided, skipping publication")
        
        # Step 4: Link to hub
        if not self.link_to_hub(usecase_name):
            print("⚠️  Linking failed, but pipeline completed")
        
        print(f"✅ Complete pipeline finished for: {usecase_name}")
        return True


def main():
    parser = argparse.ArgumentParser(description='Insurance AI Factory - Complete Automation System')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add usecase command
    add_parser = subparsers.add_parser('add-usecase', help='Add a new use case')
    add_parser.add_argument('name', help='Name of the new use case')
    add_parser.add_argument('--datasets', nargs='*', help='Optional synthetic datasets to create')
    add_parser.add_argument('--token', help='Hugging Face token for publication')
    
    # Initialize factory command
    init_parser = subparsers.add_parser('init', help='Initialize the factory')
    
    # Sync hub command
    sync_parser = subparsers.add_parser('sync-hub', help='Sync the main hub')
    
    # Register model command
    reg_parser = subparsers.add_parser('register-models', help='Register new models')
    
    args = parser.parse_args()
    
    factory = InsuranceAIPlatformFactory()
    
    if args.command == 'init':
        factory.initialize_factory()
        
    elif args.command == 'add-usecase':
        # Run the complete pipeline
        success = factory.run_complete_pipeline(
            usecase_name=args.name,
            datasets=args.datasets,
            hf_token=args.token
        )
        
        if success:
            print(f"\n🎉 Success! Use case '{args.name}' created and processed")
            print(f"📁 Location: {args.name}/")
            print(f"🌐 HF Space: https://huggingface.co/spaces/gcc-insurance-intelligence-lab/{args.name}")
        else:
            print(f"\n❌ Failed to create use case '{args.name}'")
            sys.exit(1)
            
    elif args.command == 'sync-hub':
        run_hub_sync()
        
    elif args.command == 'register-models':
        run_model_registry_hook()
        
    else:
        # Default: Show help
        parser.print_help()


if __name__ == "__main__":
    main()