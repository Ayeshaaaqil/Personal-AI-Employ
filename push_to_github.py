"""
Push all code to GitHub and trigger deployment
Usage: python push_to_github.py
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run command and show progress"""
    print(f"\n⏳ {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - Done!")
        return True
    else:
        print(f"❌ {description} - Failed!")
        print(f"Error: {result.stderr}")
        return False

def main():
    print("=" * 70)
    print("🚀 Pushing AI Employee to GitHub")
    print("=" * 70)
    
    # Check if git is initialized
    if not Path('.git').exists():
        print("\n📦 Initializing Git repository...")
        run_command("git init", "Git initialized")
    
    # Check for .gitignore
    if not Path('.gitignore').exists():
        print("\n📝 Creating .gitignore...")
        gitignore = """# Environment variables
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Sessions
*-session/
token.json

# Logs
*.log
AI_Employee_Vault/Logs/*.md

# Credentials
credentials.json
odoo_config.json
facebook_config.json
"""
        Path('.gitignore').write_text(gitignore)
        print("✅ .gitignore created")
    
    # Add all files
    run_command("git add .", "Adding all files to git")
    
    # Check status
    print("\n📊 Git Status:")
    result = subprocess.run("git status --short", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print(result.stdout)
    else:
        print("✅ Working tree clean")
    
    # Commit
    print("\n💾 Creating commit...")
    run_command('git commit -m "🎉 AI Employee - Complete Deployment\n\n- All features implemented\n- WhatsApp & LinkedIn integration\n- Professional dashboard\n- Hugging Face deployment ready\n- CI/CD pipeline configured\n\nDeveloped by: Ayesha Aaqil"', "Commit created")
    
    # Check for remote
    print("\n🔗 Checking GitHub remote...")
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
    
    if not result.stdout.strip():
        print("\n⚠️  No GitHub remote found!")
        print("\n📝 Please add your GitHub repository:")
        print("   git remote add origin https://github.com/Ayesha-Aaqil/ai-employee.git")
        print("\nThen run this script again.")
        return
    
    # Push to GitHub
    print("\n📤 Pushing to GitHub...")
    print("⚠️  This may ask for your GitHub credentials")
    
    result = subprocess.run("git push -u origin main", shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\n✅ Pushed to GitHub successfully!")
        print("\n🌐 Your repository:")
        print("   https://github.com/Ayesha-Aaqil/ai-employee")
        print("\n🔄 CI/CD pipeline will now deploy to Hugging Face!")
    else:
        print("\n⚠️  Push may have failed. Trying with master branch...")
        run_command("git push -u origin master", "Pushing to master branch")
    
    # Instructions
    print("\n" + "=" * 70)
    print("📋 NEXT STEPS:")
    print("=" * 70)
    print("\n1. ✅ Code is on GitHub")
    print("2. ⏳ CI/CD will deploy to Hugging Face (wait 5-10 minutes)")
    print("3. 🌐 Visit: https://huggingface.co/spaces/Ayesha-Aaqil/ai-employee")
    print("4. 🧪 Test all features")
    print("5. 🎉 Share your dashboard!")
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
