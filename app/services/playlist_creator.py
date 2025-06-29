from typing import List, Set
from ..models.schemas import Song, PlaylistSummary
from .csv_parser import CSVParserService
from .youtube_api import YouTubeAPIService
from config import Config
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class PlaylistCreatorService:
    """Main service that orchestrates CSV parsing and YouTube playlist creation"""
    
    def __init__(self, use_oauth: bool = False):
        """
        Initialize the service
        
        Args:
            use_oauth: Whether to use OAuth2 for YouTube API (required for playlist creation)
        """
        self.csv_parser = CSVParserService()
        self.youtube_api = YouTubeAPIService(use_oauth=use_oauth)
        self.use_oauth = use_oauth
        logger.info(f"PlaylistCreatorService initialized (OAuth: {use_oauth})")
    
    def estimate_quota_and_confirm(self, num_songs: int, playlist_name: str, is_demo: bool = False) -> bool:
        """
        Estimate quota usage and get user confirmation before processing
        
        Args:
            num_songs: Number of songs to process
            playlist_name: Name of the playlist
            is_demo: Whether this is a demo run
            
        Returns:
            True if user confirms, False if user cancels
        """
        quota_info = self.youtube_api.calculate_estimated_quota_usage(num_songs)
        
        print("\n" + "="*60)
        print("📊 QUOTA USAGE ESTIMATION")
        print("="*60)
        print(f"🎵 Playlist: {playlist_name}")
        print(f"📁 Songs to process: {num_songs}")
        print(f"🎯 Estimated success rate: {quota_info['estimated_success_rate']*100:.0f}%")
        print(f"🎶 Expected videos found: {quota_info['estimated_found_songs']}")
        
        if is_demo:
            print(f"🔍 Demo mode: Only searching (no playlist creation)")
        
        print("\n💰 Quota Usage Breakdown:")
        print(f"  • Search operations: {quota_info['breakdown']['search_operations']:,} units")
        if not is_demo:
            print(f"  • Playlist creation: {quota_info['breakdown']['playlist_creation']:,} units")
            print(f"  • Adding videos: {quota_info['breakdown']['adding_videos']:,} units")
        
        total_units = quota_info['breakdown']['search_operations']
        if not is_demo:
            total_units = quota_info['total_estimated_units']
            
        print(f"  • TOTAL ESTIMATED: {total_units:,} units")
        print(f"\n📈 Daily quota usage: {round((total_units/10000)*100, 1)}% of 10,000 units")
        
        if total_units > 10000:
            print(f"⚠️  WARNING: This exceeds daily quota!")
            print(f"📅 Estimated days needed: {max(1, round(total_units/10000, 1))}")
            print(f"💡 Consider requesting quota increase or processing in smaller batches")
        else:
            print(f"✅ Should complete within daily quota limit")
        
        print("\n" + "="*60)
        
        # Get user confirmation
        while True:
            choice = input("🤔 Do you want to continue? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                print("✅ Proceeding with playlist processing...")
                return True
            elif choice in ['n', 'no']:
                print("❌ Operation cancelled by user.")
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    
    def process_csv_to_playlist(self, csv_file_path: str, playlist_name: str = None, privacy_status: str = "private") -> PlaylistSummary:
        """
        Complete process: Parse CSV, search videos, create playlist
        
        Args:
            csv_file_path: Path to CSV file
            playlist_name: Name for the playlist (optional)
            privacy_status: Playlist privacy setting
            
        Returns:
            PlaylistSummary with results
        """
        logger.info(f"Starting playlist creation from CSV: {csv_file_path}")
        
        # Parse CSV file first to get song count
        try:
            songs = self.csv_parser.parse_csv(csv_file_path)
            if not songs:
                raise ValueError("No valid songs found in CSV file")
        except Exception as e:
            logger.error(f"Failed to parse CSV file: {e}")
            raise
        
        # Generate playlist name if not provided
        if not playlist_name:
            csv_filename = Path(csv_file_path).stem
            playlist_name = f"Playlist from {csv_filename}"
        
        # Estimate quota and get user confirmation
        if not self.estimate_quota_and_confirm(len(songs), playlist_name, is_demo=False):
            raise Exception("Operation cancelled by user")
        
        # Create YouTube playlist
        playlist_id = self.youtube_api.create_playlist(
            title=playlist_name,
            description=f"Playlist created from CSV file: {Path(csv_file_path).name}",
            privacy=privacy_status
        )
        
        if not playlist_id:
            raise Exception("Failed to create YouTube playlist")
        
        # Process songs and add to playlist
        return self._add_songs_to_playlist(songs, playlist_id, playlist_name)
    
    def demo_playlist_creation(self, csv_file_path: str, playlist_name: str = None) -> PlaylistSummary:
        """
        Demo mode: Parse CSV and search for videos without creating a playlist
        
        Args:
            csv_file_path: Path to CSV file
            playlist_name: Name for the demo playlist
            
        Returns:
            PlaylistSummary with search results (no actual playlist created)
        """
        logger.info(f"Starting demo playlist creation from CSV: {csv_file_path}")
        
        # Parse CSV file first to get song count
        try:
            songs = self.csv_parser.parse_csv(csv_file_path)
            if not songs:
                raise ValueError("No valid songs found in CSV file")
        except Exception as e:
            logger.error(f"Failed to parse CSV file: {e}")
            raise
        
        # Generate playlist name if not provided
        if not playlist_name:
            csv_filename = Path(csv_file_path).stem
            playlist_name = f"Demo Playlist from {csv_filename}"
        
        # Estimate quota and get user confirmation
        if not self.estimate_quota_and_confirm(len(songs), playlist_name, is_demo=True):
            raise Exception("Operation cancelled by user")
        
        # Demo mode - just search for videos without creating playlist
        return self._demo_search_songs(songs, playlist_name)
    
    def _demo_search_songs(self, songs: List[Song], playlist_name: str) -> PlaylistSummary:
        """
        Demo mode: Search for videos without adding them to a playlist
        
        Args:
            songs: List of songs to process
            playlist_name: Name of the demo playlist
            
        Returns:
            PlaylistSummary with search results
        """
        found_count = 0
        not_found = []
        duplicates = []
        found_video_ids: Set[str] = set()
        
        logger.info(f"Demo: Searching for {len(songs)} songs for playlist '{playlist_name}'")
        
        for i, song in enumerate(songs, 1):
            logger.info(f"Demo: Searching song {i}/{len(songs)}: {song}")
            
            # Add delay between songs to avoid rate limiting
            if i > 1:
                time.sleep(2.0)  # 2 second delay between songs
            
            try:
                # Search for video
                video = self.youtube_api.find_best_match(song.title, song.artist)
                
                if not video:
                    logger.warning(f"Demo: No video found for: {song}")
                    not_found.append(song)
                    continue
                
                # Check for duplicates
                if video['id'] in found_video_ids:
                    logger.info(f"Demo: Duplicate video found for: {song}")
                    duplicates.append(song)
                    continue
                
                # In demo mode, we just count as "found"
                found_count += 1
                found_video_ids.add(video['id'])
                logger.info(f"Demo: Found video for: {song} -> {video['title']}")
                
            except Exception as e:
                logger.error(f"Demo: Error searching for song '{song}': {e}")
                not_found.append(song)
        
        # Create demo summary (no actual playlist)
        summary = PlaylistSummary(
            playlist_name=playlist_name + " (Demo)",
            playlist_url=None,  # No actual playlist created
            playlist_id=None,   # No actual playlist created
            total_songs=len(songs),
            added_count=found_count,  # Actually "found_count" in demo mode
            not_found_count=len(not_found),
            duplicate_count=len(duplicates),
            not_found=not_found,
            duplicates=duplicates
        )
        
        logger.info(f"Demo complete: {found_count}/{len(songs)} videos found on YouTube")
        return summary
    
    def _add_songs_to_playlist(self, songs: List[Song], playlist_id: str, playlist_name: str) -> PlaylistSummary:
        """
        Search for videos and add them to the playlist
        
        Args:
            songs: List of songs to process
            playlist_id: YouTube playlist ID
            playlist_name: Name of the playlist
            
        Returns:
            PlaylistSummary with detailed results
        """
        added_count = 0
        not_found = []
        duplicates = []
        added_video_ids: Set[str] = set()
        
        logger.info(f"Processing {len(songs)} songs for playlist '{playlist_name}'")
        
        for i, song in enumerate(songs, 1):
            logger.info(f"Processing song {i}/{len(songs)}: {song}")
            
            # Add delay between songs to avoid rate limiting
            if i > 1:
                time.sleep(2.0)  # 2 second delay between songs
            
            try:
                # Search for video
                video = self.youtube_api.find_best_match(song.title, song.artist)
                
                if not video:
                    logger.warning(f"No video found for: {song}")
                    not_found.append(song)
                    continue
                
                # Check for duplicates
                if video['id'] in added_video_ids:
                    logger.info(f"Duplicate video found for: {song}")
                    duplicates.append(song)
                    continue
                
                # Add to playlist
                success = self.youtube_api.add_video_to_playlist(playlist_id, video['id'])
                
                if success:
                    added_count += 1
                    added_video_ids.add(video['id'])
                    logger.info(f"Successfully added: {song} -> {video['title']}")
                elif not success:
                    # This might be a duplicate at the YouTube level
                    logger.info(f"Video already in playlist or failed to add: {song}")
                    duplicates.append(song)
                
            except Exception as e:
                logger.error(f"Error processing song '{song}': {e}")
                not_found.append(song)
        
        # Create summary
        playlist_url = self.youtube_api.get_playlist_url(playlist_id)
        
        summary = PlaylistSummary(
            playlist_name=playlist_name,
            playlist_url=playlist_url,
            playlist_id=playlist_id,
            total_songs=len(songs),
            added_count=added_count,
            not_found_count=len(not_found),
            duplicate_count=len(duplicates),
            not_found=not_found,
            duplicates=duplicates
        )
        
        logger.info(f"Playlist creation complete: {added_count}/{len(songs)} songs added")
        return summary
    
    def preview_csv(self, csv_file_path: str, num_rows: int = 5) -> List[Song]:
        """
        Preview CSV file contents
        
        Args:
            csv_file_path: Path to CSV file
            num_rows: Number of rows to preview
            
        Returns:
            List of Song objects (preview)
        """
        return self.csv_parser.preview_csv(csv_file_path, num_rows)
    
    def validate_csv(self, csv_file_path: str) -> bool:
        """
        Validate CSV file format
        
        Args:
            csv_file_path: Path to CSV file
            
        Returns:
            True if valid, False otherwise
        """
        return self.csv_parser.validate_csv_format(csv_file_path)
    
    def test_services(self) -> dict:
        """
        Test all services are working
        
        Returns:
            Dictionary with test results
        """
        results = {
            "youtube_api": False,
            "csv_parser": False,
            "overall": False
        }
        
        try:
            # Test YouTube API
            results["youtube_api"] = self.youtube_api.test_api_connection()
            
            # Test CSV parser (basic functionality)
            results["csv_parser"] = True  # CSV parser doesn't need external connection
            
            results["overall"] = results["youtube_api"] and results["csv_parser"]
            
        except Exception as e:
            logger.error(f"Service test failed: {e}")
        
        return results
