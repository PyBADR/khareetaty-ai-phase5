"""
Hub Orchestration System
Auto-update gcc-insurance-ai-hub with newly published Spaces
"""

import os
import json
from pathlib import Path
import re
from datetime import datetime

class HubOrchestrator:
    """
    Auto-update gcc-insurance-ai-hub with newly published Spaces
    """
    
    def __init__(self, hub_path="gcc-insurance-ai-hub", spaces_base_path="."):
        self.hub_path = Path(hub_path)
        self.spaces_base_path = Path(spaces_base_path)
        self.index_file = self.hub_path / "README.md"
        
        # Define known spaces to look for
        self.known_spaces = [
            "underwriting-score-sandbox",
            "fnol-fast-track-screener", 
            "claims-journey-simulator",
            "reinsurance-pricing-mock",
            "fraud-audit-log-engine",
            "fraud-triage-sandbox",
            "fraud-signal-classifier-v1"
        ]
    
    def find_all_spaces(self):
        """Find all potential space directories"""
        spaces = []
        
        # Look for directories with the required files
        for item in self.spaces_base_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                required_files = ['app.py', 'README.md', 'model_card.md', 'requirements.txt']
                has_required_files = all((item / file).exists() for file in required_files)
                
                if has_required_files:
                    spaces.append(item.name)
        
        return spaces
    
    def update_hub_index(self, spaces_list):
        """Update the main hub README with links to all spaces"""
        if not self.index_file.exists():
            print(f"Hub index file not found: {self.index_file}")
            return False
        
        # Read current content
        with open(self.index_file, 'r') as f:
            content = f.read()
        
        # Create new spaces section
        spaces_section = "\n## Available Insurance AI Spaces\n\n"
        for space in sorted(spaces_list):
            # Convert space name to title format
            title = space.replace('-', ' ').title()
            spaces_section += f"- [{title}](https://huggingface.co/spaces/gcc-insurance-intelligence-lab/{space}) - {title}\n"
        
        spaces_section += "\n"
        
        # Look for existing spaces section and replace it, or add a new one
        if "## Available Insurance AI Spaces" in content:
            # Find and replace the existing section
            start_idx = content.find("## Available Insurance AI Spaces")
            end_idx = content.find("\n## ", start_idx + 1)  # Next section
            if end_idx == -1:
                end_idx = len(content)  # End of file
            
            new_content = content[:start_idx] + spaces_section + content[end_idx:]
        else:
            # Add new section after main heading
            main_heading_end = content.find("\n", content.find("#")) + 1
            new_content = content[:main_heading_end] + spaces_section + content[main_heading_end:]
        
        # Write updated content
        with open(self.index_file, 'w') as f:
            f.write(new_content)
        
        print(f"✓ Updated hub index with {len(spaces_list)} spaces")
        return True
    
    def update_hub_with_datasets(self):
        """Update the hub with dataset information"""
        # Look for dataset directories
        dataset_dirs = []
        for item in self.spaces_base_path.iterdir():
            if item.is_dir() and ('dataset' in item.name.lower() or 'data' in item.name.lower()):
                dataset_dirs.append(item.name)
        
        if not dataset_dirs:
            return
        
        if not self.index_file.exists():
            return
        
        # Read current content
        with open(self.index_file, 'r') as f:
            content = f.read()
        
        # Create datasets section
        datasets_section = "\n## Available Datasets\n\n"
        for dataset in sorted(dataset_dirs):
            title = dataset.replace('-', ' ').title()
            datasets_section += f"- {title} - {dataset}\n"
        
        datasets_section += "\n"
        
        # Add or update datasets section
        if "## Available Datasets" in content:
            start_idx = content.find("## Available Datasets")
            end_idx = content.find("\n## ", start_idx + 1)
            if end_idx == -1:
                end_idx = len(content)
            
            new_content = content[:start_idx] + datasets_section + content[end_idx:]
        else:
            # Add after spaces section or main content
            if "## Available Insurance AI Spaces" in content:
                spaces_end = content.find("\n## ", content.find("## Available Insurance AI Spaces") + 1)
                if spaces_end == -1:
                    spaces_end = len(content)
                new_content = content[:spaces_end] + datasets_section + content[spaces_end:]
            else:
                main_heading_end = content.find("\n", content.find("#")) + 1
                new_content = content[:main_heading_end] + datasets_section + content[main_heading_end:]
        
        # Write updated content
        with open(self.index_file, 'w') as f:
            f.write(new_content)
        
        print(f"✓ Updated hub index with {len(dataset_dirs)} datasets")
    
    def update_hub_with_models(self):
        """Update the hub with model information"""
        # Look for model directories or model files
        model_dirs = []
        for item in self.spaces_base_path.iterdir():
            if item.is_dir() and ('model' in item.name.lower() or 'classifier' in item.name.lower()):
                model_dirs.append(item.name)
        
        # Also look for model files in models directory
        models_dir = self.spaces_base_path / "models"
        if models_dir.exists():
            for model_file in models_dir.glob("*"):
                if model_file.suffix in ['.pkl', '.joblib', '.bin', '.pt', '.h5', '.onnx', '.model']:
                    model_dirs.append(model_file.name)
        
        if not model_dirs:
            return
        
        if not self.index_file.exists():
            return
        
        # Read current content
        with open(self.index_file, 'r') as f:
            content = f.read()
        
        # Create models section
        models_section = "\n## Available Models\n\n"
        for model in sorted(set(model_dirs)):  # Use set to avoid duplicates
            title = model.replace('-', ' ').replace('_', ' ').title()
            models_section += f"- {title} - {model}\n"
        
        models_section += "\n"
        
        # Add or update models section
        if "## Available Models" in content:
            start_idx = content.find("## Available Models")
            end_idx = content.find("\n## ", start_idx + 1)
            if end_idx == -1:
                end_idx = len(content)
            
            new_content = content[:start_idx] + models_section + content[end_idx:]
        else:
            # Add after datasets section or other content
            sections_to_check = ["## Available Datasets", "## Available Insurance AI Spaces"]
            insert_position = -1
            
            for section in sections_to_check:
                if section in content:
                    insert_position = content.find(section)
                    insert_position = content.find("\n## ", insert_position + 1)
                    if insert_position == -1:
                        insert_position = len(content)
                    break
            
            if insert_position == -1:
                # Default to after main heading
                insert_position = content.find("\n", content.find("#")) + 1
            
            if insert_position == 0:
                insert_position = len(content)
            
            new_content = content[:insert_position] + models_section + content[insert_position:]
        
        # Write updated content
        with open(self.index_file, 'w') as f:
            f.write(new_content)
        
        print(f"✓ Updated hub index with {len(model_dirs)} models")
    
    def sync_hub(self):
        """Sync the entire hub with current spaces, datasets, and models"""
        print("🔄 Syncing hub with current assets...")
        
        # Find all spaces
        spaces = self.find_all_spaces()
        print(f"Found {len(spaces)} spaces: {', '.join(spaces)}")
        
        # Update hub index
        if spaces:
            self.update_hub_index(spaces)
        
        # Update with datasets
        self.update_hub_with_datasets()
        
        # Update with models
        self.update_hub_with_models()
        
        print("✅ Hub synchronization complete")


def run_hub_sync():
    """Run the hub orchestration to update the main hub"""
    orchestrator = HubOrchestrator()
    orchestrator.sync_hub()


if __name__ == "__main__":
    run_hub_sync()