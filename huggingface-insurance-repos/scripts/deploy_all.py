#!/usr/bin/env python3
"""
Deploy all insurance agents to Hugging Face
This script deploys all agent repositories to Hugging Face Spaces
"""

import os
import subprocess
import sys
from pathlib import Path

def deploy_all_agents():
    """Deploy all agent repositories to Hugging Face"""
    print("🚀 Deploying all insurance agents to Hugging Face...")
    
    # Get all directories that look like agent repos
    base_path = Path(__file__).parent.parent
    agent_dirs = []
    
    for item in base_path.iterdir():
        if item.is_dir():
            # Check if it looks like an agent repo (has required files)
            required_files = ["app.py", "requirements.txt", "README.md", "model_card.md"]
            has_required = all((item / f).exists() for f in required_files)
            
            if has_required and (item / "deploy_to_hf.py").exists():
                agent_dirs.append(item)
    
    if not agent_dirs:
        print("❌ No agent repositories found to deploy")
        return False
    
    print(f"Found {len(agent_dirs)} agent repositories to deploy:")
    for agent_dir in agent_dirs:
        print(f"  - {agent_dir.name}")
    
    print("\nStarting deployment process...")
    
    successful_deploys = 0
    failed_deploys = 0
    
    for agent_dir in agent_dirs:
        print(f"\n--- Deploying {agent_dir.name} ---")
        
        deploy_script = agent_dir / "deploy_to_hf.py"
        
        try:
            # Run the deployment script
            result = subprocess.run([
                sys.executable, str(deploy_script)
            ], cwd=agent_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {agent_dir.name} deployed successfully!")
                successful_deploys += 1
            else:
                print(f"❌ {agent_dir.name} deployment failed:")
                print(result.stdout)
                print(result.stderr)
                failed_deploys += 1
                
        except Exception as e:
            print(f"❌ Error deploying {agent_dir.name}: {e}")
            failed_deploys += 1
    
    print(f"\n--- Deployment Summary ---")
    print(f"Successful: {successful_deploys}")
    print(f"Failed: {failed_deploys}")
    print(f"Total: {len(agent_dirs)}")
    
    if failed_deploys == 0:
        print("🎉 All agents deployed successfully!")
        return True
    else:
        print(f"⚠️ {failed_deploys} agents failed to deploy")
        return False

def main():
    """Main function to deploy all agents"""
    print("Insurance Agent Factory - Deploy All Script")
    print("=" * 50)
    
    success = deploy_all_agents()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()