from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query
from fastapi.responses import JSONResponse, FileResponse
from .models.schemas import PlaylistSummary
from .services.playlist_creator import PlaylistCreatorService
from config import Config
import tempfile
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Playlist Creator API",
    description="Create YouTube playlists from CSV files containing song titles and artists",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup"""
    try:
        Config.validate()
        logger.info("YouTube Playlist Creator API started successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """API information and status"""
    return {
        "message": "YouTube Playlist Creator API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "upload": "/upload-csv",
            "create_from_folder": "/create-from-csv-folder",
            "list_csv_files": "/list-csv-files",
            "preview": "/preview-csv"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test if we can initialize the service
        service = PlaylistCreatorService()
        test_results = service.test_services()
        
        return {
            "status": "healthy" if test_results["overall"] else "degraded",
            "service": "YouTube Playlist Creator",
            "csv_folder": str(Config.CSV_FOLDER),
            "csv_files_count": len(Config.get_csv_files()),
            "youtube_api": test_results["youtube_api"],
            "csv_parser": test_results["csv_parser"]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/list-csv-files")
async def list_csv_files():
    """List all CSV files in the csv_files folder"""
    csv_files = Config.get_csv_files()
    return {
        "csv_folder": str(Config.CSV_FOLDER),
        "files": [{"name": f.name, "size": f.stat().st_size} for f in csv_files],
        "count": len(csv_files)
    }

@app.get("/preview-csv")
async def preview_csv(
    filename: str = Query(..., description="CSV filename from csv_files folder"),
    rows: int = Query(5, description="Number of rows to preview")
):
    """Preview CSV file contents"""
    csv_path = Config.CSV_FOLDER / filename
    if not csv_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"CSV file '{filename}' not found in csv_files folder"
        )
    
    try:
        service = PlaylistCreatorService()
        songs = service.preview_csv(str(csv_path), rows)
        
        return {
            "filename": filename,
            "preview_rows": len(songs),
            "songs": [{"title": song.title, "artist": song.artist} for song in songs]
        }
        
    except Exception as e:
        logger.error(f"Error previewing CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-csv", response_model=PlaylistSummary)
async def upload_and_create_playlist(
    file: UploadFile = File(..., description="CSV file with Title and Artist columns"),
    playlist_name: str = Form(None, description="Name for the playlist"),
    privacy_status: str = Form("private", description="Playlist privacy: private, public, or unlisted")
):
    """Upload CSV file and create YouTube playlist"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        service = PlaylistCreatorService()
        result = service.process_csv_to_playlist(temp_file_path, playlist_name, privacy_status)
        logger.info(f"Playlist created successfully: {result.playlist_name}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing uploaded CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temp file
        os.unlink(temp_file_path)

@app.post("/create-from-csv-folder", response_model=PlaylistSummary)
async def create_playlist_from_folder(
    filename: str = Query(..., description="CSV filename from csv_files folder"),
    playlist_name: str = Query(None, description="Name for the playlist"),
    privacy_status: str = Query("private", description="Playlist privacy")
):
    """Create playlist from CSV file in the csv_files folder"""
    
    csv_path = Config.CSV_FOLDER / filename
    if not csv_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"CSV file '{filename}' not found in csv_files folder"
        )
    
    try:
        service = PlaylistCreatorService()
        result = service.process_csv_to_playlist(str(csv_path), playlist_name, privacy_status)
        logger.info(f"Playlist created from folder CSV: {result.playlist_name}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing CSV from folder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test_services():
    """Test all services and return status"""
    try:
        service = PlaylistCreatorService()
        results = service.test_services()
        
        return {
            "status": "success" if results["overall"] else "partial_failure",
            "tests": results,
            "message": "All services working" if results["overall"] else "Some services have issues"
        }
        
    except Exception as e:
        logger.error(f"Service test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid input", "detail": str(exc)}
    )

@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "File not found", "detail": str(exc)}
    )

# Run with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
