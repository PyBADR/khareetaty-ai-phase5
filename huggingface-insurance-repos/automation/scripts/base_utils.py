#!/usr/bin/env python3
"""
Base Automation Utilities
Part of gcc-insurance-intelligence-lab Platform Automation
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import shutil

class AutomationUtils:
    """Base utilities for automation scripts"""
    
    def __init__(self, base_path="/Users/bdr.ai/huggingface-insurance-repos"):
        self.base_path = Path(base_path)
        self.automation_path = self.base_path / "automation"
        self.scripts_path = self.automation_path / "scripts"
        self.templates_path = self.automation_path / "templates"
    
    def run_command(self, command, cwd=None, capture_output=True):
        """Run a shell command and return the result"""
        try:
            if isinstance(command, str):
                command = command.split()
            
            result = subprocess.run(
                command,
                cwd=cwd or self.base_path,
                capture_output=capture_output,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def find_repos(self, pattern=None):
        """Find all repository directories"""
        repos = []
        
        for item in self.base_path.iterdir():
            if item.is_dir() and not item.name.startswith(".") and item.name != "automation":
                # Check if it looks like a repo (has app.py or README.md)
                if (item / "app.py").exists() or (item / "README.md").exists():
                    if pattern is None or pattern in item.name:
                        repos.append(item)
        
        return sorted(repos)
    
    def validate_governance(self, repo_path):
        """Validate that a repository has proper governance disclaimers"""
        repo_path = Path(repo_path)
        
        required_terms = [
            "Synthetic Data Only",
            "Human-in-Loop",
            "No Pricing Authority",
            "No Payout Authority",
            "No Underwriting Authority"
        ]
        
        issues = []
        
        # Check README.md
        readme_path = repo_path / "README.md"
        if not readme_path.exists():
            issues.append("Missing README.md")
        else:
            content = readme_path.read_text()
            for term in required_terms:
                if term not in content:
                    issues.append(f"README.md missing: {term}")
        
        # Check model_card.md
        model_card_path = repo_path / "model_card.md"
        if not model_card_path.exists():
            issues.append("Missing model_card.md")
        
        # Check app.py for disclaimers
        app_path = repo_path / "app.py"
        if app_path.exists():
            content = app_path.read_text()
            if "Disclaimer" not in content and "disclaimer" not in content:
                issues.append("app.py missing disclaimers")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "repo": repo_path.name
        }
    
    def check_code_quality(self, repo_path):
        """Check code quality for a repository"""
        repo_path = Path(repo_path)
        
        issues = []
        
        # Check if app.py exists
        app_path = repo_path / "app.py"
        if not app_path.exists():
            issues.append("Missing app.py")
            return {"valid": False, "issues": issues}
        
        # Check for test file
        test_path = repo_path / "tests" / "test_smoke.py"
        if not test_path.exists():
            issues.append("Missing tests/test_smoke.py")
        
        # Check for requirements.txt
        req_path = repo_path / "requirements.txt"
        if not req_path.exists():
            issues.append("Missing requirements.txt")
        
        # Check for .gitignore
        gitignore_path = repo_path / ".gitignore"
        if not gitignore_path.exists():
            issues.append("Missing .gitignore")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "repo": repo_path.name
        }
    
    def copy_template(self, template_name, destination):
        """Copy a template file to a destination"""
        template_path = self.templates_path / template_name
        destination_path = Path(destination)
        
        if not template_path.exists():
            return {"success": False, "error": f"Template {template_name} not found"}
        
        try:
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(template_path, destination_path)
            return {"success": True, "path": str(destination_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def save_json(self, data, file_path):
        """Save data as JSON"""
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
            
            return {"success": True, "path": str(file_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def load_json(self, file_path):
        """Load JSON data"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {"success": False, "error": "File not found"}
            
            with open(file_path, "r") as f:
                data = json.load(f)
            
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_repo_info(self, repo_path):
        """Get information about a repository"""
        repo_path = Path(repo_path)
        
        info = {
            "name": repo_path.name,
            "path": str(repo_path),
            "exists": repo_path.exists(),
            "has_app": (repo_path / "app.py").exists(),
            "has_readme": (repo_path / "README.md").exists(),
            "has_model_card": (repo_path / "model_card.md").exists(),
            "has_requirements": (repo_path / "requirements.txt").exists(),
            "has_tests": (repo_path / "tests" / "test_smoke.py").exists(),
            "has_models": (repo_path / "models").exists(),
            "has_data": (repo_path / "data").exists(),
            "has_logs": (repo_path / "logs").exists(),
        }
        
        # Count files
        if repo_path.exists():
            info["file_count"] = len(list(repo_path.rglob("*")))
        
        return info
    
    def generate_status_report(self):
        """Generate a status report for all repositories"""
        repos = self.find_repos()
        
        report = {
            "generated": datetime.now().isoformat(),
            "total_repos": len(repos),
            "repos": [],
            "governance_issues": [],
            "quality_issues": []
        }
        
        for repo in repos:
            repo_info = self.get_repo_info(repo)
            governance = self.validate_governance(repo)
            quality = self.check_code_quality(repo)
            
            repo_status = {
                "name": repo.name,
                "info": repo_info,
                "governance": governance,
                "quality": quality
            }
            
            report["repos"].append(repo_status)
            
            if not governance["valid"]:
                report["governance_issues"].extend([
                    f"{repo.name}: {issue}" for issue in governance["issues"]
                ])
            
            if not quality["valid"]:
                report["quality_issues"].extend([
                    f"{repo.name}: {issue}" for issue in quality["issues"]
                ])
        
        return report

if __name__ == "__main__":
    utils = AutomationUtils()
    
    print("Testing automation utilities...")
    
    # Find repos
    repos = utils.find_repos()
    print(f"\nFound {len(repos)} repositories:")
    for repo in repos[:5]:  # Show first 5
        print(f"  - {repo.name}")
    
    # Generate status report
    print("\nGenerating status report...")
    report = utils.generate_status_report()
    print(f"Total repos: {report['total_repos']}")
    print(f"Governance issues: {len(report['governance_issues'])}")
    print(f"Quality issues: {len(report['quality_issues'])}")
    
    print("\n✅ Automation utilities test complete!")
