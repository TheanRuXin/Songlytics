import pandas as pd

from services.prediction_service import predict, FEATURES


FEATURE_RANGES = {
    "danceability": (0.0, 1.0),
    "energy": (0.0, 1.0),
    "loudness": (-60.0, 0.0),
    "speechiness": (0.0, 1.0),
    "acousticness": (0.0, 1.0),
    "instrumentalness": (0.0, 1.0),
    "liveness": (0.0, 1.0),
    "valence": (0.0, 1.0),
    "tempo": (40.0, 220.0)
}


FEATURE_LABELS = {
    "danceability": "Danceability",
    "energy": "Energy",
    "loudness": "Loudness",
    "speechiness": "Speechiness",
    "acousticness": "Acousticness",
    "instrumentalness": "Instrumentalness",
    "liveness": "Liveness",
    "valence": "Valence",
    "tempo": "Tempo"
}


def clamp(value, minimum, maximum):
    return max(
        minimum,
        min(maximum, value)
    )


def get_step(feature):
    minimum, maximum = FEATURE_RANGES[feature]

    return (maximum - minimum) * 0.10


def format_value(feature, value):
    if feature == "tempo":
        return f"{value:.0f} BPM"

    if feature == "loudness":
        return f"{value:.1f} dB"

    return f"{value:.3f}"


def test_feature_change(
    base_df,
    feature,
    new_value
):
    test_df = base_df.copy()

    test_df.loc[
        test_df.index[0],
        feature
    ] = new_value

    result = predict(test_df)

    return result["score"]


def recommend_feature_changes(
    features_df,
    explanation=None,
    max_suggestions=3
):
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

    base_df = (
        features_df[FEATURES]
        .copy()
    )

    base_score = predict(
        base_df
    )["score"]

    candidates = []

    for feature in FEATURE_RANGES:
        current_value = float(
            base_df.iloc[0][feature]
        )

        minimum, maximum = (
            FEATURE_RANGES[feature]
        )

        step = get_step(feature)

        higher_value = clamp(
            current_value + step,
            minimum,
            maximum
        )

        lower_value = clamp(
            current_value - step,
            minimum,
            maximum
        )

        test_values = []

        if higher_value != current_value:
            test_values.append(
                higher_value
            )

        if lower_value != current_value:
            test_values.append(
                lower_value
            )

        best_score = base_score
        best_value = current_value

        for new_value in test_values:
            new_score = test_feature_change(
                base_df,
                feature,
                new_value
            )

            if new_score > best_score:
                best_score = new_score
                best_value = new_value

        improvement = (
            best_score
            - base_score
        )

        if improvement <= 0.5:
            continue

        direction = (
            "increase"
            if best_value > current_value
            else "decrease"
        )

        label = FEATURE_LABELS.get(
            feature,
            feature
        )

        candidates.append({
            "feature": feature,
            "current_value": current_value,
            "suggested_value": best_value,
            "original_score": base_score,
            "predicted_score": best_score,
            "improvement": improvement,
            "message": (
                f"The model estimates that a small "
                f"{direction} in {label} may increase "
                f"the predicted popularity score by "
                f"approximately {improvement:.1f} points."
            ),
            "action": (
                f"{label}: "
                f"{format_value(feature, current_value)}"
                f" → "
                f"{format_value(feature, best_value)}"
            )
        })

    candidates.sort(
        key=lambda item: item["improvement"],
        reverse=True
    )

    return candidates[
        :max_suggestions
    ]