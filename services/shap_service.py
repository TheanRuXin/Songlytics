# shap_service.py
import joblib
import pandas as pd
import numpy as np

# 加载回归模型
saved = joblib.load("models/music_model_xgb_regressor.pkl")
model = saved["model"]
scaler = saved.get("scaler", None)
features = saved["features"]

# 回归模型使用的阈值
LOW_THRESHOLD = 34
HIGH_THRESHOLD = 67

def explain(features_df):
    """解释回归模型的预测结果"""
    features_df = features_df[features].astype(float)
    
    if scaler is not None:
        features_scaled = scaler.transform(features_df)
        features_df = pd.DataFrame(features_scaled, columns=features)
    
    # 对于回归模型，我们需要使用 SHAP
    try:
        import shap
        # 创建解释器
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(features_df)[0]
        
        # 整理结果
        explanation = []
        for i, feature in enumerate(features):
            impact = float(shap_values[i])
            explanation.append({
                "feature": feature,
                "impact": impact,
                "direction": "positive" if impact > 0 else "negative"
            })
        
        return explanation
    except Exception as e:
        print(f"SHAP error: {e}")
        # 如果 SHAP 失败，返回基于特征重要性的近似解释
        importance = model.feature_importances_
        explanation = []
        for i, feature in enumerate(features):
            explanation.append({
                "feature": feature,
                "impact": float(importance[i]),
                "direction": "positive"
            })
        return explanation