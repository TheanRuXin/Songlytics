import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (mean_absolute_error,mean_squared_error,r2_score)

df = pd.read_csv("C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_cleaned.csv")

features = ["duration_ms","explicit","danceability","energy","key","loudness","mode","speechiness","acousticness","instrumentalness","liveness","valence","tempo","time_signature"]
X = df[features]
y = df["popularity"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
model = RandomForestRegressor(
    n_estimators=500,
    min_samples_split=5,
    min_samples_leaf=1,
    max_features=0.8,
    max_depth=None,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test,y_pred)
rmse = np.sqrt(mean_squared_error(y_test,y_pred))
r2 = r2_score(y_test,y_pred)

print("Final MAE:",mae)
print("Final RMSE:",rmse)
print("Final R2:",r2)

plt.figure(figsize=(8,6))
plt.scatter(y_test,y_pred,alpha=0.3)
plt.xlabel("Actual Popularity")
plt.ylabel("Predicted Popularity")
plt.title("Actual vs Predicted Popularity")

plt.plot([0,100],[0,100],linestyle="--")
plt.show()

residuals = y_test - y_pred
plt.figure(figsize=(8,6))
plt.scatter(y_pred,residuals,alpha=0.3)
plt.axhline(y=0,linestyle="--")
plt.xlabel("Predicted Popularity")
plt.ylabel("Residual")
plt.title("Residual Plot")
plt.show()

evaluation_df = pd.DataFrame({"actual":y_test,"predicted":y_pred})
evaluation_df["error"] = abs(evaluation_df["actual"] - evaluation_df["predicted"])

evaluation_df["range"] = pd.cut(evaluation_df["actual"],bins=[-1,20,40,60,80,100],labels=["0-20","21-40","41-60","61-80","81-100"])
range_mae = (evaluation_df.groupby("range",observed=True)["error"].mean())

print("\nMAE by Popularity Range")
print(range_mae)

popularity_bins = pd.cut(
    df["popularity"],
    bins=[-1, 20, 40, 60, 80, 100],
    labels=["0-20", "21-40", "41-60", "61-80", "81-100"]
)

print("\nPopularity Range Count:")
print(popularity_bins.value_counts().sort_index())

print("\nPopularity Range Percentage:")
print(
    (popularity_bins.value_counts(normalize=True).sort_index() * 100)
    .round(2)
)