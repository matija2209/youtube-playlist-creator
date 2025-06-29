"""
YouTube API Service - handles YouTube Data API v3 operations
"""
import logging
import time
from typing import List, Optional, Dict, Any
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

from app.services.oauth_service import YouTubeOAuthService
from app.services.web_oauth_service import YouTubeWebOAuthService
from config import Config

logger = logging.getLogger(__name__)

class YouTubeAPIService:
    """Service for interacting with YouTube Data API v3"""
    
    def __init__(self, use_oauth: bool = False, oauth_service: Optional[YouTubeOAuthService] = None, web_oauth_service: Optional[YouTubeWebOAuthService] = None):
        """
        Initialize YouTube API service
        
        Args:
            use_oauth: Whether to use OAuth2 authentication (required for playlist creation)
            oauth_service: Optional OAuth service instance
        """
        self.use_oauth = use_oauth
        self.oauth_service = oauth_service
        self.web_oauth_service = web_oauth_service
        self.youtube = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize YouTube API service with appropriate authentication"""
        try:
            if self.use_oauth:
                # Prefer web OAuth service for web apps, fallback to desktop OAuth
                if self.web_oauth_service:
                    self.youtube = self.web_oauth_service.get_youtube_service()
                    logger.info("YouTube API service initialized with Web OAuth2")
                elif self.oauth_service:
                    self.youtube = self.oauth_service.get_youtube_service()
                    logger.info("YouTube API service initialized with Desktop OAuth2")
                else:
                    # Create default services - try web first, then desktop
                    try:
                        self.web_oauth_service = YouTubeWebOAuthService()
                        if self.web_oauth_service.is_authenticated():
                            self.youtube = self.web_oauth_service.get_youtube_service()
                            logger.info("YouTube API service initialized with default Web OAuth2")
                        else:
                            raise Exception("Web OAuth not authenticated")
                    except:
                        self.oauth_service = YouTubeOAuthService()
                        self.youtube = self.oauth_service.get_youtube_service()
                        logger.info("YouTube API service initialized with default Desktop OAuth2")
            else:
                # Use API key for read-only operations
                if not Config.GOOGLE_CLOUD_API_KEY:
                    raise ValueError("YouTube API key is required when not using OAuth2")
                self.youtube = build('youtube', 'v3', developerKey=Config.GOOGLE_CLOUD_API_KEY)
                logger.info("YouTube API service initialized with API key")
        except Exception as e:
            logger.error(f"Failed to initialize YouTube API service: {e}")
            raise
    
    def search_videos(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for videos on YouTube
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of video dictionaries with id, title, description, channel
        """
        try:
            logger.info(f"Searching YouTube for: '{query}'")
            
            request = self.youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results,
                order="relevance"
            )
            
            response = request.execute()
            videos = []
            
            for item in response.get('items', []):
                video = {
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt']
                }
                videos.append(video)
            
            logger.info(f"Found {len(videos)} videos for query: '{query}'")
            return videos
            
        except HttpError as e:
            logger.error(f"YouTube API error for query '{query}': {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching for '{query}': {e}")
            return []
    
    def find_best_match(self, title: str, artist: str, max_results: int = 5) -> Optional[Dict[str, Any]]:
        """
        Find the best matching video for a song
        
        Args:
            title: Song title
            artist: Artist name
            max_results: Maximum search results to consider
            
        Returns:
            Best matching video dictionary or None if not found
        """
        # Use simple "title artist" format for optimal quota usage
        query = f"{title} {artist}"
        
        videos = self.search_videos(query, max_results)
        
        if videos:
            # Simple scoring: prefer videos with both title and artist in the name
            for video in videos:
                video_title_lower = video['title'].lower()
                title_lower = title.lower()
                artist_lower = artist.lower()
                
                if title_lower in video_title_lower and artist_lower in video_title_lower:
                    logger.info(f"Found video for '{title} by {artist}': {video['title']}")
                    return video
            
            # If no perfect match, return the first result
            logger.info(f"Found video for '{title} by {artist}': {videos[0]['title']}")
            return videos[0]
        
        logger.warning(f"No suitable video found for: {title} by {artist}")
        return None
    
    def create_playlist(self, title: str, description: str = "", privacy: str = "private") -> Optional[str]:
        """
        Create a new YouTube playlist (requires OAuth2)
        
        Args:
            title: Playlist title
            description: Playlist description
            privacy: Playlist privacy setting (private, public, unlisted)
            
        Returns:
            Playlist ID if successful, None otherwise
        """
        if not self.use_oauth:
            logger.error("OAuth2 authentication required for playlist creation")
            raise ValueError("OAuth2 authentication required for playlist creation")
        
        try:
            logger.info(f"Creating playlist: '{title}'")
            
            request = self.youtube.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description,
                        "tags": ["music", "playlist", "created-by-youtube-playlist-creator"],
                        "defaultLanguage": "en"
                    },
                    "status": {
                        "privacyStatus": privacy
                    }
                }
            )
            
            response = request.execute()
            playlist_id = response['id']
            
            logger.info(f"Successfully created playlist '{title}' with ID: {playlist_id}")
            return playlist_id
            
        except HttpError as e:
            logger.error(f"YouTube API error creating playlist '{title}': {e}")
            raise Exception(f"Failed to create YouTube playlist: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating playlist '{title}': {e}")
            raise Exception(f"Failed to create YouTube playlist: {e}")
    
    def add_video_to_playlist(self, playlist_id: str, video_id: str) -> bool:
        """
        Add a video to a playlist (requires OAuth2)
        
        Args:
            playlist_id: Target playlist ID
            video_id: Video ID to add
            
        Returns:
            True if successful, False otherwise
        """
        if not self.use_oauth:
            logger.error("OAuth2 authentication required for playlist modification")
            raise ValueError("OAuth2 authentication required for playlist modification")
        
        try:
            request = self.youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            )
            
            response = request.execute()
            logger.info(f"Added video {video_id} to playlist {playlist_id}")
            return True
            
        except HttpError as e:
            logger.error(f"YouTube API error adding video {video_id} to playlist {playlist_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error adding video {video_id} to playlist {playlist_id}: {e}")
            return False
    
    def get_playlist_url(self, playlist_id: str) -> str:
        """
        Generate YouTube playlist URL
        
        Args:
            playlist_id: Playlist ID
            
        Returns:
            YouTube playlist URL
        """
        return f"https://www.youtube.com/playlist?list={playlist_id}"
    
    def check_quota_usage(self) -> Dict[str, Any]:
        """
        Check current quota usage (approximation)
        
        Returns:
            Dictionary with quota information
        """
        # This is an approximation as YouTube doesn't provide real-time quota info
        return {
            "search_cost": 100,  # units per search
            "playlist_creation_cost": 50,  # units per playlist
            "playlist_item_cost": 50,  # units per video added
            "note": "YouTube API has a default quota of 10,000 units per day"
        }

    def calculate_estimated_quota_usage(self, num_songs: int, estimated_success_rate: float = 0.8) -> Dict[str, Any]:
        """
        Calculate estimated quota usage for processing a given number of songs
        
        Args:
            num_songs: Number of songs to process
            estimated_success_rate: Estimated percentage of songs that will be found (0.0-1.0)
            
        Returns:
            Dictionary with quota usage breakdown
        """
        # Search operations (one per song)
        search_units = num_songs * 100
        
        # Playlist creation (one per playlist)
        playlist_creation_units = 50
        
        # Adding videos to playlist (estimated based on success rate)
        estimated_found_songs = int(num_songs * estimated_success_rate)
        playlist_item_units = estimated_found_songs * 50
        
        total_estimated_units = search_units + playlist_creation_units + playlist_item_units
        
        return {
            "num_songs": num_songs,
            "estimated_success_rate": estimated_success_rate,
            "estimated_found_songs": estimated_found_songs,
            "breakdown": {
                "search_operations": search_units,
                "playlist_creation": playlist_creation_units,
                "adding_videos": playlist_item_units
            },
            "total_estimated_units": total_estimated_units,
            "daily_quota_limit": 10000,
            "quota_percentage": round((total_estimated_units / 10000) * 100, 1),
            "can_complete_today": total_estimated_units <= 10000,
            "days_needed": max(1, round(total_estimated_units / 10000, 1))
        }
