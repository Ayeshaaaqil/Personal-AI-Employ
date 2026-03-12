"""
Deploy AI Employee Platinum Tier to Hugging Face Spaces

Usage:
    python deploy_to_huggingface.py --repo your-username/ai-employee-platinum
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from huggingface_hub import HfApi, login
import shutil


def deploy_to_spaces(repo_name: str, token: str):
    """Deploy to Hugging Face Spaces"""
    
    # Login to Hugging Face
    api = HfApi()
    login(token=token)
    
    # Get current directory
    current_dir = Path(__file__).parent.parent
    
    # Source files to copy
    source_files = {
        "deployment/huggingface_space/app.py": "app.py",
        "deployment/huggingface_space/requirements.txt": "requirements.txt",
        "platinum/huggingface_reasoning_engine.py": "platinum/huggingface_reasoning_engine.py",
        "platinum/huggingface_agent.py": "platinum/huggingface_agent.py",
        "platinum/prompt_templates.py": "platinum/prompt_templates.py",
    }
    
    # Create temporary deployment directory
    deploy_dir = current_dir / "deployment" / "hf_space_temp"
    deploy_dir.mkdir(exist_ok=True)
    
    # Copy files
    print("Copying files to deployment directory...")
    for src, dst in source_files.items():
        src_path = current_dir / src
        dst_path = deploy_dir / dst
        
        if src_path.exists():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            print(f"  ✓ {src} -> {dst}")
        else:
            print(f"  ✗ Source not found: {src}")
    
    # Copy README
    readme_src = current_dir / "PLATINUM_README.md"
    readme_dst = deploy_dir / "README.md"
    if readme_src.exists():
        shutil.copy2(readme_src, readme_dst)
        print("  ✓ Copied README.md")
    
    # Create or update Space
    print(f"\nCreating/updating Space: {repo_name}")
    try:
        api.create_repo(
            repo_id=repo_name,
            repo_type="space",
            space_sdk="gradio",
            exist_ok=True
        )
        print("  ✓ Space created/updated")
    except Exception as e:
        print(f"  ✗ Error creating space: {e}")
        return False
    
    # Upload files
    print("\nUploading files to Hugging Face Spaces...")
    try:
        api.upload_folder(
            folder_path=str(deploy_dir),
            repo_id=repo_name,
            repo_type="space"
        )
        print("  ✓ Files uploaded successfully")
    except Exception as e:
        print(f"  ✗ Error uploading files: {e}")
        return False
    
    # Cleanup
    print("\nCleaning up...")
    shutil.rmtree(deploy_dir)
    
    # Space URL
    space_url = f"https://huggingface.co/spaces/{repo_name}"
    print(f"\n✅ Deployment complete!")
    print(f"🚀 Your AI Employee is live at: {space_url}")
    print(f"\nNote: First deployment may take a few minutes to build.")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Deploy to Hugging Face Spaces")
    parser.add_argument(
        "--repo",
        type=str,
        required=True,
        help="Repository name (username/repo-name)"
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="Hugging Face token (or set HF_TOKEN env var)"
    )
    
    args = parser.parse_args()
    
    # Get token
    token = args.token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
    
    if not token:
        print("❌ Error: Hugging Face token required")
        print("   Set HF_TOKEN environment variable or use --token flag")
        print("   Get token from: https://huggingface.co/settings/tokens")
        sys.exit(1)
    
    # Deploy
    success = deploy_to_spaces(args.repo, token)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
