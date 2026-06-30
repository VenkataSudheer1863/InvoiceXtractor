"""
Installation Verification Script

Run this script to verify that all dependencies are installed correctly
and the system is ready to use.
"""

import sys
import os

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    print("\nChecking dependencies...")
    
    required_packages = {
        "streamlit": "streamlit",
        "pdfplumber": "pdfplumber",
        "groq": "groq",
        "pandas": "pandas",
        "openpyxl": "openpyxl",
        "dotenv": "python-dotenv",
        "pydantic": "pydantic"
    }
    
    all_installed = True
    
    for package_name, import_name in required_packages.items():
        try:
            if import_name == "dotenv":
                __import__("dotenv")
            else:
                __import__(import_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ {package_name} (not installed)")
            all_installed = False
    
    return all_installed

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\nChecking .env configuration...")
    
    if not os.path.exists(".env"):
        print("  ❌ .env file not found")
        return False
    
    required_vars = [
        "GROQ_API_KEY",
        "GROQ_MODEL"
    ]
    
    with open(".env", "r") as f:
        env_content = f.read()
    
    all_present = True
    for var in required_vars:
        if var in env_content:
            print(f"  ✅ {var}")
        else:
            print(f"  ❌ {var} (missing)")
            all_present = False
    
    return all_present

def check_project_structure():
    """Check if all required files and directories exist"""
    print("\nChecking project structure...")
    
    required_items = {
        "files": [
            "app.py",
            "test_system.py",
            "example_usage.py",
            "requirements.txt",
            "README.md"
        ],
        "directories": [
            "agents",
            "config",
            "utils",
            "docs"
        ]
    }
    
    all_present = True
    
    for file in required_items["files"]:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (missing)")
            all_present = False
    
    for directory in required_items["directories"]:
        if os.path.isdir(directory):
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/ (missing)")
            all_present = False
    
    return all_present

def check_agents():
    """Check if all agent files exist"""
    print("\nChecking agent files...")
    
    agent_files = [
        "agents/__init__.py",
        "agents/base_agent.py",
        "agents/pdf_agent.py",
        "agents/llm_agent.py",
        "agents/excel_agent.py",
        "agents/validation_agent.py",
        "agents/orchestrator.py"
    ]
    
    all_present = True
    
    for agent_file in agent_files:
        if os.path.exists(agent_file):
            print(f"  ✅ {agent_file}")
        else:
            print(f"  ❌ {agent_file} (missing)")
            all_present = False
    
    return all_present

def check_sample_files():
    """Check if sample PDF files exist"""
    print("\nChecking sample files...")
    
    sample_files = [
        "POC_1.pdf",
        "consolidated_acss_invoices_sample_output.xlsx"
    ]
    
    found_count = 0
    
    for sample_file in sample_files:
        if os.path.exists(sample_file):
            print(f"  ✅ {sample_file}")
            found_count += 1
        else:
            print(f"  ⚠️  {sample_file} (optional, not found)")
    
    return found_count > 0

def test_imports():
    """Test if agents can be imported"""
    print("\nTesting agent imports...")
    
    try:
        from agents.orchestrator import OrchestratorAgent
        print("  ✅ OrchestratorAgent")
        
        from agents.pdf_agent import PDFAgent
        print("  ✅ PDFAgent")
        
        from agents.llm_agent import LLMAgent
        print("  ✅ LLMAgent")
        
        from agents.excel_agent import ExcelAgent
        print("  ✅ ExcelAgent")
        
        from agents.validation_agent import ValidationAgent
        print("  ✅ ValidationAgent")
        
        return True
    
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("SAP Invoice Processing System - Installation Verification")
    print("=" * 60)
    
    checks = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Environment Config": check_env_file(),
        "Project Structure": check_project_structure(),
        "Agent Files": check_agents(),
        "Sample Files": check_sample_files(),
        "Agent Imports": test_imports()
    }
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    for check_name, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:.<40} {status}")
    
    all_passed = all(checks.values())
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✅ ALL CHECKS PASSED!")
        print("\nYou're ready to use the system!")
        print("\nNext steps:")
        print("  1. Run the UI: streamlit run app.py")
        print("  2. Or test: python test_system.py")
        print("  3. Or examples: python example_usage.py")
    else:
        print("❌ SOME CHECKS FAILED")
        print("\nPlease fix the issues above before using the system.")
        print("\nCommon fixes:")
        print("  • Install dependencies: pip install -r requirements.txt")
        print("  • Check .env file has all required variables")
        print("  • Ensure all files are present")
    
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
