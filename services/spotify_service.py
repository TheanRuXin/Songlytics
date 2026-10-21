import os
import time
import requests
import pandas as pd

from dotenv import load_dotenv


load_dotenv(override=True)


SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_MARKET = os.getenv("SPOTIFY_MARKET", "MY")

DATASET_PATH = os.getenv(
    "SPOTIFY_DATASET_PATH",
    "C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_cleaned.csv"
)

TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1"


AUDIO_FEATURES = [
    "duration_ms",
    "explicit",
    "danceability",
    "energy",
    "key",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "time_signature"
]


class SpotifyService:

    def __init__(self):
        self.access_token = None
        self.token_expiry = 0
        self.dataset = None

    def _validate_credentials(self):
        if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
            raise RuntimeError(
                "Spotify credentials are missing. "
                "Check SPOTIFY_CLIENT_ID and "
                "SPOTIFY_CLIENT_SECRET in your .env file."
            )

    def _get_access_token(self):
        self._validate_credentials()

        if (
            self.access_token
            and time.time() < self.token_expiry
        ):
            return self.access_token

        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials"
            },
            auth=(
                SPOTIFY_CLIENT_ID,
                SPOTIFY_CLIENT_SECRET
            ),
            timeout=10
        )

        if response.status_code != 200:
            raise RuntimeError(
                "Unable to authenticate with Spotify API."
            )

        data = response.json()

        self.access_token = data["access_token"]

        expires_in = int(
            data.get("expires_in", 3600)
        )

        self.token_expiry = (
            time.time()
            + expires_in
            - 60
        )

        return self.access_token

    def _request(
        self,
        endpoint,
        params=None,
        retry=True
    ):
        token = self._get_access_token()

        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            headers={
                "Authorization": f"Bearer {token}"
            },
            params=params,
            timeout=10
        )

        if response.status_code == 401 and retry:
            self.access_token = None
            self.token_expiry = 0

            return self._request(
                endpoint,
                params=params,
                retry=False
            )

        if response.status_code == 429:
            retry_after = int(
                response.headers.get(
                    "Retry-After",
                    1
                )
            )

            if retry and retry_after <= 3:
                time.sleep(retry_after)

                return self._request(
                    endpoint,
                    params=params,
                    retry=False
                )

            raise RuntimeError(
                "Spotify rate limit reached. "
                "Please try again later."
            )

        if response.status_code == 403:
            raise RuntimeError(
                "Spotify denied this API request."
            )

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            raise RuntimeError(
                f"Spotify API error: "
                f"{response.status_code}"
            )

        return response.json()

    def _load_dataset(self):
        if self.dataset is not None:
            return self.dataset

        if not os.path.exists(DATASET_PATH):
            raise FileNotFoundError(
                f"Dataset not found: {DATASET_PATH}"
            )

        df = pd.read_csv(DATASET_PATH)

        required_columns = [
            "track_id",
            "track_name",
            "artists",
            "track_genre"
        ] + AUDIO_FEATURES

        missing = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                "Dataset is missing columns: "
                + ", ".join(missing)
            )

        df["track_id"] = (
            df["track_id"]
            .astype(str)
            .str.strip()
        )

        df["track_name"] = (
            df["track_name"]
            .astype(str)
            .str.strip()
        )

        df["artists"] = (
            df["artists"]
            .astype(str)
            .str.strip()
        )

        self.dataset = df

        return self.dataset

    def search_song(
        self,
        query,
        limit=10
    ):
        query = str(query).strip()

        if not query:
            return []

        limit = max(
            1,
            min(int(limit), 10)
        )

        try:
            data = self._request(
                "/search",
                params={
                    "q": query,
                    "type": "track",
                    "limit": limit,
                    "market": SPOTIFY_MARKET
                }
            )

            if not data:
                return []

            tracks = (
                data
                .get("tracks", {})
                .get("items", [])
            )

            results = []

            for track in tracks:
                artists = track.get(
                    "artists",
                    []
                )

                artist_names = ", ".join(
                    artist.get(
                        "name",
                        ""
                    )
                    for artist in artists
                )

                album = track.get(
                    "album",
                    {}
                )

                images = album.get(
                    "images",
                    []
                )

                image_url = (
                    images[0].get("url")
                    if images
                    else None
                )

                external_urls = track.get(
                    "external_urls",
                    {}
                )

                results.append({
                    "track_id":
                        track.get("id"),

                    "song":
                        track.get(
                            "name",
                            "Unknown Song"
                        ),

                    "artist":
                        artist_names
                        or "Unknown Artist",

                    "album_name":
                        album.get(
                            "name",
                            "Unknown Album"
                        ),

                    "duration_ms":
                        track.get(
                            "duration_ms"
                        ),

                    "explicit":
                        track.get(
                            "explicit",
                            False
                        ),

                    "popularity":
                        track.get(
                            "popularity"
                        ),

                    "spotify_url":
                        external_urls.get(
                            "spotify"
                        ),

                    "image_url":
                        image_url
                })

            return results

        except Exception as e:
            print(
                "Spotify search error:",
                e
            )

            return []

    def get_track(
        self,
        track_id
    ):
        track_id = str(
            track_id
        ).strip()

        if not track_id:
            return None

        try:
            return self._request(
                f"/tracks/{track_id}",
                params={
                    "market":
                        SPOTIFY_MARKET
                }
            )

        except Exception as e:
            print(
                "Spotify track error:",
                e
            )

            return None

    def get_audio_features(
        self,
        track_id,
        song_name=None,
        artist_name=None
    ):
        track_id = str(
            track_id
        ).strip()

        try:
            df = self._load_dataset()

            matching = df[
                df["track_id"]
                == track_id
            ]

            if (
                matching.empty
                and song_name
                and artist_name
            ):
                song_normalized = (
                    str(song_name)
                    .strip()
                    .lower()
                )

                artist_names = [
                    artist.strip().lower()
                    for artist
                    in str(artist_name).split(",")
                    if artist.strip()
                ]

                song_mask = (
                    df["track_name"]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    == song_normalized
                )

                artist_column = (
                    df["artists"]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                )

                artist_mask = pd.Series(
                    False,
                    index=df.index
                )

                for artist in artist_names:
                    artist_mask = (
                        artist_mask
                        | artist_column.str.contains(
                            artist,
                            regex=False,
                            na=False
                        )
                    )

                matching = df[
                    song_mask
                    & artist_mask
                ]

            if matching.empty:
                return None

            row = matching.iloc[0]

            features = {}

            for feature in AUDIO_FEATURES:
                value = row[feature]

                if pd.isna(value):
                    return None

                if feature == "explicit":
                    features[feature] = int(
                        bool(value)
                    )

                elif feature in [
                    "key",
                    "mode",
                    "time_signature",
                    "duration_ms"
                ]:
                    features[feature] = int(
                        value
                    )

                else:
                    features[feature] = float(
                        value
                    )

            genre = row.get(
                "track_genre"
            )

            if pd.isna(genre):
                return None

            features[
                "track_genre"
            ] = str(
                genre
            ).strip()

            return features

        except Exception as e:
            print(
                "Local audio feature error:",
                e
            )

            return None

    def search_supported_songs(
        self,
        query,
        limit=10
    ):
        spotify_results = self.search_song(
            query,
            limit=limit
        )

        supported = []

        for track in spotify_results:
            features = self.get_audio_features(
                track_id=track["track_id"],
                song_name=track["song"],
                artist_name=track["artist"]
            )

            if features:
                result = track.copy()

                result[
                    "features"
                ] = features

                supported.append(
                    result
                )

        return supported

    def find_dataset_track(
        self,
        song_name,
        artist_name
    ):
        try:
            df = self._load_dataset()

            song_name = str(
                song_name
            ).strip().lower()

            artist_name = str(
                artist_name
            ).strip().lower()

            matching = df[
                (
                    df["track_name"]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    == song_name
                )
                &
                (
                    df["artists"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        artist_name,
                        regex=False,
                        na=False
                    )
                )
            ]

            if matching.empty:
                return None

            row = matching.iloc[0]

            return {
                "track_id":
                    row["track_id"],

                "track_name":
                    row["track_name"],

                "artists":
                    row["artists"],

                "track_genre":
                    row["track_genre"]
            }

        except Exception as e:
            print(
                "Dataset track lookup error:",
                e
            )

            return None

    def is_track_in_dataset(
        self,
        track_id
    ):
        try:
            df = self._load_dataset()

            track_id = str(
                track_id
            ).strip()

            return (
                df["track_id"]
                == track_id
            ).any()

        except Exception:
            return False


spotify_service = SpotifyService()