from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from .models.schemas import PlaylistSummary
from .services.playlist_creator import PlaylistCreatorService
from .services.web_oauth_service import YouTubeWebOAuthService
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
            "preview": "/preview-csv",
            "oauth_login": "/oauth/login",
            "oauth_callback": "/oauth/callback",
            "oauth_status": "/oauth/status",
            "oauth_demo": "/oauth/demo"
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
    privacy_status: str = Query("private", description="Playlist privacy"),
    use_oauth: bool = Query(True, description="Use OAuth2 for playlist creation (required for real playlists)")
):
    """Create playlist from CSV file in the csv_files folder"""
    
    csv_path = Config.CSV_FOLDER / filename
    if not csv_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"CSV file '{filename}' not found in csv_files folder"
        )
    
    try:
        service = PlaylistCreatorService(use_oauth=use_oauth)
        
        if use_oauth:
            result = service.process_csv_to_playlist(str(csv_path), playlist_name, privacy_status)
        else:
            # Demo mode
            result = service.demo_playlist_creation(str(csv_path), playlist_name or "Demo Playlist")
            
        logger.info(f"Playlist {'created' if use_oauth else 'demoed'} from folder CSV: {result.playlist_name}")
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

@app.get("/oauth/status")
async def oauth_status():
    """Check OAuth authentication status"""
    try:
        oauth_service = YouTubeWebOAuthService()
        is_authenticated = oauth_service.is_authenticated()
        
        if is_authenticated:
            user_info = oauth_service.get_user_info()
            return {
                "authenticated": True,
                "user_info": user_info
            }
        else:
            return {
                "authenticated": False,
                "login_url": "/oauth/login"
            }
            
    except Exception as e:
        logger.error(f"OAuth status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/oauth/login")
async def oauth_login(request: Request):
    """Initiate OAuth2 login flow - returns authorization URL for frontend"""
    try:
        oauth_service = YouTubeWebOAuthService()
        
        # Determine the correct redirect URI based on the request
        host = request.headers.get("host", "localhost:3000")
        if "ngrok" in host:
            redirect_uri = f"https://{host}/oauth/callback"
        elif "localhost:3000" in host or request.headers.get("origin", "").endswith(":3000"):
            redirect_uri = "http://localhost:3000/oauth/callback"
        else:
            redirect_uri = f"http://{host}/oauth/callback"
        
        # Generate state for security
        import secrets
        state = secrets.token_urlsafe(32)
        
        # Get authorization URL
        auth_url = oauth_service.get_authorization_url(redirect_uri, state)
        
        return {
            "authorization_url": auth_url,
            "state": state,
            "redirect_uri": redirect_uri
        }
        
    except Exception as e:
        logger.error(f"OAuth login failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/oauth/callback")
async def oauth_callback(request: Request, code: str = None, state: str = None, error: str = None):
    """OAuth2 callback endpoint - handles the redirect from Google"""
    if error:
        logger.error(f"OAuth error: {error}")
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    
    try:
        oauth_service = YouTubeWebOAuthService()
        
        # Determine the redirect URI (same logic as in login)
        host = request.headers.get("host", "localhost:3000")
        if "ngrok" in host:
            redirect_uri = f"https://{host}/oauth/callback"
        elif "localhost:3000" in host:
            redirect_uri = "http://localhost:3000/oauth/callback"
        else:
            redirect_uri = f"http://{host}/oauth/callback"
        
        # Exchange code for tokens
        token_info = oauth_service.exchange_code_for_tokens(code, redirect_uri, state)
        
        # Get user info
        user_info = oauth_service.get_user_info()
        
        return {
            "status": "success",
            "message": "Authentication completed successfully!",
            "user_info": user_info,
            "token_info": {
                "access_token": token_info["access_token"][:10] + "...",  # Truncated for security
                "expires_in": token_info["expires_in"],
                "scope": token_info["scope"]
            }
        }
        
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/oauth/demo")
async def oauth_demo():
    """Demo page showing how to use the OAuth flow from frontend"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>YouTube Playlist Creator - OAuth Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .button { background: #4285f4; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 10px 0; }
            .button:hover { background: #3367d6; }
            .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
            pre { background: #f8f9fa; padding: 15px; border-radius: 4px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>🎵 YouTube Playlist Creator - OAuth Demo</h1>
        
        <div class="info">
            <strong>This is a demo of the Web OAuth2 flow for your frontend application.</strong><br>
            Your frontend should implement similar JavaScript to handle authentication.
        </div>
        
        <div id="status"></div>
        
        <button class="button" onclick="checkStatus()">Check Auth Status</button>
        <button class="button" onclick="startAuth()">Start Authentication</button>
        <button class="button" onclick="testAPI()">Test API Call</button>
        
        <h3>Response:</h3>
        <pre id="response"></pre>
        
        <h3>How to implement in your frontend:</h3>
        <pre>
// 1. Check authentication status
fetch('/oauth/status')
  .then(response => response.json())
  .then(data => console.log(data));

// 2. Start OAuth flow
fetch('/oauth/login')
  .then(response => response.json())
  .then(data => {
    // Redirect user to authorization URL
    window.location.href = data.authorization_url;
  });

// 3. Handle callback (automatic)
// User will be redirected to /oauth/callback after authorization

// 4. Create playlist
fetch('/create-from-csv-folder?filename=sample.csv&playlist_name=My Playlist&use_oauth=true')
  .then(response => response.json())
  .then(data => console.log(data));
        </pre>
        
        <script>
            async function checkStatus() {
                try {
                    const response = await fetch('/oauth/status');
                    const data = await response.json();
                    document.getElementById('response').textContent = JSON.stringify(data, null, 2);
                    
                    if (data.authenticated) {
                        document.getElementById('status').innerHTML = 
                            '<div class="success">✅ Authenticated as: ' + data.user_info.title + '</div>';
                    } else {
                        document.getElementById('status').innerHTML = 
                            '<div class="error">❌ Not authenticated</div>';
                    }
                } catch (error) {
                    document.getElementById('status').innerHTML = 
                        '<div class="error">❌ Error: ' + error.message + '</div>';
                }
            }
            
            async function startAuth() {
                try {
                    const response = await fetch('/oauth/login');
                    const data = await response.json();
                    document.getElementById('response').textContent = JSON.stringify(data, null, 2);
                    
                    if (data.authorization_url) {
                        document.getElementById('status').innerHTML = 
                            '<div class="info">🔄 Redirecting to Google for authentication...</div>';
                        setTimeout(() => {
                            window.location.href = data.authorization_url;
                        }, 2000);
                    }
                } catch (error) {
                    document.getElementById('status').innerHTML = 
                        '<div class="error">❌ Error: ' + error.message + '</div>';
                }
            }
            
            async function testAPI() {
                try {
                    const response = await fetch('/create-from-csv-folder?filename=sample.csv&playlist_name=OAuth Test Playlist&use_oauth=true&dry_run=true');
                    const data = await response.json();
                    document.getElementById('response').textContent = JSON.stringify(data, null, 2);
                    
                    document.getElementById('status').innerHTML = 
                        '<div class="success">✅ API test completed</div>';
                } catch (error) {
                    document.getElementById('status').innerHTML = 
                        '<div class="error">❌ API Error: ' + error.message + '</div>';
                }
            }
            
            // Check status on page load
            checkStatus();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

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

# Run with: uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
