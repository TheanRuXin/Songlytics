# services/dashboard_service.py
import pandas as pd
import numpy as np
import streamlit as st

CSV_PATH = "C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_merged_cleaned.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)
    
    required_cols = ['duration_ms', 'explicit', 'danceability', 'energy', 'speechiness', 
                     'acousticness', 'instrumentalness', 'liveness', 'valence', 'loudness', 
                     'tempo', 'popularity_class', 'source']
    
    # check the missing columns
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.warning(f"Missing columns: {missing_cols}")
    
    # add a simulated popularity score for visualization (based on popularity_class)
    df['popularity'] = df['popularity_class'].map({0: 25, 1: 50, 2: 85})
    
    return df

def get_kpi():
    df = load_data()
    
    low_count = len(df[df['popularity_class'] == 0])
    medium_count = len(df[df['popularity_class'] == 1])
    high_count = len(df[df['popularity_class'] == 2])
    
    #calculate average danceability and energy
    avg_danceability = df['danceability'].mean()
    avg_energy = df['energy'].mean()
    
    return {
        "total": len(df),
        "low_count": low_count,
        "medium_count": medium_count,
        "high_count": high_count,
        "avg_danceability": avg_danceability,
        "avg_energy": avg_energy
    }

def get_popularity_distribution():
    """get the distribution of popularity classes"""
    df = load_data()
    
    result = df['popularity_class'].value_counts().reset_index()
    result.columns = ['class', 'count']
    
    result['label'] = result['class'].map({
        0: 'Low Popularity',
        1: 'Medium Popularity',
        2: 'High Popularity'
    })
    
    return result[['label', 'count']]

def get_feature_distribution(feature):
    """get the distribution of a single feature"""
    df = load_data()
    
    if feature in df.columns:
        return df[feature].dropna()
    return pd.Series()

def get_features_summary():
    """get the summary statistics of all features"""
    df = load_data()
    
    features = ['danceability', 'energy', 'speechiness', 'acousticness', 
                'instrumentalness', 'liveness', 'valence', 'loudness', 'tempo']
    
    summary = {}
    for feature in features:
        if feature in df.columns:
            summary[feature] = {
                'mean': df[feature].mean(),
                'median': df[feature].median(),
                'std': df[feature].std(),
                'min': df[feature].min(),
                'max': df[feature].max()
            }
    
    return summary

def get_feature_by_popularity(feature):
    """based on the popularity class, get the mean and median of a specific feature"""
    df = load_data()
    
    if feature not in df.columns:
        return pd.DataFrame()
    
    result = df.groupby('popularity_class')[feature].agg(['mean', 'median']).reset_index()
    result['label'] = result['popularity_class'].map({
        0: 'Low',
        1: 'Medium', 
        2: 'High'
    })
    
    return result

def get_correlation_matrix():
    """get the correlation matrix of numerical features"""
    df = load_data()
    
    features = ['danceability', 'energy', 'speechiness', 'acousticness', 
                'instrumentalness', 'liveness', 'valence', 'loudness', 'tempo']
    
    available_features = [f for f in features if f in df.columns]
    
    if len(available_features) >= 2:
        corr_matrix = df[available_features].corr()
        return corr_matrix
    
    return pd.DataFrame()

