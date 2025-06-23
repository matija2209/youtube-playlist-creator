import pytest
import tempfile
import pandas as pd
from pathlib import Path
from app.services.csv_parser import CSVParserService
from app.models.schemas import Song

class TestCSVParserService:
    def setup_method(self):
        self.service = CSVParserService()
    
    def test_parse_valid_csv(self):
        # Create temporary CSV file
        csv_content = """Title,Artist
Shape of You,Ed Sheeran
Blinding Lights,The Weeknd"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            songs = self.service.parse_csv(temp_path)
            assert len(songs) == 2
            assert songs[0].title == "Shape of You"
            assert songs[0].artist == "Ed Sheeran"
            assert songs[1].title == "Blinding Lights"
            assert songs[1].artist == "The Weeknd"
        finally:
            Path(temp_path).unlink()
    
    def test_missing_columns(self):
        # CSV without required columns
        csv_content = """Song,Performer
Shape of You,Ed Sheeran"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Missing required columns"):
                self.service.parse_csv(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_empty_csv(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="CSV file is empty"):
                self.service.parse_csv(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_validate_csv_format(self):
        # Valid format
        csv_content = """Title,Artist
Song1,Artist1"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            assert self.service.validate_csv_format(temp_path) == True
        finally:
            Path(temp_path).unlink()
        
        # Invalid format
        csv_content = """Song,Performer
Song1,Artist1"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            assert self.service.validate_csv_format(temp_path) == False
        finally:
            Path(temp_path).unlink()
