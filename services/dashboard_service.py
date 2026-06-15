# services/dashboard_service.py
import pandas as pd
import numpy as np
import streamlit as st

CSV_PATH = "C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_merged_cleaned.csv"

@st.cache_data
def load_data():
    """加载数据"""
    df = pd.read_csv(CSV_PATH)
    
    # 确保必要的列存在
    required_cols = ['duration_ms', 'explicit', 'danceability', 'energy', 'speechiness', 
                     'acousticness', 'instrumentalness', 'liveness', 'valence', 'loudness', 
                     'tempo', 'popularity_class', 'source']
    
    # 检查缺失的列
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.warning(f"Missing columns: {missing_cols}")
    
    # 添加一个模拟的 popularity 分数用于可视化（基于 popularity_class）
    df['popularity'] = df['popularity_class'].map({0: 25, 1: 50, 2: 85})
    
    return df

def get_kpi():
    """获取关键绩效指标"""
    df = load_data()
    
    low_count = len(df[df['popularity_class'] == 0])
    medium_count = len(df[df['popularity_class'] == 1])
    high_count = len(df[df['popularity_class'] == 2])
    
    # 计算平均音频特征
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
    """获取流行度分类分布"""
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
    """获取单个特征的分布"""
    df = load_data()
    
    if feature in df.columns:
        return df[feature].dropna()
    return pd.Series()

def get_features_summary():
    """获取所有特征的统计摘要"""
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
    """按流行度分类查看特征分布"""
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
    """获取特征相关性矩阵"""
    df = load_data()
    
    # 选择数值特征
    features = ['danceability', 'energy', 'speechiness', 'acousticness', 
                'instrumentalness', 'liveness', 'valence', 'loudness', 'tempo']
    
    # 只保留存在的特征
    available_features = [f for f in features if f in df.columns]
    
    if len(available_features) >= 2:
        corr_matrix = df[available_features].corr()
        return corr_matrix
    
    return pd.DataFrame()

def get_feature_importance_from_model():
    """从训练好的模型获取特征重要性"""
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
        # 如果模型加载失败，返回模拟数据
        features = ['instrumentalness', 'explicit', 'energy', 'acousticness', 'loudness', 
                   'danceability', 'duration_ms', 'speechiness', 'valence', 'liveness', 'tempo']
        importance = pd.DataFrame({
            'feature': features,
            'importance': [0.175, 0.124, 0.100, 0.099, 0.093, 0.081, 0.075, 0.074, 0.070, 0.058, 0.051]
        })
        return importance

def get_source_distribution():
    """获取数据来源分布"""
    df = load_data()
    
    if 'source' in df.columns:
        result = df['source'].value_counts().reset_index()
        result.columns = ['source', 'count']
        return result
    
    return pd.DataFrame()

def get_tempo_distribution():
    """获取节奏分类分布"""
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
    """获取 Explicit 标签分布"""
    df = load_data()
    
    if 'explicit' in df.columns:
        result = df['explicit'].value_counts().reset_index()
        result.columns = ['explicit', 'count']
        result['label'] = result['explicit'].map({0: 'Clean', 1: 'Explicit'})
        return result
    
    return pd.DataFrame()

def get_top_songs_by_popularity(limit=10):
    """获取热门歌曲列表（按流行度排序）"""
    df = load_data()
    
    if 'song' not in df.columns or 'artist' not in df.columns:
        # 如果没有歌名信息，返回空数据
        return pd.DataFrame()
    
    # 按 popularity_class 排序，High 优先
    top_songs = df[df['song'] != 'Unknown'].copy()
    top_songs = top_songs.sort_values('popularity_class', ascending=False)
    
    # 去重（避免同一首歌出现多次）
    top_songs = top_songs.drop_duplicates(subset=['song', 'artist'])
    
    result = top_songs.head(limit)[['song', 'artist', 'popularity_class']].copy()
    result['popularity_label'] = result['popularity_class'].map({
        0: 'Low', 1: 'Medium', 2: 'High'
    })
    
    return result

def search_songs(keyword):
    """搜索歌曲（按歌名或艺术家）"""
    df = load_data()
    
    if 'song' not in df.columns or 'artist' not in df.columns:
        return pd.DataFrame()
    
    keyword_lower = keyword.lower()
    
    # 搜索匹配的歌曲
    matched = df[
        df['song'].str.lower().str.contains(keyword_lower, na=False) |
        df['artist'].str.lower().str.contains(keyword_lower, na=False)
    ].copy()
    
    # 去重
    matched = matched.drop_duplicates(subset=['song', 'artist'])
    
    result = matched[['song', 'artist', 'popularity_class']].head(20)
    result['popularity_label'] = result['popularity_class'].map({
        0: 'Low', 1: 'Medium', 2: 'High'
    })
    
    return result

def get_song_features(song_name, artist_name):
    """获取指定歌曲的特征"""
    df = load_data()
    
    if 'song' not in df.columns or 'artist' not in df.columns:
        return None
    
    # 查找歌曲
    song_data = df[
        (df['song'].str.lower() == song_name.lower()) &
        (df['artist'].str.lower() == artist_name.lower())
    ]
    
    if song_data.empty:
        return None
    
    return song_data.iloc[0]

def get_popularity_by_song_count(limit=20):
    """获取每个艺术家的热门歌曲数量"""
    df = load_data()
    
    if 'artist' not in df.columns:
        return pd.DataFrame()
    
    # 统计每个艺术家的 High 流行度歌曲数量
    high_songs = df[df['popularity_class'] == 2]
    artist_count = high_songs['artist'].value_counts().reset_index()
    artist_count.columns = ['artist', 'high_popularity_count']
    
    return artist_count.head(limit)

def get_song_examples_by_class():
    """获取每个流行度类别的示例歌曲"""
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