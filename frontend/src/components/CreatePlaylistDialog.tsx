'use client'

import React, { useState } from 'react';
import { X, Plus } from 'lucide-react';
import { PlaylistCategory } from '@/types';

interface CreatePlaylistDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onCreatePlaylist: (name: string, category: PlaylistCategory) => void;
}

const CATEGORIES: { value: PlaylistCategory; label: string; emoji: string }[] = [
  { value: 'kpop', label: 'K-Pop', emoji: '🇰🇷' },
  { value: 'jpop', label: 'J-Pop', emoji: '🇯🇵' },
  { value: 'english', label: 'English', emoji: '🇺🇸' },
  { value: 'cpop', label: 'C-Pop', emoji: '🇨🇳' },
  { value: 'custom', label: 'Custom', emoji: '🎵' },
];

const CreatePlaylistDialog: React.FC<CreatePlaylistDialogProps> = ({
  isOpen,
  onClose,
  onCreatePlaylist,
}) => {
  const [name, setName] = useState('');
  const [category, setCategory] = useState<PlaylistCategory>('custom');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    try {
      await onCreatePlaylist(name.trim(), category);
      setName('');
      setCategory('custom');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-xl max-w-md w-full p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white">Create New Playlist</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="playlist-name" className="block text-sm font-medium text-gray-300 mb-2">
              Playlist Name
            </label>
            <input
              id="playlist-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Enter playlist name..."
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Category
            </label>
            <div className="grid grid-cols-2 gap-3">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat.value}
                  type="button"
                  onClick={() => setCategory(cat.value)}
                  className={`
                    flex items-center space-x-3 p-3 rounded-lg border transition-all
                    ${category === cat.value
                      ? 'bg-purple-600 border-purple-500 text-white'
                      : 'bg-gray-800 border-gray-600 text-gray-300 hover:bg-gray-700'
                    }
                  `}
                >
                  <span className="text-lg">{cat.emoji}</span>
                  <span className="text-sm font-medium">{cat.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!name.trim() || loading}
              className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-600/50 text-white rounded-lg transition-colors"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <Plus className="h-4 w-4" />
                  <span>Create</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreatePlaylistDialog;