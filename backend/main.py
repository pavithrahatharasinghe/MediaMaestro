from dotenv import load_dotenv
import os

load_dotenv()  # This line loads the environment variables from the .env file

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

# Import our modules (we'll handle imports gracefully)
try:
    from models.database import get_db, init_db, Playlist, Song, DownloadJob
    from utils.spotify_manager import SpotifyManager
    from utils.youtube_downloader import YouTubeDownloader
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
spotify_manager = SpotifyManager() if 'SpotifyManager' in globals() else None
youtube_downloader = YouTubeDownloader() if 'YouTubeDownloader' in globals() else None

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
    return {
        "status": "healthy",
        "spotify_configured": bool(os.getenv("SPOTIFY_CLIENT_ID")),
        "database_connected": True  # We'll implement proper health checks later
    }

# Spotify Authentication Routes
@app.get("/auth/spotify/login")
async def spotify_login():
    """Get Spotify authorization URL"""
    if not spotify_manager:
        raise HTTPException(status_code=503, detail="Spotify manager not available")
    
    try:
        auth_url = spotify_manager.get_auth_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/spotify/callback")
async def spotify_callback(code: str = Query(...)):
    """Handle Spotify authentication callback"""
    if not spotify_manager:
        raise HTTPException(status_code=503, detail="Spotify manager not available")
    
    try:
        success = spotify_manager.authenticate(code)
        if success:
            return {"message": "Authentication successful"}
        else:
            raise HTTPException(status_code=400, detail="Authentication failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    name: str,
    category: str,
    create_spotify: bool = False,
    db: Session = Depends(get_db)
):
    """Create a new playlist"""
    try:
        # Check if playlist already exists
        existing = db.query(Playlist).filter(Playlist.name == name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Playlist already exists")
        
        spotify_id = None
        if create_spotify and spotify_manager:
            spotify_id = spotify_manager.create_playlist(name, f"MediaMaestro - {category}")
        
        playlist = Playlist(
            name=name,
            category=category,
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
    
    try:
        results = spotify_manager.search_track(q, artist)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/spotify/playlists")
async def get_spotify_playlists():
    """Get user's Spotify playlists"""
    if not spotify_manager:
        raise HTTPException(status_code=503, detail="Spotify manager not available")
    
    try:
        playlists = spotify_manager.get_user_playlists()
        return {"playlists": playlists}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)