# train_model_regression.py
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import shap
import os

from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    classification_report,
    confusion_matrix
)
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

print("=" * 60)
print("SONGLYTICS - XGBOOST REGRESSION TRAINING")
print("=" * 60)

os.makedirs("models", exist_ok=True)

df = pd.read_csv(
    "C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_merged_cleaned.csv"
)

FEATURES = [
    "duration_ms",
    "explicit",
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo"
]

# Only keep rows with a real popularity score (should be ~100% after the
# updated cleaning script, but this keeps the training script safe even if
# you re-run it on an older/partial dataset).
df = df.dropna(subset=["popularity"]).copy()
df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce")
df = df.dropna(subset=["popularity"])

print(f"\nDataset shape (with popularity): {df.shape}")
print(f"Popularity range: {df['popularity'].min():.1f} - {df['popularity'].max():.1f}")
print(f"Popularity mean / median: {df['popularity'].mean():.2f} / {df['popularity'].median():.2f}")

if "source" in df.columns:
    print("\nSource breakdown:")
    print(df["source"].value_counts())

X = df[FEATURES]
y = df["popularity"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=FEATURES, index=X.index)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

print(f"\nTrain shape: {X_train.shape}")
print(f"Test shape: {X_test.shape}")

print("\n" + "=" * 60)
print("TRAINING XGBOOST REGRESSOR")
print("=" * 60)

model = XGBRegressor(
    n_estimators=800,
    max_depth=7,
    learning_rate=0.03,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,
    gamma=0.1,
    reg_alpha=0.1,
    reg_lambda=1.0,
    objective="reg:squarederror",
    eval_metric="rmse",
    random_state=42,
    n_jobs=-1,
    verbosity=0
)

model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False
)

print("Model training complete")

print("\n" + "=" * 60)
print("CROSS-VALIDATION (R^2)")
print("=" * 60)

cv = KFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="r2", n_jobs=-1)
print(f"5-fold CV R^2: {np.mean(cv_scores):.4f} (+/- {np.std(cv_scores) * 2:.4f})")

print("\n" + "=" * 60)
print("MODEL EVALUATION (REGRESSION)")
print("=" * 60)

y_pred = model.predict(X_test)
y_pred = np.clip(y_pred, 0, 100)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Test RMSE: {rmse:.3f}")
print(f"Test MAE:  {mae:.3f}")
print(f"Test R^2:  {r2:.4f}")
print(f"CV R^2:    {np.mean(cv_scores):.4f}")

# ------------------------------------------------------------------
# Predicted vs Actual scatter
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 7))
sample_idx = np.random.choice(len(y_test), size=min(5000, len(y_test)), replace=False)
plt.scatter(y_test.values[sample_idx], y_pred[sample_idx], alpha=0.15, s=10)
plt.plot([0, 100], [0, 100], 'r--', linewidth=2)
plt.xlabel("Actual Popularity")
plt.ylabel("Predicted Popularity")
plt.title(f"Predicted vs Actual (R^2={r2:.3f}, RMSE={rmse:.2f})")
plt.xlim(0, 100)
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig("models/regression_pred_vs_actual.png", dpi=150)
print("\nPredicted vs Actual plot saved to 'models/regression_pred_vs_actual.png'")

# ------------------------------------------------------------------
# Residual plot
# ------------------------------------------------------------------
residuals = y_test.values - y_pred
fig, ax = plt.subplots(figsize=(8, 5))
plt.scatter(y_pred, residuals, alpha=0.15, s=10)
plt.axhline(0, color='r', linestyle='--', linewidth=2)
plt.xlabel("Predicted Popularity")
plt.ylabel("Residual (Actual - Predicted)")
plt.title("Residual Plot")
plt.tight_layout()
plt.savefig("models/regression_residuals.png", dpi=150)
print("Residual plot saved to 'models/regression_residuals.png'")

# ------------------------------------------------------------------
# Map continuous predictions back to Low/Medium/High to compare
# against the original classification approach
# ------------------------------------------------------------------
def to_class(pop):
    if pop >= 67:
        return 2
    elif pop >= 34:
        return 1
    else:
        return 0

y_test_class = y_test.apply(to_class)
y_pred_class = pd.Series(y_pred, index=y_test.index).apply(to_class)

print("\n" + "=" * 60)
print("CLASSIFICATION VIEW (regression output binned into Low/Med/High)")
print("=" * 60)
print(classification_report(
    y_test_class, y_pred_class,
    target_names=["Low", "Medium", "High"],
    zero_division=0
))

cm = confusion_matrix(y_test_class, y_pred_class)
print("Confusion Matrix:")
print(cm)

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Low', 'Medium', 'High'],
            yticklabels=['Low', 'Medium', 'High'])
