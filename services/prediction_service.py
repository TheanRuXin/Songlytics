# prediction_service.py
import numpy as np
import joblib
import pandas as pd

# 加载回归模型
saved = joblib.load("models/music_model_xgb_regressor.pkl")

model = saved["model"]
FEATURES = saved["features"]
scaler = saved.get("scaler", None)

# 回归模型的阈值（将分数转换为类别）
LOW_THRESHOLD = 34
HIGH_THRESHOLD = 67

label_map = {
    0: "Low Popularity",
    1: "Medium Popularity",
    2: "High Popularity"
}

short_label_map = {
    0: "Low",
    1: "Medium",
    2: "High"
}

def predict(features_df):
    """使用回归模型预测"""
    features_df = features_df[FEATURES].astype(float)
    
    if scaler is not None:
        features_scaled = scaler.transform(features_df)
        features_df = pd.DataFrame(features_scaled, columns=FEATURES)
    
    # 回归模型输出连续分数（没有 predict_proba）
    score = model.predict(features_df)[0]
    
    # 将分数转换为类别
    if score >= HIGH_THRESHOLD:
        pred_class = 2
    elif score >= LOW_THRESHOLD:
        pred_class = 1
    else:
        pred_class = 0
    
    # 计算置信度（基于与阈值的距离）
    if pred_class == 2:
        confidence_score = min((score - HIGH_THRESHOLD) / 33, 1.0)
    elif pred_class == 1:
        confidence_score = min((score - LOW_THRESHOLD) / 33, 1.0)
    else:
        confidence_score = min((LOW_THRESHOLD - score) / 34, 1.0)
    
    if confidence_score > 0.7:
        confidence = "High"
    elif confidence_score > 0.5:
        confidence = "Medium"
    else:
        confidence = "Low"
    
    return {
        "label": label_map[pred_class],
        "short_label": short_label_map[pred_class],
        "class_id": pred_class,
        "probability": float(confidence_score),
        "score": float(score),
        "confidence": confidence,
        "all_probabilities": {
            "Low": float(1 - confidence_score) if pred_class == 0 else 0,
            "Medium": float(confidence_score) if pred_class == 1 else 0,
            "High": float(confidence_score) if pred_class == 2 else 0
        }
    }

def predict_batch(features_df):
    """批量预测"""
    features_df = features_df[FEATURES].astype(float)
    
    if scaler is not None:
        features_scaled = scaler.transform(features_df)
        features_df = pd.DataFrame(features_scaled, columns=FEATURES)
    
    scores = model.predict(features_df)
    
    predictions = []
    for score in scores:
        if score >= HIGH_THRESHOLD:
            pred_class = 2
        elif score >= LOW_THRESHOLD:
            pred_class = 1
        else:
            pred_class = 0
        
        predictions.append({
            "label": label_map[pred_class],
            "short_label": short_label_map[pred_class],
            "class_id": pred_class,
            "score": float(score)
        })
    
    return predictions

def get_feature_importance():
    if hasattr(model, 'feature_importances_'):
        importance = pd.DataFrame({
            "feature": FEATURES,
            "importance": model.feature_importances_
        }).sort_values(by="importance", ascending=False)
        return importance
    else:
        return None