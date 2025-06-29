import click
from pathlib import Path
from .services.playlist_creator import PlaylistCreatorService
from .services.oauth_service import YouTubeOAuthService
from config import Config
import logging

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """YouTube Playlist Creator CLI"""
    try:
        Config.validate()
    except ValueError as e:
        click.echo(f"❌ Configuration Error: {e}", err=True)
        exit(1)

@cli.command()
@click.option('--list-files', '-l', is_flag=True, help='List available CSV files')
@click.option('--file', '-f', help='Specify CSV filename (from csv_files folder)')
@click.option('--playlist-name', '-n', help='Name for the playlist')
@click.option('--privacy', '-p', default='private', 
              type=click.Choice(['private', 'public', 'unlisted']), 
              help='Playlist privacy setting')
@click.option('--dry-run', '-d', is_flag=True, help='Demo mode - search for videos without creating playlist')
@click.option('--oauth', '-o', is_flag=True, help='Use OAuth2 authentication (required for real playlist creation)')
def create(list_files, file, playlist_name, privacy, dry_run, oauth):
    """Create YouTube playlist from CSV file in csv_files folder"""
    
    if list_files:
        _list_csv_files()
        return
    
    if not file:
        click.echo("Available CSV files:")
        _list_csv_files()
        file = click.prompt("Enter CSV filename")
    
    csv_path = Config.CSV_FOLDER / file
    if not csv_path.exists():
        click.echo(f"❌ File not found: {csv_path}", err=True)
        return 1
    
    try:
        click.echo(f"🎵 Processing CSV file: {file}")
        click.echo(f"📁 Full path: {csv_path}")
        
        if dry_run:
            click.echo("🔍 DRY RUN MODE - Searching for videos without creating playlist")
            click.echo("="*60)
        
        # Check if trying to create real playlist without OAuth
        if not dry_run and not oauth:
            click.echo("⚠️ Warning: Real playlist creation requires OAuth2 authentication.")
            click.echo("   Use --oauth flag to authenticate, or --dry-run to demo without creating playlist.")
            if not click.confirm("Continue with dry-run mode?"):
                return 1
            dry_run = True
        
        service = PlaylistCreatorService(use_oauth=oauth)
        
        if dry_run:
            # Demo mode - just search for videos
            result = service.demo_playlist_creation(str(csv_path), playlist_name or "Demo Playlist")
        else:
            # Real mode - create playlist with OAuth2
            result = service.process_csv_to_playlist(str(csv_path), playlist_name, privacy)
        
        # Display results
        click.echo("\n" + "="*50)
        if dry_run:
            click.echo("🎯 DEMO PLAYLIST SEARCH COMPLETE!")
        else:
            click.echo("🎉 PLAYLIST CREATION COMPLETE!")
        click.echo("="*50)
        click.echo(f"📋 Playlist: {result.playlist_name}")
        if not dry_run and result.playlist_url:
            click.echo(f"🔗 URL: {result.playlist_url}")
        click.echo(f"📊 Total songs processed: {result.total_songs}")
        click.echo(f"✅ Videos found: {result.added_count}")
        click.echo(f"❌ Not found: {result.not_found_count}")
        click.echo(f"🔄 Duplicates skipped: {result.duplicate_count}")
        
        if result.not_found:
            click.echo(f"\n❌ Songs not found:")
            for song in result.not_found:
                click.echo(f"  - {song.title} by {song.artist}")
                
        if result.duplicates:
            click.echo(f"\n🔄 Duplicate songs skipped:")
            for song in result.duplicates:
                click.echo(f"  - {song.title} by {song.artist}")
                
        if dry_run:
            click.echo(f"\n💡 To create real playlists, OAuth2 authentication is required.")
            click.echo(f"   This demo shows the {result.added_count} videos that would be added to the playlist.")
        
    except Exception as e:
        logger.error(f"Error creating playlist: {e}")
        click.echo(f"❌ Error: {str(e)}", err=True)
        return 1

@cli.command()
@click.option('--file', '-f', help='CSV filename to preview')
@click.option('--rows', '-r', default=5, help='Number of rows to preview')
def preview(file, rows):
    """Preview CSV file contents"""
    
    if not file:
        click.echo("Available CSV files:")
        _list_csv_files()
        file = click.prompt("Enter CSV filename to preview")
    
    csv_path = Config.CSV_FOLDER / file
    if not csv_path.exists():
        click.echo(f"❌ File not found: {csv_path}", err=True)
        return 1
    
    try:
        service = PlaylistCreatorService()
        songs = service.preview_csv(str(csv_path), rows)
        
        if songs:
            click.echo(f"\n📄 Preview of {file} (first {len(songs)} rows):")
            click.echo("-" * 50)
            for i, song in enumerate(songs, 1):
                click.echo(f"{i:2d}. {song.title} by {song.artist}")
        else:
            click.echo("❌ No valid songs found in CSV file")
            
    except Exception as e:
        click.echo(f"❌ Error previewing file: {str(e)}", err=True)

