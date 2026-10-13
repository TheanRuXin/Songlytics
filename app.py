import streamlit as st

from services.db_service import initialize_database
from _pages.prediction import show_prediction
from _pages.history import show_history
from _pages.login import show_login, logout_user
from _pages.analysis import show_analysis


st.set_page_config(
    page_title="SONGlytics",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def setup_database():
    return initialize_database()

def initialize_session():
    defaults = {
        "authenticated": False,
        "user_id": None,
        "username": None,
        "email": None,
        "show_simulation_mode": False
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def show_home():
    st.markdown(
        """
        <style>
        .home-title {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(120deg, #4ecdc4, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
        }

        .home-subtitle {
            font-size: 1.1rem;
            opacity: 0.8;
            margin-bottom: 30px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="home-title">🎵 SONGlytics</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="home-subtitle">AI-powered song popularity prediction and music analytics.</p>',
        unsafe_allow_html=True
    )

    st.markdown("### Welcome to SONGlytics")

    st.write(
        "SONGlytics analyzes musical characteristics and uses machine learning "
        "to estimate a song's popularity score while providing interactive "
        "analytics and model explanations."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("### 🔮 Popularity Prediction")
            st.write(
                "Predict a continuous popularity score from 0 to 100 "
                "using the Random Forest regression model."
            )

    with col2:
        with st.container(border=True):
            st.markdown("### 📊 Music Analytics")
            st.write(
                "Explore song and audio-feature patterns through "
                "interactive Power BI visualizations."
            )

    with col3:
        with st.container(border=True):
            st.markdown("### 🧠 Explainable AI")
            st.write(
                "Use SHAP analysis to understand which characteristics "
                "push a model prediction higher or lower."
            )

    st.markdown("### SONGlytics Features")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("#### 🎧 Multiple Input Methods")
            st.write(
                "Search songs through Spotify, select songs from the "
                "SONGlytics dataset, or manually enter audio characteristics."
            )

        with st.container(border=True):
            st.markdown("#### 🎛️ What-If Simulation")
            st.write(
                "Change selected audio characteristics and observe how "
                "the model's predicted popularity score responds."
            )

    with col2:
        with st.container(border=True):
            st.markdown("#### 📈 Power BI Analysis")
            st.write(
                "View interactive dashboards for popularity distributions, "
                "genres, audio characteristics and dataset trends."
            )

        with st.container(border=True):
            st.markdown("#### 🔐 Personal History")
            st.write(
                "Sign in to securely save predictions and simulations "
                "in PostgreSQL for later review."
            )

    st.divider()

    st.caption(
        "Random Forest Regression | SHAP Explainability | "
        "Power BI | PostgreSQL | Spotify Integration"
    )

def show_sidebar():
    with st.sidebar:
        st.markdown("## 🎵 SONGlytics")
        st.caption("Song Popularity Analytics")

        st.divider()

        if st.session_state.get("authenticated", False):
            username = st.session_state.get("username", "User")

            st.success(
                f"👤 Signed in as **{username}**"
            )
        else:
            st.info("👤 Guest Mode")
            st.caption(
                "Sign in to save prediction and simulation history."
            )

        st.divider()

        navigation = st.radio(
            "Navigation",
            [
                "🏠 Home",
                "📊 Analysis",
                "🎵 Prediction",
                "📚 History",
                "👤 Account"
            ],
            key="main_navigation"
        )

        st.divider()

        if st.session_state.get("authenticated", False):
            if st.button(
                "🚪 Log Out",
                use_container_width=True,
                key="sidebar_logout"
            ):
                logout_user()
                st.rerun()

        st.caption("SONGlytics FYP")

        return navigation

def main():
    initialize_session()

    database_ready = setup_database()

    if not database_ready:
        st.warning(
            "⚠️ PostgreSQL is currently unavailable. "
            "Prediction and analysis can still be used, "
            "but login and history may be unavailable."
        )

    navigation = show_sidebar()

    if navigation == "🏠 Home":
        show_home()

    elif navigation == "📊 Analysis":
        show_analysis()

    elif navigation == "🎵 Prediction":
        show_prediction()

    elif navigation == "📚 History":
        show_history()

    elif navigation == "👤 Account":
        show_login()


if __name__ == "__main__":
    main()