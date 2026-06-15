import pandas as pd
import numpy as np
import chardet


def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))
        return result['encoding']


def read_csv_with_encoding(file_path):
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252', 'utf-16']

    for encoding in encodings:
        try:
            print(f"   Trying encoding: {encoding}")
            df = pd.read_csv(file_path, encoding=encoding)
            print(f"   Success with {encoding}")
            return df
        except (UnicodeDecodeError, UnicodeError):
            continue
    try:
        detected = detect_encoding(file_path)
        print(f"   Detected encoding: {detected}")
        df = pd.read_csv(file_path, encoding=detected)
        return df
    except Exception:
        raise Exception(f"Could not read file: {file_path}")


FEATURES = [
    "duration_ms",
    "explicit",
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo"
]

TARGET_COLS = ['popularity', 'popularity_class']


def drop_incomplete_features(df_clean):
    """Drop rows with missing values in feature/metadata columns only.
    Rows that are missing popularity / popularity_class are KEPT
    (they're just unusable for regression, but still fine for
    classification / EDA / recommendation)."""
    feature_cols = [c for c in df_clean.columns if c not in TARGET_COLS]
    return df_clean.dropna(subset=feature_cols)


def classify_popularity_value(p):
    """0-100 popularity score -> 0/1/2 class. NaN-safe."""
    if pd.isna(p):
        return np.nan
    if p >= 67:
        return 2.0
    elif p >= 34:
        return 1.0
    else:
        return 0.0


def final_genre_categorization(genre_value):
    """Complete genre categorization: split + map to main categories"""
    if pd.isna(genre_value) or genre_value == 'Unknown':
        return 'Unknown'

    genre_str = str(genre_value).strip().lower()

    # Split by comma, take first one
    if ',' in genre_str:
        genre_str = genre_str.split(',')[0]

    # Handle slash
    if '/' in genre_str:
        genre_str = genre_str.split('/')[0]

    genre_str = genre_str.strip()

    # Pop
    pop_keywords = ['pop', 'indie pop', 'synth pop', 'dream pop', 'bubblegum pop']
    for kw in pop_keywords:
        if kw in genre_str:
            return 'Pop'

    # Rock
    rock_keywords = ['rock', 'hard rock', 'alternative rock', 'punk rock', 'indie rock',
                     'classic rock', 'soft rock', 'garage rock', 'heavy metal', 'metal']
    for kw in rock_keywords:
        if kw in genre_str:
            return 'Rock'

    # Hip Hop
    hiphop_keywords = ['hip hop', 'hip-hop', 'rap', 'trap']
    for kw in hiphop_keywords:
        if kw in genre_str:
            return 'Hip Hop'

    # Electronic
    electronic_keywords = ['electronic', 'edm', 'dance', 'house', 'techno', 'trance',
                           'dubstep', 'electro', 'dance/electronic']
    for kw in electronic_keywords:
        if kw in genre_str:
            return 'Electronic'

    # R&B / Soul
    rnb_keywords = ['r&b', 'rnb', 'soul']
    for kw in rnb_keywords:
        if kw in genre_str:
            return 'R&B'

    # Latin
    latin_keywords = ['latin', 'reggaeton', 'salsa', 'bachata', 'cumbia', 'tango']
    for kw in latin_keywords:
        if kw in genre_str:
            return 'Latin'

    # Country
    country_keywords = ['country', 'bluegrass']
    for kw in country_keywords:
        if kw in genre_str:
            return 'Country'

    # Jazz
    jazz_keywords = ['jazz', 'bebop', 'swing', 'fusion jazz']
    for kw in jazz_keywords:
        if kw in genre_str:
            return 'Jazz'

    # Classical
    classical_keywords = ['classical', 'opera', 'orchestra', 'symphony']
    for kw in classical_keywords:
        if kw in genre_str:
            return 'Classical'

    # Blues
    blues_keywords = ['blues']
    for kw in blues_keywords:
        if kw in genre_str:
            return 'Blues'

    # Folk
    folk_keywords = ['folk', 'acoustic', 'folk/acoustic']
    for kw in folk_keywords:
        if kw in genre_str:
            return 'Folk'

    # World
    world_keywords = ['world', 'world/traditional']
    for kw in world_keywords:
        if kw in genre_str:
            return 'World'

    # Reggae
    reggae_keywords = ['reggae']
    for kw in reggae_keywords:
        if kw in genre_str:
            return 'Reggae'

    # Soundtrack
    soundtrack_keywords = ['soundtrack', 'movie']
    for kw in soundtrack_keywords:
        if kw in genre_str:
            return 'Soundtrack'

    # Children
    children_keywords = ["children's music", "children’s music"]
    for kw in children_keywords:
        if kw in genre_str:
            return 'Children'

    # Comedy
    comedy_keywords = ['comedy']
    for kw in comedy_keywords:
        if kw in genre_str:
            return 'Comedy'

    # Anime
    anime_keywords = ['anime']
    for kw in anime_keywords:
        if kw in genre_str:
            return 'Anime'

    # Ska
    ska_keywords = ['ska']
    for kw in ska_keywords:
        if kw in genre_str:
            return 'Ska'

    # Indie
    indie_keywords = ['indie']
    for kw in indie_keywords:
        if kw in genre_str:
            return 'Indie'

    # Study
    study_keywords = ['study']
    for kw in study_keywords:
        if kw in genre_str:
            return 'Study'

    # Easy Listening
    easy_keywords = ['easy listening']
    for kw in easy_keywords:
        if kw in genre_str:
            return 'Easy Listening'

    # Cantopop (treat as Pop)
    if 'cantopop' in genre_str:
        return 'Pop'

    return 'Other'


