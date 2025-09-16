import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
MEDIA_DIR = BASE_DIR / "media"
DOWNLOADS_DIR = BASE_DIR / "downloads"

# Create media organization structure
PLAYLISTS = {
    "kpop": "K-Pop",
    "jpop": "J-Pop", 
    "english": "English",
    "cpop": "C-Pop",
    "custom": "Custom"
}

# File extensions
AUDIO_EXTENSIONS = [".mp3", ".flac", ".wav", ".m4a", ".aac"]
VIDEO_EXTENSIONS = [".mp4", ".mkv", ".avi", ".webm"]

# Spotify API Configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8000/callback")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mediamaestro.db")

# Create directories
for playlist in PLAYLISTS.keys():
    for media_type in ["mp3", "flac", "video"]:
        (MEDIA_DIR / playlist / media_type).mkdir(parents=True, exist_ok=True)

DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)