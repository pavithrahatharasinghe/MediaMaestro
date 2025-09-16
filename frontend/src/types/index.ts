export interface Playlist {
  id: number;
  name: string;
  category: string;
  spotify_id?: string;
  song_count: number;
  created_at: string;
}

export interface Song {
  id: number;
  title: string;
  artist: string;
  album?: string;
  mp3_path?: string;
  flac_path?: string;
  video_path?: string;
  spotify_id?: string;
  youtube_id?: string;
  duration?: number;
}

export interface YouTubeVideo {
  id: string;
  title: string;
  uploader: string;
  duration: number;
  view_count: number;
  url: string;
  thumbnail: string;
}

export interface SpotifyTrack {
  id: string;
  name: string;
  artists: string[];
  album: string;
  duration_ms: number;
  preview_url?: string;
  external_urls: {
    spotify: string;
  };
}

export interface DownloadJob {
  job_id: number;
  status: 'pending' | 'downloading' | 'completed' | 'failed';
  result: any;
}

export interface FileOrganization {
  mp3_count: number;
  flac_count: number;
  video_count: number;
  mp3_files: string[];
  flac_files: string[];
  video_files: string[];
  is_balanced: boolean;
}

export type PlaylistCategory = 'kpop' | 'jpop' | 'english' | 'cpop' | 'custom';

export interface AppState {
  isSpotifyConnected: boolean;
  currentPlaylist?: Playlist;
  selectedSongs: Song[];
}