from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import sqlite3

Base = declarative_base()

class Playlist(Base):
    __tablename__ = "playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String)  # kpop, jpop, english, cpop, custom
    spotify_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    songs = relationship("Song", back_populates="playlist")

class Song(Base):
    __tablename__ = "songs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist = Column(String, index=True)
    album = Column(String, nullable=True)
    
    # Local file paths
    mp3_path = Column(String, nullable=True)
    flac_path = Column(String, nullable=True)
    video_path = Column(String, nullable=True)
    
    # External IDs
    spotify_id = Column(String, unique=True, nullable=True)
    youtube_id = Column(String, unique=True, nullable=True)
    
    # Metadata
    duration = Column(Integer, nullable=True)  # in seconds
    file_size = Column(Integer, nullable=True)  # in bytes
    quality = Column(String, nullable=True)  # 320kbps, FLAC, etc.
    
    # Relationships
    playlist_id = Column(Integer, ForeignKey("playlists.id"))
    playlist = relationship("Playlist", back_populates="songs")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DownloadJob(Base):
    __tablename__ = "download_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=True)
    status = Column(String, default="pending")  # pending, downloading, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

# Database setup
DATABASE_URL = "sqlite:///./mediamaestro.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()