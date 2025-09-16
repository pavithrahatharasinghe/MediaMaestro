from dotenv import load_dotenv
import os

load_dotenv()  # This line loads the environment variables from the .env file

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for request bodies
class CreatePlaylistRequest(BaseModel):
    name: str
    category: str
    create_spotify: bool = False

class CopyFilesRequest(BaseModel):
    source_paths: List[str]
    target_playlist: str

class MatchPlaylistRequest(BaseModel):
    playlist_key: str
    spotify_playlist_id: Optional[str] = None

# Import our modules (we'll handle imports gracefully)
try:
    from models.database import get_db, init_db, Playlist, Song, DownloadJob
    from utils.spotify_manager import SpotifyManager
    from utils.youtube_downloader import YouTubeDownloader
    from utils.file_manager import FileManager
except ImportError as e:
    logging.warning(f"Some modules not available: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="MediaMaestro API",
    description="Media management system with Spotify integration and YouTube downloader",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
try:
    spotify_manager = SpotifyManager()
    logger.info(f"Spotify manager initialized - configured: {spotify_manager.configured}")
except Exception as e:
    logger.error(f"Failed to initialize Spotify manager: {e}")
    spotify_manager = None

try:
    youtube_downloader = YouTubeDownloader() if 'YouTubeDownloader' in globals() else None
    if youtube_downloader:
        logger.info("YouTube downloader initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize YouTube downloader: {e}")
    youtube_downloader = None

try:
    file_manager = FileManager() if 'FileManager' in globals() else None
    if file_manager:
        logger.info("File manager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize File manager: {e}")
    file_manager = None

# Initialize database
try:
    init_db()
except Exception as e:
    logging.warning(f"Database initialization failed: {e}")

@app.get("/")
async def root():
    return {
        "message": "MediaMaestro API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    auth_status = spotify_manager.get_authentication_status() if spotify_manager else {
        "configured": False, 
        "authenticated": False, 
        "client_id_set": False, 
        "client_secret_set": False,
        "has_cached_token": False
    }
    
    return {
        "status": "healthy",
        "spotify": auth_status,
        "youtube_available": youtube_downloader is not None,
        "database_connected": True  # We'll implement proper health checks later
    }

# Spotify Authentication Routes
@app.get("/auth/spotify/login")
async def spotify_login():
    """Get Spotify authorization URL"""
    if not spotify_manager:
        raise HTTPException(status_code=503, detail="Spotify manager not available")
    
    if not spotify_manager.configured:
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "Spotify not configured",
                "message": "Please set valid SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your .env file",
                "instructions": [
                    "1. Go to https://developer.spotify.com/dashboard",
                    "2. Create a new app or use an existing one",
                    "3. Copy your Client ID and Client Secret",
                    "4. Add them to your .env file",
                    "5. Add 'http://localhost:8000/auth/spotify/callback' to your app's redirect URIs",
                    "6. Restart the application"
                ]
            }
        )
    
    try:
        auth_url = spotify_manager.get_auth_url()
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"Spotify auth URL error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get auth URL: {str(e)}")

@app.get("/auth/spotify/callback")
async def spotify_callback(code: str = Query(...)):
    """Handle Spotify authentication callback"""
    if not spotify_manager:
        raise HTTPException(status_code=503, detail="Spotify manager not available")
    
    if not spotify_manager.configured:
        raise HTTPException(status_code=400, detail="Spotify not configured. Please check your environment variables.")
    
    try:
        success = spotify_manager.authenticate(code)
        if success:
            return {"message": "Authentication successful", "authenticated": True}
        else:
            raise HTTPException(status_code=400, detail="Authentication failed. Please try again.")
    except Exception as e:
        logger.error(f"Spotify callback error: {e}")
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

@app.get("/auth/spotify/status")
async def spotify_auth_status():
    """Check Spotify authentication status"""
    if not spotify_manager:
        return {
            "configured": False,
            "authenticated": False,
            "client_id_set": False,
            "client_secret_set": False,
            "has_cached_token": False,
            "error": "Spotify manager not available"
        }
    
    return spotify_manager.get_authentication_status()

@app.post("/auth/spotify/logout")
async def spotify_logout():
    """Logout from Spotify and clear tokens"""
    if not spotify_manager:
        raise HTTPException(status_code=503, detail="Spotify manager not available")
    
    success = spotify_manager.logout()
    return {"success": success, "message": "Logged out successfully" if success else "Logout failed"}

