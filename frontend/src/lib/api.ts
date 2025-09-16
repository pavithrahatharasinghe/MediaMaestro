import axios, { AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface APIError {
  message: string;
  status: number;
  details?: string;
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
    
    // Set up axios interceptors for better error handling
    axios.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error);
        return Promise.reject(this.handleError(error));
      }
    );
  }

  private handleError(error: AxiosError): APIError {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      const status = error.response.status;
      const data = error.response.data as any;
      
      let message = 'An error occurred';
      let details = '';
      
      if (data?.detail) {
        if (typeof data.detail === 'string') {
          message = data.detail;
        } else {
          message = JSON.stringify(data.detail);
        }
      } else if (data?.message) {
        message = data.message;
      }
      
      // Specific error handling for common scenarios
      switch (status) {
        case 401:
          message = 'Authentication required. Please connect to Spotify first.';
          break;
        case 503:
          if (message.includes('Spotify not configured')) {
            message = 'Spotify is not configured. Please set up your Spotify API credentials.';
            details = 'Check your .env file for SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET';
          } else if (message.includes('Spotify manager not available')) {
            message = 'Spotify service is temporarily unavailable.';
          }
          break;
        case 500:
          if (message.includes('Spotify search failed')) {
            message = 'Spotify search is currently unavailable. Please try again later.';
          }
          break;
      }
      
      return {
        message,
        status,
        details
      };
    } else if (error.request) {
      // The request was made but no response was received
      return {
        message: 'Unable to connect to server. Please check your connection.',
        status: 0
      };
    } else {
      // Something happened in setting up the request that triggered an Error
      return {
        message: error.message || 'An unexpected error occurred',
        status: 0
      };
    }
  }

  // Health check
  async healthCheck() {
    const response = await axios.get(`${this.baseURL}/health`);
    return response.data;
  }

  // Spotify Authentication
  async getSpotifyAuthUrl() {
    const response = await axios.get(`${this.baseURL}/auth/spotify/login`);
    return response.data;
  }

  async spotifyCallback(code: string) {
    const response = await axios.get(`${this.baseURL}/auth/spotify/callback?code=${code}`);
    return response.data;
  }

  // Playlist Management
  async getPlaylists() {
    const response = await axios.get(`${this.baseURL}/playlists`);
    return response.data;
  }

  async createPlaylist(name: string, category: string, createSpotify: boolean = false) {
    const response = await axios.post(`${this.baseURL}/playlists`, {
      name,
      category,
      create_spotify: createSpotify
    });
    return response.data;
  }

  async getPlaylistSongs(playlistId: number) {
    const response = await axios.get(`${this.baseURL}/playlists/${playlistId}/songs`);
    return response.data;
  }

  // YouTube Operations
  async searchYouTube(query: string, maxResults: number = 5) {
    const response = await axios.get(`${this.baseURL}/youtube/search`, {
      params: { q: query, max_results: maxResults }
    });
    return response.data;
  }

  async downloadYouTube(url: string, formatType: string = 'mp3', playlistId?: number) {
    const response = await axios.post(`${this.baseURL}/youtube/download`, {
      url,
      format_type: formatType,
      playlist_id: playlistId
    });
    return response.data;
  }

  // Spotify Search
  async searchSpotify(query: string, artist?: string) {
    const response = await axios.get(`${this.baseURL}/spotify/search`, {
      params: { q: query, artist }
    });
    return response.data;
  }

  // Spotify Search Demo (works without authentication)
  async searchSpotifyDemo(query: string, artist?: string) {
    const response = await axios.get(`${this.baseURL}/spotify/search/demo`, {
      params: { q: query, artist }
    });
    return response.data;
  }

  async getSpotifyPlaylists() {
    const response = await axios.get(`${this.baseURL}/spotify/playlists`);
    return response.data;
  }

  // File Organization
  async organizePlaylistFiles(playlistId: number) {
    const response = await axios.get(`${this.baseURL}/files/organize/${playlistId}`);
    return response.data;
  }
}

export const apiClient = new APIClient();
export default APIClient;