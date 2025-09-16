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
        
        if self.client_id and self.client_secret and self.client_id not in ["demo_client_id", "your_spotify_client_id_here"]:
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
                
                logger.info("Spotify manager initialized with valid credentials")
            except Exception as e:
                logger.error(f"Failed to initialize Spotify OAuth: {e}")
                self.configured = False
        else:
            logger.warning("Spotify credentials not found or placeholder values detected. Please set valid SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
    
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
            # Check if we have a valid token
            if self.sp_oauth:
                token_info = self.sp_oauth.get_cached_token()
                if not token_info:
                    return False
                
                # Check if token is expired
                if self.sp_oauth.is_token_expired(token_info):
                    # Try to refresh the token
                    try:
                        token_info = self.sp_oauth.refresh_access_token(token_info['refresh_token'])
                        if token_info:
                            self.sp = spotipy.Spotify(auth=token_info['access_token'])
                        else:
                            return False
                    except Exception as e:
                        logger.debug(f"Token refresh failed: {e}")
                        return False
                
                # Test the actual connection with the token
                if self.sp:
                    try:
                        user = self.sp.current_user()
                        if user and user.get('id'):
                            return True
                    except Exception as e:
                        logger.debug(f"Authentication test failed: {e}")
                        self.sp = None
                        
        except Exception as e:
            logger.debug(f"Authentication check failed: {e}")
            self.sp = None
        
        return False
    
    def get_auth_url(self) -> str:
        """Get Spotify authorization URL"""
        if not self.configured:
            raise Exception("Spotify not configured. Please set valid SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your environment variables.")
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
                # Test the authentication by getting user info
                user = self.sp.current_user()
                if user and user.get('id'):
                    logger.info(f"Spotify authentication successful for user: {user.get('display_name', user.get('id'))}")
                    return True
                else:
                    logger.error("Authentication failed - could not get user information")
                    return False
        except Exception as e:
            logger.error(f"Spotify authentication failed: {e}")
        return False
    
    def search_track(self, query: str, artist: str = None) -> List[Dict]:
        """Search for tracks on Spotify"""
        if not self.configured:
            raise Exception("Spotify not configured. Please set valid SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your environment variables.")
            
        if not self.is_authenticated():
            raise Exception("Not authenticated with Spotify. Please complete the authentication flow first.")
        
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
            if "token" in str(e).lower() or "auth" in str(e).lower():
                # Clear invalid token and require re-authentication
                self.sp = None
                if self.token_file.exists():
                    self.token_file.unlink()
                raise Exception("Spotify authentication expired. Please authenticate again.")
            raise Exception(f"Spotify search failed: {str(e)}")
    
    def get_authentication_status(self) -> Dict[str, any]:
        """Get detailed authentication status"""
        return {
            "configured": self.configured,
            "authenticated": self.is_authenticated() if self.configured else False,
            "client_id_set": bool(self.client_id and self.client_id not in ["your_spotify_client_id_here", ""]),
            "client_secret_set": bool(self.client_secret and self.client_secret not in ["your_spotify_client_secret_here", ""]),
            "has_cached_token": self.token_file.exists() if self.configured else False
        }
    
    def get_user_playlists(self) -> List[Dict]:
        """Get user's Spotify playlists"""
        if not self.configured:
            raise Exception("Spotify not configured. Please set valid SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your environment variables.")
            
        if not self.is_authenticated():
            raise Exception("Not authenticated with Spotify. Please complete the authentication flow first.")
        
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
            if "token" in str(e).lower() or "auth" in str(e).lower():
                self.sp = None
                if self.token_file.exists():
                    self.token_file.unlink()
                raise Exception("Spotify authentication expired. Please authenticate again.")
            raise Exception(f"Failed to get playlists: {str(e)}")
    
    def create_playlist(self, name: str, description: str = "", public: bool = False) -> Optional[str]:
        """Create a new Spotify playlist"""
        if not self.configured:
            raise Exception("Spotify not configured. Please set valid SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your environment variables.")
            
        if not self.is_authenticated():
            raise Exception("Not authenticated with Spotify. Please complete the authentication flow first.")
        
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
            if "token" in str(e).lower() or "auth" in str(e).lower():
                self.sp = None
                if self.token_file.exists():
                    self.token_file.unlink()
                raise Exception("Spotify authentication expired. Please authenticate again.")
            raise Exception(f"Failed to create playlist: {str(e)}")
    
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> bool:
        """Add tracks to a Spotify playlist"""
        if not self.is_authenticated():
            raise Exception("Not authenticated with Spotify. Please complete the authentication flow first.")
        
        try:
            # Spotify API limits to 100 tracks per request
            for i in range(0, len(track_ids), 100):
                batch = track_ids[i:i+100]
                self.sp.playlist_add_items(playlist_id, batch)
            return True
        except Exception as e:
            logger.error(f"Failed to add tracks to playlist: {e}")
            if "token" in str(e).lower() or "auth" in str(e).lower():
                self.sp = None
                if self.token_file.exists():
                    self.token_file.unlink()
                raise Exception("Spotify authentication expired. Please authenticate again.")
            raise Exception(f"Failed to add tracks to playlist: {str(e)}")
    
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """Get tracks from a Spotify playlist"""
        if not self.is_authenticated():
            raise Exception("Not authenticated with Spotify. Please complete the authentication flow first.")
        
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
            if "token" in str(e).lower() or "auth" in str(e).lower():
                self.sp = None
                if self.token_file.exists():
                    self.token_file.unlink()
                raise Exception("Spotify authentication expired. Please authenticate again.")
            raise Exception(f"Failed to get playlist tracks: {str(e)}")
    
    def logout(self) -> bool:
        """Logout and clear authentication"""
        try:
            self.sp = None
            if self.token_file.exists():
                self.token_file.unlink()
                logger.info("Spotify token cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to logout: {e}")
            return False