@cli.command()
def test():
    """Test system configuration and services"""
    click.echo("🔧 Testing system configuration...")
    
    try:
        # Test configuration
        Config.validate()
        click.echo("✅ Configuration is valid")
        
        # Test services
        service = PlaylistCreatorService()
        results = service.test_services()
        
        click.echo(f"✅ CSV Parser: {'Working' if results['csv_parser'] else 'Failed'}")
        click.echo(f"{'✅' if results['youtube_api'] else '❌'} YouTube API: {'Connected' if results['youtube_api'] else 'Failed'}")
        
        if results['overall']:
            click.echo("🎉 All systems ready!")
            click.echo("💡 Use --dry-run flag to demo playlist creation without OAuth2")
        else:
            click.echo("⚠️ Some services are not working properly")
            
    except Exception as e:
        click.echo(f"❌ Test failed: {str(e)}", err=True)

def _list_csv_files():
    """Helper to list available CSV files"""
    csv_files = Config.get_csv_files()
    if not csv_files:
        click.echo("No CSV files found in csv_files/ folder")
        click.echo(f"📁 Add CSV files to: {Config.CSV_FOLDER}")
    else:
        for csv_file in csv_files:
            click.echo(f"  📄 {csv_file.name}")

@cli.command()
def setup():
    """Setup and validate configuration"""
    click.echo("🔧 Validating configuration...")
    try:
        Config.validate()
        click.echo("✅ Configuration is valid!")
        click.echo(f"📁 CSV folder: {Config.CSV_FOLDER}")
        click.echo(f"📄 Available CSV files: {len(Config.get_csv_files())}")
        
        # Check if API key is set
        if Config.YOUTUBE_API_KEY == "your_youtube_api_key_here":
            click.echo("⚠️ Warning: Please set your YouTube API key in .env file")
        else:
            click.echo("✅ YouTube API key is configured")
            click.echo("💡 Use --dry-run flag to demo functionality without OAuth2")
            
    except Exception as e:
        click.echo(f"❌ Configuration error: {e}", err=True)

@cli.command()
def auth_login():
    """Authenticate with YouTube using OAuth2"""
    click.echo("🔐 Starting YouTube OAuth2 authentication...")
    
    try:
        oauth_service = YouTubeOAuthService()
        credentials = oauth_service.authenticate()
        
        # Get user info to confirm authentication
        user_info = oauth_service.get_user_info()
        if user_info:
            click.echo("✅ Authentication successful!")
            click.echo(f"📺 Channel: {user_info.get('title', 'Unknown')}")
            click.echo(f"👥 Subscribers: {user_info.get('subscriber_count', 'N/A')}")
            click.echo(f"🎥 Videos: {user_info.get('video_count', 'N/A')}")
        else:
            click.echo("✅ Authentication successful!")
        
        click.echo("💡 You can now create playlists using --oauth flag")
        
    except FileNotFoundError as e:
        click.echo(f"❌ Client secrets file not found: {e}")
        click.echo("💡 Please ensure client_secrets.json is in the project root")
    except Exception as e:
        click.echo(f"❌ Authentication failed: {e}", err=True)

@cli.command()
def auth_status():
    """Check OAuth2 authentication status"""
    try:
        oauth_service = YouTubeOAuthService()
        
        if oauth_service.is_authenticated():
            click.echo("✅ You are authenticated with YouTube")
            
            # Get user info
            user_info = oauth_service.get_user_info()
            if user_info:
                click.echo(f"📺 Channel: {user_info.get('title', 'Unknown')}")
        else:
            click.echo("❌ Not authenticated")
            click.echo("💡 Run 'python -m app.cli auth-login' to authenticate")
            
    except FileNotFoundError:
        click.echo("❌ OAuth2 not configured (client_secrets.json not found)")
    except Exception as e:
        click.echo(f"❌ Error checking status: {e}", err=True)

@cli.command()
def auth_logout():
    """Revoke OAuth2 authentication"""
    try:
        oauth_service = YouTubeOAuthService()
        oauth_service.revoke_authentication()
        click.echo("✅ Successfully logged out")
        
    except Exception as e:
        click.echo(f"❌ Error during logout: {e}", err=True)

if __name__ == '__main__':
    cli()