# Playlist Management Routes
@app.get("/playlists")
async def get_playlists(db: Session = Depends(get_db)):
    """Get all local playlists"""
    try:
        playlists = db.query(Playlist).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "spotify_id": p.spotify_id,
                "song_count": len(p.songs) if p.songs else 0,
                "created_at": p.created_at
            }
            for p in playlists
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/playlists")
async def create_playlist(
    request: CreatePlaylistRequest,
    db: Session = Depends(get_db)
):
    """Create a new playlist"""
    try:
        # Check if playlist already exists
        existing = db.query(Playlist).filter(Playlist.name == request.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Playlist already exists")
        
        spotify_id = None
        if request.create_spotify and spotify_manager and spotify_manager.configured and spotify_manager.sp:
            spotify_id = spotify_manager.create_playlist(request.name, f"MediaMaestro - {request.category}")
        
        playlist = Playlist(
            name=request.name,
            category=request.category,
            spotify_id=spotify_id
        )
        
        db.add(playlist)
        db.commit()
        db.refresh(playlist)
        
        return {
            "id": playlist.id,
            "name": playlist.name,
            "category": playlist.category,
            "spotify_id": playlist.spotify_id
        }
    except Exception as e:
        logger.error(f"Failed to create playlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Song Management Routes
@app.get("/playlists/{playlist_id}/songs")
async def get_playlist_songs(playlist_id: int, db: Session = Depends(get_db)):
    """Get songs in a playlist"""
    try:
        playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        
        return [
            {
                "id": s.id,
                "title": s.title,
                "artist": s.artist,
                "album": s.album,
                "mp3_path": s.mp3_path,
                "flac_path": s.flac_path,
                "video_path": s.video_path,
                "spotify_id": s.spotify_id,
                "youtube_id": s.youtube_id,
                "duration": s.duration
            }
            for s in playlist.songs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# YouTube Download Routes
@app.get("/youtube/search")
async def search_youtube(q: str = Query(...), max_results: int = 5):
    """Search YouTube for videos"""
    if not youtube_downloader:
        raise HTTPException(status_code=503, detail="YouTube downloader not available")
    
    try:
        results = youtube_downloader.search_youtube(q, max_results)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/youtube/download")
async def download_youtube(
    url: str,
    format_type: str = "mp3",  # mp3, flac, video
    playlist_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Download from YouTube"""
    if not youtube_downloader:
        raise HTTPException(status_code=503, detail="YouTube downloader not available")
    
    try:
        # Get playlist folder if specified
        playlist_folder = None
        if playlist_id:
            playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
            if playlist:
                playlist_folder = playlist.category
        
        # Create download job
        job = DownloadJob(url=url, status="pending")
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Start download (in a real app, this would be async)
        if format_type in ["mp3", "flac"]:
            result = youtube_downloader.download_audio(url, format_type, playlist_folder)
        else:
            result = youtube_downloader.download_video(url, playlist_folder)
        
        # Update job status
        if result.get('success'):
            job.status = "completed"
            job.progress = 100
            
            # Create song record if successful
            if playlist_id:
                song = Song(
                    title=result.get('title'),
                    artist=result.get('uploader'),
                    youtube_id=result.get('youtube_id'),
                    playlist_id=playlist_id
                )
                
                if format_type == "mp3":
                    song.mp3_path = result.get('file_path')
                elif format_type == "flac":
                    song.flac_path = result.get('file_path')
                elif format_type == "video":
                    song.video_path = result.get('file_path')
                
                db.add(song)
        else:
            job.status = "failed"
            job.error_message = result.get('error')
        
        db.commit()
        
        return {
            "job_id": job.id,
            "status": job.status,
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# File Management Routes
@app.get("/files/organize/{playlist_id}")
async def organize_playlist_files(playlist_id: int, db: Session = Depends(get_db)):
    """Organize and tally files in a playlist"""
    if not youtube_downloader:
        raise HTTPException(status_code=503, detail="YouTube downloader not available")
    
    try:
        playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        
        organization_info = youtube_downloader.organize_files(playlist.category)
        return organization_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Spotify Integration Routes
@app.get("/spotify/search")
async def search_spotify(q: str = Query(...), artist: Optional[str] = None):
    """Search Spotify for tracks"""
    if not spotify_manager:
        raise HTTPException(status_code=503, detail="Spotify manager not available")
    
    if not spotify_manager.configured:
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "Spotify not configured",
                "message": "Please set valid SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your .env file",
                "setup_required": True
            }
        )
    
    if not spotify_manager.is_authenticated():
        raise HTTPException(
            status_code=401, 
            detail={
                "error": "Not authenticated",
                "message": "Please authenticate with Spotify first",
                "auth_required": True
            }
        )
    
    try:
        results = spotify_manager.search_track(q, artist)
        return {"results": results}
    except Exception as e:
        logger.error(f"Spotify search error: {e}")
        if "authentication" in str(e).lower() or "token" in str(e).lower():
            raise HTTPException(
                status_code=401, 
                detail={
                    "error": "Authentication expired",
                    "message": str(e),
                    "auth_required": True
                }
            )
        raise HTTPException(status_code=500, detail=f"Spotify search failed: {str(e)}")



@app.get("/spotify/playlists")
async def get_spotify_playlists():
    """Get user's Spotify playlists"""
    if not spotify_manager:
        raise HTTPException(status_code=503, detail="Spotify manager not available")
    
    if not spotify_manager.configured:
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "Spotify not configured",
                "message": "Please set valid SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your .env file",
                "setup_required": True
            }
        )
    
    if not spotify_manager.is_authenticated():
        raise HTTPException(
            status_code=401, 
            detail={
                "error": "Not authenticated",
                "message": "Please authenticate with Spotify first",
                "auth_required": True
            }
        )
    
    try:
        playlists = spotify_manager.get_user_playlists()
        return {"playlists": playlists}
    except Exception as e:
        logger.error(f"Spotify playlists error: {e}")
        if "authentication" in str(e).lower() or "token" in str(e).lower():
            raise HTTPException(
                status_code=401, 
                detail={
                    "error": "Authentication expired",
                    "message": str(e),
                    "auth_required": True
                }
            )
        raise HTTPException(status_code=500, detail=f"Failed to get playlists: {str(e)}")

@app.get("/spotify/playlists/{playlist_id}/tracks")
async def get_spotify_playlist_tracks(playlist_id: str):
    """Get tracks from a specific Spotify playlist"""
    if not spotify_manager:
        raise HTTPException(status_code=503, detail="Spotify manager not available")
    
    if not spotify_manager.configured:
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "Spotify not configured",
                "message": "Please set valid SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your .env file",
                "setup_required": True
            }
        )
    
    if not spotify_manager.is_authenticated():
        raise HTTPException(
            status_code=401, 
            detail={
                "error": "Not authenticated",
                "message": "Please authenticate with Spotify first",
                "auth_required": True
            }
        )
    
    try:
        tracks = spotify_manager.get_playlist_tracks(playlist_id)
        return {"tracks": tracks, "playlist_id": playlist_id}
    except Exception as e:
        logger.error(f"Spotify playlist tracks error: {e}")
        if "authentication" in str(e).lower() or "token" in str(e).lower():
            raise HTTPException(
                status_code=401, 
                detail={
                    "error": "Authentication expired",
                    "message": str(e),
                    "auth_required": True
                }
            )
        raise HTTPException(status_code=500, detail=f"Failed to get playlist tracks: {str(e)}")