def clean_and_categorize_genre(g):
    """Clean and categorize genre in one function"""
    if pd.isna(g):
        return 'Unknown'
    g = str(g)
    if ',' in g:
        g = g.split(',')[0]
    if '/' in g:
        g = g.split('/')[0]
    g = g.strip().lower()
    return final_genre_categorization(g)


def clean_dataset1(df):
    print("\n Dataset 1")
    print(f"   Original shape: {df.shape}")
    print(f"   Columns: {df.columns.tolist()[:10]}...")

    df_clean = pd.DataFrame()

    duration_col = None
    for col in ['duration_ms', 'duration', 'Duration']:
        if col in df.columns:
            duration_col = col
            break

    if duration_col:
        df_clean['duration_ms'] = pd.to_numeric(df[duration_col], errors='coerce')
    else:
        df_clean['duration_ms'] = 180000

    # explicit
    if 'explicit' in df.columns:
        df_clean['explicit'] = df['explicit'].astype(int)
    else:
        df_clean['explicit'] = 0

    audio_features = ['danceability', 'energy', 'speechiness', 'acousticness',
                      'instrumentalness', 'liveness', 'valence']

    for col in audio_features:
        if col in df.columns:
            df_clean[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.5)
        else:
            df_clean[col] = 0.5

    if 'loudness' in df.columns:
        df_clean['loudness'] = pd.to_numeric(df['loudness'], errors='coerce').fillna(-10)
    else:
        df_clean['loudness'] = -10

    if 'tempo' in df.columns:
        df_clean['tempo'] = pd.to_numeric(df['tempo'], errors='coerce').fillna(120)
    else:
        df_clean['tempo'] = 120

    # --- popularity / popularity_class (NaN-safe, keeps continuous score) ---
    if 'popularity' in df.columns:
        pop_score = pd.to_numeric(df['popularity'], errors='coerce')
        df_clean['popularity'] = pop_score
        df_clean['popularity_class'] = pop_score.apply(classify_popularity_value)
    elif 'streams' in df.columns:
        streams = pd.to_numeric(df['streams'], errors='coerce')
        df_clean['popularity'] = np.nan  # streams is not on a 0-100 scale
        df_clean['popularity_class'] = pd.cut(
            streams,
            bins=[0, 100000, 1000000, float('inf')],
            labels=[0, 1, 2]
        ).astype(float)
    else:
        df_clean['popularity'] = np.nan
        df_clean['popularity_class'] = np.nan

    if 'song' in df.columns:
        df_clean['song'] = df['song']
    elif 'track_name' in df.columns:
        df_clean['song'] = df['track_name']
    else:
        df_clean['song'] = 'Unknown'

    if 'artist' in df.columns:
        df_clean['artist'] = df['artist']
    elif 'artist_name' in df.columns:
        df_clean['artist'] = df['artist_name']
    elif 'artists' in df.columns:
        df_clean['artist'] = df['artists']
    else:
        df_clean['artist'] = 'Unknown'

    # Genre with full categorization
    if 'genre' in df.columns:
        df_clean['genre'] = df['genre'].apply(clean_and_categorize_genre)
    else:
        df_clean['genre'] = 'Unknown'

    df_clean['source'] = 'spotify_normalize'

    df_clean = drop_incomplete_features(df_clean)
    df_clean = df_clean[df_clean['duration_ms'] > 30000]
    df_clean = df_clean[df_clean['duration_ms'] < 600000]
    df_clean = df_clean[df_clean['tempo'].between(40, 240)]
    df_clean = df_clean[df_clean['loudness'].between(-60, 0)]

    print(f"   Cleaned shape: {df_clean.shape}")
    if len(df_clean) > 0:
        print(f"   Class distribution:\n{df_clean['popularity_class'].value_counts(dropna=False)}")
        print(f"   Rows with continuous popularity: {df_clean['popularity'].notna().sum()}")

    return df_clean


