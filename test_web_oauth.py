#!/usr/bin/env python3
"""
Test script for web OAuth flow
"""
import logging
import sys
import os

# Add the project root to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.web_oauth_service import YouTubeWebOAuthService

# Enable debug logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_web_oauth():
    print("🌐 Testing Web OAuth Flow...")
    print("=" * 50)
    
    try:
        # Check if web_client_secrets.json exists and has real credentials
        if not os.path.exists("web_client_secrets.json"):
            print("❌ web_client_secrets.json not found!")
            print("📋 Please create Web Application OAuth2 credentials in Google Cloud Console first.")
            return False
        
        # Read the file to check for placeholder values
        with open("web_client_secrets.json", "r") as f:
            content = f.read()
            if "YOUR_ACTUAL_WEB_CLIENT_ID" in content or "PLACEHOLDER" in content:
                print("❌ web_client_secrets.json contains placeholder values!")
                print("📋 Please replace with real Web Application OAuth2 credentials from Google Cloud Console.")
                return False
        
        print("✅ web_client_secrets.json exists and appears to have real credentials")
        
        # Initialize web OAuth service
        print("🔧 Initializing Web OAuth service...")
        oauth_service = YouTubeWebOAuthService("web_client_secrets.json")
        
        # Test authorization URL generation
        redirect_uri = "http://localhost:3000/oauth/callback"
        
        print("🔗 Generating authorization URL...")
        auth_url = oauth_service.get_authorization_url(redirect_uri)
        
        print("✅ Authorization URL generated successfully!")
        print("📋 Authorization URL:")
        print(f"   {auth_url}")
        print()
        print("🌐 To complete the test:")
        print("   1. Copy the URL above and open it in your browser")
        print("   2. Log in to Google and grant permissions")
        print("   3. After redirect, copy the 'code' parameter from the callback URL")
        print("   4. Enter it below")
        print()
        
        # Manual code exchange test
        while True:
            auth_code = input("📝 Enter the authorization code (or 'skip' to test URL generation only): ").strip()
            
            if auth_code.lower() == 'skip':
                print("⏭️  Skipping token exchange test")
                return True
            
            if not auth_code:
                print("⚠️  Please enter a code or 'skip'")
                continue
            
            try:
                print("🔄 Exchanging authorization code for tokens...")
                token_info = oauth_service.exchange_code_for_tokens(auth_code, redirect_uri)
                
                print("✅ Token exchange successful!")
                print(f"🔑 Access token: {token_info['access_token'][:20]}...")
                print(f"🔄 Refresh token: {'Yes' if token_info.get('refresh_token') else 'No'}")
                
                # Test getting user info
                print("👤 Testing user info retrieval...")
                user_info = oauth_service.get_user_info()
                if user_info:
                    print(f"   📺 Channel: {user_info.get('title', 'Unknown')}")
                    print(f"   🆔 Channel ID: {user_info.get('channel_id', 'Unknown')}")
                
                return True
                
            except Exception as e:
                print(f"❌ Token exchange failed: {e}")
                retry = input("🔄 Try again with a new code? (y/N): ").strip().lower()
                if retry != 'y':
                    return False
            
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("📋 Please ensure web_client_secrets.json exists with valid OAuth2 credentials.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False

def test_fastapi_integration():
    """Test FastAPI OAuth endpoints"""
    print("\n🚀 Testing FastAPI OAuth Integration...")
    print("=" * 50)
    
    try:
        import requests
        base_url = "http://localhost:3000"
        
        print("🔍 Testing OAuth endpoints...")
        
        # Test OAuth status
        try:
            response = requests.get(f"{base_url}/oauth/status", timeout=5)
            print(f"✅ /oauth/status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️  FastAPI server not running. Start with: uvicorn app.main:app --reload --port 3000")
            return False
        
        # Test OAuth login
        response = requests.get(f"{base_url}/oauth/login", timeout=5)
        print(f"✅ /oauth/login: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'auth_url' in data:
                print(f"   🔗 Auth URL generated: {data['auth_url'][:50]}...")
        
        return True
        
    except ImportError:
        print("⚠️  'requests' not installed. Install with: pip install requests")
        return False
    except Exception as e:
        print(f"❌ FastAPI integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧹 Cleaning up old web tokens for fresh test...")
    if os.path.exists("web_token.json"):
        os.remove("web_token.json")
        print("🧹 Removed old web_token.json")
    print()
    
    success = test_web_oauth()
    print("=" * 50)
    
    if success:
        print("🎉 Web OAuth is working correctly!")
        print("✅ Authorization URL generation works")
        print("🔄 Next: Test FastAPI integration")
        
        # Test FastAPI integration if requested
        test_integration = input("\n🚀 Test FastAPI integration? (y/N): ").strip().lower()
        if test_integration == 'y':
            test_fastapi_integration()
    else:
        print("⚠️  Web OAuth needs fixing.")
        print("📋 Follow the setup instructions to create real OAuth2 credentials.") 