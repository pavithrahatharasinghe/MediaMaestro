# MediaMaestro

A comprehensive media management system with Spotify API integration, YouTube downloader, and advanced file organization capabilities.

## Features

### 🎵 Core Functionality
- **Playlist Management**: Create and organize playlists by category (K-Pop, J-Pop, English, C-Pop, Custom)
- **Spotify Integration**: Browse your Spotify library, search tracks, and sync playlists
- **YouTube Downloader**: Download music from YouTube in multiple formats (MP3, FLAC, Video)
- **File Organization**: Automatic file organization with balanced tallying across formats
- **Database Management**: SQLite database to track local files, streaming IDs, and metadata

### 🎨 Modern UI
- **Next.js Frontend**: Modern React-based interface with TypeScript
- **Tailwind CSS**: Beautiful, responsive design with dark theme
- **Real-time Updates**: Live status updates for downloads and file organization
- **Intuitive Navigation**: Easy-to-use interface for managing large music collections

### 🔗 API Integration
- **Spotify Web API**: Full authentication and library access
- **YouTube Search**: Advanced search capabilities with metadata extraction
- **RESTful Backend**: FastAPI-powered backend with comprehensive API endpoints
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Architecture

```
MediaMaestro/
├── frontend/           # Next.js React application
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── lib/        # API client and utilities
│   │   ├── types/      # TypeScript type definitions
│   │   └── app/        # Next.js app router pages
├── backend/            # Python FastAPI backend
│   ├── models/         # Database models
│   ├── utils/          # Spotify and YouTube utilities
│   ├── api/            # API routes
│   └── main.py         # FastAPI application
└── media/              # Organized media files
    ├── kpop/           # K-Pop playlist
    │   ├── mp3/
    │   ├── flac/
    │   └── video/
    ├── jpop/           # J-Pop playlist
    └── ...
```

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Spotify Developer Account (for API access)

### Backend Setup

1. **Install Python dependencies:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your Spotify API credentials
```

3. **Run the backend:**
```bash
python main.py
```
The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Run the development server:**
```bash
npm run dev
```
The frontend will be available at `http://localhost:3000`

## Configuration

### Spotify API Setup
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Add `http://localhost:8000/auth/spotify/callback` to redirect URIs
4. Copy Client ID and Client Secret to your `.env` file

### Environment Variables
```env
# Spotify API Configuration
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8000/auth/spotify/callback

# Database Configuration
DATABASE_URL=sqlite:///./mediamaestro.db

# Application Configuration
DEBUG=true
LOG_LEVEL=info
```

## Usage

### Creating Playlists
1. Click "Create Playlist" in the header
2. Choose a name and category (K-Pop, J-Pop, English, C-Pop, or Custom)
3. Optionally create a corresponding Spotify playlist

### Searching and Downloading
1. Click "Search" in the header
2. Switch between YouTube and Spotify search
3. For YouTube: Download in MP3, FLAC, or Video format
4. For Spotify: Preview tracks and open in Spotify

### File Organization
- Files are automatically organized by playlist category
- Each playlist has separate folders for MP3, FLAC, and Video files
- The system tracks file balance and provides recommendations
- Database maintains relationships between local files and streaming IDs

## API Endpoints

### Playlist Management
- `GET /playlists` - List all playlists
- `POST /playlists` - Create new playlist
- `GET /playlists/{id}/songs` - Get playlist songs

### Search and Download
- `GET /youtube/search` - Search YouTube
- `POST /youtube/download` - Download from YouTube
- `GET /spotify/search` - Search Spotify

### File Organization
- `GET /files/organize/{playlist_id}` - Get file organization status

### Authentication
- `GET /auth/spotify/login` - Get Spotify auth URL
- `GET /auth/spotify/callback` - Handle Spotify callback

## Future Enhancements

### Planned Features
- **User Authentication**: Multi-user support with individual libraries
- **Built-in Player**: Integrated media player with playlist support
- **Advanced Matching**: AI-powered song matching between formats
- **Cloud Storage**: Integration with cloud storage providers
- **Mobile App**: React Native mobile application
- **Commercial Features**: Subscription tiers and advanced analytics

### Scalability Considerations
- PostgreSQL migration for production use
- Redis caching for improved performance
- Docker containerization
- Kubernetes orchestration
- CDN integration for media delivery

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on GitHub or contact the maintainers.

---

**MediaMaestro** - Your comprehensive media management solution 🎵
