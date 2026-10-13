import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

df = pd.read_csv("C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_cleaned.csv")

print("Dataset Shape:", df.shape)
print("Number of Genres:", df["track_genre"].nunique())

audio_features = ["duration_ms","explicit","danceability","energy","key","loudness","mode","speechiness","acousticness","instrumentalness","liveness", "valence", "tempo","time_signature"]

target = "popularity"

X_audio = df[audio_features]
y = df[target]

genre_features = audio_features + ["track_genre"]

X_genre = df[genre_features]

train_indices, test_indices = train_test_split(df.index,test_size=0.2,random_state=42)

# Audio only
X_audio_train = X_audio.loc[train_indices]
X_audio_test = X_audio.loc[test_indices]

# Audio + Genre
X_genre_train = X_genre.loc[train_indices]
X_genre_test = X_genre.loc[test_indices]

# Same target
y_train = y.loc[train_indices]
y_test = y.loc[test_indices]

print("\nTrain / Test Split")
print("Training:", len(train_indices))
print("Testing :", len(test_indices))

rf_parameters = {
    "n_estimators": 500,
    "min_samples_split": 5,
    "min_samples_leaf": 1,
    "max_features": 0.8,
    "max_depth": None,
    "random_state": 42,
    "n_jobs": -1
}

print("TRAINING AUDIO-ONLY MODEL")

audio_model = RandomForestRegressor(**rf_parameters)
audio_model.fit(X_audio_train,y_train)

audio_pred = audio_model.predict(X_audio_test)

audio_mae = mean_absolute_error(y_test,audio_pred)

audio_rmse = np.sqrt(mean_squared_error(y_test,audio_pred))

audio_r2 = r2_score(y_test,audio_pred)

# Audio features remain unchanged.
# track_genre will be converted using One-Hot Encoding.
preprocessor = ColumnTransformer(
    transformers=[("genre",OneHotEncoder(handle_unknown="ignore"),["track_genre"])],remainder="passthrough")

genre_model = Pipeline([
    (
        "preprocessor",
        preprocessor
    ),
    (
        "random_forest",
        RandomForestRegressor(
            **rf_parameters
        )
    )
])

print("TRAINING AUDIO + GENRE MODEL")

genre_model.fit(
    X_genre_train,
    y_train
)

genre_pred = genre_model.predict(
    X_genre_test
)

genre_mae = mean_absolute_error(
    y_test,
    genre_pred
)

genre_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        genre_pred
    )
)

genre_r2 = r2_score(
    y_test,
    genre_pred
)
comparison = pd.DataFrame({
    "Model": [
        "Audio Features Only",
        "Audio Features + Genre"
    ],

    "MAE": [
        audio_mae,
        genre_mae
    ],

    "RMSE": [
        audio_rmse,
        genre_rmse
    ],

    "R2": [
        audio_r2,
        genre_r2
    ]
})

print("AUDIO-ONLY VS AUDIO + GENRE")

print(
    comparison
    .round(4)
    .to_string(index=False)
)


def calculate_range_mae(actual, predicted):

    evaluation = pd.DataFrame({
        "actual": actual.to_numpy(),
        "predicted": predicted
    })

    evaluation["Absolute Error"] = np.abs(
        evaluation["actual"]
        - evaluation["predicted"]
    )

    evaluation["Popularity Range"] = pd.cut(
        evaluation["actual"],
        bins=[
            -1,
            20,
            40,
            60,
            80,
            100
        ],
        labels=[
            "0-20",
            "21-40",
            "41-60",
            "61-80",
            "81-100"
        ]
    )

    return (
        evaluation
        .groupby(
            "Popularity Range",
            observed=True
        )["Absolute Error"]
        .mean()
    )


audio_range_mae = calculate_range_mae(
    y_test,
    audio_pred
)

genre_range_mae = calculate_range_mae(
    y_test,
    genre_pred
)


range_comparison = pd.DataFrame({
    "Audio Only MAE":
        audio_range_mae,

    "Audio + Genre MAE":
        genre_range_mae
})


range_comparison["Improvement"] = (
    range_comparison["Audio Only MAE"]
    - range_comparison["Audio + Genre MAE"]
)


print("MAE BY POPULARITY RANGE")

print(
    range_comparison.round(4)
)



comparison.to_csv(
    "genre_model_comparison.csv",
    index=False
)

range_comparison.to_csv(
    "genre_range_comparison.csv"
)

print("\nResults saved:")
print("genre_model_comparison.csv")
print("genre_range_comparison.csv")