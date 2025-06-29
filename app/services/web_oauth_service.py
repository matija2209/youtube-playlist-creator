"""
Web OAuth2 Authentication Service for YouTube API (FastAPI Backend)
"""
import os
import json
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlencode

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class YouTubeWebOAuthService:
    """Handles Web OAuth2 authentication for YouTube API (FastAPI backend)"""
    
    # YouTube API requires specific scopes for playlist management
    SCOPES = [
        'https://www.googleapis.com/auth/youtube',
        'https://www.googleapis.com/auth/youtube.force-ssl'
    ]
    
    def __init__(self, client_secrets_file: str = "web_client_secrets.json"):
        """
        Initialize Web OAuth service for FastAPI backend
        
        Args:
            client_secrets_file: Path to OAuth web client secrets JSON file
        """
        self.client_secrets_file = client_secrets_file
        self.credentials: Optional[Credentials] = None
        self.youtube = None
        
        # Ensure client secrets file exists
        if not os.path.exists(client_secrets_file):
            raise FileNotFoundError(
                f"Web OAuth client secrets file not found: {client_secrets_file}\n"
                "Please create this file with your Web Application OAuth2 credentials."
            )
    
    def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """
        Get the authorization URL for the OAuth2 flow
        
        Args:
            redirect_uri: The redirect URI registered in Google Cloud Console
            state: Optional state parameter for security
            
        Returns:
            Authorization URL for the user to visit
        """
        try:
            flow = Flow.from_client_secrets_file(
                self.client_secrets_file,
                scopes=self.SCOPES,
                redirect_uri=redirect_uri
            )
            
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent',
                state=state
            )
            
            logger.info(f"Generated authorization URL for redirect_uri: {redirect_uri}")
            return auth_url
            
        except Exception as e:
            logger.error(f"Failed to generate authorization URL: {e}")
            raise
    
    def exchange_code_for_tokens(self, code: str, redirect_uri: str, state: str = None) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            code: Authorization code from Google
            redirect_uri: The same redirect URI used in authorization
            state: State parameter for verification
            
        Returns:
            Dictionary containing token information
        """
        try:
            flow = Flow.from_client_secrets_file(
                self.client_secrets_file,
                scopes=self.SCOPES,
                redirect_uri=redirect_uri
            )
            
            # Exchange code for tokens
            flow.fetch_token(code=code)
            self.credentials = flow.credentials
            
            # Save credentials
            self.save_credentials()
            
            logger.info("Successfully exchanged authorization code for tokens")
            
            return {
                'access_token': self.credentials.token,
                'refresh_token': self.credentials.refresh_token,
                'expires_in': 3600,  # Default expiry
                'scope': ' '.join(self.SCOPES),
                'token_type': 'Bearer'
            }
            
        except Exception as e:
            logger.error(f"Failed to exchange code for tokens: {e}")
            raise
    
    def save_credentials(self, token_file: str = "web_token.json"):
        """Save credentials to file"""
        if self.credentials:
            with open(token_file, 'w') as token:
                token.write(self.credentials.to_json())
                logger.info(f"Saved credentials to {token_file}")
    
    def load_credentials(self, token_file: str = "web_token.json") -> bool:
        """
        Load credentials from file
        
        Returns:
            True if credentials loaded and valid, False otherwise
        """
        if not os.path.exists(token_file):
            return False
        
        try:
            self.credentials = Credentials.from_authorized_user_file(
                token_file, self.SCOPES
            )
            
            # Check if credentials are valid
            if self.credentials.expired and self.credentials.refresh_token:
                logger.info("Refreshing expired credentials...")
                self.credentials.refresh(Request())
                self.save_credentials(token_file)
            
            if self.credentials.valid:
                logger.info("Loaded valid credentials from file")
                return True
            else:
                logger.warning("Loaded credentials are not valid")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return False
    
    def get_youtube_service(self):
        """
        Get authenticated YouTube API service
        
        Returns:
            YouTube API service object
        """
        if not self.youtube and self.credentials and self.credentials.valid:
            self.youtube = build('youtube', 'v3', credentials=self.credentials)
            logger.info("YouTube API service initialized with Web OAuth2")
        
        return self.youtube
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        if not self.credentials:
            return self.load_credentials()
        
        return (
            self.credentials is not None and 
            self.credentials.valid and 
            not self.credentials.expired
        )
    
    def revoke_authentication(self):
        """Revoke current authentication and remove token file"""
        if self.credentials:
            try:
                self.credentials.revoke(Request())
                logger.info("Web OAuth2 credentials revoked")
            except Exception as e:
                logger.warning(f"Failed to revoke credentials: {e}")
        
        # Remove token file
        token_file = "web_token.json"
        if os.path.exists(token_file):
            os.remove(token_file)
            logger.info("Removed web token file")
        
        self.credentials = None
        self.youtube = None
    
    def get_user_info(self) -> dict:
        """Get authenticated user's YouTube channel information"""
        youtube = self.get_youtube_service()
        if not youtube:
            return {}
        
        try:
            request = youtube.channels().list(
                part="snippet,statistics",
                mine=True
            )
            response = request.execute()
            
            if 'items' in response and response['items']:
                channel = response['items'][0]
                return {
                    'channel_id': channel['id'],
                    'title': channel['snippet']['title'],
                    'description': channel['snippet']['description'],
                    'subscriber_count': channel['statistics'].get('subscriberCount', 'N/A'),
                    'video_count': channel['statistics'].get('videoCount', 'N/A'),
                    'view_count': channel['statistics'].get('viewCount', 'N/A')
                }
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return {}
        
        return {} 