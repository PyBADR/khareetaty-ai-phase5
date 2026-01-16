#!/usr/bin/env python3
"""
Hub Orchestrator - Automated gcc-insurance-ai-hub Updates

This script:
- Auto-updates gcc-insurance-ai-hub repository
- Adds buttons for newly published Spaces
- Syncs README index
- Lists datasets and models linked
- Pushes updates to HuggingFace
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_utils import AutomationUtils


class HubOrchestrator:
    """Manages gcc-insurance-ai-hub updates and synchronization"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.hub_repo = self.base_path / "gcc-insurance-ai-hub"
        self.hf_org = "gcc-insurance-intelligence-lab"
        self.utils = AutomationUtils(str(self.base_path))
        
    def discover_spaces(self) -> List[Dict]:
        """Discover all Spaces (repos with app.py)"""
        print("\n🔍 Discovering Spaces...")
        spaces = []
        
        repos = self.utils.find_repos()
        for repo in repos:
            # Skip the hub itself
            if repo.name == "gcc-insurance-ai-hub":
                continue
                
            app_file = repo / "app.py"
            if app_file.exists():
                # Extract metadata
                space_info = self._extract_space_metadata(repo)
                spaces.append(space_info)
                print(f"  ✓ Found Space: {repo.name}")
                
        print(f"\n📊 Total Spaces discovered: {len(spaces)}")
        return spaces
    
    def _extract_space_metadata(self, repo_path: Path) -> Dict:
        """Extract metadata from a Space repository"""
        metadata = {
            "name": repo_path.name,
            "title": repo_path.name.replace('-', ' ').replace('_', ' ').title(),
            "path": str(repo_path),
            "url": f"https://huggingface.co/spaces/{self.hf_org}/{repo_path.name}",
            "has_model": (repo_path / "models").exists(),
            "has_dataset": (repo_path / "data").exists(),
            "description": ""
        }
        
        # Try to extract description from README
        readme_path = repo_path / "README.md"
        if readme_path.exists():
            try:
                with open(readme_path, 'r') as f:
                    lines = f.readlines()
                    # Look for first paragraph after title
                    for i, line in enumerate(lines):
                        if line.strip() and not line.startswith('#') and not line.startswith('---'):
                            metadata["description"] = line.strip()[:200]
                            break
            except Exception as e:
                print(f"  ⚠️  Could not read README for {repo_path.name}: {e}")
                
        return metadata
    
    def discover_models(self) -> List[Dict]:
        """Discover all models across repositories"""
        print("\n🤖 Discovering Models...")
        models = []
        
        repos = self.utils.find_repos()
        for repo in repos:
            models_dir = repo / "models"
            if models_dir.exists():
                # Check for packaged models
                for item in models_dir.iterdir():
                    if item.is_dir() and '_v' in item.name:
                        config_file = item / "config.json"
                        if config_file.exists():
                            try:
                                with open(config_file, 'r') as f:
                                    config = json.load(f)
                                    models.append({
                                        "name": config.get("model_name", item.name),
                                        "version": config.get("version", "unknown"),
                                        "repository": repo.name,
                                        "path": str(item)
                                    })
                                    print(f"  ✓ Found Model: {config.get('model_name')} ({config.get('version')})")
                            except Exception as e:
                                print(f"  ⚠️  Error reading model config: {e}")
                                
        print(f"\n📊 Total Models discovered: {len(models)}")
        return models
    
    def discover_datasets(self) -> List[Dict]:
        """Discover all datasets across repositories"""
        print("\n📊 Discovering Datasets...")
        datasets = []
        
        repos = self.utils.find_repos()
        for repo in repos:
            data_dir = repo / "data"
            if data_dir.exists():
                registry_file = data_dir / ".dataset_registry.json"
                if registry_file.exists():
                    try:
                        with open(registry_file, 'r') as f:
                            registry = json.load(f)
                            for dataset in registry.get("datasets", []):
                                datasets.append({
                                    "name": dataset["filename"],
                                    "repository": repo.name,
                                    "size": dataset.get("size_bytes", 0),
                                    "synthetic": dataset.get("synthetic", True)
                                })
                                print(f"  ✓ Found Dataset: {dataset['filename']} in {repo.name}")
                    except Exception as e:
                        print(f"  ⚠️  Error reading dataset registry: {e}")
                        
        print(f"\n📊 Total Datasets discovered: {len(datasets)}")
        return datasets
    
    def generate_space_buttons(self, spaces: List[Dict]) -> str:
        """Generate HTML buttons for Spaces"""
        buttons_html = "## 🚀 Available Spaces\n\n"
        buttons_html += "<div style='display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; margin: 20px 0;'>\n\n"
        
        # Sort spaces alphabetically
        sorted_spaces = sorted(spaces, key=lambda x: x['title'])
        
        for space in sorted_spaces:
            # Determine icon based on space type
            icon = "📊"  # Default
            if "fraud" in space['name'].lower():
                icon = "🔍"
            elif "claim" in space['name'].lower():
                icon = "📝"
            elif "risk" in space['name'].lower():
                icon = "⚠️"
            elif "price" in space['name'].lower() or "premium" in space['name'].lower():
                icon = "💰"
            elif "underwriting" in space['name'].lower():
                icon = "📊"
                
            button_html = f"""<a href="{space['url']}" target="_blank" style="text-decoration: none;">
    <div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; transition: transform 0.2s;">
        <h3 style="margin: 0 0 10px 0; color: white;">{icon} {space['title']}</h3>
        <p style="margin: 0; font-size: 14px; opacity: 0.9;">{space['description'][:100] if space['description'] else 'Insurance AI Application'}</p>
        <div style="margin-top: 10px; font-size: 12px; opacity: 0.8;">
            {'🤖 Model' if space['has_model'] else ''} {'📊 Dataset' if space['has_dataset'] else ''}
        </div>
    </div>
</a>\n\n"""
            buttons_html += button_html
            
        buttons_html += "</div>\n\n"
        return buttons_html
    
    def generate_models_section(self, models: List[Dict]) -> str:
        """Generate models section for README"""
        if not models:
            return ""
            
        section = "## 🤖 Available Models\n\n"
        section += "| Model Name | Version | Repository | Status |\n"
        section += "|------------|---------|------------|--------|\n"
        
        for model in sorted(models, key=lambda x: x['name']):
            section += f"| {model['name']} | {model['version']} | {model['repository']} | ✅ Ready |\n"
            
        section += "\n"
        return section
    
    def generate_datasets_section(self, datasets: List[Dict]) -> str:
        """Generate datasets section for README"""
        if not datasets:
            return ""
            
        section = "## 📊 Available Datasets\n\n"
        section += "| Dataset Name | Repository | Size | Type |\n"
        section += "|--------------|------------|------|------|\n"
        
        for dataset in sorted(datasets, key=lambda x: x['name']):
            size_kb = dataset['size'] / 1024 if dataset['size'] > 0 else 0
            section += f"| {dataset['name']} | {dataset['repository']} | {size_kb:.1f} KB | ✅ Synthetic |\n"
            
        section += "\n"
        return section
    
    def update_hub_readme(self, spaces: List[Dict], models: List[Dict], datasets: List[Dict]) -> bool:
        """Update the hub README with current inventory"""
        print("\n📝 Updating Hub README...")
        
        if not self.hub_repo.exists():
            print(f"  ⚠️  Hub repository not found at {self.hub_repo}")
            return False
            
        readme_path = self.hub_repo / "README.md"
        
        # Generate new README content
        readme_content = f"""---
title: GCC Insurance Intelligence Lab Hub
emoji: 🏭
colorFrom: blue
colorTo: purple
sdk: static
pinned: true
---

# 🏭 GCC Insurance Intelligence Lab

**Welcome to the Insurance AI Factory!**

This hub provides access to all insurance AI applications, models, and datasets developed by the GCC Insurance Intelligence Lab.

⚠️ **All content is for educational and research purposes only. Built with 100% synthetic data.**

---

{self.generate_space_buttons(spaces)}

---

{self.generate_models_section(models)}

---

{self.generate_datasets_section(datasets)}

---

## 🛡️ Governance & Safety

### Core Principles

✅ **Synthetic Data Only**: All models and datasets use 100% synthetic data
✅ **Human-in-Loop**: All predictions require human review
✅ **Educational Purpose**: For learning and demonstration only
❌ **No Production Authority**: Not for actual underwriting, pricing, or payout decisions
❌ **No PII**: No personally identifiable information
❌ **No Confidential Data**: No real business or customer data

### Disclaimers

**IMPORTANT**: These applications and models:
- Are NOT validated for production use
- Have NO underwriting authority
- Have NO pricing authority  
- Have NO payout decision authority
- Must NOT be used with real customer data
- Require qualified professional oversight

---

## 🛠️ Platform Automation

This lab features automated:
- ✅ Repository generation
- ✅ CI/CD deployment
- ✅ Model packaging and versioning
- ✅ Dataset management
- ✅ Hub synchronization
- ✅ Code quality enforcement
- ✅ Governance validation

### Quick Start

To add a new use case:
```bash
/add-usecase <use-case-name>
```

---

## 📚 Documentation

- [Automation Playbook](./lab-automation-playbook.md)
- [Developer Guide](./developer-guide.md)
- [Governance Rules](./governance-rules.md)
- [Add Use Case Template](./add-usecase-template.md)

---

## 📊 Statistics

- **Total Spaces**: {len(spaces)}
- **Total Models**: {len(models)}
- **Total Datasets**: {len(datasets)}
- **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 👥 Contact

For questions, issues, or contributions, please refer to the individual repository documentation.

---

**Status**: 🟢 Production Ready - Insurance AI Factory Mode Activated

*Generated automatically by Hub Orchestrator*
"""
        
        # Write README
        try:
            with open(readme_path, 'w') as f:
                f.write(readme_content)
            print(f"  ✓ README updated successfully")
            print(f"  📊 {len(spaces)} Spaces, {len(models)} Models, {len(datasets)} Datasets")
            return True
        except Exception as e:
            print(f"  ❌ Error writing README: {e}")
            return False
    
    def push_to_huggingface(self) -> bool:
        """Push hub updates to HuggingFace"""
        print("\n🚀 Pushing updates to HuggingFace...")
        
        if not self.hub_repo.exists():
            print(f"  ⚠️  Hub repository not found")
            return False
            
        try:
            # Git add
            result = self.utils.run_command("git add .", cwd=str(self.hub_repo))
            if not result["success"]:
                print(f"  ⚠️  Git add failed: {result['error']}")
                return False
                
            # Git commit
            commit_msg = f"Auto-update hub - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            result = self.utils.run_command(f'git commit -m "{commit_msg}"', cwd=str(self.hub_repo))
            if not result["success"] and "nothing to commit" not in result["error"]:
                print(f"  ⚠️  Git commit failed: {result['error']}")
                return False
                
            # Git push
            result = self.utils.run_command("git push", cwd=str(self.hub_repo))
            if not result["success"]:
                print(f"  ⚠️  Git push failed: {result['error']}")
                print(f"  💡 You may need to configure git credentials or push manually")
                return False
                
            print(f"  ✓ Successfully pushed to HuggingFace")
            return True
            
        except Exception as e:
            print(f"  ❌ Error pushing to HuggingFace: {e}")
            return False
    
    def orchestrate(self, push: bool = False) -> Dict:
        """Main orchestration workflow"""
        print("\n" + "="*60)
        print("🏭 HUB ORCHESTRATOR - Synchronizing gcc-insurance-ai-hub")
        print("="*60)
        
        # Discover all resources
        spaces = self.discover_spaces()
        models = self.discover_models()
        datasets = self.discover_datasets()
        
        # Update hub README
        readme_updated = self.update_hub_readme(spaces, models, datasets)
        
        # Optionally push to HuggingFace
        pushed = False
        if push and readme_updated:
            pushed = self.push_to_huggingface()
            
        # Summary
        summary = {
            "spaces_discovered": len(spaces),
            "models_discovered": len(models),
            "datasets_discovered": len(datasets),
            "readme_updated": readme_updated,
            "pushed_to_hf": pushed,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save summary
        summary_file = self.base_path / "automation" / "hub_orchestration_summary.json"
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        print("\n" + "="*60)
        print("✅ HUB ORCHESTRATION COMPLETE")
        print("="*60)
        print(f"Spaces: {len(spaces)} | Models: {len(models)} | Datasets: {len(datasets)}")
        print(f"README Updated: {'Yes' if readme_updated else 'No'}")
        print(f"Pushed to HF: {'Yes' if pushed else 'No'}")
        
        return summary


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Hub Orchestrator - Automated gcc-insurance-ai-hub updates"
    )
    parser.add_argument(
        '--push',
        action='store_true',
        help='Push updates to HuggingFace after updating'
    )
    parser.add_argument(
        '--base-path',
        default=os.getcwd(),
        help='Base path for repositories'
    )
    
    args = parser.parse_args()
    
    orchestrator = HubOrchestrator(args.base_path)
    orchestrator.orchestrate(push=args.push)
    
    print("\n✅ Hub orchestration complete!")


if __name__ == "__main__":
    main()
