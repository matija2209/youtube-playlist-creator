import googleapiclient.discovery
import googleapiclient.errors
from typing import List, Optional
from ..models.schemas import Song, YouTubeVideo
from config import Config
import logging

logger = logging.getLogger(__name__)

class YouTubeAPIService:
    """Service for interacting with YouTube Data API v3"""
    
    def __init__(self):
        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.api_key = Config.YOUTUBE_API_KEY
        
        if not self.api_key:
            raise ValueError("YouTube API key is required")
        
        # Build the YouTube service
        self.youtube = googleapiclient.discovery.build(
            self.api_service_name, 
            self.api_version, 
            developerKey=self.api_key
        )
        logger.info("YouTube API service initialized")
    
    def search_video(self, song: Song) -> Optional[YouTubeVideo]:
        """
        Search for a video based on song title and artist
        
        Args:
            song: Song object with title and artist
            
        Returns:
            YouTubeVideo object if found, None otherwise
        """
        try:
            # Create search query
            query = f"{song.title} {song.artist}"
            logger.debug(f"Searching for: {query}")
            
            # Search for videos
            search_response = self.youtube.search().list(
                q=query,
                part="id,snippet",
                maxResults=Config.MAX_SEARCH_RESULTS,
                type="video"
            ).execute()
            
            # Process search results
            for item in search_response.get("items", []):
                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]
                channel_title = item["snippet"]["channelTitle"]
                description = item["snippet"]["description"]
                
                # Basic relevance check - if song title appears in video title
                if (song.title.lower() in title.lower() or 
                    song.artist.lower() in title.lower() or
                    song.artist.lower() in channel_title.lower()):
                    
                    video = YouTubeVideo(
                        video_id=video_id,
                        title=title,
                        channel_title=channel_title,
                        description=description
                    )
                    logger.info(f"Found video for '{song}': {title}")
                    return video
            
            logger.warning(f"No suitable video found for: {song}")
            return None
            
        except googleapiclient.errors.HttpError as e:
            logger.error(f"YouTube API error searching for '{song}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error searching for '{song}': {e}")
            return None
    
    def create_playlist(self, title: str, description: str = "", privacy_status: str = "private") -> Optional[str]:
        """
        Create a new YouTube playlist
        
        Args:
            title: Playlist title
            description: Playlist description
            privacy_status: Playlist privacy (private, public, unlisted)
            
        Returns:
            Playlist ID if successful, None otherwise
        """
        try:
            playlists_insert_response = self.youtube.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description
                    },
                    "status": {
                        "privacyStatus": privacy_status
                    }
                }
            ).execute()
            
            playlist_id = playlists_insert_response["id"]
            logger.info(f"Created playlist '{title}' with ID: {playlist_id}")
            return playlist_id
            
        except googleapiclient.errors.HttpError as e:
            logger.error(f"YouTube API error creating playlist '{title}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating playlist '{title}': {e}")
            return None
    
    def add_video_to_playlist(self, playlist_id: str, video_id: str) -> bool:
        """
        Add a video to a playlist
        
        Args:
            playlist_id: YouTube playlist ID
            video_id: YouTube video ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.youtube.playlistItems().insert(
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
            ).execute()
            
            logger.debug(f"Added video {video_id} to playlist {playlist_id}")
            return True
            
        except googleapiclient.errors.HttpError as e:
            # Check if it's a duplicate error
            if "videoAlreadyInPlaylist" in str(e):
                logger.info(f"Video {video_id} already in playlist {playlist_id}")
                return False  # Indicate this was a duplicate
            else:
                logger.error(f"YouTube API error adding video to playlist: {e}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error adding video to playlist: {e}")
            return False
    
    def get_playlist_url(self, playlist_id: str) -> str:
        """
        Generate playlist URL from playlist ID
        
        Args:
            playlist_id: YouTube playlist ID
            
        Returns:
            Full YouTube playlist URL
        """
        return f"https://www.youtube.com/playlist?list={playlist_id}"
    
    def test_api_connection(self) -> bool:
        """
        Test if API connection is working
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Simple test - search for a common term
            search_response = self.youtube.search().list(
                q="test",
                part="id",
                maxResults=1,
                type="video"
            ).execute()
            
            logger.info("YouTube API connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"YouTube API connection test failed: {e}")
            return False
