import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import(mean_absolute_error,mean_squared_error,r2_score)

df = pd.read_csv("C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_cleaned.csv")

features = ["duration_ms","explicit","danceability","energy","key","loudness","mode","speechiness","acousticness","instrumentalness","liveness","valence","tempo","time_signature"]

X = df[features]
y = df["popularity"]

popularity_bins = pd.cut(df["popularity"], bins=[-1,20,40,60,80,100],labels=["0-20","21-40","41-60","61-80","81-100"])

print("Popularity Range Distribution")
print("Count:",popularity_bins.value_counts().sort_index())
print("\nPercentage:",(popularity_bins.value_counts(normalize=True).sort_index()*100).round(2))

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2, random_state=42)
print("Train / Test Split")
print("X_train:",X_train.shape)
print("X_test:",X_test.shape)
print("y_train:",y_train.shape)
print("y_test:",y_test.shape)

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

train_bins = pd.cut(y_train,bins=[-1,20,40,60,80,100],labels=False)

bin_counts = train_bins.value_counts().sort_index()

print("Training Range Counts:",bin_counts)

weight_map = {
    0: 1.0,
    1: 1.0,
    2: 1.0,
    3: 2.0,
    4: 5.0
}

sample_weights = train_bins.map(weight_map )
print("\nSample Weight Summary:",sample_weights.describe())

weighted_rf = RandomForestRegressor( 
    n_estimators=500,
    min_samples_split=5,
    min_samples_leaf=1,
    max_features=0.8,
    max_depth=None,
    random_state=42,
    n_jobs=-1
)

weighted_rf.fit(X_train,y_train,sample_weight=sample_weights)

weighted_pred = weighted_rf.predict(X_test)

weighted_mae = mean_absolute_error(y_test,weighted_pred)
weighted_rmse = np.sqrt(mean_squared_error(y_test,weighted_pred))
weighted_r2 = r2_score(y_test,weighted_pred)

normal_eval = pd.DataFrame({"actual": y_test.to_numpy(),"predicted": y_pred})
normal_eval["Absolute Error"] = np.abs(normal_eval["actual"] - normal_eval["predicted"])
normal_eval["Popularity Range"] = pd.cut(normal_eval["actual"],bins=[-1,20,40,60,80,100],labels=["0-20","21-40","41-60","61-80","81-100"])
normal_range_mae = (normal_eval.groupby("Popularity Range",observed=True)["Absolute Error"].mean())

weighted_eval = pd.DataFrame({"actual": y_test.to_numpy(),"predicted": weighted_pred})
weighted_eval["Absolute Error"] = np.abs(weighted_eval["actual"] - weighted_eval["predicted"])
weighted_eval["Popularity Range"] = pd.cut(weighted_eval["actual"],bins=[-1,20,40,60,80,100],labels=["0-20","21-40","41-60","61-80","81-100"])
weighted_range_mae = (weighted_eval.groupby("Popularity Range",observed=True)["Absolute Error"].mean())

comparison = pd.DataFrame({
    "Model":["Normal Tuned Random Forest","Weighted Random Forest"],
    "MAE" : [mae,weighted_mae],
    "RMSE" : [rmse,weighted_rmse],
    "R2 Score" : [r2,weighted_r2]
    })

print("Overall Model Comparison:",comparison.round(4).to_string(index=False))
range_comparison = pd.DataFrame({
    "Normal RF MAE":normal_range_mae,
    "Weighted RF MAE":weighted_range_mae})

range_comparison["Improvement"] = (range_comparison["Normal RF MAE"] - range_comparison["Weighted RF MAE"])

print("MAE by popularity range",range_comparison.round(4))
