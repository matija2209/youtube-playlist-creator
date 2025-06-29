"""
OAuth2 Authentication Service for YouTube API
"""
import os
import json
import logging
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class YouTubeOAuthService:
    """Handles OAuth2 authentication for YouTube API"""
    
    # YouTube API requires specific scopes for playlist management
    SCOPES = [
        'https://www.googleapis.com/auth/youtube',
        'https://www.googleapis.com/auth/youtube.force-ssl'
    ]
    
    def __init__(self, client_secrets_file: str = "client_secrets.json"):
        """
        Initialize OAuth service
        
        Args:
            client_secrets_file: Path to OAuth client secrets JSON file
        """
        self.client_secrets_file = client_secrets_file
        self.credentials: Optional[Credentials] = None
        self.youtube = None
        
        # Ensure client secrets file exists
        if not os.path.exists(client_secrets_file):
            raise FileNotFoundError(
                f"OAuth client secrets file not found: {client_secrets_file}\n"
                "Please create this file with your OAuth2 credentials."
            )
    
    def authenticate(self, force_reauth: bool = False) -> Credentials:
        """
        Authenticate user with OAuth2 flow
        
        Args:
            force_reauth: Force re-authentication even if token exists
            
        Returns:
            Google OAuth2 credentials
        """
        token_file = "token.json"
        
        # Load existing token if available and not forcing reauth
        if not force_reauth and os.path.exists(token_file):
            try:
                self.credentials = Credentials.from_authorized_user_file(
                    token_file, self.SCOPES
                )
                logger.info("Loaded existing OAuth2 token")
            except Exception as e:
                logger.warning(f"Failed to load existing token: {e}")
                self.credentials = None
        
        # If there are no (valid) credentials available, let the user log in
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                try:
                    logger.info("Refreshing expired OAuth2 token...")
                    self.credentials.refresh(Request())
                    logger.info("Successfully refreshed OAuth2 token")
                except Exception as e:
                    logger.warning(f"Failed to refresh token: {e}")
                    self.credentials = None
            
            if not self.credentials:
                logger.info("Starting OAuth2 authentication flow...")
                
                # Use InstalledAppFlow for CLI authentication
                logger.info("Starting OAuth2 authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.SCOPES
                )
                
                try:
                    self.credentials = flow.run_local_server(
                        port=3000,
                        prompt='consent',
                        authorization_prompt_message='Please visit this URL to authorize the application: {url}',
                        success_message='Authentication successful! You can close this window.',
                    )
                except Exception as e:
                    logger.warning(f"Local server failed: {e}. Trying manual flow...")
                    # Fall back to manual flow
                    auth_url, _ = flow.authorization_url(prompt='consent')
                    print(f"Please visit this URL to authorize the application: {auth_url}")
                    auth_code = input("Enter the authorization code: ")
                    flow.fetch_token(code=auth_code)
                    self.credentials = flow.credentials
                        
                logger.info("OAuth2 authentication completed successfully")
        
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(self.credentials.to_json())
            logger.info("Saved OAuth2 token for future use")
        
        return self.credentials
    
    def get_youtube_service(self, force_reauth: bool = False):
        """
        Get authenticated YouTube API service
        
        Args:
            force_reauth: Force re-authentication
            
        Returns:
            YouTube API service object
        """
        if not self.youtube or force_reauth:
            credentials = self.authenticate(force_reauth)
            self.youtube = build('youtube', 'v3', credentials=credentials)
            logger.info("YouTube API service initialized with OAuth2")
        
        return self.youtube
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
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
                logger.info("OAuth2 credentials revoked")
            except Exception as e:
                logger.warning(f"Failed to revoke credentials: {e}")
        
        # Remove token file
        token_file = "token.json"
        if os.path.exists(token_file):
            os.remove(token_file)
            logger.info("Removed token file")
        
        self.credentials = None
        self.youtube = None
    
    def get_user_info(self) -> dict:
        """Get authenticated user's YouTube channel information"""
        if not self.youtube:
            self.get_youtube_service()
        
        try:
            request = self.youtube.channels().list(
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