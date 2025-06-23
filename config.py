import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Project paths
    PROJECT_ROOT = Path(__file__).parent
    CSV_FOLDER = PROJECT_ROOT / "csv_files"
    LOGS_FOLDER = PROJECT_ROOT / "logs"
    
    # YouTube API
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    
    # Playlist defaults
    DEFAULT_PLAYLIST_PRIVACY: str = os.getenv("DEFAULT_PLAYLIST_PRIVACY", "private")
    
    # CSV processing
    CSV_REQUIRED_COLUMNS: list = ["Title", "Artist"]
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.YOUTUBE_API_KEY:
            raise ValueError("YOUTUBE_API_KEY environment variable is required")
        
        # Create necessary directories
        cls.CSV_FOLDER.mkdir(exist_ok=True)
        cls.LOGS_FOLDER.mkdir(exist_ok=True)
        
    @classmethod
    def get_csv_files(cls) -> list:
        """Get all CSV files in the csv_files folder"""
        return list(cls.CSV_FOLDER.glob("*.csv"))
