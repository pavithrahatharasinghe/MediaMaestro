import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Dict, Optional
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class SpotifyManager:
    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8000/auth/spotify/callback")
        
        self.scope = "user-library-read playlist-modify-public playlist-modify-private user-read-private playlist-read-private"
        
        # Token storage path
        self.token_file = Path("./spotify_token.json")
        
        # Only initialize OAuth if credentials are available
        self.sp_oauth = None
        self.sp = None
        self.configured = False
        
        if self.client_id and self.client_secret and self.client_id != "demo_client_id":
            try:
                self.sp_oauth = SpotifyOAuth(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    redirect_uri=self.redirect_uri,
                    scope=self.scope,
                    cache_path=str(self.token_file)
                )
                self.configured = True
                
                # Try to load existing token
                self._load_token()
                
                logger.info("Spotify manager initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Spotify OAuth: {e}")
                self.configured = False
        else:
            logger.warning("Spotify credentials not found or using demo credentials")
    
    def _load_token(self):
        """Load existing token if available and valid"""
        try:
            if self.token_file.exists():
                token_info = self.sp_oauth.get_cached_token()
                if token_info:
                    self.sp = spotipy.Spotify(auth=token_info['access_token'])
                    logger.info("Loaded existing Spotify token")
                    return True
        except Exception as e:
            logger.error(f"Failed to load existing token: {e}")
        return False
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated with Spotify"""
        if not self.configured:
            return False
        
        try:
            if self.sp:
                # Test the connection
                self.sp.current_user()
                return True
        except Exception as e:
            logger.debug(f"Authentication check failed: {e}")
            self.sp = None
        
        return False
    
    def get_auth_url(self) -> str:
        """Get Spotify authorization URL"""
        if not self.configured:
            raise Exception("Spotify not configured - please set valid SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
        return self.sp_oauth.get_authorize_url()
    
    def authenticate(self, code: str) -> bool:
        """Authenticate with authorization code"""
        if not self.configured:
            logger.error("Cannot authenticate - Spotify not configured")
            return False
            
        try:
            token_info = self.sp_oauth.get_access_token(code)
            if token_info:
                self.sp = spotipy.Spotify(auth=token_info['access_token'])
                logger.info("Spotify authentication successful")
                return True
        except Exception as e:
            logger.error(f"Spotify authentication failed: {e}")
        return False
    
    def search_track(self, query: str, artist: str = None) -> List[Dict]:
        """Search for tracks on Spotify"""
        if not self.configured:
            raise Exception("Spotify not configured - please set valid SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
            
        if not self.is_authenticated():
            raise Exception("Not authenticated with Spotify - please authenticate first")
        
        search_query = query
        if artist:
            search_query = f"track:{query} artist:{artist}"
        
        try:
            results = self.sp.search(q=search_query, type='track', limit=10)
            tracks = []
            
            for track in results['tracks']['items']:
                tracks.append({
                    'id': track['id'],
                    'name': track['name'],
                    'artists': [artist['name'] for artist in track['artists']],
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'preview_url': track['preview_url'],
                    'external_urls': track['external_urls']
                })
            
            return tracks
        except Exception as e:
            logger.error(f"Spotify search failed: {e}")
            return []
    
    def get_user_playlists(self) -> List[Dict]:
        """Get user's Spotify playlists"""
        if not self.configured:
            raise Exception("Spotify not configured - please set valid SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
            
        if not self.is_authenticated():
            raise Exception("Not authenticated with Spotify - please authenticate first")
        
        try:
            playlists = self.sp.current_user_playlists()
            return [{
                'id': playlist['id'],
                'name': playlist['name'],
                'description': playlist['description'],
                'tracks_total': playlist['tracks']['total'],
                'external_urls': playlist['external_urls'],
                'owner': playlist['owner']['display_name'] if playlist['owner']['display_name'] else playlist['owner']['id']
            } for playlist in playlists['items']]
        except Exception as e:
            logger.error(f"Failed to get playlists: {e}")
            return []
    
    def create_playlist(self, name: str, description: str = "", public: bool = False) -> Optional[str]:
        """Create a new Spotify playlist"""
        if not self.configured:
            raise Exception("Spotify not configured - please set valid SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
            
        if not self.is_authenticated():
            raise Exception("Not authenticated with Spotify - please authenticate first")
        
        try:
            user = self.sp.current_user()
            playlist = self.sp.user_playlist_create(
                user['id'], 
                name, 
                public=public, 
                description=description
            )
            return playlist['id']
        except Exception as e:
            logger.error(f"Failed to create playlist: {e}")
            return None
    
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> bool:
        """Add tracks to a Spotify playlist"""
        if not self.is_authenticated():
            raise Exception("Not authenticated with Spotify - please authenticate first")
        
        try:
            # Spotify API limits to 100 tracks per request
            for i in range(0, len(track_ids), 100):
                batch = track_ids[i:i+100]
                self.sp.playlist_add_items(playlist_id, batch)
            return True
        except Exception as e:
            logger.error(f"Failed to add tracks to playlist: {e}")
            return False
    
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """Get tracks from a Spotify playlist"""
        if not self.is_authenticated():
            raise Exception("Not authenticated with Spotify - please authenticate first")
        
        try:
            results = self.sp.playlist_tracks(playlist_id)
            tracks = []
            
            for item in results['items']:
                if item['track']:
                    track = item['track']
                    tracks.append({
                        'id': track['id'],
                        'name': track['name'],
                        'artists': [artist['name'] for artist in track['artists']],
                        'album': track['album']['name'],
                        'duration_ms': track['duration_ms'],
                        'preview_url': track['preview_url'],
                        'external_urls': track['external_urls']
                    })
            
            return tracks
        except Exception as e:
            logger.error(f"Failed to get playlist tracks: {e}")
            return []
    
    def search_track_demo(self, query: str, artist: str = None) -> List[Dict]:
        """Demo search that returns sample data without authentication"""
        logger.info(f"Performing demo Spotify search for: {query}")
        
        # Generate more realistic demo data based on query
        demo_genres = ['pop', 'rock', 'hip-hop', 'electronic', 'indie', 'jazz', 'classical']
        import random
        
        tracks = []
        search_terms = query.lower().split()
        
        # Create sample tracks with variation
        sample_templates = [
            {"name": f"{query} (Radio Edit)", "artist": "Popular Artist", "album": "Hit Singles"},
            {"name": f"{query} - Acoustic Version", "artist": "Indie Artist", "album": "Acoustic Sessions"},
            {"name": f"{query} (Remix)", "artist": "DJ Producer", "album": "Remix Collection"},
            {"name": f"The {query} Song", "artist": "Alternative Band", "album": "Latest Album"},
            {"name": f"{query} Blues", "artist": "Blues Legend", "album": "Classic Blues"},
        ]
        
        for i, template in enumerate(sample_templates[:3]):  # Limit to 3 results
            duration = random.randint(180000, 300000)  # 3-5 minutes
            track = {
                'id': f'demo_{i+1}_{hash(query) % 1000}',
                'name': template["name"],
                'artists': [template["artist"]] + ([artist] if artist else []),
                'album': template["album"],
                'duration_ms': duration,
                'preview_url': None,  # No preview in demo mode
                'external_urls': {
                    'spotify': f'https://open.spotify.com/track/demo_{i+1}_{hash(query) % 1000}'
                }
            }
            tracks.append(track)
        
        return tracks