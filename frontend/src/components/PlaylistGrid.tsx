'use client'

import React from 'react';
import { Music, Folder } from 'lucide-react';
import { Playlist } from '@/types';

interface PlaylistGridProps {
  playlists: Playlist[];
  selectedPlaylist: Playlist | null;
  onSelectPlaylist: (playlist: Playlist) => void;
}

const getCategoryColor = (category: string) => {
  const colors = {
    kpop: 'from-pink-500 to-purple-500',
    jpop: 'from-red-500 to-orange-500',
    english: 'from-blue-500 to-indigo-500',
    cpop: 'from-yellow-500 to-red-500',
    custom: 'from-gray-500 to-gray-700',
  };
  return colors[category as keyof typeof colors] || colors.custom;
};

const getCategoryIcon = (category: string) => {
  const icons = {
    kpop: '🇰🇷',
    jpop: '🇯🇵',
    english: '🇺🇸',
    cpop: '🇨🇳',
    custom: '🎵',
  };
  return icons[category as keyof typeof icons] || icons.custom;
};

const PlaylistGrid: React.FC<PlaylistGridProps> = ({
  playlists,
  selectedPlaylist,
  onSelectPlaylist,
}) => {
  if (playlists.length === 0) {
    return (
      <div className="text-center py-12">
        <Folder className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-white mb-2">No playlists yet</h3>
        <p className="text-gray-400 mb-6">Create your first playlist to get started</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {playlists.map((playlist) => (
        <div
          key={playlist.id}
          onClick={() => onSelectPlaylist(playlist)}
          className={`
            relative overflow-hidden rounded-xl cursor-pointer transition-all duration-200 transform hover:scale-105
            ${selectedPlaylist?.id === playlist.id 
              ? 'ring-2 ring-purple-400 shadow-2xl' 
              : 'hover:shadow-xl'
            }
          `}
        >
          {/* Gradient Background */}
          <div className={`absolute inset-0 bg-gradient-to-br ${getCategoryColor(playlist.category)} opacity-80`} />
          
          {/* Content */}
          <div className="relative p-6 text-white">
            <div className="flex items-start justify-between mb-4">
              <div className="text-2xl">
                {getCategoryIcon(playlist.category)}
              </div>
              {playlist.spotify_id && (
                <div className="w-3 h-3 bg-green-400 rounded-full" title="Synced with Spotify" />
              )}
            </div>
            
            <h3 className="font-semibold text-lg mb-2 truncate">
              {playlist.name}
            </h3>
            
            <div className="flex items-center space-x-4 text-sm opacity-90">
              <div className="flex items-center space-x-1">
                <Music className="h-4 w-4" />
                <span>{playlist.song_count} songs</span>
              </div>
              <div className="capitalize">
                {playlist.category}
              </div>
            </div>
            
            <div className="mt-4 text-xs opacity-75">
              Created {new Date(playlist.created_at).toLocaleDateString()}
            </div>
          </div>
          
          {/* Overlay for selected state */}
          {selectedPlaylist?.id === playlist.id && (
            <div className="absolute inset-0 bg-white/10 pointer-events-none" />
          )}
        </div>
      ))}
    </div>
  );
};

export default PlaylistGrid;