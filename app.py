import streamlit as st

from services.db_service import initialize_database
from _pages.prediction import show_prediction
from _pages.history import show_history
from _pages.login import show_login, logout_user
from _pages.analysis import show_analysis
from _pages.profile import show_profile

st.set_page_config(
    page_title="Songlytics",
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
        "<h1 style='font-size:70px;'>🎵 Songlytics</h1>",
        unsafe_allow_html=True
    )

    st.subheader(
        "Music Analytics and Song Popularity Prediction Platform"
    )

    st.write(
        "Songlytics uses machine learning to predict song popularity "
        "and provides music analytics, explainable AI, recommendations "
        "and what-if simulation."
    )

    st.divider()

    st.header("Main Functions")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📊 Analysis")
        st.write(
            "Explore popularity trends, genres "
            "and audio feature patterns."
        )

    with col2:
        st.subheader("🔮 Prediction")
        st.write(
            "Predict song popularity using "
            "Random Forest Regression."
        )

    with col3:
        st.subheader("🧠 Explainable AI")
        st.write(
            "Understand how audio features "
            "influence the prediction."
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎛️ What-If Simulation")
        st.write(
            "Change audio features and observe "
            "the new predicted score."
        )

    with col2:
        st.subheader("📚 History")
        st.write(
            "Review previous predictions and "
            "simulation results."
        )

    st.divider()

    st.caption(
        "Streamlit | Python | Random Forest Regression | "
        "SHAP | PostgreSQL | Spotify"
    )

def show_sidebar():
    with st.sidebar:
        st.markdown(
            "## 🎵 Songlytics"
        )

        st.caption(
            "Music Analytics & Popularity Prediction"
        )

        st.divider()

        if st.session_state.get(
            "authenticated",
            False
        ):
            username = (
                st.session_state.get(
                    "username",
                    "User"
                )
            )

            st.success(
                f"👤 Signed in as **{username}**"
            )

        else:
            st.info(
                "👤 Guest Mode"
            )

            st.caption(
                "Sign in to save prediction "
                "and simulation history."
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

        if st.session_state.get(
            "authenticated",
            False
        ):
            if st.button(
                "🚪 Log Out",
                use_container_width=True,
                key="sidebar_logout"
            ):
                logout_user()
                st.rerun()

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

        if st.session_state.get(
            "authenticated",
            False
        ):
            show_profile()

        else:
            show_login()


if __name__ == "__main__":
    main()