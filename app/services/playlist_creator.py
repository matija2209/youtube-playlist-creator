from typing import List, Set
from ..models.schemas import Song, PlaylistSummary
from .csv_parser import CSVParserService
from .youtube_api import YouTubeAPIService
from config import Config
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PlaylistCreatorService:
    """Main service that orchestrates CSV parsing and YouTube playlist creation"""
    
    def __init__(self):
        self.csv_parser = CSVParserService()
        self.youtube_api = YouTubeAPIService()
        logger.info("PlaylistCreatorService initialized")
    
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
        
        # Parse CSV file
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
        
        # Create YouTube playlist
        playlist_id = self.youtube_api.create_playlist(
            title=playlist_name,
            description=f"Playlist created from CSV file: {Path(csv_file_path).name}",
            privacy_status=privacy_status
        )
        
        if not playlist_id:
            raise Exception("Failed to create YouTube playlist")
        
        # Process songs and add to playlist
        return self._add_songs_to_playlist(songs, playlist_id, playlist_name)
    
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
            
            try:
                # Search for video
                video = self.youtube_api.search_video(song)
                
                if not video:
                    logger.warning(f"No video found for: {song}")
                    not_found.append(song)
                    continue
                
                # Check for duplicates
                if video.video_id in added_video_ids:
                    logger.info(f"Duplicate video found for: {song}")
                    duplicates.append(song)
                    continue
                
                # Add to playlist
                success = self.youtube_api.add_video_to_playlist(playlist_id, video.video_id)
                
                if success:
                    added_count += 1
                    added_video_ids.add(video.video_id)
                    logger.info(f"Successfully added: {song} -> {video.title}")
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
