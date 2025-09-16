import yt_dlp
import os
from pathlib import Path
from typing import Dict, List, Optional
import logging
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
import asyncio

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    def __init__(self, download_dir: str = "./downloads"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # Quality options
        self.mp3_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'writeinfojson': True,
        }
        
        self.flac_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'flac',
            }],
            'writeinfojson': True,
        }
        
        self.video_opts = {
            'format': 'best[height<=720]',
            'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
            'writeinfojson': True,
        }
    
    def search_youtube(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for videos on YouTube"""
        search_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                search_results = ydl.extract_info(
                    f"ytsearch{max_results}:{query}",
                    download=False
                )
                
                videos = []
                for entry in search_results.get('entries', []):
                    videos.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'uploader': entry.get('uploader'),
                        'duration': entry.get('duration'),
                        'view_count': entry.get('view_count'),
                        'url': entry.get('webpage_url'),
                        'thumbnail': entry.get('thumbnail')
                    })
                
                return videos
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            return []
    
    def download_audio(self, url: str, format_type: str = "mp3", playlist_folder: str = None) -> Dict:
        """Download audio from YouTube URL"""
        try:
            opts = self.mp3_opts if format_type == "mp3" else self.flac_opts
            
            # Set output directory based on playlist
            if playlist_folder:
                output_dir = self.download_dir / playlist_folder / format_type
                output_dir.mkdir(parents=True, exist_ok=True)
                opts = opts.copy()
                opts['outtmpl'] = str(output_dir / '%(title)s.%(ext)s')
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Find the downloaded file
                title = info.get('title', 'Unknown')
                expected_file = self.download_dir / f"{title}.{format_type}"
                
                if playlist_folder:
                    expected_file = self.download_dir / playlist_folder / format_type / f"{title}.{format_type}"
                
                return {
                    'success': True,
                    'title': title,
                    'file_path': str(expected_file),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'youtube_id': info.get('id')
                }
                
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_video(self, url: str, playlist_folder: str = None) -> Dict:
        """Download video from YouTube URL"""
        try:
            opts = self.video_opts.copy()
            
            # Set output directory based on playlist
            if playlist_folder:
                output_dir = self.download_dir / playlist_folder / "video"
                output_dir.mkdir(parents=True, exist_ok=True)
                opts['outtmpl'] = str(output_dir / '%(title)s.%(ext)s')
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                title = info.get('title', 'Unknown')
                # Video files can have various extensions
                expected_file = self.download_dir / f"{title}.mp4"
                
                if playlist_folder:
                    expected_file = self.download_dir / playlist_folder / "video" / f"{title}.mp4"
                
                return {
                    'success': True,
                    'title': title,
                    'file_path': str(expected_file),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'youtube_id': info.get('id')
                }
                
        except Exception as e:
            logger.error(f"Video download failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_audio_metadata(self, file_path: str) -> Dict:
        """Extract metadata from audio file"""
        try:
            file_path = Path(file_path)
            
            if file_path.suffix.lower() == '.mp3':
                audio = MP3(file_path)
                return {
                    'title': audio.get('TIT2', [None])[0],
                    'artist': audio.get('TPE1', [None])[0],
                    'album': audio.get('TALB', [None])[0],
                    'duration': audio.info.length,
                    'bitrate': audio.info.bitrate,
                    'format': 'MP3'
                }
            elif file_path.suffix.lower() == '.flac':
                audio = FLAC(file_path)
                return {
                    'title': audio.get('TITLE', [None])[0],
                    'artist': audio.get('ARTIST', [None])[0],
                    'album': audio.get('ALBUM', [None])[0],
                    'duration': audio.info.length,
                    'bitrate': audio.info.bitrate,
                    'format': 'FLAC'
                }
        except Exception as e:
            logger.error(f"Failed to extract metadata: {e}")
            
        return {}
    
    def organize_files(self, playlist_folder: str) -> Dict:
        """Organize and tally files in playlist folder"""
        try:
            base_dir = self.download_dir / playlist_folder
            
            mp3_dir = base_dir / "mp3"
            flac_dir = base_dir / "flac"
            video_dir = base_dir / "video"
            
            # Count files in each directory
            mp3_files = list(mp3_dir.glob("*.mp3")) if mp3_dir.exists() else []
            flac_files = list(flac_dir.glob("*.flac")) if flac_dir.exists() else []
            video_files = list(video_dir.glob("*.mp4")) if video_dir.exists() else []
            
            return {
                'mp3_count': len(mp3_files),
                'flac_count': len(flac_files),
                'video_count': len(video_files),
                'mp3_files': [str(f) for f in mp3_files],
                'flac_files': [str(f) for f in flac_files],
                'video_files': [str(f) for f in video_files],
                'is_balanced': len(mp3_files) == len(flac_files) == len(video_files)
            }
            
        except Exception as e:
            logger.error(f"Failed to organize files: {e}")
            return {}