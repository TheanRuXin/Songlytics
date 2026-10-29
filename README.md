# 🎵 Songlytics

**Songlytics** is a web-based music analytics and song popularity prediction platform developed using **Python** and **Streamlit**.

The system uses a **Random Forest Regression** model to estimate a song's popularity score from 0 to 100 based on its audio characteristics and genre. It also provides interactive music analytics, explainable AI, model-based recommendations, what-if simulation, prediction history, and PDF report generation.

---

## 📌 Project Overview

Music streaming platforms contain large amounts of music data, but understanding how different audio characteristics influence song popularity can be difficult.

Songlytics provides an integrated platform that allows users to:

- Explore music dataset trends.
- Predict song popularity.
- Understand how audio features affect model predictions.
- Experiment with feature adjustments.
- Review previous prediction and simulation records.
- Generate PDF reports.

The system is designed to provide a more interactive and explainable approach to music popularity analysis.

---

# ✨ Main Features

## 📊 Music Analytics

The Analysis page provides interactive visualisations for exploring the Spotify music dataset.

Users can analyse:

- Popularity distribution
- Genre performance
- Audio feature distributions
- Feature relationships
- Dataset statistics
- Correlation between audio characteristics and popularity

Users can also apply filters to explore specific parts of the dataset.

---

## 🔮 Song Popularity Prediction

Songlytics predicts a continuous popularity score between:

```text
0 – 100
```

The prediction model is based on **Random Forest Regression**.

Prediction results are also grouped into three labels for easier interpretation:

```text
Low Popularity     : Score < 40

Medium Popularity  : Score 40 – 59

High Popularity    : Score >= 60
```

The labels are used only for displaying prediction results.  
The machine learning model itself remains a regression model.

---

# 🎧 Prediction Input Methods

Songlytics provides two methods for making predictions.

## 1. Spotify-Assisted Search

Users can search for a song using Spotify.

The system:

1. Searches Spotify for the song.
2. Matches the Spotify result with the Songlytics dataset.
3. Loads the available audio features.
4. Sends the features to the prediction model.
5. Displays the predicted popularity score.

Only songs supported by the Songlytics dataset can be automatically loaded.

---

## 2. Manual Input

Users can manually enter the required audio characteristics.

This method is useful when the required song is not available through the supported Spotify search.

---

# 🎚️ Audio Features

The prediction model uses the following features:

```text
duration_ms
explicit
danceability
energy
key
loudness
mode
speechiness
acousticness
instrumentalness
liveness
valence
tempo
time_signature
track_genre
```

The `track_genre` feature is encoded using One-Hot Encoding before being passed to the machine learning model.

---

# 🤖 Machine Learning Model

Songlytics uses a **Random Forest Regression** model.

The final model configuration includes:

```text
n_estimators = 500
min_samples_split = 5
min_samples_leaf = 1
max_features = 0.8
max_depth = None
random_state = 42
```

The dataset is divided into:

```text
80% Training Data
20% Testing Data
```

with:

```text
random_state = 42
```

---

# 📈 Model Performance

The final Random Forest model achieved approximately:

## Training Performance

```text
MAE  : 4.44
RMSE : 6.94
R²   : 0.887
```

## Testing Performance

```text
MAE  : 10.05
RMSE : 14.81
R²   : 0.475
```

The test R² value means that the model explains approximately **47.5% of the variation in popularity scores in the testing dataset**.

It should not be interpreted as classification accuracy.

---

# 🧠 Explainable AI

Songlytics uses **SHAP (SHapley Additive exPlanations)** to explain individual predictions.

SHAP values help users understand whether a feature:

```text
Pushes the prediction higher
```

or:

```text
Pushes the prediction lower
```

The feature impact is displayed using an interactive chart.

This improves the transparency and interpretability of the machine learning model.

---

# 💡 Model-Based Recommendations

For songs predicted as Low or Medium popularity, Songlytics can generate model-based suggestions.