def clean_dataset2(df):
    print("Dataset 2")
    print(f"   Original shape: {df.shape}")
    print(f"   Columns: {df.columns.tolist()[:10]}...")

    df_clean = pd.DataFrame()

    if 'duration_ms' in df.columns:
        df_clean['duration_ms'] = pd.to_numeric(df['duration_ms'], errors='coerce')
    else:
        df_clean['duration_ms'] = 180000

    if 'explicit' in df.columns:
        df_clean['explicit'] = df['explicit'].astype(int)
    else:
        df_clean['explicit'] = 0

    percent_cols = ['danceability_%', 'valence_%', 'energy_%',
                    'acousticness_%', 'instrumentalness_%', 'liveness_%', 'speechiness_%']

    for col in percent_cols:
        base_col = col.replace('_%', '')
        if col in df.columns:
            df_clean[base_col] = pd.to_numeric(df[col], errors='coerce') / 100
        else:
            if base_col in df.columns:
                df_clean[base_col] = pd.to_numeric(df[base_col], errors='coerce')
            else:
                df_clean[base_col] = 0.5

    if 'loudness' in df.columns:
        df_clean['loudness'] = pd.to_numeric(df['loudness'], errors='coerce').fillna(-6)
    elif 'energy' in df.columns:
        df_clean['loudness'] = -20 + (df_clean['energy'] * 20)
    else:
        df_clean['loudness'] = -6

    # tempo (bpm)
    if 'bpm' in df.columns:
        df_clean['tempo'] = pd.to_numeric(df['bpm'], errors='coerce')
    elif 'tempo' in df.columns:
        df_clean['tempo'] = pd.to_numeric(df['tempo'], errors='coerce')
    else:
        df_clean['tempo'] = 120

    if 'song' in df.columns:
        df_clean['song'] = df['song']
    elif 'track_name' in df.columns:
        df_clean['song'] = df['track_name']
    else:
        df_clean['song'] = 'Unknown'

    if 'artist' in df.columns:
        df_clean['artist'] = df['artist']
    elif 'artist_name' in df.columns:
        df_clean['artist'] = df['artist_name']
    elif 'artists' in df.columns:
        df_clean['artist'] = df['artists']
    else:
        df_clean['artist'] = 'Unknown'

    # --- popularity / popularity_class (NaN-safe, keeps continuous score) ---
    if 'popularity' in df.columns:
        pop_score = pd.to_numeric(df['popularity'], errors='coerce')
        df_clean['popularity'] = pop_score
        df_clean['popularity_class'] = pop_score.apply(classify_popularity_value)
    elif 'streams' in df.columns:
        streams = pd.to_numeric(df['streams'], errors='coerce')
        df_clean['popularity'] = np.nan
        df_clean['popularity_class'] = pd.cut(
            streams,
            bins=[0, 100000, 1000000, float('inf')],
            labels=[0, 1, 2]
        ).astype(float)
    else:
        df_clean['popularity'] = np.nan
        df_clean['popularity_class'] = np.nan

    # Genre with full categorization
    if 'genre' in df.columns:
        df_clean['genre'] = df['genre'].apply(clean_and_categorize_genre)
    else:
        df_clean['genre'] = 'Unknown'

    df_clean = drop_incomplete_features(df_clean)
    df_clean = df_clean[df_clean['tempo'].between(40, 240)]
    df_clean = df_clean[df_clean['danceability'].between(0, 1)]
    df_clean = df_clean[df_clean['energy'].between(0, 1)]
    df_clean = df_clean[df_clean['loudness'].between(-60, 0)]
    df_clean['source'] = 'spotify_features'

    print(f"   Cleaned shape: {df_clean.shape}")
    if len(df_clean) > 0:
        print(f"   Class distribution:\n{df_clean['popularity_class'].value_counts(dropna=False)}")
        print(f"   Rows with continuous popularity: {df_clean['popularity'].notna().sum()}")

    return df_clean


