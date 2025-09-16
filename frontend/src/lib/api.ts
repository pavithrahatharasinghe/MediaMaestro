import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
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