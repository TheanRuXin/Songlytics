import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import os

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

df = pd.read_csv(
    "C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_cleaned.csv"
)

features = [
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
    "time_signature",
    "track_genre"
]

X = df[features]

y = df["popularity"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("FINAL MODEL EVALUATION")
print("\nTraining Samples:", len(X_train))
print("Testing Samples :", len(X_test))

preprocessor = ColumnTransformer(
    transformers=[
        (
            "genre",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            ["track_genre"]
        )
    ],
    remainder="passthrough"
)

final_model = Pipeline([
    (
        "preprocessor",
        preprocessor
    ),

    (
        "random_forest",
        RandomForestRegressor(
            n_estimators=500,
            min_samples_split=5,
            min_samples_leaf=1,
            max_features=0.8,
            max_depth=None,
            random_state=42,
            n_jobs=-1
        )
    )
])

print("\nTraining final model...")

final_model.fit(X_train,y_train)

train_pred = final_model.predict(X_train)
test_pred = final_model.predict(X_test)

train_mae = mean_absolute_error(y_train,train_pred)
train_rmse = np.sqrt(mean_squared_error(y_train,train_pred))
train_r2 = r2_score(y_train,train_pred)

test_mae = mean_absolute_error(y_test,test_pred)
test_rmse = np.sqrt(mean_squared_error(y_test,test_pred))
test_r2 = r2_score(y_test,test_pred)

print("FINAL PERFORMANCE")

print("\nTraining Performance")

print(
    "Train MAE :",
    round(train_mae, 4)
)

print(
    "Train RMSE:",
    round(train_rmse, 4)
)

print(
    "Train R²  :",
    round(train_r2, 4)
)

print("\nTesting Performance")

print(
    "Test MAE :",
    round(test_mae, 4)
)

print(
    "Test RMSE:",
    round(test_rmse, 4)
)

print(
    "Test R²  :",
    round(test_r2, 4)
)

plt.figure(figsize=(8, 6))

plt.scatter(
    y_test,
    test_pred,
    alpha=0.25
)

plt.plot(
    [0, 100],
    [0, 100],
    linestyle="--"
)

plt.xlabel(
    "Actual Popularity"
)

plt.ylabel(
    "Predicted Popularity"
)

plt.title(
    "Actual vs Predicted Popularity"
)

plt.tight_layout()

plt.savefig(
    "final_actual_vs_predicted.png",
    dpi=300
)

plt.show()

residuals = (
    y_test.to_numpy()
    - test_pred
)

plt.figure(figsize=(8, 6))

plt.scatter(
    test_pred,
    residuals,
    alpha=0.25
)

plt.axhline(
    y=0,
    linestyle="--"
)

plt.xlabel(
    "Predicted Popularity"
)

plt.ylabel(
    "Residual (Actual - Predicted)"
)

plt.title(
    "Residual Plot"
)

plt.tight_layout()

plt.savefig(
    "final_residual_plot.png",
    dpi=300
)

plt.show()

plt.figure(figsize=(8, 6))

plt.hist(
    residuals,
    bins=40
)

plt.axvline(
    x=0,
    linestyle="--"
)

plt.xlabel(
    "Residual"
)

plt.ylabel(
    "Frequency"
)

plt.title(
    "Distribution of Residuals"
)

plt.tight_layout()

plt.savefig(
    "final_residual_distribution.png",
    dpi=300
)

plt.show()

evaluation_df = pd.DataFrame({
    "actual":
        y_test.to_numpy(),

    "predicted":
        test_pred
})


evaluation_df["absolute_error"] = np.abs(
    evaluation_df["actual"]
    - evaluation_df["predicted"]
)


evaluation_df["residual"] = (
    evaluation_df["actual"]
    - evaluation_df["predicted"]
)
evaluation_df["popularity_range"] = pd.cut(
    evaluation_df["actual"],

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

range_mae = (
    evaluation_df
    .groupby(
        "popularity_range",
        observed=True
    )["absolute_error"]
    .mean()
)

print("MAE BY POPULARITY RANGE")

print(
    range_mae.round(4)
)

range_count = (
    evaluation_df
    .groupby(
        "popularity_range",
        observed=True
    )
    .size()
)

print("TEST SAMPLE COUNT BY POPULARITY RANGE")

print(
    range_count
)

range_prediction = (
    evaluation_df
    .groupby(
        "popularity_range",
        observed=True
    )
    .agg(
        Actual_Mean=("actual", "mean"),
        Predicted_Mean=("predicted", "mean"),
        MAE=("absolute_error", "mean")
    )
)

print("PREDICTION BY POPULARITY RANGE")

print(
    range_prediction.round(4)
)

overall_results = pd.DataFrame({
    "Metric": [
        "MAE",
        "RMSE",
        "R2"
    ],

    "Training": [
        train_mae,
        train_rmse,
        train_r2
    ],

    "Testing": [
        test_mae,
        test_rmse,
        test_r2
    ]
})

overall_results.to_csv(
    "final_model_metrics.csv",
    index=False
)


range_prediction.to_csv(
    "final_range_evaluation.csv"
)


evaluation_df.to_csv(
    "final_predictions.csv",
    index=False
)

print("FILES SAVED")

print("final_model_metrics.csv")
print("final_range_evaluation.csv")
print("final_predictions.csv")

print("final_actual_vs_predicted.png")
print("final_residual_plot.png")
print("final_residual_distribution.png")

os.makedirs("saved_models", exist_ok=True)

model_data = {
    "model": final_model,
    "features": features,
    "mae": test_mae,
    "rmse": test_rmse,
    "r2": test_r2
}

joblib.dump(model_data, "machine_learning/songlytics_regression_rf.pkl")