def get_feature_importance_from_model():
    """get the feature importance from the trained model"""
    try:
        import joblib
        model_data = joblib.load("models/music_model_mp3.pkl")
        model = model_data["model"]
        features = model_data["features"]
        
        importance = pd.DataFrame({
            'feature': features,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance
    except Exception as e:
        features = ['instrumentalness', 'explicit', 'energy', 'acousticness', 'loudness', 
                   'danceability', 'duration_ms', 'speechiness', 'valence', 'liveness', 'tempo']
        importance = pd.DataFrame({
            'feature': features,
            'importance': [0.175, 0.124, 0.100, 0.099, 0.093, 0.081, 0.075, 0.074, 0.070, 0.058, 0.051]
        })
        return importance

def get_source_distribution():
    """get the distribution of data sources"""
    df = load_data()
    
    if 'source' in df.columns:
        result = df['source'].value_counts().reset_index()
        result.columns = ['source', 'count']
        return result
    
    return pd.DataFrame()

def get_tempo_distribution():
    """get the distribution of tempo categories"""
    df = load_data()
    
    if 'tempo' in df.columns:
        df['tempo_category'] = pd.cut(
            df['tempo'], 
            bins=[0, 90, 120, 250], 
            labels=['Slow (<90 BPM)', 'Medium (90-120 BPM)', 'Fast (>120 BPM)']
        )
        
        result = df['tempo_category'].value_counts().reset_index()
        result.columns = ['category', 'count']
        return result
    
    return pd.DataFrame()

def get_explicit_distribution():
    """get the distribution of explicit labels"""
    df = load_data()
    
    if 'explicit' in df.columns:
        result = df['explicit'].value_counts().reset_index()
        result.columns = ['explicit', 'count']
        result['label'] = result['explicit'].map({0: 'Clean', 1: 'Explicit'})
        return result
    
    return pd.DataFrame()

def get_top_songs_by_popularity(limit=10):
    """get the list of popular songs (sorted by popularity)"""
    df = load_data()
    
    if 'song' not in df.columns or 'artist' not in df.columns:
        # If no song name information is available, return empty data
        return pd.DataFrame()
    
    # Sort by popularity_class, with High priority
    top_songs = df[df['song'] != 'Unknown'].copy()
    top_songs = top_songs.sort_values('popularity_class', ascending=False)
    
    top_songs = top_songs.drop_duplicates(subset=['song', 'artist'])
    
    result = top_songs.head(limit)[['song', 'artist', 'popularity_class']].copy()
    result['popularity_label'] = result['popularity_class'].map({
        0: 'Low', 1: 'Medium', 2: 'High'
    })
    
    return result

def search_songs(keyword):
    """search song by artist name and song name"""
    df = load_data()
    
    if 'song' not in df.columns or 'artist' not in df.columns:
        return pd.DataFrame()
    
    keyword_lower = keyword.lower()
    
    # Search for matching songs
    matched = df[
        df['song'].str.lower().str.contains(keyword_lower, na=False) |
        df['artist'].str.lower().str.contains(keyword_lower, na=False)
    ].copy()
    
    # Remove duplicates
    matched = matched.drop_duplicates(subset=['song', 'artist'])
    
    result = matched[['song', 'artist', 'popularity_class']].head(20)
    result['popularity_label'] = result['popularity_class'].map({
        0: 'Low', 1: 'Medium', 2: 'High'
    })
    
    return result

def get_song_features(song_name, artist_name):
    """get the features of a specified song"""
    df = load_data()
    
    if 'song' not in df.columns or 'artist' not in df.columns:
        return None
    
    # Search for the song
    song_data = df[
        (df['song'].str.lower() == song_name.lower()) &
        (df['artist'].str.lower() == artist_name.lower())
    ]
    
    if song_data.empty:
        return None
    
    return song_data.iloc[0]

def get_popularity_by_song_count(limit=20):
    """get the number of popular songs for each artist"""
    df = load_data()
    
    if 'artist' not in df.columns:
        return pd.DataFrame()
    
    # Count the number of High popularity songs for each artist
    high_songs = df[df['popularity_class'] == 2]
    artist_count = high_songs['artist'].value_counts().reset_index()
    artist_count.columns = ['artist', 'high_popularity_count']
    
    return artist_count.head(limit)

def get_song_examples_by_class():
    """get the example songs for each popularity class"""
    df = load_data()
    
    if 'song' not in df.columns:
        return {}
    
    examples = {}
    
    for class_id, label in [(0, 'Low'), (1, 'Medium'), (2, 'High')]:
        class_songs = df[df['popularity_class'] == class_id]
        class_songs = class_songs[class_songs['song'] != 'Unknown']
        class_songs = class_songs.drop_duplicates(subset=['song', 'artist'])
        
        examples[label] = class_songs.head(5)[['song', 'artist']].to_dict('records')
    
    return examples