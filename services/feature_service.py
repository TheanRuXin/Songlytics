import pandas as pd
from services.spotify_service import get_track_features

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

def extract_features_from_spotify(track_id):

    f = get_track_features(track_id)

    df = pd.DataFrame([f])

    df = df[FEATURES]

    return df