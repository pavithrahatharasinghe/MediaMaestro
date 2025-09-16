import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class SpotifyManager:
    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8000/auth/spotify/callback")
        
        self.scope = "user-library-read playlist-modify-public playlist-modify-private user-read-private"
        
        # Only initialize OAuth if credentials are available
        self.sp_oauth = None
        self.sp = None
        self.configured = False
        
        if self.client_id and self.client_secret:
            try:
                self.sp_oauth = SpotifyOAuth(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    redirect_uri=self.redirect_uri,
                    scope=self.scope
                )
                self.configured = True
                logger.info("Spotify manager initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Spotify OAuth: {e}")
                self.configured = False
        else:
            logger.warning("Spotify credentials not found in environment variables")
    
    def get_auth_url(self) -> str:
        """Get Spotify authorization URL"""
        if not self.configured:
            raise Exception("Spotify not configured - missing credentials")
        return self.sp_oauth.get_authorize_url()
    
    def authenticate(self, code: str) -> bool:
        """Authenticate with authorization code"""
        if not self.configured:
            logger.error("Cannot authenticate - Spotify not configured")
            return False
            
        try:
            token_info = self.sp_oauth.get_access_token(code)
            self.sp = spotipy.Spotify(auth=token_info['access_token'])
            return True
        except Exception as e:
            logger.error(f"Spotify authentication failed: {e}")
            return False
    
    def search_track(self, query: str, artist: str = None) -> List[Dict]:
        """Search for tracks on Spotify"""
        if not self.configured:
            raise Exception("Spotify not configured - missing credentials")
            
        if not self.sp:
            raise Exception("Not authenticated with Spotify")
        
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
    
    def search_track_demo(self, query: str, artist: str = None) -> List[Dict]:
        """Demo search function that returns mock data when not configured"""
        demo_tracks = [
            {
                'id': 'demo_1',
                'name': f'Demo Song - {query}',
                'artists': ['Demo Artist'],
                'album': 'Demo Album',
                'duration_ms': 180000,
                'preview_url': None,
                'external_urls': {'spotify': 'https://open.spotify.com/track/demo'}
            },
            {
                'id': 'demo_2', 
                'name': f'Another Demo - {query}',
                'artists': ['Demo Artist 2'],
                'album': 'Demo Album 2',
                'duration_ms': 210000,
                'preview_url': None,
                'external_urls': {'spotify': 'https://open.spotify.com/track/demo2'}
            }
        ]
        return demo_tracks
    
    def get_user_playlists(self) -> List[Dict]:
        """Get user's Spotify playlists"""
        if not self.configured:
            raise Exception("Spotify not configured - missing credentials")
            
        if not self.sp:
            raise Exception("Not authenticated with Spotify")
        
        try:
            playlists = self.sp.current_user_playlists()
            return [{
                'id': playlist['id'],
                'name': playlist['name'],
                'description': playlist['description'],
                'tracks_total': playlist['tracks']['total'],
                'external_urls': playlist['external_urls']
            } for playlist in playlists['items']]
        except Exception as e:
            logger.error(f"Failed to get playlists: {e}")
            return []
    
    def create_playlist(self, name: str, description: str = "", public: bool = False) -> Optional[str]:
        """Create a new Spotify playlist"""
        if not self.configured:
            raise Exception("Spotify not configured - missing credentials")
            
        if not self.sp:
            raise Exception("Not authenticated with Spotify")
        
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
        if not self.sp:
            raise Exception("Not authenticated with Spotify")
        
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
        if not self.sp:
            raise Exception("Not authenticated with Spotify")
        
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
                        'duration_ms': track['duration_ms']
                    })
            
            return tracks
        except Exception as e:
            logger.error(f"Failed to get playlist tracks: {e}")
            return []