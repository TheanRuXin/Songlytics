import joblib
import numpy as np
import shap

MODEL_PATH = "machine_learning/songlytics_regression_rf.pkl"

model_data = joblib.load(MODEL_PATH)

pipeline = model_data["model"]
FEATURES = model_data["features"]

preprocessor = pipeline.named_steps["preprocessor"]
random_forest = pipeline.named_steps["random_forest"]

explainer = shap.TreeExplainer(random_forest)

def clean_feature_name(name):
    name = str(name)

    if name.startswith("genre__track_genre_"):
        return "track_genre"

    if name.startswith("remainder__"):
        return name.replace("remainder__", "", 1)

    return name

def explain(features_df):
    missing = [
        feature
        for feature in FEATURES
        if feature not in features_df.columns
    ]

    if missing:
        raise ValueError(
            "Missing required features: "
            + ", ".join(missing)
        )

    input_df = features_df[FEATURES].copy()

    transformed = preprocessor.transform(input_df)

    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()

    transformed = np.asarray(
        transformed,
        dtype=float
    )

    feature_names = (
        preprocessor
        .get_feature_names_out()
        .tolist()
    )

    shap_values = explainer.shap_values(
        transformed,
        approximate=True,
        check_additivity=False
    )

    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    shap_values = np.asarray(shap_values)

    if shap_values.ndim == 1:
        impacts = shap_values
    else:
        impacts = shap_values[0]

    grouped = {}

    for feature_name, impact in zip(
        feature_names,
        impacts
    ):
        clean_name = clean_feature_name(
            feature_name
        )

        grouped[clean_name] = (
            grouped.get(clean_name, 0.0)
            + float(impact)
        )

    explanation = []

    for feature, impact in grouped.items():
        explanation.append({
            "feature": feature,
            "impact": float(impact)
        })

    explanation.sort(
        key=lambda item: abs(item["impact"]),
        reverse=True
    )

    return explanation

def get_base_value():
    expected_value = explainer.expected_value

    if isinstance(
        expected_value,
        (list, tuple, np.ndarray)
    ):
        expected_value = np.asarray(
            expected_value
        ).flatten()[0]

    return float(expected_value)

def explain_with_details(features_df):
    explanation = explain(features_df)

    prediction = float(
        pipeline.predict(
            features_df[FEATURES]
        )[0]
    )

    return {
        "prediction": prediction,
        "base_value": get_base_value(),
        "features": explanation
    }