plt.title('Confusion Matrix (Regression -> Class, threshold 34/67)')
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.tight_layout()
plt.savefig('models/regression_confusion_matrix.png', dpi=150)
print("\nConfusion matrix saved to 'models/regression_confusion_matrix.png'")

# ------------------------------------------------------------------
# Feature importance
# ------------------------------------------------------------------
importance = pd.DataFrame({
    "feature": FEATURES,
    "importance": model.feature_importances_
}).sort_values(by="importance", ascending=False)

print("\n" + "=" * 60)
print("FEATURE IMPORTANCE")
print("=" * 60)
for _, row in importance.iterrows():
    bar = "#" * int(row['importance'] * 50)
    print(f"  {row['feature']:18} {row['importance']:.4f} {bar}")

fig, ax = plt.subplots(figsize=(10, 6))
colors = plt.cm.viridis(np.linspace(0, 1, len(importance)))
plt.barh(importance['feature'], importance['importance'], color=colors)
plt.xlabel('Importance', fontsize=12)
plt.title('XGBoost Feature Importance (Regression)', fontsize=14)
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('models/feature_importance_regression.png', dpi=150)
print("\nFeature importance plot saved to 'models/feature_importance_regression.png'")

# ------------------------------------------------------------------
# SHAP explanation (global)
# ------------------------------------------------------------------
print("\n" + "=" * 60)
print("SHAP EXPLANATION")
print("=" * 60)

# Sample test set for SHAP (full test set would be slow / huge plots)
shap_sample_size = min(2000, len(X_test))
X_shap = X_test.sample(n=shap_sample_size, random_state=42)

explainer = shap.TreeExplainer(model)
shap_values = explainer(X_shap)

print(f"SHAP values computed for {shap_sample_size} test samples")

# Beeswarm summary plot (shows direction + magnitude of effect per feature)
plt.figure(figsize=(10, 7))
shap.summary_plot(shap_values, X_shap, show=False)
plt.tight_layout()
plt.savefig('models/shap_summary_beeswarm.png', dpi=150, bbox_inches='tight')
plt.close()
print("SHAP beeswarm plot saved to 'models/shap_summary_beeswarm.png'")

plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X_shap, plot_type="bar", show=False)
plt.tight_layout()
plt.savefig('models/shap_summary_bar.png', dpi=150, bbox_inches='tight')
plt.close()
print("SHAP bar plot saved to 'models/shap_summary_bar.png'")

model_path = "models/music_model_xgb_regressor.pkl"
joblib.dump({
    "model": model,
    "features": FEATURES,
    "scaler": scaler,
    "test_rmse": rmse,
    "test_mae": mae,
    "test_r2": r2,
    "cv_r2": np.mean(cv_scores),
    "class_thresholds": {"low_max": 34, "high_min": 67}
}, model_path)
print(f"\nRegression model saved to '{model_path}'")

with open("models/model_config_regression.txt", "w") as f:
    f.write("=" * 60 + "\n")
    f.write("SONGLYTICS REGRESSION MODEL CONFIGURATION\n")
    f.write("=" * 60 + "\n\n")
    f.write("Target: popularity (continuous, 0-100)\n\n")
    f.write("Class mapping (for display only):\n")
    f.write("  popularity < 34          -> Low\n")
    f.write("  34 <= popularity < 67    -> Medium\n")
    f.write("  popularity >= 67         -> High\n\n")
    f.write(f"Test RMSE: {rmse:.4f}\n")
    f.write(f"Test MAE:  {mae:.4f}\n")
    f.write(f"Test R^2:  {r2:.4f}\n")
    f.write(f"5-fold CV R^2: {np.mean(cv_scores):.4f}\n\n")
    f.write("Feature Importance:\n")
    for _, row in importance.iterrows():
        f.write(f"  {row['feature']:18}: {row['importance']:.4f}\n")
    f.write("\n" + "=" * 60 + "\n")
    f.write("Hyperparameters:\n")
    f.write("  n_estimators: 800\n")
    f.write("  max_depth: 7\n")
    f.write("  learning_rate: 0.03\n")
    f.write("  subsample: 0.8\n")
    f.write("  colsample_bytree: 0.8\n")
    f.write("  min_child_weight: 3\n")
    f.write("  gamma: 0.1\n")
    f.write("  reg_alpha: 0.1\n")
    f.write("  reg_lambda: 1.0\n")
    f.write("=" * 60 + "\n")

print("Model configuration saved to 'models/model_config_regression.txt'")

print("\n" + "=" * 60)
print("TRAINING COMPLETE")
print("=" * 60)
print("\nFiles saved in 'models/' folder:")
print("  - music_model_xgb_regressor.pkl")
print("  - model_config_regression.txt")
print("  - regression_pred_vs_actual.png")
print("  - regression_residuals.png")
print("  - regression_confusion_matrix.png")
print("  - feature_importance_regression.png")
print("  - shap_summary_beeswarm.png")
print("  - shap_summary_bar.png")