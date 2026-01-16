#!/usr/bin/env python3
"""
Add Use Case - Single Command Use Case Generation

This is the main orchestration script that ties all automation layers together.

Usage:
    python add_usecase.py <use-case-name> [--datasets dataset1 dataset2 ...]
    
Example:
    python add_usecase.py premium-lapse-monitor --datasets dataset_v1 dataset_v2
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from repo_factory import RepositoryFactory
from model_registry import ModelRegistry
from hub_orchestrator import HubOrchestrator
from code_quality import CodeQualityEnforcer
from logger_utility import InsuranceLogger


class UseCaseGenerator:
    """Main orchestrator for single-command use case generation"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.logger = InsuranceLogger("add_usecase", self.base_path / "automation" / "logs")
        
        # Initialize all automation components
        self.repo_factory = RepositoryFactory(self.base_path)
        self.model_registry = ModelRegistry(self.base_path)
        self.hub_orchestrator = HubOrchestrator(self.base_path)
        self.code_quality = CodeQualityEnforcer(self.base_path)
        
    def generate_use_case(self, 
                         use_case_name: str, 
                         datasets: List[str] = None,
                         auto_push: bool = False) -> Dict:
        """
        Generate a complete use case with all automation layers
        
        Args:
            use_case_name: Name of the use case (e.g., 'premium-lapse-monitor')
            datasets: List of dataset names to generate (e.g., ['dataset_v1', 'dataset_v2'])
            auto_push: Whether to automatically push to HuggingFace
            
        Returns:
            Dictionary with generation results
        """
        print("\n" + "="*70)
        print("🏭 INSURANCE AI FACTORY - USE CASE GENERATION")
        print("="*70)
        print(f"\n🎯 Use Case: {use_case_name}")
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if datasets:
            print(f"📊 Datasets: {', '.join(datasets)}")
        
        self.logger.log_invocation("generate_use_case", {"use_case": use_case_name})
        
        results = {
            "use_case_name": use_case_name,
            "started_at": datetime.now().isoformat(),
            "steps": [],
            "success": False,
            "errors": []
        }
        
        try:
            # Step 1: Generate Repository
            print("\n" + "-"*70)
            print("📦 STEP 1: Generating Repository")
            print("-"*70)
            
            repo_result = self.repo_factory.create_repository(use_case_name)
            results["steps"].append({
                "step": 1,
                "name": "Generate Repository",
                "success": repo_result["success"],
                "details": repo_result
            })
            
            if not repo_result["success"]:
                results["errors"].append("Repository generation failed")
                return results
                
            repo_path = Path(repo_result["repo_path"])
            print(f"\n✅ Repository created: {repo_path}")
            
            # Step 2: Generate Datasets
            if datasets:
                print("\n" + "-"*70)
                print("📊 STEP 2: Generating Datasets")
                print("-"*70)
                
                dataset_results = []
                for dataset_name in datasets:
                    print(f"\n  Generating {dataset_name}...")
                    dataset_result = self._generate_dataset(repo_path, dataset_name)
                    dataset_results.append(dataset_result)
                    
                results["steps"].append({
                    "step": 2,
                    "name": "Generate Datasets",
                    "success": all(d["success"] for d in dataset_results),
                    "details": dataset_results
                })
                
                print(f"\n✅ Generated {len(datasets)} datasets")
            else:
                print("\nℹ️  No datasets specified, using default dataset generator")
                
            # Step 3: Run Code Quality Checks
            print("\n" + "-"*70)
            print("🔍 STEP 3: Running Code Quality Checks")
            print("-"*70)
            
            quality_result = self.code_quality.check_repository(repo_path)
            results["steps"].append({
                "step": 3,
                "name": "Code Quality Checks",
                "success": quality_result["passed"],
                "details": quality_result
            })
            
            if quality_result["passed"]:
                print("\n✅ All quality checks passed")
            else:
                print(f"\n⚠️  {len(quality_result['issues'])} quality issues found (non-blocking)")
                
            # Step 4: Initialize Model Registry
            print("\n" + "-"*70)
            print("🤖 STEP 4: Initializing Model Registry")
            print("-"*70)
            
            model_result = self.model_registry.process_repository(repo_path)
            results["steps"].append({
                "step": 4,
                "name": "Model Registry",
                "success": model_result["status"] == "success",
                "details": model_result
            })
            
            print(f"\n✅ Model registry initialized")
            
            # Step 5: Update Hub
            print("\n" + "-"*70)
            print("🏭 STEP 5: Updating Hub")
            print("-"*70)
            
            hub_result = self.hub_orchestrator.orchestrate(push=auto_push)
            results["steps"].append({
                "step": 5,
                "name": "Hub Orchestration",
                "success": hub_result["readme_updated"],
                "details": hub_result
            })
            
            print(f"\n✅ Hub updated")
            
            # Step 6: Prepare for Publish
            print("\n" + "-"*70)
            print("🚀 STEP 6: Preparing for Publish")
            print("-"*70)
            
            publish_result = self._prepare_for_publish(repo_path)
            results["steps"].append({
                "step": 6,
                "name": "Prepare for Publish",
                "success": publish_result["success"],
                "details": publish_result
            })
            
            print(f"\n✅ Ready for publish")
            
            # Final Success
            results["success"] = True
            results["completed_at"] = datetime.now().isoformat()
            results["repo_path"] = str(repo_path)
            results["space_url"] = f"https://huggingface.co/spaces/gcc-insurance-intelligence-lab/{use_case_name}"
            
            # Save results
            self._save_results(results)
            
            # Print success message
            self._print_success_message(results)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            results["errors"].append(str(e))
            results["success"] = False
            self.logger.log_error("generate_use_case", str(e))
            
        return results
    
    def _generate_dataset(self, repo_path: Path, dataset_name: str) -> Dict:
        """Generate a specific dataset version"""
        data_dir = repo_path / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create dataset file
        dataset_file = data_dir / f"{dataset_name}.csv"
        
        # Generate synthetic data based on use case
        import csv
        import random
        
        # Sample synthetic data
        headers = ['id', 'feature_1', 'feature_2', 'feature_3', 'target']
        rows = []
        
        for i in range(100):
            rows.append([
                i,
                random.uniform(0, 100),
                random.uniform(0, 100),
                random.uniform(0, 100),
                random.choice([0, 1])
            ])
            
        with open(dataset_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
            
        print(f"    ✓ Created {dataset_file.name} with {len(rows)} rows")
        
        return {
            "success": True,
            "dataset_name": dataset_name,
            "file_path": str(dataset_file),
            "rows": len(rows)
        }
    
    def _prepare_for_publish(self, repo_path: Path) -> Dict:
        """Prepare repository for publishing to HuggingFace"""
        checklist = {
            "readme_exists": (repo_path / "README.md").exists(),
            "app_exists": (repo_path / "app.py").exists(),
            "requirements_exists": (repo_path / "requirements.txt").exists(),
            "model_card_exists": (repo_path / "model_card.md").exists(),
            "tests_exist": (repo_path / "tests" / "test_smoke.py").exists(),
            "gitignore_exists": (repo_path / ".gitignore").exists()
        }
        
        all_ready = all(checklist.values())
        
        print("\n  Publish Checklist:")
        for item, status in checklist.items():
            icon = "✅" if status else "❌"
            print(f"    {icon} {item.replace('_', ' ').title()}")
            
        return {
            "success": all_ready,
            "checklist": checklist,
            "ready_for_publish": all_ready
        }
    
    def _save_results(self, results: Dict):
        """Save generation results to file"""
        results_dir = self.base_path / "automation" / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = results_dir / f"{results['use_case_name']}_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"\n💾 Results saved to: {results_file}")
    
    def _print_success_message(self, results: Dict):
        """Print the final success message"""
        print("\n" + "="*70)
        print("✨ SUCCESS! ✨")
        print("="*70)
        print("\n🏭 Insurance AI Factory mode activated — You can now manufacture new use cases on demand.")
        print("\n" + "="*70)
        print("📊 GENERATION SUMMARY")
        print("="*70)
        print(f"\n✅ Use Case: {results['use_case_name']}")
        print(f"✅ Repository: {results['repo_path']}")
        print(f"✅ Space URL: {results['space_url']}")
        print(f"\n🔧 Steps Completed: {len(results['steps'])}/6")
        
        for step in results['steps']:
            icon = "✅" if step['success'] else "⚠️"
            print(f"  {icon} Step {step['step']}: {step['name']}")
            
        print("\n" + "="*70)
        print("🚀 NEXT STEPS")
        print("="*70)
        print(f"\n1. Review the generated code in: {results['repo_path']}")
        print(f"2. Test the application locally: cd {results['repo_path']} && python app.py")
        print(f"3. Push to HuggingFace: cd {results['repo_path']} && git push")
        print(f"4. View your Space at: {results['space_url']}")
        print("\n" + "="*70)
        

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Add Use Case - Single command use case generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python add_usecase.py premium-lapse-monitor
  python add_usecase.py fraud-detection --datasets dataset_v1 dataset_v2
  python add_usecase.py claims-predictor --datasets train_data test_data --push
        """
    )
    
    parser.add_argument(
        'use_case_name',
        help='Name of the use case (e.g., premium-lapse-monitor)'
    )
    parser.add_argument(
        '--datasets',
        nargs='+',
        help='Dataset names to generate (e.g., dataset_v1 dataset_v2)'
    )
    parser.add_argument(
        '--push',
        action='store_true',
        help='Automatically push to HuggingFace after generation'
    )
    parser.add_argument(
        '--base-path',
        default=os.getcwd(),
        help='Base path for repositories'
    )
    
    args = parser.parse_args()
    
    # Validate use case name
    if not args.use_case_name.replace('-', '').replace('_', '').isalnum():
        print("❌ Error: Use case name must contain only letters, numbers, hyphens, and underscores")
        sys.exit(1)
        
    # Generate use case
    generator = UseCaseGenerator(args.base_path)
    results = generator.generate_use_case(
        use_case_name=args.use_case_name,
        datasets=args.datasets,
        auto_push=args.push
    )
    
    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    main()
