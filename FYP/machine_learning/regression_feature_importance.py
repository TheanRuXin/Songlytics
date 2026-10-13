import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

df = pd.read_csv("C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_cleaned.csv")

features = [
    "duration_ms", "explicit", "danceability", "energy", "key", "loudness",
    "mode", "speechiness", "acousticness", "instrumentalness", "liveness",
    "valence", "tempo", "time_signature", "track_genre"
]

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
        n_estimators=500,
        min_samples_split=5,
        min_samples_leaf=1,
        max_features=0.8,
        max_depth=None,
        random_state=42,
        n_jobs=-1
    ))
])

model.fit(X_train, y_train)
pred = model.predict(X_test)

mae = mean_absolute_error(y_test, pred)
rmse = np.sqrt(mean_squared_error(y_test, pred))
r2 = r2_score(y_test, pred)

print("MAE:", round(mae, 4))
print("RMSE:", round(rmse, 4))
print("R2 Score:", round(r2, 4))

result = permutation_importance(
    model,
    X_test,
    y_test,
    scoring="neg_mean_absolute_error",
    n_repeats=5,
    random_state=42,
    n_jobs=-1
)

importance_df = pd.DataFrame({
    "Feature": features,
    "Importance": result.importances_mean,
    "Std": result.importances_std
}).sort_values("Importance", ascending=False).reset_index(drop=True)

importance_df.index = importance_df.index + 1
importance_df.index.name = "Rank"

print("\nFeature Importance")
print(importance_df.round(4))

plot_df = importance_df.sort_values("Importance")

plt.figure(figsize=(10, 8))
plt.barh(plot_df["Feature"], plot_df["Importance"], xerr=plot_df["Std"])
plt.xlabel("Permutation Importance (Increase in MAE)")
plt.ylabel("Feature")
plt.title("Permutation Feature Importance")
plt.tight_layout()
plt.savefig("permutation_feature_importance.png", dpi=300)
plt.show()

importance_df.to_csv("permutation_feature_importance.csv")