The recommendation system identifies possible audio feature adjustments that may improve the model's predicted popularity score.

These recommendations are based on machine learning predictions and should not be interpreted as guaranteed real-world improvements.

---

# 🎛️ What-If Simulation

The What-If Simulation feature allows users to modify selected audio characteristics and observe how the predicted popularity score changes.

The system displays:

```text
Original Score
New Score
Score Difference
Changed Audio Features
```

Users can:

- Reset the simulation.
- Return to the original prediction result.
- Directly predict another song.

Simulation results represent changes in the model prediction and do not guarantee changes in real-world song popularity.

---

# 📚 Prediction and Simulation History

Registered users can save their prediction and simulation records.

The History page contains two sections:

```text
Prediction History
Simulation History
```

Users can:

- View previous records.
- View detailed information.
- Review audio features.
- Review simulation changes.
- Delete individual records.
- Generate PDF reports.

Prediction and simulation records are associated with the authenticated user.

---

# 📄 PDF Report Generation

Songlytics supports PDF report generation using **ReportLab**.

Prediction reports may include:

- Song information
- Prediction result
- Predicted popularity score
- Input method
- Prediction date
- Audio feature values

Simulation reports may include:

- Original score
- New score
- Score difference
- Modified audio features
- Simulation date

---

# 👤 User Account

Users can create an account to access additional system functionality.

Account features include:

- Registration
- Login
- Logout
- Edit profile
- Change password
- Forgot password
- Email OTP password reset

Guest users can still use prediction and analysis features, but prediction and simulation history will not be saved.

---

# 🔐 Security Features

Songlytics implements several security mechanisms.

## Password Hashing

Passwords are hashed using:

```text
bcrypt
```

Plain-text passwords are not stored in the PostgreSQL database.

---

## SQL Injection Protection

Database queries use parameterized SQL statements.

Example:

```python
cursor.execute(
    "SELECT * FROM users WHERE email = %s",
    (email,)
)
```

User input is passed separately from the SQL statement, which helps prevent SQL Injection attacks.

---

## Input Validation

The system validates:

- Username
- Email address
- Password
- User ID
- Prediction values

Password requirements include:

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

---

## Environment Variables

Sensitive credentials are stored in a `.env` file instead of being hard-coded into the source code.

Examples include:

```text
Database credentials
Spotify credentials
Email credentials
```

The `.env` file should not be uploaded to GitHub.

---

# 🗄️ Database

Songlytics uses **PostgreSQL** for persistent data storage.

Main database tables include:

```text
users
prediction_history
simulation_history
```

## Users Table

Stores:

```text
id
username
email
password_hash
created_at
last_login
```

## Prediction History

Stores:

```text
id
user_id
display_name
label
predicted_score
input_source
features
created_at
```

## Simulation History

Stores:

```text
id
user_id
display_name
original_score
new_score
changes
created_at
```

Prediction features and simulation changes are stored using JSON-compatible structures.

---

# 🧹 Dataset Preparation

The original Spotify dataset contained approximately:

```text
114,000 records
```

After preprocessing, the cleaned dataset contains:

```text
89,740 records
```

The preprocessing process includes:

```python
df = pd.read_csv("dataset.csv")

df = df.dropna()

df = df.drop_duplicates(
    subset="track_id",
    keep="first"
)

df = df.drop(
    columns=["Unnamed: 0"],
    errors="ignore"
)

df = df[
    df["popularity"].between(0, 100)
].copy()
```

The cleaned dataset contains no missing values and removes duplicate track IDs before model development.

---

# 🛠️ Technologies Used

## Frontend / Web Application

```text
Streamlit
```

## Programming Language

```text
Python
```

## Machine Learning

```text
Scikit-learn
Random Forest Regression
```

## Data Processing

```text
Pandas
NumPy
```

## Data Visualisation

```text
Plotly
Streamlit Charts
```

## Explainable AI

```text
SHAP
```

## Database

```text
PostgreSQL
psycopg2
```

## Password Security

```text
bcrypt
```

## PDF Generation

```text
ReportLab
```

## External Integration

```text
Spotify API
Gmail SMTP
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/TheanRuXin/Songlytics.git
```

Move into the project directory:

```bash
cd Songlytics
```

---

## 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate the environment:

```bash
venv\Scripts\activate
```

For macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Configuration

Create a `.env` file in the project root.

Example:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=songlytics
DB_USER=your_database_user
DB_PASSWORD=your_database_password

SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

EMAIL_ADDRESS=your_email@gmail.com
EMAIL_APP_PASSWORD=your_google_app_password
```

Do not upload the `.env` file to GitHub.

Add it to `.gitignore`:

```text
.env
```

---

# 🗄️ PostgreSQL Setup

Ensure PostgreSQL is installed and running.

Create a database for the project.

Example:

```sql
CREATE DATABASE songlytics;
```

Configure the database credentials in `.env`.

When Songlytics starts, the database initialization service will prepare the required database structure if supported by the current implementation.

---

# ▶️ Running Songlytics

Start the application using:

```bash
streamlit run app.py
```

After Streamlit starts, open the local address displayed in the terminal.

Usually:

```text
http://localhost:8501
```

---

# 🧭 System Navigation

The main navigation contains:

```text
🏠 Home
📊 Analysis
🎵 Prediction
📚 History
👤 Account
```

## Home

Provides an overview of Songlytics and its main functionality.

## Analysis

Provides interactive music analytics and dataset visualisations.

## Prediction

Allows users to search supported Spotify songs or manually enter audio features.

## History

Allows authenticated users to review prediction and simulation records.

## Account

Provides authentication and account management functionality.

---

# 🔄 Prediction Workflow

A typical prediction process is:

```text
Select Prediction Page
        ↓
Choose Input Method
        ↓
Spotify Search / Manual Input
        ↓
Load Audio Features
        ↓
Run Prediction
        ↓
Popularity Score
        ↓
SHAP Explanation
        ↓
Recommendations
        ↓
Optional What-If Simulation
```

After completing a prediction or simulation, users can directly select:

```text
Predict Another Song
```

to begin a new prediction without returning through previous pages.

---

# 🔄 Simulation Workflow

```text
Prediction Result
        ↓
What-If Simulation
        ↓
Modify Audio Features
        ↓
Run Simulation
        ↓
Compare Scores
        ↓
View Feature Changes
```

Users may then:

```text
Reset Simulation
Back to Prediction Result
Predict Another Song
```

```

The system should treat this input as normal data rather than executable SQL because parameterized SQL queries are used.

---

# ⚠️ Limitations

Song popularity cannot be completely determined by audio characteristics alone.

External factors such as:

- Artist popularity
- Marketing
- Playlist placement
- Social media exposure
- Release timing
- Fan base
- Promotion strategies

may significantly affect real-world popularity.

Therefore, Songlytics predictions should be interpreted as machine learning estimates rather than guaranteed future performance.

---

# 🚀 Future Improvements

Possible future enhancements include:

- Larger and more recent music datasets.
- Additional artist-level features.
- Streaming and social media features.
- Improved recommendation algorithms.
- More advanced machine learning models.
- Cloud deployment.
- Mobile application support.
- More detailed explainability reports.
- Real-time music trend analysis.

---

# 📌 Disclaimer

Songlytics is developed for academic and educational purposes.

Prediction results, recommendations, SHAP explanations and simulation outcomes are based on the trained machine learning model and the available dataset.

The system does not guarantee actual commercial or streaming success for any song.

---

# 👩‍💻 Developer

**Thean Ru Xin**

Final Year Project  
Software Development / Computing Project

---

# 📄 License

This project is developed for academic purposes.

Please contact the project developer before reusing substantial parts of the project source code, model or documentation.
