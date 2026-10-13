import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor

df = pd.read_csv("C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_cleaned.csv")

audio_features = [
    "duration_ms", "explicit", "danceability", "energy", "key", "loudness",
    "mode", "speechiness", "acousticness", "instrumentalness", "liveness",
    "valence", "tempo", "time_signature"
]

features = audio_features + ["track_genre"]
X = df[features]
y = df["popularity"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

preprocessor = ColumnTransformer(
    [("genre", OneHotEncoder(handle_unknown="ignore"), ["track_genre"])],
    remainder="passthrough"
)

model = Pipeline([
    ("preprocessor", preprocessor),
    ("random_forest", RandomForestRegressor(
        n_estimators=500, min_samples_split=5, min_samples_leaf=1,
        max_features=0.8, max_depth=None, random_state=42, n_jobs=-1
    ))
])

print("Training model...")
model.fit(X_train, y_train)

sample = X_test.sample(n=50, random_state=42)
sample_y = y_test.loc[sample.index]

X_transformed = model.named_steps["preprocessor"].transform(sample)
if hasattr(X_transformed, "toarray"):
    X_transformed = X_transformed.toarray()

rf = model.named_steps["random_forest"]
feature_names = model.named_steps["preprocessor"].get_feature_names_out()

clean_names = [
    name.replace("genre__track_genre_", "genre_")
    if name.startswith("genre__track_genre_")
    else name.replace("remainder__", "")
    for name in feature_names
]

print("Calculating SHAP values...")

explainer = shap.TreeExplainer(rf)
shap_values = explainer.shap_values(
    X_transformed,
    approximate=True,
    check_additivity=False
)

print("SHAP completed.")

importance = np.abs(shap_values).mean(axis=0)

groups = [
    "track_genre" if name.startswith("genre_") else name
    for name in clean_names
]

shap_df = pd.DataFrame({
    "Feature": groups,
    "Importance": importance
})

shap_grouped = (
    shap_df.groupby("Feature", as_index=False)["Importance"]
    .sum()
    .sort_values("Importance", ascending=False)
    .reset_index(drop=True)
)

shap_grouped.index += 1
shap_grouped.index.name = "Rank"

print("\nSHAP Feature Importance")
print(shap_grouped.round(4))

plot_df = shap_grouped.sort_values("Importance")

plt.figure(figsize=(10, 8))
plt.barh(plot_df["Feature"], plot_df["Importance"])
plt.xlabel("Mean Absolute SHAP Value")
plt.ylabel("Feature")
plt.title("SHAP Feature Importance")
plt.tight_layout()
plt.savefig("shap_feature_importance.png", dpi=300)
plt.show()

audio_indices = [
    i for i, name in enumerate(clean_names)
    if name in audio_features
]

shap.summary_plot(
    shap_values[:, audio_indices],
    X_transformed[:, audio_indices],
    feature_names=[clean_names[i] for i in audio_indices],
    show=False
)

plt.tight_layout()
plt.savefig("shap_audio_summary.png", dpi=300, bbox_inches="tight")
plt.show()

song_index = 0

print("\nSingle Song")
print("Actual Popularity:", sample_y.iloc[song_index])
print("Predicted Popularity:", round(model.predict(sample.iloc[[song_index]])[0], 2))
print("Genre:", sample.iloc[song_index]["track_genre"])

song_explanation = shap.Explanation(
    values=shap_values[song_index],
    base_values=np.asarray(explainer.expected_value).flatten()[0],
    data=X_transformed[song_index],
    feature_names=clean_names
)

shap.plots.waterfall(song_explanation, max_display=12, show=False)
plt.tight_layout()
plt.savefig("shap_single_song.png", dpi=300, bbox_inches="tight")
plt.show()

shap_grouped.to_csv("shap_feature_importance.csv")