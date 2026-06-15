import pandas as pd

def recommend_feature_changes(features_df, explanation):
    recommendations = []
    
    if not features_df.empty:
        current = features_df.iloc[0]

        negative_impacts = [e for e in explanation if e.get("direction") == "negative"]
        negative_impacts.sort(key=lambda x: x.get("impact", 0))
        
        for item in negative_impacts:
            feature = item["feature"]
            
            try:
                current_val = float(current.get(feature, 0.5))
            except (ValueError, TypeError):
                current_val = 0.5
            
            suggestion = get_intelligent_suggestion(feature, current_val)
            
            if suggestion is not None:
                recommendations.append(suggestion)
    
    if not recommendations:
        recommendations.append({
            "message": " Your audio features look great!",
            "action": "Try adjusting different features to see how popularity changes."
        })
    
    return recommendations

def get_intelligent_suggestion(feature, current_val):
    
    optimal_ranges = {
        "danceability": (0.6, 0.85),
        "energy": (0.6, 0.85),
        "tempo": (100.0, 140.0),
        "acousticness": (0.05, 0.35),
        "valence": (0.5, 0.85),
        "loudness": (-8.0, -4.0),
        "instrumentalness": (0.0, 0.1),
        "duration_ms": (180000.0, 270000.0),
        "speechiness": (0.03, 0.1),
        "liveness": (0.05, 0.2),
    }
    
    feature_names = {
        "danceability": "💃 Danceability",
        "energy": "⚡ Energy",
        "tempo": "⏱️ Tempo",
        "acousticness": "🎸 Acousticness",
        "valence": "😊 Valence (Positivity)",
        "loudness": "🔊 Loudness",
        "instrumentalness": "🎹 Instrumentalness",
        "duration_ms": "📏 Duration",
        "speechiness": "🗣️ Speechiness",
        "liveness": "🎤 Liveness",
        "explicit": "🔞 Explicit"
    }

    if feature == "explicit":
        if current_val == 0:
            return {
                "message": " Adding explicit content might increase appeal for some audiences",
                "action": "Consider creating both explicit and clean versions"
            }
        else:
            return {
                "message": " Clean versions often have broader reach",
                "action": "Consider releasing a clean version alongside explicit"
            }

    if feature in optimal_ranges:
        min_val, max_val = optimal_ranges[feature]

        if min_val <= current_val <= max_val:
            return None  

        if feature == "duration_ms":
            if current_val < min_val:
                return {
                    "message": " Songs that are too short may not engage listeners enough",
                    "action": f"Increase Duration from {current_val/1000:.0f}s to at least {min_val/1000:.0f}s"
                }
            elif current_val > max_val:
                return {
                    "message": " Very long songs may lose listener attention",
                    "action": f"Reduce Duration from {current_val/1000:.0f}s to below {max_val/1000:.0f}s"
                }

        if current_val < min_val:
            diff = min_val - current_val
            return {
                "message": f" Increasing {feature_names.get(feature, feature)} could improve popularity",
                "action": f"Increase from {current_val:.2f} to at least {min_val:.2f} (+{diff:.2f})"
            }

        if current_val > max_val:
            diff = current_val - max_val
            return {
                "message": f" Decreasing {feature_names.get(feature, feature)} could improve popularity",
                "action": f"Decrease from {current_val:.2f} to below {max_val:.2f} (-{diff:.2f})"
            }

    return None