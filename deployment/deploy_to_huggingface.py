"""
Deploy AI Employee to Hugging Face Spaces
Usage: python deploy_to_huggingface.py --repo Ayesha-Aaqil/ai-employee
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from huggingface_hub import HfApi, login

def main():
    parser = argparse.ArgumentParser(description='Deploy to Hugging Face Spaces')
    parser.add_argument('--repo', type=str, default='Ayesha-Aaqil/ai-employee',
                       help='Hugging Face Space repo (username/repo-name)')
    parser.add_argument('--token', type=str, default=None,
                       help='Hugging Face token (or set HF_TOKEN env var)')
    args = parser.parse_args()
    
    # Get token
    token = args.token or os.getenv('HF_TOKEN')
    if not token:
        print("❌ Error: Please provide --token or set HF_TOKEN environment variable")
        print("   Get token from: https://huggingface.co/settings/tokens")
        print("\n   Or pass directly:")
        print("   python deploy_to_huggingface.py --repo Ayesha-Aaqil/ai-employee --token hf_xxx")
        sys.exit(1)
    
    print("=" * 70)
    print("🚀 Deploying AI Employee to Hugging Face Spaces")
    print("=" * 70)
    print(f"📂 Repository: {args.repo}")
    print(f"🔑 Token: {'✓' + token[:6]}...{token[-4:]}")
    print("=" * 70)
    
    # Login to Hugging Face
    print("\n🔐 Logging in to Hugging Face...")
    try:
        login(token=token)
        print("✅ Logged in successfully!")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        sys.exit(1)
    
    # Create Space if it doesn't exist
    print(f"\n📦 Creating/verifying Space: {args.repo}...")
    try:
        api = HfApi()
        username = args.repo.split('/')[0]
        space_name = args.repo.split('/')[1]
        
        # Try to create space (will fail if exists, which is fine)
        try:
            api.create_repo(
                repo_id=args.repo,
                repo_type="space",
                space_sdk="gradio",
                space_hardware="cpu-basic",
                exist_ok=True
            )
            print("✅ Space created successfully!")
        except Exception as e:
            if "You already created this repo" in str(e):
                print("✅ Space already exists!")
            else:
                raise e
        
    except Exception as e:
        print(f"❌ Error creating space: {e}")
        sys.exit(1)
    
    # Prepare files for deployment
    print("\n📁 Preparing files for deployment...")
    
    # Create deployment directory
    deploy_dir = Path("deployment/huggingface_space")
    deploy_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy main app
    import shutil
    shutil.copy("web_dashboard/app.py", deploy_dir / "app.py")
    print("✅ Copied app.py")
    
    # Create requirements.txt for Space
    requirements = """# Hugging Face Spaces compatible dependencies
gradio==4.44.1
huggingface-hub==0.23.0
google-auth==2.28.0
google-auth-oauthlib==1.2.0
google-api-python-client==2.118.0
playwright==1.40.0
python-dotenv==1.0.0
requests==2.31.0
"""
    (deploy_dir / "requirements.txt").write_text(requirements)
    print("✅ Created requirements.txt")

    # Create .python-version file
    (deploy_dir / ".python-version").write_text("3.11\n")
    print("✅ Created .python-version")
    
    # Create .env.example
    env_example = """# Hugging Face Space Environment Variables
HUGGINGFACE_TOKEN=your_hf_token
VAULT_PATH=./AI_Employee_Vault

# Gmail (optional)
GMAIL_CREDENTIALS={"installed":{...}}

# Other services (optional)
FACEBOOK_ACCESS_TOKEN=your_token
LINKEDIN_SESSION_PATH=./linkedin-session
"""
    (deploy_dir / ".env.example").write_text(env_example)
    print("✅ Created .env.example")
    
    # Create README for Space
    readme = """---
title: AI Employee Dashboard
emoji: 🤖
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
license: mit
python_version: 3.11
---

# AI Employee Dashboard

**Your life and business on autopilot!**

## Python Runtime

This Space runs on **Python 3.10** for compatibility.

## Features

- Email Management with Auto-Reply
- WhatsApp Integration
- LinkedIn Automation
- Facebook Monitoring
- Task Management
- CEO Briefings
- AI Assistant Chat
- Settings & Configuration

## Created by

**Ayesha Aaqil** - AI Automation Expert
"""
    (deploy_dir / "README.md").write_text(readme, encoding='utf-8')
    print("✅ Created README.md")
    
    # Upload to Hugging Face
    print("\n📤 Uploading files to Hugging Face...")
    try:
        api.upload_folder(
            folder_path=str(deploy_dir),
            repo_id=args.repo,
            repo_type="space",
            commit_message="Deploy AI Employee Dashboard v1.0"
        )
        print("✅ Files uploaded successfully!")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        sys.exit(1)
    
    # Get Space URL
    space_url = f"https://huggingface.co/spaces/{args.repo}"
    
    print("\n" + "=" * 70)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("=" * 70)
    print(f"\n🌐 Your AI Employee is live at:")
    print(f"   {space_url}")
    print(f"\n⏳ Note: Space may take 2-5 minutes to build and start")
    print(f"\n📊 Monitor build status: {space_url}/tree/main")
    print("\n" + "=" * 70)
    
    # Create success file
    success_file = Path("DEPLOYMENT_SUCCESS.txt")
    success_file.write_text(f"""Deployment Successful!
=====================

Space URL: {space_url}
Repository: {args.repo}
Date: {__import__('datetime').datetime.now().isoformat()}

Next Steps:
1. Wait 2-5 minutes for build
2. Visit {space_url}
3. Test all features
4. Share with team!

Developed by: Ayesha Aaqil
""")
    print(f"✅ Created DEPLOYMENT_SUCCESS.txt")
    
    print("\n✨ Thank you for using AI Employee! ✨")
    print("\n🚀 Share your dashboard: " + space_url)


if __name__ == '__main__':
    main()
