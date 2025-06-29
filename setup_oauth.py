#!/usr/bin/env python3
"""
Quick OAuth2 setup verification and testing script
"""
import os
import sys
import subprocess

def print_banner():
    print("🚀 YouTube Playlist Creator - OAuth2 Setup")
    print("=" * 50)
    print()

def check_file_exists(filename, description):
    """Check if a file exists and return status"""
    exists = os.path.exists(filename)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filename}")
    return exists

def check_placeholder_content(filename, placeholder_texts):
    """Check if file contains placeholder content"""
    if not os.path.exists(filename):
        return True  # If file doesn't exist, consider it as placeholder
    
    try:
        with open(filename, 'r') as f:
            content = f.read()
            for placeholder in placeholder_texts:
                if placeholder in content:
                    return True
        return False
    except:
        return True

def run_test_script(script_name, description):
    """Run a test script and return success status"""
    print(f"\n🧪 Running {description}...")
    print("-" * 30)
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=False, 
                              text=True)
        success = result.returncode == 0
        
        if success:
            print(f"✅ {description} completed successfully!")
        else:
            print(f"❌ {description} failed!")
        
        return success
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    print_banner()
    
    # Phase 1: Check credential files
    print("📋 Phase 1: Checking credential files...")
    print("-" * 40)
    
    desktop_exists = check_file_exists("client_secrets.json", "Desktop OAuth credentials")
    web_exists = check_file_exists("web_client_secrets.json", "Web OAuth credentials")
    
    if not desktop_exists or not web_exists:
        print("\n❌ Missing credential files!")
        print("📋 Please follow the setup guide: OAUTH_SETUP_GUIDE.md")
        print("   Step 1: Create OAuth2 credentials in Google Cloud Console")
        return False
    
    # Check for placeholder content
    print("\n🔍 Checking for placeholder content...")
    
    desktop_placeholder = check_placeholder_content("client_secrets.json", 
                                                   ["YOUR_NEW_DESKTOP_CLIENT_ID", "PLACEHOLDER"])
    web_placeholder = check_placeholder_content("web_client_secrets.json", 
                                               ["YOUR_ACTUAL_WEB_CLIENT_ID", "PLACEHOLDER"])
    
    if desktop_placeholder:
        print("❌ client_secrets.json contains placeholder values!")
        print("📋 Please replace with real credentials from Google Cloud Console")
        return False
    
    if web_placeholder:
        print("❌ web_client_secrets.json contains placeholder values!")
        print("📋 Please replace with real credentials from Google Cloud Console")
        return False
    
    print("✅ Credential files appear to have real values")
    
    # Phase 2: Test scripts
    print("\n🧪 Phase 2: Running OAuth tests...")
    print("-" * 40)
    
    # Ask user what they want to test
    print("Which tests would you like to run?")
    print("1. Desktop OAuth only")
    print("2. Web OAuth only") 
    print("3. Full integration only")
    print("4. All tests (recommended)")
    print("5. Skip tests")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            run_test_script("test_desktop_oauth.py", "Desktop OAuth Test")
            break
        elif choice == "2":
            run_test_script("test_web_oauth.py", "Web OAuth Test")
            break
        elif choice == "3":
            run_test_script("test_full_integration.py", "Full Integration Test")
            break
        elif choice == "4":
            print("\n🚀 Running all tests in sequence...")
            
            # Run desktop OAuth first
            desktop_success = run_test_script("test_desktop_oauth.py", "Desktop OAuth Test")
            
            if desktop_success:
                # Run web OAuth test
                web_success = run_test_script("test_web_oauth.py", "Web OAuth Test")
                
                if web_success:
                    # Run full integration
                    run_test_script("test_full_integration.py", "Full Integration Test")
            
            break
        elif choice == "5":
            print("⏭️  Skipping tests")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")
    
    # Phase 3: Next steps
    print("\n🎯 Phase 3: Next steps...")
    print("-" * 40)
    
    print("✅ OAuth2 setup verification complete!")
    print()
    
    print("🚀 Quick start commands:")
    print("   # Test CLI with demo mode")
    print("   python -m app.cli create-demo-playlist csv_files/sample.csv 'Test Playlist'")
    print()
    
    print("   # Test CLI with real playlist (requires working OAuth)")
    print("   python -m app.cli create-playlist csv_files/sample.csv 'My Playlist' --privacy private")
    print()
    
    print("   # Start FastAPI server")
    print("   uvicorn app.main:app --reload --port 3000")
    print()
    
    print("📚 Documentation:")
    print("   • Complete setup guide: OAUTH_SETUP_GUIDE.md")
    print("   • API docs: http://localhost:3000/docs (when server running)")
    print("   • Project README: README.md")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 