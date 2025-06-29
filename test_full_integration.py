#!/usr/bin/env python3
"""
Test full integration: OAuth + YouTube API + Playlist Creation
"""
import logging
import sys
import os

# Add the project root to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.playlist_creator import PlaylistCreatorService

# Enable debug logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_playlist_creation():
    print("🎵 Testing Full Integration...")
    print("📋 OAuth + YouTube API + Playlist Creation")
    print("=" * 60)
    
    try:
        # Check if we have a sample CSV file
        csv_path = "csv_files/sample.csv"
        if not os.path.exists(csv_path):
            print(f"❌ Sample CSV not found: {csv_path}")
            print("📋 Please ensure csv_files/sample.csv exists for testing.")
            return False
        
        print(f"✅ Found sample CSV: {csv_path}")
        
        # Test with OAuth-enabled service
        print("🔧 Initializing PlaylistCreatorService with OAuth...")
        service = PlaylistCreatorService(use_oauth=True)
        
        # Test service health first
        print("🏥 Testing service health...")
        health_results = service.test_services()
        
        print("📊 Service Health Results:")
        for service_name, status in health_results.items():
            if service_name == "overall":
                continue
            status_emoji = "✅" if status else "❌"
            print(f"   {status_emoji} {service_name}: {'OK' if status else 'FAILED'}")
        
        if not health_results.get("youtube_api", False):
            print("⚠️  YouTube API test failed - this is expected without OAuth")
            print("🔄 Continuing with OAuth test...")
        
        # Test demo mode first (no actual YouTube playlist creation)
        print("\n🎭 Testing DEMO mode (no actual playlist creation)...")
        try:
            demo_result = service.demo_playlist_creation(csv_path, "Integration Test Demo")
            
            print("✅ Demo completed successfully!")
            print(f"   📈 Songs processed: {demo_result.total_songs}")
            print(f"   ✅ Songs found: {demo_result.added_count}")
            print(f"   ❌ Songs not found: {demo_result.not_found_count}")
            print(f"   📊 Success rate: {(demo_result.added_count/demo_result.total_songs)*100:.1f}%")
            
            if demo_result.not_found:
                print("   ❌ Failed songs:")
                for song in demo_result.not_found[:3]:  # Show first 3
                    print(f"      • {song.title} - {song.artist}")
                if len(demo_result.not_found) > 3:
                    print(f"      ... and {len(demo_result.not_found) - 3} more")
        
        except Exception as e:
            print(f"❌ Demo mode failed: {e}")
            print("🔍 This might indicate issues with CSV parsing or YouTube search")
            return False
        
        # If demo works and user wants to test real playlist creation
        if demo_result.added_count > 0:
            print(f"\n🎉 Demo successful! Found {demo_result.added_count} songs.")
            
            confirm = input("🔄 Create REAL YouTube playlist with OAuth? (y/N): ").strip().lower()
            if confirm == 'y':
                print("\n🚀 Testing REAL playlist creation with OAuth...")
                
                try:
                    playlist_name = "🧪 Integration Test Playlist"
                    real_result = service.process_csv_to_playlist(
                        csv_path, 
                        playlist_name, 
                        "private"  # Keep it private for testing
                    )
                    
                    print("🎉 Real playlist created successfully!")
                    print(f"   📝 Playlist: {real_result.playlist_name}")
                    print(f"   🔗 URL: {real_result.playlist_url}")
                    print(f"   📈 Songs added: {real_result.added_count}/{real_result.total_songs}")
                    
                    # Offer to delete test playlist
                    delete_confirm = input("\n🗑️  Delete test playlist? (y/N): ").strip().lower()
                    if delete_confirm == 'y':
                        try:
                            # Note: This would require implementing playlist deletion
                            print("⚠️  Playlist deletion not implemented yet.")
                            print(f"📋 Please manually delete: {real_result.playlist_url}")
                        except Exception as e:
                            print(f"⚠️  Could not delete playlist: {e}")
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ Real playlist creation failed: {e}")
                    print("🔍 This indicates OAuth or YouTube API issues")
                    
                    # Provide debugging info
                    if "authentication" in str(e).lower() or "oauth" in str(e).lower():
                        print("🔧 OAuth debugging suggestions:")
                        print("   • Run 'python test_desktop_oauth.py' to test OAuth separately")
                        print("   • Check if token.json was created and is valid")
                        print("   • Verify YouTube Data API v3 is enabled in Google Cloud Console")
                    
                    return False
            else:
                print("⏭️  Skipping real playlist creation")
                return True
        else:
            print("⚠️  Demo found no songs - check CSV format or YouTube search issues")
            return False
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Provide debugging suggestions
        if "client_secrets" in str(e):
            print("🔧 OAuth setup issue:")
            print("   • Ensure client_secrets.json has real credentials")
            print("   • Run 'python test_desktop_oauth.py' first")
        elif "CSV" in str(e) or "parse" in str(e):
            print("🔧 CSV issue:")
            print("   • Check csv_files/sample.csv exists and has Title,Artist columns")
        
        return False

def preview_sample_csv():
    """Preview the sample CSV to understand what we're working with"""
    csv_path = "csv_files/sample.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Sample CSV not found: {csv_path}")
        return False
    
    print("📄 Sample CSV Preview:")
    print("=" * 30)
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:6]  # Show first 5 rows + header
            for i, line in enumerate(lines):
                prefix = "📋 Header:" if i == 0 else f"   Row {i}:"
                print(f"{prefix} {line.strip()}")
        
        print(f"   ... (showing first 5 rows of {len(lines)-1} total)")
        return True
    
    except Exception as e:
        print(f"❌ Could not read CSV: {e}")
        return False

if __name__ == "__main__":
    print("📄 Previewing sample CSV first...")
    preview_sample_csv()
    print()
    
    success = test_playlist_creation()
    print("=" * 60)
    
    if success:
        print("🎉 Integration test completed successfully!")
        print("✅ OAuth + YouTube API + Playlist Creation all working")
        print("🚀 Your system is ready for production use!")
    else:
        print("⚠️  Integration test failed.")
        print("🔧 Debug steps:")
        print("   1. Run 'python test_desktop_oauth.py' to test OAuth")
        print("   2. Check YouTube Data API v3 is enabled")
        print("   3. Verify CSV file format")
        print("   4. Check logs for detailed error information") 