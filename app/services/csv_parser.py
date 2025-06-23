import pandas as pd
from typing import List
from ..models.schemas import Song
import logging

logger = logging.getLogger(__name__)

class CSVParserService:
    """Service for parsing CSV files containing song data"""
    
    def __init__(self):
        self.required_columns = ["Title", "Artist"]
    
    def parse_csv(self, file_path: str) -> List[Song]:
        """
        Parse CSV file and return list of Song objects
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of Song objects
            
        Raises:
            ValueError: If required columns are missing
            FileNotFoundError: If file doesn't exist
        """
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            logger.info(f"Successfully read CSV file: {file_path}")
            logger.info(f"CSV shape: {df.shape}")
            
            # Validate required columns exist
            missing_columns = [col for col in self.required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}. Available columns: {list(df.columns)}")
            
            # Remove rows with missing title or artist
            df = df.dropna(subset=self.required_columns)
            logger.info(f"After removing rows with missing data: {df.shape}")
            
            # Convert to Song objects
            songs = []
            for _, row in df.iterrows():
                song = Song(
                    title=str(row['Title']).strip(),
                    artist=str(row['Artist']).strip()
                )
                songs.append(song)
            
            logger.info(f"Parsed {len(songs)} songs from CSV")
            return songs
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {file_path}")
            raise
        except pd.errors.EmptyDataError:
            logger.error(f"CSV file is empty: {file_path}")
            raise ValueError("CSV file is empty")
        except Exception as e:
            logger.error(f"Error parsing CSV file {file_path}: {str(e)}")
            raise
    
    def validate_csv_format(self, file_path: str) -> bool:
        """
        Validate if CSV file has the correct format
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            df = pd.read_csv(file_path, nrows=1)  # Read only first row
            return all(col in df.columns for col in self.required_columns)
        except Exception:
            return False
    
    def preview_csv(self, file_path: str, num_rows: int = 5) -> List[Song]:
        """
        Preview first few rows of CSV file
        
        Args:
            file_path: Path to the CSV file
            num_rows: Number of rows to preview
            
        Returns:
            List of Song objects (first num_rows)
        """
        try:
            df = pd.read_csv(file_path, nrows=num_rows)
            
            if not all(col in df.columns for col in self.required_columns):
                return []
            
            songs = []
            for _, row in df.iterrows():
                song = Song(
                    title=str(row['Title']).strip(),
                    artist=str(row['Artist']).strip()
                )
                songs.append(song)
            
            return songs
        except Exception as e:
            logger.error(f"Error previewing CSV: {str(e)}")
            return []
