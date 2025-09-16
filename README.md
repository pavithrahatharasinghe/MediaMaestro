# MediaMaestro

A comprehensive media management system with Spotify API integration, YouTube downloader, and advanced file organization capabilities. Designed as a desktop application for managing your music collection across multiple formats (MP3, FLAC, Video) with seamless Spotify synchronization.

## ✨ Key Features

### 🎵 Core Functionality
- **External Media Storage**: Store your files outside the project folder with configurable directory paths
- **Spotify Integration**: Complete authentication flow, browse playlists, and sync with local files
- **YouTube Downloader**: Download music from YouTube in multiple formats (MP3, FLAC, Video)
- **File Organization**: Automatic file organization with balanced tallying across formats
- **Format Matching**: Find missing formats (mp3/flac/video) and show availability status
- **Desktop App Experience**: One-command startup for both Windows and Linux/macOS

### 🔗 Advanced Integration
- **Spotify Playlist Browsing**: View and compare your Spotify playlists with local files
- **File Format Detection**: Automatically detect and report missing formats for each song
- **Duplicate Management**: Smart duplicate detection when copying files
- **Cross-Platform Support**: Works on Windows, macOS, and Linux with platform-specific launchers

### 🎨 Modern UI
- **Next.js Frontend**: Modern React-based interface with TypeScript
- **Tailwind CSS**: Beautiful, responsive design with dark theme
- **Real-time Updates**: Live status updates for downloads and file organization

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

## 🚀 Quick Start (Desktop Application Mode)

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 18+** with npm
- **Spotify Developer Account** (for API access)

### One-Command Startup

#### Windows
1. Download/clone the repository
2. Double-click `start.bat` or run from command prompt:
```cmd
start.bat
```

#### Linux/macOS
1. Download/clone the repository
2. Run the startup script:
```bash
chmod +x start.sh
./start.sh
```

The startup script will:
- ✅ Check and install all dependencies
- ✅ Create virtual environment for Python
- ✅ Install npm packages
- ✅ Create default .env file
- ✅ Start both backend and frontend servers
- ✅ Open your browser automatically
- ✅ Provide clear status updates

### Manual Setup (Advanced Users)

If you prefer manual setup or need more control:

### Manual Setup (Advanced Users)

If you prefer manual setup or need more control:

#### Backend Setup

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
# Edit .env with your Spotify API credentials and media directory
```

3. **Run the backend:**
```bash
python main.py
```
The API will be available at `http://localhost:8000`

#### Frontend Setup

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

## ⚙️ Configuration

### Spotify API Setup
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Add `http://localhost:8000/auth/spotify/callback` to redirect URIs
4. Copy Client ID and Client Secret to your `.env` file

### Environment Variables
```env
# Spotify API Configuration (REQUIRED)
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8000/auth/spotify/callback

# External Media Directory (RECOMMENDED)
# Store your files outside the project folder
EXTERNAL_MEDIA_DIR=/path/to/your/external/media/folder

# Database Configuration
DATABASE_URL=sqlite:///./mediamaestro.db

# Application Configuration
DEBUG=true
LOG_LEVEL=info
```

### External Media Directory Setup

**Important**: It's recommended to store your media files outside the project folder.

1. Create a dedicated folder for your media (e.g., `D:\MyMusic` on Windows or `/home/user/MyMusic` on Linux)
2. Set the `EXTERNAL_MEDIA_DIR` in your `.env` file:
   ```env
   EXTERNAL_MEDIA_DIR=/path/to/your/media/folder
   ```
3. The system will automatically create the following structure:
   ```
   /your/media/folder/
   ├── kpop/
   │   ├── mp3/
   │   ├── flac/
   │   └── video/
   ├── jpop/
   ├── english/
   ├── cpop/
   └── custom/
   ```

## 📱 Usage Guide

### Getting Started with Spotify
1. **Launch the application** using `start.sh` or `start.bat`
2. **Navigate to the app** at `http://localhost:3000`
3. **Click "Connect Spotify"** to authenticate with your Spotify account
4. **Browse your playlists** and start managing your music collection

### File Management Workflow

#### 1. Copy Your Existing Files
```bash
# Use the API to copy files to the organized structure
curl -X POST "http://localhost:8000/files/copy" \
  -H "Content-Type: application/json" \
  -d '{
    "source_paths": ["/path/to/your/song1.mp3", "/path/to/your/song2.flac"],
    "target_playlist": "kpop"
  }'
```

#### 2. Scan Your Media Directory
```bash
# Check the organization status of all files
curl -X GET "http://localhost:8000/files/scan"
```

#### 3. Find Missing Formats
```bash
# See which songs are missing in mp3/flac/video formats
curl -X GET "http://localhost:8000/files/missing/kpop"
```

