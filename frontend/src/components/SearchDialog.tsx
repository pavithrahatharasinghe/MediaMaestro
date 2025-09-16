'use client'

import React, { useState } from 'react';
import { X, Search, Youtube, ExternalLink, Download, Music, AlertCircle } from 'lucide-react';
import { Playlist, YouTubeVideo, SpotifyTrack } from '@/types';
import { apiClient, APIError } from '@/lib/api';

interface SearchDialogProps {
  isOpen: boolean;
  onClose: () => void;
  selectedPlaylist: Playlist | null;
}

type SearchType = 'youtube' | 'spotify';

const SearchDialog: React.FC<SearchDialogProps> = ({
  isOpen,
  onClose,
  selectedPlaylist,
}) => {
  const [searchType, setSearchType] = useState<SearchType>('youtube');
  const [query, setQuery] = useState('');
  const [youtubeResults, setYoutubeResults] = useState<YouTubeVideo[]>([]);
  const [spotifyResults, setSpotifyResults] = useState<SpotifyTrack[]>([]);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [errorDetails, setErrorDetails] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setErrorDetails(null);
    
    try {
      if (searchType === 'youtube') {
        const { results } = await apiClient.searchYouTube(query.trim(), 10);
        setYoutubeResults(results);
        setSpotifyResults([]);
      } else {
        // Perform Spotify search - no fallback to demo mode
        const { results } = await apiClient.searchSpotify(query.trim());
        setSpotifyResults(results);
        setYoutubeResults([]);
      }
    } catch (error) {
      console.error('Search failed:', error);
      const apiError = error as APIError;
      setError(apiError.message);
      setErrorDetails(apiError.details || null);
      
      // Clear results on error
      setYoutubeResults([]);
      setSpotifyResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (url: string, format: 'mp3' | 'flac' | 'video') => {
    if (!selectedPlaylist) {
      alert('Please select a playlist first');
      return;
    }

    setDownloading(url);
    try {
      await apiClient.downloadYouTube(url, format, selectedPlaylist.id);
      alert('Download started successfully!');
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed. Please try again.');
    } finally {
      setDownloading(null);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-xl max-w-4xl w-full max-h-[80vh] overflow-hidden border border-gray-700">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <h2 className="text-xl font-semibold text-white">Search & Download</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Search Form */}
        <div className="p-6 border-b border-gray-700">
          <div className="flex space-x-4 mb-4">
            <button
              type="button"
              onClick={() => setSearchType('youtube')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                searchType === 'youtube'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <Youtube className="h-4 w-4" />
              <span>YouTube</span>
            </button>
            <button
              type="button"
              onClick={() => setSearchType('spotify')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                searchType === 'spotify'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <ExternalLink className="h-4 w-4" />
              <span>Spotify</span>
            </button>
          </div>

          <form onSubmit={handleSearch} className="flex space-x-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-1 px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder={`Search ${searchType === 'youtube' ? 'YouTube' : 'Spotify'}...`}
            />
            <button
              type="submit"
              disabled={loading}
              className="flex items-center space-x-2 px-6 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-600/50 text-white rounded-lg transition-colors"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Search className="h-4 w-4" />
              )}
              <span>Search</span>
            </button>
          </form>

          {selectedPlaylist && (
            <div className="mt-3 text-sm text-gray-400">
              Downloading to: <span className="text-purple-400">{selectedPlaylist.name}</span>
            </div>
          )}
        </div>

        {/* Results */}
        <div className="p-6 max-h-96 overflow-y-auto">
          {/* Error Display */}
          {error && (
            <div className="mb-4 p-4 bg-red-900/50 border border-red-600 rounded-lg">
              <div className="flex items-start space-x-3">
                <AlertCircle className="h-5 w-5 text-red-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-red-200 font-medium">{error}</p>
                  {errorDetails && (
                    <p className="text-red-300 text-sm mt-1 whitespace-pre-line">{errorDetails}</p>
                  )}
                  {searchType === 'spotify' && error.includes('Spotify') && (
                    <div className="mt-2 text-sm text-red-300">
                      <p>To use Spotify search:</p>
                      <ol className="list-decimal list-inside mt-1 space-y-1">
                        <li>Set up Spotify API credentials in your .env file</li>
                        <li>Connect to Spotify using the authentication flow</li>
                      </ol>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          {searchType === 'youtube' && youtubeResults.length > 0 && (
            <div className="space-y-4">
              {youtubeResults.map((video) => (
                <div key={video.id} className="flex items-center space-x-4 p-4 bg-gray-800 rounded-lg">
                  <img
                    src={video.thumbnail}
                    alt={video.title}
                    className="w-16 h-12 object-cover rounded"
                  />
                  <div className="flex-1 min-w-0">
                    <h3 className="text-white font-medium truncate">{video.title}</h3>
                    <div className="text-sm text-gray-400">
                      {video.uploader} • {formatDuration(video.duration)} • {video.view_count?.toLocaleString()} views
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleDownload(video.url, 'mp3')}
                      disabled={downloading === video.url}
                      className="flex items-center space-x-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-600/50 text-white text-sm rounded transition-colors"
                    >
                      <Download className="h-3 w-3" />
                      <span>MP3</span>
                    </button>
                    <button
                      onClick={() => handleDownload(video.url, 'flac')}
                      disabled={downloading === video.url}
                      className="flex items-center space-x-1 px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-green-600/50 text-white text-sm rounded transition-colors"
                    >
                      <Download className="h-3 w-3" />
                      <span>FLAC</span>
                    </button>
                    <button
                      onClick={() => handleDownload(video.url, 'video')}
                      disabled={downloading === video.url}
                      className="flex items-center space-x-1 px-3 py-1 bg-red-600 hover:bg-red-700 disabled:bg-red-600/50 text-white text-sm rounded transition-colors"
                    >
                      <Download className="h-3 w-3" />
                      <span>Video</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {searchType === 'spotify' && spotifyResults.length > 0 && (
            <div className="space-y-4">
              {spotifyResults.map((track) => (
                <div key={track.id} className="flex items-center space-x-4 p-4 bg-gray-800 rounded-lg">
                  <div className="w-16 h-12 bg-gray-700 rounded flex items-center justify-center">
                    <Music className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-white font-medium truncate">{track.name}</h3>
                    <div className="text-sm text-gray-400">
                      {track.artists.join(', ')} • {track.album} • {formatDuration(Math.floor(track.duration_ms / 1000))}
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <a
                      href={track.external_urls.spotify}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-1 px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors"
                    >
                      <ExternalLink className="h-3 w-3" />
                      <span>Open</span>
                    </a>
                    {track.preview_url && (
                      <button
                        onClick={() => {
                          const audio = new Audio(track.preview_url);
                          audio.play();
                        }}
                        className="flex items-center space-x-1 px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded transition-colors"
                      >
                        <Music className="h-3 w-3" />
                        <span>Preview</span>
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {!loading && !error && query && (
            (searchType === 'youtube' && youtubeResults.length === 0) ||
            (searchType === 'spotify' && spotifyResults.length === 0)
          ) && (
            <div className="text-center py-8">
              <div className="text-gray-400">No results found for "{query}"</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchDialog;