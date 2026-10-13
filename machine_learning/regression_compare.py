import pandas as pd
import numpy as np
import time 

df = pd.read_csv("C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_cleaned.csv")

features = ["duration_ms","explicit","danceability","energy","key","loudness","mode","speechiness","acousticness","instrumentalness","liveness","valence","tempo","time_signature"]

X = df[features]
y = df["popularity"]

print(X.shape)
print(y.shape)

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2, random_state=42)

print("X_train:",X_train.shape)
print("X_test:",X_test.shape)
print("y_train:",y_train.shape)
print("y_test:",y_test.shape)

from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error,r2_score

# Dummy Regressor
start_time = time.time()
baseline = DummyRegressor(strategy="mean")
baseline.fit(X_train,y_train)
baseline_time = time.time() - start_time

y_pred_baseline = baseline.predict(X_test)

print("y_train mean:",y_train.mean())
print("y_test mean:",y_test.mean())

print("baseline prediction unique value:")
print(np.unique(y_pred_baseline)[:10])

print("y_test variance:",np.var(y_test))

mae = mean_absolute_error(y_test, y_pred_baseline)
rmse = np.sqrt(mean_squared_error(y_test,y_pred_baseline))
r2 = r2_score(y_test,y_pred_baseline)

print("Baseline MAE:", mae)
print("Baseline RMSE:", rmse)
print("Baseline r2:",r2)
print("Baseline Training Time:", round(baseline_time, 4), "seconds")

#Linear Regression
from sklearn.linear_model import LinearRegression
start_time = time.time()

linear_model = LinearRegression()
linear_model.fit(X_train,y_train)

linear_time = time.time() - start_time

y_pred_linear = linear_model.predict(X_test)
linear_mae = mean_absolute_error(y_test,y_pred_linear)
linear_rmse = np.sqrt(mean_squared_error(y_test,y_pred_linear))
linear_r2 = r2_score(y_test,y_pred_linear)

print("Linear Regression MAE:",linear_mae)
print("Linear Regression RMSE:",linear_rmse)
print("Linear Regression R2:",linear_r2)
print("Linear Regression Training Time:", round(linear_time, 4), "seconds")

#Ridge Regression
start_time = time.time()
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

ridge_model = Pipeline([
    ("scaler", StandardScaler()),
    ("model", Ridge(alpha=1.0))
])
ridge_model.fit(X_train, y_train)

ridge_time = time.time() - start_time

y_pred_ridge = ridge_model.predict(X_test)
ridge_mae = mean_absolute_error(y_test, y_pred_ridge)
ridge_rmse = np.sqrt(mean_squared_error(y_test, y_pred_ridge))
ridge_r2 = r2_score(y_test, y_pred_ridge)

print("Ridge Regression MAE:", ridge_mae)
print("Ridge Regression RMSE:", ridge_rmse)
print("Ridge Regression R2:", ridge_r2)
print("Ridge Regression Training Time:", round(ridge_time, 4), "seconds")

# Decision Tree
start_time = time.time()
from sklearn.tree import DecisionTreeRegressor
tree_model = DecisionTreeRegressor(random_state=42)
tree_model.fit(X_train, y_train)
tree_time = time.time() - start_time

y_pred_tree = tree_model.predict(X_test)
tree_mae = mean_absolute_error(y_test, y_pred_tree)
tree_rmse = np.sqrt(mean_squared_error(y_test, y_pred_tree))
tree_r2 = r2_score(y_test, y_pred_tree)

print("Decision Tree MAE:", tree_mae)
print("Decision Tree RMSE:", tree_rmse)
print("Decision Tree R2:", tree_r2)
print("Decision Tree Training Time:", round(tree_time, 4), "seconds")

# Random Forest
start_time = time.time()
from sklearn.ensemble import RandomForestRegressor

rf_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)
rf_time = time.time() - start_time

y_pred_rf = rf_model.predict(X_test)
rf_mae = mean_absolute_error(y_test, y_pred_rf)
rf_rmse = np.sqrt(mean_squared_error(y_test, y_pred_rf))
rf_r2 = r2_score(y_test, y_pred_rf)

print("Random Forest MAE:", rf_mae)
print("Random Forest RMSE:", rf_rmse)
print("Random Forest R2:", rf_r2)
print("Random Forest Training Time:", round(rf_time, 4), "seconds")

