import joblib
import numpy as np

MODEL_PATH = "machine_learning/songlytics_regression_rf.pkl"

model_data = joblib.load(MODEL_PATH)

model = model_data["model"]
FEATURES = model_data["features"]

MAE = model_data.get("mae", 0)
RMSE = model_data.get("rmse", 0)
R2 = model_data.get("r2", 0)


def get_label(score):
    if score >= 60:
        return "High Popularity"
    elif score >= 40:
        return "Medium Popularity"
    else:
        return "Low Popularity"


def get_genres():
    encoder = model.named_steps["preprocessor"].named_transformers_["genre"]
    return encoder.categories_[0].tolist()


def predict(features_df):
    missing_features = [
        feature
        for feature in FEATURES
        if feature not in features_df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing required features: {', '.join(missing_features)}"
        )

    input_df = features_df[FEATURES].copy()

    score = float(model.predict(input_df)[0])
    score = float(np.clip(score, 0, 100))

    return {
        "score": score,
        "label": get_label(score),
        "mae": float(MAE),
        "rmse": float(RMSE),
        "r2": float(R2)
    }