def clean_dataset3(df):
    print("Dataset 3")
    print(f"   Original shape: {df.shape}")
    print(f"   Columns: {df.columns.tolist()[:10]}...")

    df_clean = pd.DataFrame()

    if 'duration_ms' in df.columns:
        df_clean['duration_ms'] = pd.to_numeric(df['duration_ms'], errors='coerce')
    else:
        df_clean['duration_ms'] = 180000

    if 'explicit' in df.columns:
        df_clean['explicit'] = df['explicit'].astype(int)
    else:
        df_clean['explicit'] = 0

    audio_features = ['danceability', 'energy', 'speechiness', 'acousticness',
                      'instrumentalness', 'liveness', 'valence']

    for col in audio_features:
        if col in df.columns:
            df_clean[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.5)
        else:
            df_clean[col] = 0.5

    # loudness
    if 'loudness' in df.columns:
        df_clean['loudness'] = pd.to_numeric(df['loudness'], errors='coerce')
    else:
        df_clean['loudness'] = -10

    # tempo
    if 'tempo' in df.columns:
        df_clean['tempo'] = pd.to_numeric(df['tempo'], errors='coerce')
    else:
        df_clean['tempo'] = 120

    # --- popularity / popularity_class (NaN-safe, keeps continuous score) ---
    if 'popularity' in df.columns:
        pop_score = pd.to_numeric(df['popularity'], errors='coerce')
        df_clean['popularity'] = pop_score
        df_clean['popularity_class'] = pop_score.apply(classify_popularity_value)
    elif 'streams' in df.columns:
        streams = pd.to_numeric(df['streams'], errors='coerce')
        df_clean['popularity'] = np.nan
        df_clean['popularity_class'] = pd.cut(
            streams,
            bins=[0, 100000, 1000000, float('inf')],
            labels=[0, 1, 2]
        ).astype(float)
    else:
        df_clean['popularity'] = np.nan
        df_clean['popularity_class'] = np.nan

    if 'song' in df.columns:
        df_clean['song'] = df['song']
    elif 'track_name' in df.columns:
        df_clean['song'] = df['track_name']
    else:
        df_clean['song'] = 'Unknown'

    if 'artist' in df.columns:
        df_clean['artist'] = df['artist']
    elif 'artist_name' in df.columns:
        df_clean['artist'] = df['artist_name']
    elif 'artists' in df.columns:
        df_clean['artist'] = df['artists']
    else:
        df_clean['artist'] = 'Unknown'

    # Genre with full categorization
    if 'genre' in df.columns:
        df_clean['genre'] = df['genre'].apply(clean_and_categorize_genre)
    elif 'track_genre' in df.columns:
        df_clean['genre'] = df['track_genre'].apply(clean_and_categorize_genre)
    else:
        df_clean['genre'] = 'Unknown'

    df_clean['source'] = 'tracks_detailed'

    df_clean = drop_incomplete_features(df_clean)
    df_clean = df_clean[df_clean['duration_ms'] > 30000]
    df_clean = df_clean[df_clean['duration_ms'] < 600000]
    df_clean = df_clean[df_clean['tempo'].between(40, 240)]
    df_clean = df_clean[df_clean['loudness'].between(-60, 0)]
    df_clean = df_clean[df_clean['danceability'].between(0, 1)]
    df_clean = df_clean[df_clean['energy'].between(0, 1)]

    print(f"   Cleaned shape: {df_clean.shape}")
    if len(df_clean) > 0:
        print(f"   Class distribution:\n{df_clean['popularity_class'].value_counts(dropna=False)}")
        print(f"   Rows with continuous popularity: {df_clean['popularity'].notna().sum()}")

    return df_clean


