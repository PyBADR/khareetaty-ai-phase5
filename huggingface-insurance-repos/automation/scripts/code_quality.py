#!/usr/bin/env python3
"""
Code Quality Enforcer - Automated Code Quality and Governance Checks

This script:
- Enforces import sorting
- Enforces PEP8 formatting
- Validates governance compliance
- Ensures test_smoke.py exists
- Applies quality rules across all repos
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
import re

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_utils import run_command, get_all_repos, validate_governance


class CodeQualityEnforcer:
    """Enforces code quality standards across repositories"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.issues_found = []
        
    def check_import_sorting(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Check if imports are sorted in a Python file"""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Extract import statements
            import_pattern = r'^(import |from \S+ import )'
            lines = content.split('\n')
            imports = []
            import_block_started = False
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                if re.match(import_pattern, stripped):
                    imports.append((i, stripped))
                    import_block_started = True
                elif import_block_started and stripped and not stripped.startswith('#'):
                    # End of import block
                    break
                    
            if len(imports) > 1:
                # Check if sorted
                import_lines = [imp[1] for imp in imports]
                sorted_imports = sorted(import_lines)
                
                if import_lines != sorted_imports:
                    issues.append(f"Imports not sorted in {file_path.name}")
                    return False, issues
                    
        except Exception as e:
            issues.append(f"Error checking imports in {file_path.name}: {e}")
            return False, issues
            
        return True, []
    
    def check_pep8_compliance(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Check PEP8 compliance using basic rules"""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines, 1):
                # Check line length (max 100 chars, relaxed from 79)
                if len(line.rstrip()) > 100:
                    issues.append(f"{file_path.name}:{i} - Line too long ({len(line.rstrip())} > 100)")
                    
                # Check trailing whitespace
                if line.rstrip() != line.rstrip('\n').rstrip('\r'):
                    issues.append(f"{file_path.name}:{i} - Trailing whitespace")
                    
                # Check tabs vs spaces
                if '\t' in line:
                    issues.append(f"{file_path.name}:{i} - Tab character found (use spaces)")
                    
        except Exception as e:
            issues.append(f"Error checking PEP8 in {file_path.name}: {e}")
            return False, issues
            
        return len(issues) == 0, issues
    
    def check_governance_content(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Check for required governance disclaimers"""
        issues = []
        
        # Only check certain files
        if file_path.name not in ['README.md', 'app.py', 'model_card.md']:
            return True, []
            
        try:
            with open(file_path, 'r') as f:
                content = f.read().lower()
                
            # Required terms for governance
            required_terms = [
                'synthetic',
                'disclaimer',
            ]
            
            # Prohibited terms
            prohibited_terms = [
                'real customer data',
                'production use',
                'personally identifiable',
            ]
            
            # Check for required terms
            for term in required_terms:
                if term not in content:
                    issues.append(f"{file_path.name} - Missing required term: '{term}'")
                    
            # Check for proper disclaimers (should mention these are NOT allowed)
            governance_keywords = ['underwriting authority', 'pricing authority', 'payout']
            has_governance = any(keyword in content for keyword in governance_keywords)
            
            if file_path.name in ['README.md', 'model_card.md'] and not has_governance:
                issues.append(f"{file_path.name} - Missing governance disclaimers")
                
        except Exception as e:
            issues.append(f"Error checking governance in {file_path.name}: {e}")
            return False, issues
            
        return len(issues) == 0, issues
    
    def check_test_exists(self, repo_path: Path) -> Tuple[bool, List[str]]:
        """Check if test_smoke.py exists"""
        issues = []
        
        test_file = repo_path / "tests" / "test_smoke.py"
        if not test_file.exists():
            issues.append(f"Missing test_smoke.py in {repo_path.name}")
            return False, issues
            
        return True, []
    
    def check_prohibited_content(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Check for prohibited content patterns"""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Patterns that should NOT appear (indicating production use)
            prohibited_patterns = [
                (r'\bSSN\b', 'Social Security Number reference'),
                (r'\bPII\b.*(?!no|not|without)', 'PII reference without negation'),
                (r'production.*database', 'Production database reference'),
                (r'real.*customer.*data', 'Real customer data reference'),
                (r'\$\d+\.\d{2}.*premium', 'Actual premium pricing'),
            ]
            
            for pattern, description in prohibited_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(f"{file_path.name} - Prohibited content: {description}")
                    
        except Exception as e:
            issues.append(f"Error checking prohibited content in {file_path.name}: {e}")
            return False, issues
            
        return len(issues) == 0, issues
    
    def check_repository(self, repo_path: Path) -> Dict:
        """Run all quality checks on a repository"""
        print(f"\n{'='*60}")
        print(f"Checking: {repo_path.name}")
        print(f"{'='*60}")
        
        results = {
            "repository": repo_path.name,
            "files_checked": 0,
            "issues": [],
            "passed": True
        }
        
        # Check test exists
        test_ok, test_issues = self.check_test_exists(repo_path)
        if not test_ok:
            results["issues"].extend(test_issues)
            results["passed"] = False
            
        # Check Python files
        python_files = list(repo_path.rglob('*.py'))
        for py_file in python_files:
            # Skip __pycache__ and .venv
            if '__pycache__' in str(py_file) or '.venv' in str(py_file):
                continue
                
            results["files_checked"] += 1
            
            # Import sorting
            import_ok, import_issues = self.check_import_sorting(py_file)
            if not import_ok:
                results["issues"].extend(import_issues)
                results["passed"] = False
                
            # PEP8 compliance (basic)
            pep8_ok, pep8_issues = self.check_pep8_compliance(py_file)
            if not pep8_ok:
                results["issues"].extend(pep8_issues[:5])  # Limit to 5 issues per file
                results["passed"] = False
                
            # Prohibited content
            prohibited_ok, prohibited_issues = self.check_prohibited_content(py_file)
            if not prohibited_ok:
                results["issues"].extend(prohibited_issues)
                results["passed"] = False
                
        # Check markdown files for governance
        md_files = list(repo_path.glob('*.md'))
        for md_file in md_files:
            results["files_checked"] += 1
            
            governance_ok, governance_issues = self.check_governance_content(md_file)
            if not governance_ok:
                results["issues"].extend(governance_issues)
                results["passed"] = False
                
        # Print results
        if results["passed"]:
            print(f"  ✅ All checks passed ({results['files_checked']} files)")
        else:
            print(f"  ⚠️  {len(results['issues'])} issues found:")
            for issue in results["issues"][:10]:  # Show first 10
                print(f"    - {issue}")
            if len(results["issues"]) > 10:
                print(f"    ... and {len(results['issues']) - 10} more")
                
        return results
    
    def enforce_quality(self, fix: bool = False) -> Dict:
        """Enforce code quality across all repositories"""
        print("\n" + "="*60)
        print("🔍 CODE QUALITY ENFORCER")
        print("="*60)
        
        repos = get_all_repos(self.base_path)
        summary = {
            "total_repos": len(repos),
            "repos_checked": 0,
            "repos_passed": 0,
            "total_issues": 0,
            "results": []
        }
        
        for repo in repos:
            # Skip hub and automation
            if repo.name in ['gcc-insurance-ai-hub', 'automation']:
                continue
                
            result = self.check_repository(repo)
            summary["results"].append(result)
            summary["repos_checked"] += 1
            
            if result["passed"]:
                summary["repos_passed"] += 1
            else:
                summary["total_issues"] += len(result["issues"])
                
        # Print summary
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        print(f"Repositories Checked: {summary['repos_checked']}/{summary['total_repos']}")
        print(f"Repositories Passed: {summary['repos_passed']}/{summary['repos_checked']}")
        print(f"Total Issues Found: {summary['total_issues']}")
        
        if summary['repos_passed'] == summary['repos_checked']:
            print("\n✅ All repositories passed quality checks!")
        else:
            print(f"\n⚠️  {summary['repos_checked'] - summary['repos_passed']} repositories need attention")
            
        # Save summary
        import json
        summary_file = self.base_path / "automation" / "code_quality_summary.json"
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\n💾 Summary saved to: {summary_file}")
        
        return summary


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Code Quality Enforcer - Automated quality and governance checks"
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to auto-fix issues (not implemented yet)'
    )
    parser.add_argument(
        '--base-path',
        default=os.getcwd(),
        help='Base path for repositories'
    )
    
    args = parser.parse_args()
    
    enforcer = CodeQualityEnforcer(args.base_path)
    enforcer.enforce_quality(fix=args.fix)
    
    print("\n✅ Code quality enforcement complete!")


if __name__ == "__main__":
    main()
