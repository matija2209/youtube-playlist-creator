from pydantic import BaseModel
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """Represents a song with title and artist"""
    title: str
    artist: str
    
    def __str__(self):
        return f"{self.title} by {self.artist}"

@dataclass 
class YouTubeVideo:
    """Represents a YouTube video found in search"""
    video_id: str
    title: str
    channel_title: str
    description: str = ""
    
class PlaylistSummary(BaseModel):
    """Summary of playlist creation results"""
    playlist_name: str
    playlist_url: str
    playlist_id: str
    total_songs: int
    added_count: int
    not_found_count: int
    duplicate_count: int
    not_found: List[Song] = []
    duplicates: List[Song] = []
    
    class Config:
        arbitrary_types_allowed = True

class CSVUpload(BaseModel):
    """Schema for CSV file upload"""
    filename: str
    content: bytes
    
class PlaylistRequest(BaseModel):
    """Schema for playlist creation request"""
    csv_file: str
    playlist_name: Optional[str] = None
    privacy_status: str = "private"
