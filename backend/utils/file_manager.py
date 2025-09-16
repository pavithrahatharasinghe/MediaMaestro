import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from difflib import SequenceMatcher
from config import MEDIA_DIR, PLAYLISTS
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
import re

logger = logging.getLogger(__name__)

class FileManager:
    def __init__(self):
        self.media_dir = MEDIA_DIR
        self.supported_audio = ['.mp3', '.flac', '.wav', '.m4a', '.aac']
        self.supported_video = ['.mp4', '.mkv', '.avi', '.webm', '.mov']
    
    def scan_media_directory(self) -> Dict:
        """Scan the entire media directory and return file organization status"""
        result = {
            'playlists': {},
            'total_files': 0,
            'orphaned_files': []
        }
        
        try:
            for playlist_key, playlist_name in PLAYLISTS.items():
                playlist_dir = self.media_dir / playlist_key
                
                if not playlist_dir.exists():
                    continue
                
                playlist_data = {
                    'name': playlist_name,
                    'mp3_files': [],
                    'flac_files': [],
                    'video_files': [],
                    'mp3_count': 0,
                    'flac_count': 0,
                    'video_count': 0,
                    'is_balanced': False
                }
                
                # Scan each format directory
                for format_type in ['mp3', 'flac', 'video']:
                    format_dir = playlist_dir / format_type
                    if format_dir.exists():
                        if format_type in ['mp3', 'flac']:
                            files = [f for f in format_dir.iterdir() 
                                   if f.is_file() and f.suffix.lower() in self.supported_audio]
                        else:
                            files = [f for f in format_dir.iterdir() 
                                   if f.is_file() and f.suffix.lower() in self.supported_video]
                        
                        playlist_data[f'{format_type}_files'] = [
                            {
                                'name': f.name,
                                'path': str(f),
                                'size': f.stat().st_size,
                                'metadata': self._extract_metadata(f)
                            } for f in files
                        ]
                        playlist_data[f'{format_type}_count'] = len(files)
                        result['total_files'] += len(files)
                
                # Check if balanced
                playlist_data['is_balanced'] = (
                    playlist_data['mp3_count'] == playlist_data['flac_count'] == playlist_data['video_count']
                )
                
                result['playlists'][playlist_key] = playlist_data
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to scan media directory: {e}")
            return result
    
    def _extract_metadata(self, file_path: Path) -> Dict:
        """Extract metadata from audio/video file"""
        try:
            if file_path.suffix.lower() == '.mp3':
                audio = MP3(file_path)
                return {
                    'title': str(audio.get('TIT2', ['Unknown'])[0]) if audio.get('TIT2') else 'Unknown',
                    'artist': str(audio.get('TPE1', ['Unknown'])[0]) if audio.get('TPE1') else 'Unknown',
                    'album': str(audio.get('TALB', ['Unknown'])[0]) if audio.get('TALB') else 'Unknown',
                    'duration': getattr(audio.info, 'length', 0),
                    'bitrate': getattr(audio.info, 'bitrate', 0),
                    'format': 'MP3'
                }
            elif file_path.suffix.lower() == '.flac':
                audio = FLAC(file_path)
                return {
                    'title': audio.get('TITLE', ['Unknown'])[0] if audio.get('TITLE') else 'Unknown',
                    'artist': audio.get('ARTIST', ['Unknown'])[0] if audio.get('ARTIST') else 'Unknown',
                    'album': audio.get('ALBUM', ['Unknown'])[0] if audio.get('ALBUM') else 'Unknown',
                    'duration': getattr(audio.info, 'length', 0),
                    'bitrate': getattr(audio.info, 'bitrate', 0),
                    'format': 'FLAC'
                }
        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {e}")
        
        return {
            'title': file_path.stem,
            'artist': 'Unknown',
            'album': 'Unknown',
            'duration': 0,
            'bitrate': 0,
            'format': file_path.suffix.upper()[1:]  # Remove the dot
        }
    
    def copy_files_to_media_directory(self, source_paths: List[str], target_playlist: str) -> Dict:
        """Copy files from external locations to media directory"""
        result = {
            'success': [],
            'failed': [],
            'duplicates': [],
            'total_processed': 0
        }
        
        try:
            playlist_dir = self.media_dir / target_playlist
            
            for source_path in source_paths:
                source = Path(source_path)
                result['total_processed'] += 1
                
                if not source.exists():
                    result['failed'].append({
                        'file': str(source),
                        'error': 'File does not exist'
                    })
                    continue
                
                # Determine file type and target directory
                if source.suffix.lower() in self.supported_audio:
                    if source.suffix.lower() == '.mp3':
                        target_dir = playlist_dir / 'mp3'
                    elif source.suffix.lower() == '.flac':
                        target_dir = playlist_dir / 'flac'
                    else:
                        target_dir = playlist_dir / 'mp3'  # Default audio to mp3 folder
                elif source.suffix.lower() in self.supported_video:
                    target_dir = playlist_dir / 'video'
                else:
                    result['failed'].append({
                        'file': str(source),
                        'error': 'Unsupported file format'
                    })
                    continue
                
                target_dir.mkdir(parents=True, exist_ok=True)
                target_path = target_dir / source.name
                
                # Check for duplicates
                if target_path.exists():
                    result['duplicates'].append({
                        'file': str(source),
                        'target': str(target_path)
                    })
                    continue
                
                try:
                    shutil.copy2(source, target_path)
                    result['success'].append({
                        'file': str(source),
                        'target': str(target_path),
                        'metadata': self._extract_metadata(target_path)
                    })
                except Exception as e:
                    result['failed'].append({
                        'file': str(source),
                        'error': str(e)
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to copy files: {e}")
            result['failed'].append({
                'error': f"General error: {str(e)}"
            })
            return result
    
    def find_missing_formats(self, playlist_key: str) -> Dict:
        """Find songs that are missing in certain formats"""
        result = {
            'missing_mp3': [],
            'missing_flac': [],
            'missing_video': [],
            'complete_songs': []
        }
        
        try:
            playlist_dir = self.media_dir / playlist_key
            
            # Get all unique song names (normalized)
            all_songs = {}
            
            for format_type in ['mp3', 'flac', 'video']:
                format_dir = playlist_dir / format_type
                if format_dir.exists():
                    for file in format_dir.iterdir():
                        if file.is_file():
                            normalized_name = self._normalize_filename(file.stem)
                            if normalized_name not in all_songs:
                                all_songs[normalized_name] = {
                                    'original_name': file.stem,
                                    'formats': {}
                                }
                            all_songs[normalized_name]['formats'][format_type] = str(file)
            
            # Check which formats are missing for each song
            for song_name, song_data in all_songs.items():
                formats = song_data['formats']
                
                if 'mp3' not in formats:
                    result['missing_mp3'].append(song_data['original_name'])
                if 'flac' not in formats:
                    result['missing_flac'].append(song_data['original_name'])
                if 'video' not in formats:
                    result['missing_video'].append(song_data['original_name'])
                
                if len(formats) == 3:  # Has all formats
                    result['complete_songs'].append(song_data['original_name'])
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to find missing formats: {e}")
            return result
    
    def _normalize_filename(self, filename: str) -> str:
        """Normalize filename for comparison"""
        # Remove common variations and normalize
        normalized = filename.lower()
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove special characters
        normalized = re.sub(r'\s+', ' ', normalized)     # Normalize spaces
        normalized = normalized.strip()
        return normalized
    
    def match_with_spotify_tracks(self, playlist_key: str, spotify_tracks: List[Dict]) -> Dict:
        """Match local files with Spotify tracks"""
        result = {
            'matched': [],
            'local_only': [],
            'spotify_only': [],
            'match_confidence': {}
        }
        
        try:
            # Get local files
            scan_result = self.scan_media_directory()
            if playlist_key not in scan_result['playlists']:
                return result
            
            local_playlist = scan_result['playlists'][playlist_key]
            
            # Create list of all local songs
            local_songs = set()
            for format_type in ['mp3_files', 'flac_files', 'video_files']:
                for file_info in local_playlist[format_type]:
                    # Use metadata title if available, otherwise filename
                    title = file_info.get('metadata', {}).get('title', file_info['name'])
                    artist = file_info.get('metadata', {}).get('artist', 'Unknown')
                    local_songs.add(self._normalize_track_name(title, artist))
            
            # Create list of Spotify songs
            spotify_songs = set()
            spotify_lookup = {}
            for track in spotify_tracks:
                track_name = self._normalize_track_name(
                    track['name'], 
                    ', '.join(track['artists'])
                )
                spotify_songs.add(track_name)
                spotify_lookup[track_name] = track
            
            # Find matches and differences
            matched_songs = local_songs.intersection(spotify_songs)
            local_only_songs = local_songs - spotify_songs
            spotify_only_songs = spotify_songs - local_songs
            
            # Prepare results
            result['matched'] = list(matched_songs)
            result['local_only'] = list(local_only_songs)
            result['spotify_only'] = list(spotify_only_songs)
            
            # Add fuzzy matching for close matches
            for local_song in local_only_songs:
                best_match = None
                best_ratio = 0
                
                for spotify_song in spotify_only_songs:
                    ratio = SequenceMatcher(None, local_song, spotify_song).ratio()
                    if ratio > best_ratio and ratio > 0.8:  # 80% similarity threshold
                        best_ratio = ratio
                        best_match = spotify_song
                
                if best_match:
                    result['match_confidence'][local_song] = {
                        'spotify_match': best_match,
                        'confidence': best_ratio
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to match with Spotify tracks: {e}")
            return result
    
    def _normalize_track_name(self, title: str, artist: str) -> str:
        """Normalize track name for matching"""
        normalized = f"{title} - {artist}".lower()
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized.strip()