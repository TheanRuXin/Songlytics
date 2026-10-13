import pandas as pd
import numpy as np
import time

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

# Load data
df = pd.read_csv("C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_cleaned.csv")

# Features and target
features = [
    "duration_ms", "explicit", "danceability", "energy", "key", "loudness",
    "mode", "speechiness", "acousticness", "instrumentalness", "liveness",
    "valence", "tempo", "time_signature","track_genre"
]

X = df[features]
y = df["popularity"]

# Train / Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "genre",
            OneHotEncoder(handle_unknown="ignore"),
            ["track_genre"]
        )
    ],
    remainder="passthrough"
)

current_model = Pipeline([("preprocessor",preprocessor),("random_forest",RandomForestRegressor(
    n_estimators=500,
    min_samples_split=5,
    min_samples_leaf=1,
    max_features=0.8,
    max_depth=None,
    random_state=42,
    n_jobs=-1
))])

start_time = time.time()
current_model.fit(X_train, y_train)
current_training_time = time.time() - start_time
current_pred = current_model.predict(X_test)

current_mae = mean_absolute_error(y_test,current_pred)
current_rmse = np.sqrt(mean_squared_error(y_test,current_pred))
current_r2 = r2_score(y_test,current_pred)
print("\nCurrent Audio + Genre Results")
print("MAE:",round(current_mae,4))
print("RMSE:",round(current_rmse,4))
print("R2 Score:",round(current_r2,4))
print("Training Time:",round(current_training_time,2),"seconds")

tuning_pipeline = Pipeline([
    (
        "preprocessor",
        preprocessor
    ),
    (
        "random_forest",
        RandomForestRegressor(
            random_state=42,
            n_jobs=1
        )
    )
])

param_dist = {
    "random_forest__n_estimators": [300,500,700],
    "random_forest__max_depth": [None,15,20,30],
    "random_forest__min_samples_split": [2,5,10],
    "random_forest__min_samples_leaf": [1,2,4],
    "random_forest__max_features": ["sqrt",0.5,0.8,1.0]
}

search = RandomizedSearchCV(

    estimator=tuning_pipeline,
    param_distributions=param_dist,
    # Number of random parameter combinations
    n_iter=15,
    # Minimize MAE
    scoring="neg_mean_absolute_error",
    # 3-fold cross validation
    cv=3,
    random_state=42,
    # Use all CPU cores for parallel CV
    n_jobs=-1,
    verbose=2,
    # Automatically refit best model
    refit=True,
    return_train_score=True
)

print("STARTING RANDOM FOREST GENRE TUNING")

print("15 parameter combinations × 3-fold CV")

print("Approximately 45 model fits will be performed.")

search_start_time = time.time()

search.fit(X_train,y_train)
search_time = (time.time()- search_start_time)

# Best Parameters
print("\nBest Parameters")
print(search.best_params_)
print("Best CV MAE:", round(-search.best_score_, 4))
print("Search Time:", round(search_time, 2), "seconds")

# Best Model
best_model = search.best_estimator_

# Predictions
train_pred = best_model.predict(X_train)
test_pred = best_model.predict(X_test)

# Train Metrics
train_mae = mean_absolute_error(y_train, train_pred)
train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
train_r2 = r2_score(y_train, train_pred)

# Test Metrics
test_mae = mean_absolute_error(y_test, test_pred)
test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
test_r2 = r2_score(y_test, test_pred)

# Results
print("\nTuned Audio + Genre Random Forest Result")
print("Train MAE:", round(train_mae, 4))
print("Test MAE:", round(test_mae, 4))
print("Train RMSE:", round(train_rmse, 4))
print("Test RMSE:", round(test_rmse, 4))
print("Train R²:", round(train_r2, 4))
print("Test R²:", round(test_r2, 4))

comparison = pd.DataFrame({
    "Model": [
        "Current Audio + Genre RF",
        "Tuned Audio + Genre RF"
    ],

    "MAE": [
        current_mae,
        test_mae
    ],

    "RMSE": [
        current_rmse,
        test_rmse
    ],

    "R2": [
        current_r2,
        test_r2
    ]
})

print("CURRENT VS TUNED MODEL")

print(comparison.round(4).to_string(index=False))

def calculate_range_mae(actual,predicted):

    evaluation = pd.DataFrame({
        "actual":np.asarray(actual),
        "predicted":np.asarray(predicted)
    })

    evaluation["absolute_error"] = np.abs(evaluation["actual"] - evaluation["predicted"])

    evaluation["popularity_range"] = pd.cut(
        evaluation["actual"],
        bins=[-1,20,40,60,80,100],
        labels=["0-20","21-40","41-60","61-80","81-100"]
    )

    result = (
        evaluation
        .groupby(
            "popularity_range",
            observed=True
        )["absolute_error"]
        .mean()
    )

    return result

current_range_mae = calculate_range_mae(y_test,current_pred)

tuned_range_mae = calculate_range_mae(y_test,test_pred)

range_comparison = pd.DataFrame({
    "Current Genre RF MAE":
        current_range_mae,
    "Tuned Genre RF MAE":
        tuned_range_mae
})

range_comparison["Improvement"] = (
    range_comparison[
        "Current Genre RF MAE"
    ]
    -
    range_comparison[
        "Tuned Genre RF MAE"
    ]
)

print("MAE BY POPULARITY RANGE")

print(
    range_comparison.round(4)
)

mae_improvement = (current_mae- test_mae)

rmse_improvement = (current_rmse- test_rmse)

r2_improvement = (test_r2- current_r2)

print("TUNING IMPROVEMENT")

print("MAE improvement :",round(mae_improvement, 4))
print("RMSE improvement:",round(rmse_improvement, 4))
print("R² improvement  :",round(r2_improvement, 4))

comparison.to_csv("genre_tuning_comparison.csv",index=False)

range_comparison.to_csv("genre_tuning_range_comparison.csv")