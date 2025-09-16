# MediaMaestro Quick Setup Guide

## 🚀 5-Minute Setup

### 1. Get Spotify API Credentials
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click "Create an App"
3. Fill in app name: "MediaMaestro"
4. Add redirect URI: `http://localhost:8000/auth/spotify/callback`
5. Copy your Client ID and Client Secret

### 2. Configure MediaMaestro
1. Edit the `.env` file in the root directory
2. Replace `your_spotify_client_id_here` with your actual Client ID
3. Replace `your_spotify_client_secret_here` with your actual Client Secret
4. (Optional) Set `EXTERNAL_MEDIA_DIR` to store files outside the project

### 3. Launch the Application

#### Windows
```cmd
# Double-click start.bat or run:
start.bat
```

#### Linux/macOS
```bash
# Make executable and run:
chmod +x start.sh
./start.sh
```

### 4. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 5. Connect to Spotify
1. Click "Connect Spotify" in the web interface
2. Authorize MediaMaestro to access your Spotify account
3. Start managing your music collection!

## 📁 Directory Structure

After setup, your media will be organized like this:

```
/your/media/directory/
├── kpop/
│   ├── mp3/          # K-Pop MP3 files
│   ├── flac/         # K-Pop FLAC files
│   └── video/        # K-Pop video files
├── jpop/             # J-Pop files
├── english/          # English music
├── cpop/             # C-Pop files
└── custom/           # Custom playlists
```

## 🔧 Key Features to Try

1. **Browse Spotify Playlists**: View your existing Spotify playlists
2. **Copy Local Files**: Organize your existing music collection
3. **Find Missing Formats**: See which songs need MP3/FLAC/video versions
4. **Match with Spotify**: Compare local files with Spotify playlists
5. **Download from YouTube**: Get missing formats from YouTube

## 🆘 Need Help?

Check the main README.md for detailed documentation and troubleshooting.

### Common Issues:
- **"Spotify not configured"**: Make sure your credentials are in `.env`
- **Permission errors**: Check file/folder permissions for media directory
- **Port conflicts**: Close other applications using ports 3000 or 8000