#### 4. Match with Spotify Playlists
```bash
# Compare local files with your Spotify playlist
curl -X POST "http://localhost:8000/files/match-spotify" \
  -H "Content-Type: application/json" \
  -d '{
    "playlist_key": "kpop",
    "spotify_playlist_id": "your_spotify_playlist_id"
  }'
```

### Managing Playlists

#### Create a New Playlist
1. Click "Create Playlist" in the header
2. Choose a name and category (K-Pop, J-Pop, English, C-Pop, or Custom)
3. Optionally create a corresponding Spotify playlist

#### Searching and Downloading
1. Click "Search" in the header
2. Switch between YouTube and Spotify search
3. For YouTube: Download in MP3, FLAC, or Video format
4. For Spotify: Preview tracks and open in Spotify

### File Organization Features

- **Automatic Organization**: Files are organized by playlist category
- **Format Separation**: Each playlist has separate folders for MP3, FLAC, and Video files
- **Balance Tracking**: System tracks file balance and provides recommendations
- **Duplicate Detection**: Smart duplicate handling when copying files
- **Metadata Extraction**: Automatic extraction of song metadata

## 🔧 API Endpoints

### Authentication
- `GET /auth/spotify/login` - Get Spotify auth URL
- `GET /auth/spotify/callback` - Handle Spotify callback
- `GET /auth/spotify/status` - Check authentication status

### File Management
- `GET /files/scan` - Scan all media files
- `POST /files/copy` - Copy files to media directory
- `GET /files/missing/{playlist}` - Find missing formats
- `POST /files/match-spotify` - Match with Spotify playlist

### Spotify Integration
- `GET /spotify/search` - Search Spotify tracks
- `GET /spotify/playlists` - Get user playlists
- `GET /spotify/playlists/{id}/tracks` - Get playlist tracks

### Playlist Management
- `GET /playlists` - List local playlists
- `POST /playlists` - Create new playlist
- `GET /playlists/{id}/songs` - Get playlist songs

### Configuration
- `GET /config/media-directory` - Get media directory config
- `GET /health` - System health check

## 🎯 Real-World Usage Examples

### Scenario 1: Organizing Your Existing Music Collection
```bash
# 1. Set up external media directory
echo "EXTERNAL_MEDIA_DIR=/home/user/MyMusicLibrary" >> .env

# 2. Copy your existing files
curl -X POST "http://localhost:8000/files/copy" \
  -H "Content-Type: application/json" \
  -d '{
    "source_paths": [
      "/old/music/folder/song1.mp3",
      "/downloads/song2.flac",
      "/videos/song3.mp4"
    ],
    "target_playlist": "kpop"
  }'

# 3. Check what's missing
curl -X GET "http://localhost:8000/files/missing/kpop"
```

### Scenario 2: Syncing with Spotify Playlists
```bash
# 1. Get your Spotify playlists
curl -X GET "http://localhost:8000/spotify/playlists"

# 2. Compare with local files
curl -X POST "http://localhost:8000/files/match-spotify" \
  -H "Content-Type: application/json" \
  -d '{
    "playlist_key": "kpop",
    "spotify_playlist_id": "37i9dQZF1DX4JAvHpjipBk"
  }'
```

### Scenario 3: Desktop Application Workflow
1. **Double-click** `start.bat` (Windows) or run `./start.sh` (Linux/Mac)
2. **Browser opens automatically** to `http://localhost:3000`
3. **Connect Spotify** using the built-in authentication
4. **Browse your playlists** and see matched/unmatched songs
5. **Copy files** from anywhere on your system to organized folders
6. **Download missing formats** from YouTube
7. **Keep everything synced** between local files and Spotify

## 🛠️ Troubleshooting

### Spotify Authentication Issues
- **Status**: "Setup Required" or "Connect Spotify"
  - **Setup Required**: You need to configure Spotify API credentials
  - **Connect Spotify**: Credentials are configured, but you need to authenticate
- **Setup Steps**:
  1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
  2. Create a new app (or use existing one)
  3. Copy your Client ID and Client Secret to `.env` file
  4. Add `http://localhost:8000/auth/spotify/callback` to your app's redirect URIs
  5. Restart the application
  6. Click "Connect Spotify" to authenticate
- **Authentication Required**: All Spotify features require proper authentication - no demo mode
- **Token Refresh**: The app automatically refreshes expired tokens

### File Management Issues
- **Error**: "File manager not available"
  - **Solution**: Restart the backend server
  - **Check**: Permissions on your external media directory

### Startup Script Issues
- **Windows**: If `start.bat` fails, check that Python and Node.js are in your PATH
- **Linux/Mac**: Ensure `start.sh` has execute permissions: `chmod +x start.sh`

### Port Conflicts
- If ports 8000 or 3000 are in use:
  - **Backend**: Edit `main.py` and change the port in `uvicorn.run()`
  - **Frontend**: Set `PORT=3001` environment variable before running `npm run dev`

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
