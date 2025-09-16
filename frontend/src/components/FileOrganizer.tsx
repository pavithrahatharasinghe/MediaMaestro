'use client'

import React, { useState, useEffect } from 'react';
import { BarChart3, RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react';
import { FileOrganization } from '@/types';
import { apiClient } from '@/lib/api';

interface FileOrganizerProps {
  playlistId: number;
}

const FileOrganizer: React.FC<FileOrganizerProps> = ({ playlistId }) => {
  const [organization, setOrganization] = useState<FileOrganization | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadOrganization();
  }, [playlistId]);

  const loadOrganization = async () => {
    setLoading(true);
    try {
      const data = await apiClient.organizePlaylistFiles(playlistId);
      setOrganization(data);
    } catch (error) {
      console.error('Failed to load file organization:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="mt-6 flex items-center justify-center py-4">
        <RefreshCw className="h-5 w-5 text-gray-400 animate-spin" />
      </div>
    );
  }

  if (!organization) {
    return null;
  }

  return (
    <div className="mt-6">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-medium text-white">File Organization</h4>
        <button
          onClick={loadOrganization}
          className="text-gray-400 hover:text-white transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
        </button>
      </div>

      <div className="space-y-3">
        {/* Balance Status */}
        <div className={`flex items-center space-x-2 p-3 rounded-lg ${
          organization.is_balanced 
            ? 'bg-green-600/20 text-green-400'
            : 'bg-yellow-600/20 text-yellow-400'
        }`}>
          {organization.is_balanced ? (
            <CheckCircle className="h-4 w-4" />
          ) : (
            <AlertTriangle className="h-4 w-4" />
          )}
          <span className="text-sm">
            {organization.is_balanced ? 'All files balanced' : 'Files not balanced'}
          </span>
        </div>

        {/* File Counts */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-400 rounded-full"></div>
              <span className="text-gray-300">MP3 Files</span>
            </div>
            <span className="text-white font-medium">{organization.mp3_count}</span>
          </div>

          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-400 rounded-full"></div>
              <span className="text-gray-300">FLAC Files</span>
            </div>
            <span className="text-white font-medium">{organization.flac_count}</span>
          </div>

          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-400 rounded-full"></div>
              <span className="text-gray-300">Video Files</span>
            </div>
            <span className="text-white font-medium">{organization.video_count}</span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="text-xs text-gray-400">File Balance</div>
          <div className="grid grid-cols-3 gap-1 h-2">
            <div className="bg-blue-400 rounded-sm opacity-60"></div>
            <div className="bg-green-400 rounded-sm opacity-60"></div>
            <div className="bg-red-400 rounded-sm opacity-60"></div>
          </div>
          <div className="grid grid-cols-3 gap-1 text-xs text-center text-gray-400">
            <div>{organization.mp3_count}</div>
            <div>{organization.flac_count}</div>
            <div>{organization.video_count}</div>
          </div>
        </div>

        {/* Recommendations */}
        {!organization.is_balanced && (
          <div className="mt-4 p-3 bg-yellow-600/10 border border-yellow-600/20 rounded-lg">
            <div className="text-xs text-yellow-400 font-medium mb-1">Recommendations:</div>
            <div className="text-xs text-gray-300">
              {organization.mp3_count < Math.max(organization.flac_count, organization.video_count) && 
                'Consider downloading more MP3 files. '}
              {organization.flac_count < Math.max(organization.mp3_count, organization.video_count) && 
                'Consider downloading more FLAC files. '}
              {organization.video_count < Math.max(organization.mp3_count, organization.flac_count) && 
                'Consider downloading more video files. '}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileOrganizer;