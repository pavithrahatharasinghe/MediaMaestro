'use client'

import React, { useState, useEffect } from 'react';
import { Plus, Music, Folder, Settings, Search, Download, ExternalLink, Youtube } from 'lucide-react';
import { Playlist, Song, PlaylistCategory } from '@/types';
import { apiClient } from '@/lib/api';
import PlaylistGrid from './PlaylistGrid';
import CreatePlaylistDialog from './CreatePlaylistDialog';
import SearchDialog from './SearchDialog';
import FileOrganizer from './FileOrganizer';

interface DashboardProps {}

const Dashboard: React.FC<DashboardProps> = () => {
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [selectedPlaylist, setSelectedPlaylist] = useState<Playlist | null>(null);
  const [songs, setSongs] = useState<Song[]>([]);
  const [spotifyStatus, setSpotifyStatus] = useState({
    configured: false,
    authenticated: false,
    client_id_set: false,
    client_secret_set: false,
    has_cached_token: false
  });
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showSearchDialog, setShowSearchDialog] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPlaylists();
    checkSpotifyStatus();
  }, []);

  const loadPlaylists = async () => {
    try {
      const data = await apiClient.getPlaylists();
      setPlaylists(data);
    } catch (error) {
      console.error('Failed to load playlists:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkSpotifyStatus = async () => {
    try {
      const status = await apiClient.getSpotifyAuthStatus();
      setSpotifyStatus(status);
    } catch (error) {
      console.error('Failed to check Spotify status:', error);
      setSpotifyStatus({
        configured: false,
        authenticated: false,
        client_id_set: false,
        client_secret_set: false,
        has_cached_token: false
      });
    }
  };

  const handleCreatePlaylist = async (name: string, category: PlaylistCategory) => {
    try {
      await apiClient.createPlaylist(name, category, spotifyStatus.authenticated);
      loadPlaylists();
      setShowCreateDialog(false);
    } catch (error) {
      console.error('Failed to create playlist:', error);
    }
  };

  const handleSelectPlaylist = async (playlist: Playlist) => {
    setSelectedPlaylist(playlist);
    try {
      const playlistSongs = await apiClient.getPlaylistSongs(playlist.id);
      setSongs(playlistSongs);
    } catch (error) {
      console.error('Failed to load playlist songs:', error);
    }
  };

  const handleSpotifyLogin = async () => {
    try {
      const { auth_url } = await apiClient.getSpotifyAuthUrl();
      window.open(auth_url, '_blank');
    } catch (error) {
      console.error('Failed to get Spotify auth URL:', error);
    }
  };

  const handleSpotifyLogout = async () => {
    try {
      await apiClient.spotifyLogout();
      checkSpotifyStatus(); // Refresh status
    } catch (error) {
      console.error('Failed to logout from Spotify:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading MediaMaestro...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Music className="h-8 w-8 text-purple-400" />
              <h1 className="text-2xl font-bold text-white">MediaMaestro</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowSearchDialog(true)}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                <Search className="h-4 w-4" />
                <span>Search</span>
              </button>
              
              <button
                onClick={() => setShowCreateDialog(true)}
                className="flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
              >
                <Plus className="h-4 w-4" />
                <span>Create Playlist</span>
              </button>
              
              {!spotifyStatus.configured ? (
                <div className="flex items-center space-x-2 px-4 py-2 bg-orange-600/20 text-orange-400 rounded-lg">
                  <ExternalLink className="h-4 w-4" />
                  <span>Setup Required</span>
                </div>
              ) : !spotifyStatus.authenticated ? (
                <button
                  onClick={handleSpotifyLogin}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                >
                  <ExternalLink className="h-4 w-4" />
                  <span>Connect Spotify</span>
                </button>
              ) : (
                <div className="flex items-center space-x-2">
                  <div className="flex items-center space-x-2 px-4 py-2 bg-green-600/20 text-green-400 rounded-lg">
                    <ExternalLink className="h-4 w-4" />
                    <span>Connected</span>
                  </div>
                  <button
                    onClick={handleSpotifyLogout}
                    className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg transition-colors"
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Playlists Section */}
          <div className="lg:col-span-2">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">Your Playlists</h2>
                <div className="text-sm text-gray-300">
                  {playlists.length} playlist{playlists.length !== 1 ? 's' : ''}
                </div>
              </div>
              
              <PlaylistGrid
                playlists={playlists}
                selectedPlaylist={selectedPlaylist}
                onSelectPlaylist={handleSelectPlaylist}
              />
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Current Playlist Info */}
            {selectedPlaylist && (
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <h3 className="text-lg font-semibold text-white mb-4">
                  {selectedPlaylist.name}
                </h3>
                <div className="space-y-2 text-sm text-gray-300">
                  <div>Category: {selectedPlaylist.category}</div>
                  <div>Songs: {songs.length}</div>
                  {selectedPlaylist.spotify_id && (
                    <div className="flex items-center space-x-2">
                      <ExternalLink className="h-4 w-4 text-green-400" />
                      <span>Synced with Spotify</span>
                    </div>
                  )}
                </div>
                
                {/* File Organization */}
                <FileOrganizer playlistId={selectedPlaylist.id} />
              </div>
            )}

            {/* Recent Songs */}
            {songs.length > 0 && (
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <h3 className="text-lg font-semibold text-white mb-4">Recent Songs</h3>
                <div className="space-y-3">
                  {songs.slice(0, 5).map((song) => (
                    <div key={song.id} className="flex items-center space-x-3">
                      <div className="flex-1 min-w-0">
                        <div className="text-white text-sm font-medium truncate">
                          {song.title}
                        </div>
                        <div className="text-gray-400 text-xs truncate">
                          {song.artist}
                        </div>
                      </div>
                      <div className="flex space-x-1">
                        {song.mp3_path && (
                          <div className="w-2 h-2 bg-blue-400 rounded-full" title="MP3" />
                        )}
                        {song.flac_path && (
                          <div className="w-2 h-2 bg-green-400 rounded-full" title="FLAC" />
                        )}
                        {song.video_path && (
                          <div className="w-2 h-2 bg-red-400 rounded-full" title="Video" />
                        )}
                        {song.spotify_id && (
                          <div className="w-2 h-2 bg-green-500 rounded-full" title="Spotify" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button className="w-full flex items-center space-x-3 px-4 py-3 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg transition-colors">
                  <Youtube className="h-4 w-4" />
                  <span>Download from YouTube</span>
                </button>
                <button className="w-full flex items-center space-x-3 px-4 py-3 bg-green-600/20 hover:bg-green-600/30 text-green-400 rounded-lg transition-colors">
                  <ExternalLink className="h-4 w-4" />
                  <span>Import from Spotify</span>
                </button>
                <button className="w-full flex items-center space-x-3 px-4 py-3 bg-purple-600/20 hover:bg-purple-600/30 text-purple-400 rounded-lg transition-colors">
                  <Folder className="h-4 w-4" />
                  <span>Organize Files</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Dialogs */}
      <CreatePlaylistDialog
        isOpen={showCreateDialog}
        onClose={() => setShowCreateDialog(false)}
        onCreatePlaylist={handleCreatePlaylist}
      />

      <SearchDialog
        isOpen={showSearchDialog}
        onClose={() => setShowSearchDialog(false)}
        selectedPlaylist={selectedPlaylist}
      />
    </div>
  );
};

export default Dashboard;