def clean_dataset4(df):
    print("Dataset 4")
    print(f"   Original shape: {df.shape}")
    print(f"   Columns: {df.columns.tolist()}")

    df_clean = pd.DataFrame()

    if 'length' in df.columns:
        length_seconds = pd.to_numeric(df['length'], errors='coerce')
        df_clean['duration_ms'] = length_seconds * 1000
    else:
        df_clean['duration_ms'] = 180000

    df_clean['explicit'] = 0

    def normalize_percent(val):
        if pd.isna(val):
            return 0.5
        if val > 1:
            return val / 100
        return val

    if 'danceability' in df.columns:
        df_clean['danceability'] = pd.to_numeric(df['danceability'], errors='coerce').apply(normalize_percent)
    else:
        df_clean['danceability'] = 0.5

    if 'energy' in df.columns:
        df_clean['energy'] = pd.to_numeric(df['energy'], errors='coerce').apply(normalize_percent)
    else:
        df_clean['energy'] = 0.5

    if 'speechiness' in df.columns:
        df_clean['speechiness'] = pd.to_numeric(df['speechiness'], errors='coerce').apply(normalize_percent)
    else:
        df_clean['speechiness'] = 0.5

    if 'acousticness' in df.columns:
        df_clean['acousticness'] = pd.to_numeric(df['acousticness'], errors='coerce')
        if df_clean['acousticness'].max() > 1:
            df_clean['acousticness'] = df_clean['acousticness'] / 100
        df_clean['acousticness'] = df_clean['acousticness'].clip(0, 1)
    else:
        df_clean['acousticness'] = 0.5

    df_clean['instrumentalness'] = 0.0


    if 'liveness' in df.columns:
        df_clean['liveness'] = pd.to_numeric(df['liveness'], errors='coerce').apply(normalize_percent)
    else:
        df_clean['liveness'] = 0.5

    if 'valence' in df.columns:
        df_clean['valence'] = pd.to_numeric(df['valence'], errors='coerce').apply(normalize_percent)
    elif 'valance' in df.columns:
        df_clean['valence'] = pd.to_numeric(df['valance'], errors='coerce').apply(normalize_percent)
    else:
        df_clean['valence'] = 0.5

    if 'loudness' in df.columns:
        df_clean['loudness'] = pd.to_numeric(df['loudness'], errors='coerce')
    elif 'loudness.dB' in df.columns:
        df_clean['loudness'] = pd.to_numeric(df['loudness.dB'], errors='coerce')
    else:
        df_clean['loudness'] = -10

    # tempo (BPM)
    if 'tempo' in df.columns:
        df_clean['tempo'] = pd.to_numeric(df['tempo'], errors='coerce')
    elif 'beats.per.minute' in df.columns:
        df_clean['tempo'] = pd.to_numeric(df['beats.per.minute'], errors='coerce')
    elif 'bpm' in df.columns:
        df_clean['tempo'] = pd.to_numeric(df['bpm'], errors='coerce')
    else:
        df_clean['tempo'] = 120

    # --- popularity / popularity_class (NaN-safe, keeps continuous score) ---
    if 'popularity' in df.columns:
        raw_pop = pd.to_numeric(df['popularity'], errors='coerce')
        if raw_pop.notna().any() and raw_pop.max() <= 1:
            pop_score = raw_pop * 100
        else:
            pop_score = raw_pop
        df_clean['popularity'] = pop_score
        df_clean['popularity_class'] = pop_score.apply(classify_popularity_value)
    else:
        df_clean['popularity'] = np.nan
        df_clean['popularity_class'] = np.nan

    # song - 使用 title 列
    if 'song' in df.columns:
        df_clean['song'] = df['song'].astype(str)
    elif 'track_name' in df.columns:
        df_clean['song'] = df['track_name'].astype(str)
    elif 'title' in df.columns:
        df_clean['song'] = df['title'].astype(str)
    else:
        df_clean['song'] = 'Unknown'

    # artist
    if 'artist' in df.columns:
        df_clean['artist'] = df['artist'].astype(str)
    elif 'artist_name' in df.columns:
        df_clean['artist'] = df['artist_name'].astype(str)
    elif 'artists' in df.columns:
        df_clean['artist'] = df['artists'].astype(str)
    else:
        df_clean['artist'] = 'Unknown'

    if 'genre' in df.columns:
        df_clean['genre'] = df['genre'].apply(clean_and_categorize_genre)
    elif 'top_genre' in df.columns:
        df_clean['genre'] = df['top_genre'].apply(clean_and_categorize_genre)
    elif 'top genre' in df.columns:
        df_clean['genre'] = df['top genre'].apply(clean_and_categorize_genre)
    else:
        df_clean['genre'] = 'Unknown'

    df_clean['source'] = 'top_streamed'

    print(f"   Before cleaning: {len(df_clean)} rows")

    df_clean = drop_incomplete_features(df_clean)
    print(f"   After dropna: {len(df_clean)} rows")

    if len(df_clean) > 0:
        df_clean = df_clean[df_clean['duration_ms'] > 10000]
        df_clean = df_clean[df_clean['duration_ms'] < 900000]

        df_clean = df_clean[df_clean['tempo'].between(30, 250)]

        df_clean = df_clean[df_clean['loudness'].between(-70, 10)]

        df_clean = df_clean[df_clean['danceability'].between(0, 1)]
        df_clean = df_clean[df_clean['energy'].between(0, 1)]

    print(f"   Cleaned shape: {df_clean.shape}")
    if len(df_clean) > 0:
        print(f"   Rows with continuous popularity: {df_clean['popularity'].notna().sum()}")

    return df_clean


