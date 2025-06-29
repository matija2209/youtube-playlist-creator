#!/usr/bin/env python3
"""
Test script for desktop OAuth flow
"""
import logging
import sys
import os

# Add the project root to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.oauth_service import YouTubeOAuthService

# Enable debug logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_desktop_oauth():
    print("🚀 Testing Desktop OAuth Flow...")
    print("=" * 50)
    
    try:
        # Check if client_secrets.json exists and has real credentials
        if not os.path.exists("client_secrets.json"):
            print("❌ client_secrets.json not found!")
            print("📋 Please create OAuth2 credentials in Google Cloud Console first.")
            return False
        
        # Read the file to check for placeholder values
        with open("client_secrets.json", "r") as f:
            content = f.read()
            if "YOUR_NEW_DESKTOP_CLIENT_ID" in content or "PLACEHOLDER" in content:
                print("❌ client_secrets.json contains placeholder values!")
                print("📋 Please replace with real OAuth2 credentials from Google Cloud Console.")
                return False
        
        print("✅ client_secrets.json exists and appears to have real credentials")
        
        # Initialize OAuth service
        print("🔧 Initializing OAuth service...")
        oauth_service = YouTubeOAuthService("client_secrets.json")
        
        # Test authentication
        print("📋 Starting authentication...")
        print("🌐 This will open your browser for Google login...")
        
        credentials = oauth_service.authenticate(force_reauth=True)
        
        if credentials and credentials.valid:
            print("✅ Authentication successful!")
            
            # Test getting user info
            print("👤 Getting user information...")
            user_info = oauth_service.get_user_info()
            if user_info:
                print(f"   📺 Channel: {user_info.get('title', 'Unknown')}")
                print(f"   🆔 Channel ID: {user_info.get('channel_id', 'Unknown')}")
                print(f"   👥 Subscribers: {user_info.get('subscriber_count', 'N/A')}")
                print(f"   🎥 Videos: {user_info.get('video_count', 'N/A')}")
            
            # Test YouTube API service
            print("🎵 Testing YouTube API service...")
            youtube = oauth_service.get_youtube_service()
            if youtube:
                print("✅ YouTube API service initialized successfully!")
            
            return True
        else:
            print("❌ Authentication failed!")
            return False
            
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("📋 Please ensure client_secrets.json exists with valid OAuth2 credentials.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False

def cleanup_tokens():
    """Clean up any existing tokens for fresh testing"""
    token_files = ["token.json", "web_token.json"]
    for token_file in token_files:
        if os.path.exists(token_file):
            os.remove(token_file)
            print(f"🧹 Removed old {token_file}")

if __name__ == "__main__":
    print("🧹 Cleaning up old tokens for fresh test...")
    cleanup_tokens()
    print()
    
    success = test_desktop_oauth()
    print("=" * 50)
    
    if success:
        print("🎉 Desktop OAuth is working correctly!")
        print("✅ You can now use the CLI with OAuth authentication.")
        print("🔄 Next: Run 'python test_web_oauth.py' to test web OAuth")
    else:
        print("⚠️  Desktop OAuth needs fixing.")
        print("📋 Follow the setup instructions to create real OAuth2 credentials.") 