# Extra Trees
start_time = time.time()
from sklearn.ensemble import ExtraTreesRegressor

extra_model = ExtraTreesRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)
extra_model.fit(X_train, y_train)
extra_time = time.time() - start_time

y_pred_extra = extra_model.predict(X_test)
extra_mae = mean_absolute_error(y_test, y_pred_extra)
extra_rmse = np.sqrt(mean_squared_error(y_test, y_pred_extra))
extra_r2 = r2_score(y_test, y_pred_extra)

print("Extra Trees MAE:", extra_mae)
print("Extra Trees RMSE:", extra_rmse)
print("Extra Trees R2:", extra_r2)
print("Extra Trees Training Time:", round(extra_time, 4), "seconds")

# Gradient Boosting
start_time = time.time()
from sklearn.ensemble import GradientBoostingRegressor

gb_model = GradientBoostingRegressor(
    n_estimators=100,
    random_state=42
)
gb_model.fit(X_train, y_train)
gb_time = time.time() - start_time

y_pred_gb = gb_model.predict(X_test)
gb_mae = mean_absolute_error(y_test, y_pred_gb)
gb_rmse = np.sqrt(mean_squared_error(y_test, y_pred_gb))
gb_r2 = r2_score(y_test, y_pred_gb)

print("Gradient Boosting MAE:", gb_mae)
print("Gradient Boosting RMSE:", gb_rmse)
print("Gradient Boosting R2:", gb_r2)
print("Gradient Boosting Training Time:", round(gb_time, 4), "seconds")

#XGBoost
start_time = time.time()

from xgboost import XGBRegressor
xg_model = XGBRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)
xg_model.fit(X_train, y_train)

xg_time = time.time() - start_time

xg_train_pred = xg_model.predict(X_train)
xg_test_pred = xg_model.predict(X_test)

xg_train_mae = mean_absolute_error(y_train, xg_train_pred)
xg_test_mae = mean_absolute_error(y_test, xg_test_pred)

xg_train_rmse = np.sqrt(mean_squared_error(y_train, xg_train_pred))
xg_test_rmse = np.sqrt(mean_squared_error(y_test, xg_test_pred))

xg_train_r2 = r2_score(y_train, xg_train_pred)
xg_test_r2 = r2_score(y_test, xg_test_pred)

print("XGBoost Train MAE:", round(xg_train_mae, 4))
print("XGBoost Test MAE:", round(xg_test_mae, 4))
print("XGBoost Train RMSE:", round(xg_train_rmse, 4))
print("XGBoost Test RMSE:", round(xg_test_rmse, 4))
print("XGBoost Train R²:", round(xg_train_r2, 4))
print("XGBoost Test R²:", round(xg_test_r2, 4))
print("XGBoost Training Time:", round(xg_time, 4), "seconds")

# Hist Gradient Boosting
start_time = time.time()
from sklearn.ensemble import HistGradientBoostingRegressor

hist_gb_model = HistGradientBoostingRegressor(
    random_state=42
)
hist_gb_model.fit(X_train, y_train)

hist_gb_time = time.time() - start_time

y_pred_hist_gb = hist_gb_model.predict(X_test)
hist_gb_mae = mean_absolute_error(y_test, y_pred_hist_gb)
hist_gb_rmse = np.sqrt(mean_squared_error(y_test, y_pred_hist_gb))
hist_gb_r2 = r2_score(y_test, y_pred_hist_gb)

print("Hist Gradient Boosting MAE:", hist_gb_mae)
print("Hist Gradient Boosting RMSE:", hist_gb_rmse)
print("Hist Gradient Boosting R2:", hist_gb_r2)
print("Hist Gradient Boosting Training Time:",round(hist_gb_time, 4),"seconds")

# KNN
start_time = time.time()
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

knn_model = Pipeline([
    ("scaler", StandardScaler()),
    ("model", KNeighborsRegressor(
        n_neighbors=5,
        n_jobs=-1
    ))
])
knn_model.fit(X_train, y_train)

knn_time = time.time() - start_time

y_pred_knn = knn_model.predict(X_test)
knn_mae = mean_absolute_error(y_test, y_pred_knn)
knn_rmse = np.sqrt(mean_squared_error(y_test, y_pred_knn))
knn_r2 = r2_score(y_test, y_pred_knn)

print("KNN MAE:", knn_mae)
print("KNN RMSE:", knn_rmse)
print("KNN R2:", knn_r2)
print("KNN Training Time:", round(knn_time, 4), "seconds")