def main():
    print("=" * 60)
    print("SPOTIFY DATASETS CLEANING AND MERGING")
    print("=" * 60)

    file_paths = {
        'dataset1': "C:/Users/ruxin/Documents/ruxin/FYP/Data/songs_normalize.csv",
        'dataset2': "C:/Users/ruxin/Documents/ruxin/FYP/Data/SpotifyFeatures.csv",
        'dataset3': "C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify-tracks-dataset-detailed.csv",
        'dataset4': "C:/Users/ruxin/Documents/ruxin/FYP/Data/Top 100 most Streamed - Sheet1.csv"
    }

    print("\nLoading datasets with encoding detection...")

    datasets = {}
    for name, path in file_paths.items():
        print(f"\nLoading {name}...")
        try:
            datasets[name] = read_csv_with_encoding(path)
        except Exception as e:
            print(f"   Error loading {name}: {e}")
            datasets[name] = None

    df_cleaned_list = []

    if datasets['dataset1'] is not None:
        df1_clean = clean_dataset1(datasets['dataset1'])
        if len(df1_clean) > 0:
            df_cleaned_list.append(df1_clean)

    if datasets['dataset2'] is not None:
        df2_clean = clean_dataset2(datasets['dataset2'])
        if len(df2_clean) > 0:
            df_cleaned_list.append(df2_clean)

    if datasets['dataset3'] is not None:
        df3_clean = clean_dataset3(datasets['dataset3'])
        if len(df3_clean) > 0:
            df_cleaned_list.append(df3_clean)

    if datasets['dataset4'] is not None:
        df4_clean = clean_dataset4(datasets['dataset4'])
        if len(df4_clean) > 0:
            df_cleaned_list.append(df4_clean)

    if not df_cleaned_list:
        print("\nNo datasets loaded successfully!")
        return

    print("\n" + "=" * 60)
    print("MERGING DATASETS")
    print("=" * 60)

    for i, df in enumerate(df_cleaned_list):
        for col in FEATURES + ['popularity_class', 'popularity', 'source', 'genre']:
            if col not in df.columns:
                if col in ('source', 'genre'):
                    df[col] = 'unknown'
                elif col in ('popularity', 'popularity_class'):
                    df[col] = np.nan
                else:
                    df[col] = 0

    df_merged = pd.concat(df_cleaned_list, ignore_index=True)

    df_merged = df_merged.drop_duplicates(subset=FEATURES)

    print(f"\nMerged dataset shape: {df_merged.shape}")

    print("\n" + "=" * 60)
    print("FINAL DATASET STATISTICS")
    print("=" * 60)

    print(f"\nTotal songs: {len(df_merged):,}")

    print("\nPopularity Class Distribution (includes NaN where popularity unknown):")
    class_counts = df_merged['popularity_class'].value_counts(dropna=False).sort_index()
    for cls, count in class_counts.items():
        if pd.isna(cls):
            label = "Unknown / no popularity data"
        else:
            label = {0: "Low (0-33)", 1: "Medium (34-66)", 2: "High (67-100)"}.get(cls, f"Class {cls}")
        pct = count / len(df_merged) * 100
        bar = "#" * int(pct / 2)
        print(f"  {label}: {count:6,} ({pct:5.1f}%) {bar}")

    n_with_pop = df_merged['popularity'].notna().sum()
    print(f"\nRows with continuous popularity score (usable for regression): "
          f"{n_with_pop:,} ({n_with_pop/len(df_merged)*100:.1f}%)")

    print("\nData Sources:")
    if 'source' in df_merged.columns:
        print(df_merged['source'].value_counts())

    print("\nGenre Distribution (After Categorization):")
    genre_counts = df_merged['genre'].value_counts().head(20)
    for genre, count in genre_counts.items():
        pct = count / len(df_merged) * 100
        bar = "#" * int(pct / 2)
        print(f"  {genre}: {count:6,} ({pct:5.1f}%) {bar}")

    unknown_count = (df_merged['genre'] == 'unknown').sum()
    if unknown_count > 0:
        print(f"\n  Unknown genre: {unknown_count:,} ({unknown_count/len(df_merged)*100:.1f}%)")

    output_path = "C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_merged_cleaned.csv"
    df_merged.to_csv(output_path, index=False, encoding='utf-8')
    print(f"\nFinal dataset saved to: {output_path}")

    features_path = "C:/Users/ruxin/Documents/ruxin/FYP/Data/features.txt"
    with open(features_path, 'w') as f:
        for feat in FEATURES:
            f.write(f"{feat}\n")
    print(f"Features list saved to: {features_path}")

    print("\nSample data (first 5 rows):")
    print(df_merged[FEATURES + ['popularity', 'popularity_class', 'genre']].head())

    print("\n" + "=" * 60)
    print("ALL DONE!")
    print("=" * 60)

    return df_merged


if __name__ == "__main__":
    df_final = main()