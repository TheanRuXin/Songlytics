# spotify_service.py
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import streamlit as st

CLIENT_ID = "8da405a927a44e38b765532c2fe981ab"
CLIENT_SECRET = "9bc17da1916f4954ae0022d0bd067835"

class SpotifyService:
    def __init__(self):
        try:
            self.client_credentials_manager = SpotifyClientCredentials(
                client_id=CLIENT_ID, 
                client_secret=CLIENT_SECRET
            )
            self.sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)
            self.is_available = True
        except Exception as e:
            st.warning(f"Spotify API not available: {e}. Using local dataset as fallback.")
            self.is_available = False
    
    def search_song(self, query, limit=10):
        """搜索歌曲"""
        if not self.is_available:
            return self._search_local(query, limit)
        
        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = []
            for track in results['tracks']['items']:
                tracks.append({
                    'track_id': track['id'],
                    'song': track['name'],
                    'artist': ', '.join([a['name'] for a in track['artists']]),
                    'album_name': track['album']['name'],
                    'popularity': track['popularity'],  # Spotify's own popularity (0-100)
                    'explicit': 1 if track['explicit'] else 0
                })
            return tracks
        except Exception as e:
            st.error(f"Spotify search failed: {e}")
            return []
    
    def get_audio_features(self, track_id):
        """获取音频特征"""
        if not self.is_available:
            return None
        
        try:
            features = self.sp.audio_features(track_id)[0]
            if not features:
                return None
            
            return {
                "duration_ms": features['duration_ms'],
                "explicit": 1 if features.get('explicit', False) else 0,
                "danceability": features['danceability'],
                "energy": features['energy'],
                "loudness": features['loudness'],
                "speechiness": features['speechiness'],
                "acousticness": features['acousticness'],
                "instrumentalness": features['instrumentalness'],
                "liveness": features['liveness'],
                "valence": features['valence'],
                "tempo": features['tempo']
            }
        except Exception as e:
            st.error(f"Failed to get audio features: {e}")
            return None
    
    def _search_local(self, query, limit=10):
        """Fallback: search in local CSV"""
        # 读取你的 dataset
        CSV_PATH = "C:/Users/ruxin/Documents/ruxin/FYP/Data/clean_spotify.csv"
        df = pd.read_csv(CSV_PATH)
        
        df["song"] = df["song"].astype(str).str.lower()
        df["artist"] = df["artist"].astype(str).str.lower()
        query_lower = query.lower()
        
        # 搜索匹配的歌曲
        matches = df[
            df["song"].str.contains(query_lower, na=False) | 
            df["artist"].str.contains(query_lower, na=False)
        ].head(limit)
        
        tracks = []
        for _, row in matches.iterrows():
            tracks.append({
                'track_id': row.get('track_id', ''),
                'song': row['song'],
                'artist': row['artist'],
                'album_name': row.get('album_name', ''),
                'popularity': row.get('popularity', 50),
                'explicit': row.get('explicit', 0)
            })
        return tracks

# 全局实例
spotify_service = SpotifyService()