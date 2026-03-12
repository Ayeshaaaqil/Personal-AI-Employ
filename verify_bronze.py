"""
Bronze Tier Verification Script

Run this script to verify that all Bronze tier components are working correctly.
"""

import sys
from pathlib import Path

def check_mark(symbol: str) -> str:
    """Return check or cross symbol."""
    return symbol

def test_vault_structure() -> bool:
    """Test that vault folder structure exists."""
    print("\n=== Testing Vault Structure ===")
    
    vault_path = Path(__file__).parent / 'AI_Employee_Vault'
    required_folders = [
        'Inbox',
        'Needs_Action',
        'Done',
        'Pending_Approval',
        'Approved',
        'Rejected',
        'Plans',
        'Briefings',
        'Accounting',
        'Logs',
        'Invoices'
    ]
    
    all_exist = True
    for folder in required_folders:
        folder_path = vault_path / folder
        if folder_path.exists() and folder_path.is_dir():
            print(f"  [OK] {folder}/")
        else:
            print(f"  [FAIL] {folder}/ - Missing")
            all_exist = False
    
    return all_exist

def test_vault_files() -> bool:
    """Test that required vault files exist."""
    print("\n=== Testing Vault Files ===")
    
    vault_path = Path(__file__).parent / 'AI_Employee_Vault'
    required_files = [
        'Dashboard.md',
        'Company_Handbook.md',
        'Business_Goals.md'
    ]
    
    all_exist = True
    for file in required_files:
        file_path = vault_path / file
        if file_path.exists():
            content = file_path.read_text()
            print(f"  [OK] {file} ({len(content)} bytes)")
        else:
            print(f"  [FAIL] {file} - Missing")
            all_exist = False
    
    return all_exist

def test_watcher_modules() -> bool:
    """Test that watcher modules can be imported."""
    print("\n=== Testing Watcher Modules ===")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'watchers'))
        from base_watcher import BaseWatcher
        print("  [OK] base_watcher.py")
    except ImportError as e:
        print(f"  [FAIL] base_watcher.py - {e}")
        return False
    
    try:
        from filesystem_watcher import FileSystemWatcher
        print("  [OK] filesystem_watcher.py")
    except ImportError as e:
        print(f"  [FAIL] filesystem_watcher.py - {e}")
        return False
    
    return True

def test_orchestrator() -> bool:
    """Test that orchestrator module can be imported."""
    print("\n=== Testing Orchestrator ===")
    
    try:
        from orchestrator import Orchestrator
        print("  [OK] orchestrator.py")
        return True
    except ImportError as e:
        print(f"  [FAIL] orchestrator.py - {e}")
        return False

def test_dependencies() -> bool:
    """Test that required dependencies are installed."""
    print("\n=== Testing Dependencies ===")
    
    try:
        import watchdog
        print(f"  [OK] watchdog (installed)")
        return True
    except ImportError:
        print("  [FAIL] watchdog - Not installed")
        print("        Run: pip install -r watchers/requirements.txt")
        return False

def test_claude_code() -> bool:
    """Test that Qwen Code is installed."""
    print("\n=== Testing Qwen Code ===")
    
    import subprocess
    import platform
    
    # On Windows, need shell=True to find npm-installed packages
    use_shell = platform.system() == 'Windows'
    
    try:
        result = subprocess.run(['qwen', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10,
                              shell=use_shell)
        if result.returncode == 0:
            print(f"  [OK] Qwen Code installed (v{result.stdout.strip()})")
            return True
        else:
            print(f"  [WARN] Qwen Code returned: {result.stderr}")
            return False
    except FileNotFoundError:
        print("  [FAIL] Qwen Code not found")
        print("        Install Qwen Code CLI")
        return False
    except Exception as e:
        print(f"  [WARN] Could not verify Qwen Code: {e}")
        return False

def test_agent_skills() -> bool:
    """Test that agent skill documentation exists."""
    print("\n=== Testing Agent Skills ===")
    
    skills_path = Path(__file__).parent / '.qwen' / 'skills'
    
    if not skills_path.exists():
        print(f"  [FAIL] Skills directory missing")
        return False
    
    # Check vault-operations skill
    vault_skill = skills_path / 'vault-operations' / 'SKILL.md'
    if vault_skill.exists():
        content = vault_skill.read_text()
        print(f"  [OK] vault-operations ({len(content)} bytes)")
        return True
    else:
        print(f"  [FAIL] vault-operations skill missing")
        return False

def main():
    """Run all verification tests."""
    print("=" * 50)
    print("  BRONZE TIER VERIFICATION")
    print("=" * 50)
    
    results = []
    
    results.append(("Vault Structure", test_vault_structure()))
    results.append(("Vault Files", test_vault_files()))
    results.append(("Watcher Modules", test_watcher_modules()))
    results.append(("Orchestrator", test_orchestrator()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("Claude Code", test_claude_code()))
    results.append(("Agent Skills", test_agent_skills()))
    
    print("\n" + "=" * 50)
    print("  SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        symbol = "[PASS]" if result else "[FAIL]"
        print(f"  {symbol} {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  Bronze Tier verification SUCCESSFUL!")
        print("\n  Next steps:")
        print("  1. Open AI_Employee_Vault in Obsidian")
        print("  2. Run: cd watchers && python filesystem_watcher.py ../AI_Employee_Vault")
        print("  3. Drop a test file in AI_Employee_Vault/Inbox/")
        print("  4. Watch the magic happen!")
        return 0
    else:
        print("\n  Some tests failed. Please review and fix.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