#catboost
start_time = time.time()

from catboost import CatBoostRegressor
cat_model = CatBoostRegressor(
    iterations=500,
    learning_rate=0.05,
    depth=6,
    loss_function="RMSE",
    random_seed=42,
    verbose=0
)

cat_model.fit(
    X_train,
    y_train
)

cat_training_time = time.time() - start_time

y_pred_train_cat = cat_model.predict(X_train)
y_pred_test_cat = cat_model.predict(X_test)

cat_train_mae = mean_absolute_error(y_train,y_pred_train_cat)
cat_train_rmse = np.sqrt(mean_squared_error(y_train,y_pred_train_cat))
cat_train_r2 = r2_score(y_train,y_pred_train_cat)
cat_test_mae = mean_absolute_error(y_test,y_pred_test_cat)
cat_test_rmse = np.sqrt(mean_squared_error(y_test,y_pred_test_cat))
cat_test_r2 = r2_score(y_test,y_pred_test_cat)

print("CatBoost Train Mae:", round(cat_train_mae,4))
print("CatBoost Test Mae:", round(cat_test_mae,4))

print("CatBoost Train RMSE:", round(cat_train_rmse,4))
print("CatBoost Test RMSE:", round(cat_test_rmse,4))

print("CatBoost Train R2:", round(cat_train_r2,4))
print("CatBoost Test R2:", round(cat_test_r2,4))
print("CatBoost Training Time:", round(cat_training_time,4),"seconds")


results_df = pd.DataFrame({
    "Model": [
        "Baseline",
        "Linear Regression",
        "Ridge Regression",
        "Decision Tree",
        "Random Forest",
        "Extra Trees",
        "Gradient Boosting",
        "Hist Gradient Boosting",
        "XGBoost",
        "KNN",
        "CatBoost"
    ],
    
    "Test MAE": [
        mae,
        linear_mae,
        ridge_mae,
        tree_mae,
        rf_mae,
        extra_mae,
        gb_mae,
        hist_gb_mae,
        xg_test_mae,
        knn_mae,
        cat_test_mae
    ],
    
    "Test RMSE": [
        rmse,
        linear_rmse,
        ridge_rmse,
        tree_rmse,
        rf_rmse,
        extra_rmse,
        gb_rmse,
        hist_gb_rmse,
        xg_test_rmse,
        knn_rmse,
        cat_test_rmse
    ],
    
    "Test R2": [
        r2,
        linear_r2,
        ridge_r2,
        tree_r2,
        rf_r2,
        extra_r2,
        gb_r2,
        hist_gb_r2,
        xg_test_r2,
        knn_r2,
        cat_test_r2
    ],
    
    "Training Time": [
        baseline_time,
        linear_time,
        ridge_time,
        tree_time,
        rf_time,
        extra_time,
        gb_time,
        hist_gb_time,
        xg_time,
        knn_time,
        cat_training_time
    ]
})

print("\nModel Comparison")
print(results_df)

#identify best model based on Test R2
best_model_row = results_df.loc[results_df["Test R2"].idxmax()]

print("BEST INITIAL MODEL")

print("Model:", best_model_row["Model"])
print("Test MAE:", round(best_model_row["Test MAE"], 4))
print("Test RMSE:", round(best_model_row["Test RMSE"], 4))
print("Test R²:", round(best_model_row["Test R2"], 4))

print("OVERFITTING CHECK")

models = {
    "Decision Tree": tree_model,
    "Random Forest": rf_model,
    "Extra Trees": extra_model,
    "Hist Gradient Boosting": hist_gb_model
}

candidate_models = [
    "Decision Tree",
    "Random Forest",
    "Extra Trees",
    "Hist Gradient Boosting",
]

for name in candidate_models:

    model = models[name]

    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    train_mae = mean_absolute_error(
        y_train,
        y_train_pred
    )

    test_mae = mean_absolute_error(
        y_test,
        y_test_pred
    )

    train_r2 = r2_score(
        y_train,
        y_train_pred
    )

    test_r2 = r2_score(
        y_test,
        y_test_pred
    )

    print("\n", name)
    print("Train MAE:", round(train_mae, 4))
    print("Test MAE :", round(test_mae, 4))
    print("Train R² :", round(train_r2, 4))
    print("Test R²  :", round(test_r2, 4))