# File Management Routes
@app.get("/files/scan")
async def scan_media_files():
    """Scan all media files and return organization status"""
    if not file_manager:
        raise HTTPException(status_code=503, detail="File manager not available")
    
    try:
        result = file_manager.scan_media_directory()
        return result
    except Exception as e:
        logger.error(f"File scan error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to scan files: {str(e)}")

@app.post("/files/copy")
async def copy_files_to_media(request: CopyFilesRequest):
    """Copy files from external locations to media directory"""
    if not file_manager:
        raise HTTPException(status_code=503, detail="File manager not available")
    
    try:
        result = file_manager.copy_files_to_media_directory(
            request.source_paths, 
            request.target_playlist
        )
        return result
    except Exception as e:
        logger.error(f"File copy error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to copy files: {str(e)}")

@app.get("/files/missing/{playlist_key}")
async def find_missing_formats(playlist_key: str):
    """Find songs missing in certain formats for a playlist"""
    if not file_manager:
        raise HTTPException(status_code=503, detail="File manager not available")
    
    try:
        result = file_manager.find_missing_formats(playlist_key)
        return result
    except Exception as e:
        logger.error(f"Missing formats check error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check missing formats: {str(e)}")

@app.post("/files/match-spotify")
async def match_with_spotify_playlist(request: MatchPlaylistRequest):
    """Match local files with Spotify playlist"""
    if not file_manager:
        raise HTTPException(status_code=503, detail="File manager not available")
    
    if not spotify_manager:
        raise HTTPException(status_code=503, detail="Spotify manager not available")
    
    try:
        # Get Spotify playlist tracks if playlist ID provided
        spotify_tracks = []
        if request.spotify_playlist_id:
            if not spotify_manager.is_authenticated():
                raise HTTPException(status_code=401, detail="Not authenticated with Spotify")
            spotify_tracks = spotify_manager.get_playlist_tracks(request.spotify_playlist_id)
        
        result = file_manager.match_with_spotify_tracks(request.playlist_key, spotify_tracks)
        return result
    except Exception as e:
        logger.error(f"Spotify matching error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to match with Spotify: {str(e)}")

@app.get("/config/media-directory")
async def get_media_directory_config():
    """Get current media directory configuration"""
    from config import MEDIA_DIR, EXTERNAL_MEDIA_DIR
    return {
        "media_directory": str(MEDIA_DIR),
        "external_configured": EXTERNAL_MEDIA_DIR is not None,
        "external_path": EXTERNAL_MEDIA_DIR
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)