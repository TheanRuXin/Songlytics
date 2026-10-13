import streamlit as st

from services.db_service import initialize_database
from services.auth_service import (
    register_user,
    authenticate_user,
    get_user_by_id
)

@st.cache_resource
def setup_database():
    return initialize_database()

def initialize_auth_state():
    defaults = {
        "authenticated": False,
        "user_id": None,
        "username": None,
        "email": None
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def set_logged_in_user(user):
    st.session_state["authenticated"] = True
    st.session_state["user_id"] = user["id"]
    st.session_state["username"] = user["username"]
    st.session_state["email"] = user["email"]

def logout_user():
    auth_keys = [
        "authenticated",
        "user_id",
        "username",
        "email"
    ]

    prediction_keys = [
        "prediction_done",
        "temp_features_df",
        "temp_song_name",
        "temp_artist_name",
        "temp_input_source",
        "last_prediction_result",
        "last_features_df",
        "last_explanation",
        "sim_features",
        "song_name",
        "song_name_for_sim",
        "show_simulation_mode"
    ]

    for key in auth_keys + prediction_keys:
        st.session_state.pop(key, None)

    initialize_auth_state()

def show_logged_in():
    user_id = st.session_state.get("user_id")
    user = get_user_by_id(user_id)

    if not user:
        logout_user()
        st.error("Unable to load user account.")
        return

    st.markdown(
        """
        <style>
        .account-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(120deg, #4ecdc4, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
        }

        .account-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 28px;
            color: white;
            margin: 20px 0;
        }

        .account-name {
            font-size: 2rem;
            font-weight: 700;
        }

        .account-detail {
            font-size: 1rem;
            opacity: 0.9;
            margin-top: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="account-title">👤 My Account</p>',
        unsafe_allow_html=True
    )

    st.caption("Manage your SONGlytics account and session")

    st.markdown(
        f"""
        <div class="account-card">
            <div style="font-size: 0.9rem; opacity: 0.85;">
                Logged in as
            </div>

            <div class="account-name">
                {user["username"]}
            </div>

            <div class="account-detail">
                📧 {user["email"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "User ID",
            user["id"]
        )

    with col2:
        if user.get("last_login"):
            st.metric(
                "Last Login",
                user["last_login"].strftime(
                    "%d %b %Y %H:%M"
                )
            )
        else:
            st.metric(
                "Last Login",
                "Current session"
            )

    st.info(
        "Your prediction and simulation history will be "
        "saved automatically while you are logged in."
    )

    st.divider()

    if st.button(
        "🚪 Log Out",
        type="primary",
        use_container_width=True
    ):
        logout_user()
        st.success("Logged out successfully.")
        st.rerun()

def show_login_form():
    st.markdown("### 🔐 Login")

    identifier = st.text_input(
        "Username or Email",
        placeholder="Enter your username or email",
        key="login_identifier"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        key="login_password"
    )

    if st.button(
        "🔓 Login",
        type="primary",
        use_container_width=True,
        key="login_button"
    ):
        if not identifier.strip():
            st.warning(
                "Please enter your username or email."
            )
            return

        if not password:
            st.warning(
                "Please enter your password."
            )
            return

        with st.spinner(
            "Signing in..."
        ):
            result = authenticate_user(
                identifier,
                password
            )

        if result["success"]:
            set_logged_in_user(
                result["user"]
            )

            st.success(
                f"Welcome back, "
                f"{result['user']['username']}!"
            )

            st.rerun()

        else:
            st.error(
                result["message"]
            )

def show_register_form():
    st.markdown("### ✨ Create Account")

    username = st.text_input(
        "Username",
        placeholder="Choose a username",
        key="register_username"
    )

    email = st.text_input(
        "Email",
        placeholder="you@example.com",
        key="register_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Create a strong password",
        key="register_password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Enter the password again",
        key="register_confirm_password"
    )

    st.caption(
        "Password must contain at least 8 characters, "
        "including uppercase, lowercase and a number."
    )

    if st.button(
        "🚀 Create Account",
        type="primary",
        use_container_width=True,
        key="register_button"
    ):
        if not username.strip():
            st.warning(
                "Please enter a username."
            )
            return

        if not email.strip():
            st.warning(
                "Please enter an email address."
            )
            return

        if not password:
            st.warning(
                "Please enter a password."
            )
            return

        if password != confirm_password:
            st.error(
                "Passwords do not match."
            )
            return

        with st.spinner(
            "Creating your account..."
        ):
            result = register_user(
                username,
                email,
                password
            )

        if result["success"]:
            set_logged_in_user(
                result["user"]
            )

            st.success(
                "Account created successfully!"
            )

            st.rerun()

        else:
            st.error(
                result["message"]
            )

def show_login():
    initialize_auth_state()

    if not setup_database():
        st.error(
            "Unable to connect to the SONGlytics database."
        )

        st.caption(
            "Please check your PostgreSQL server and .env configuration."
        )

        return

    if st.session_state.get(
        "authenticated",
        False
    ):
        show_logged_in()
        return

    st.markdown(
        """
        <style>
        .login-title {
            font-size: 2.6rem;
            font-weight: 700;
            background: linear-gradient(120deg, #4ecdc4, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
        }

        .login-subtitle {
            font-size: 1rem;
            opacity: 0.8;
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="login-title">🎵 Welcome to SONGlytics</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="login-subtitle">'
        'Sign in to save predictions, simulations and history.'
        '</p>',
        unsafe_allow_html=True
    )

    login_tab, register_tab = st.tabs(
        [
            "🔐 Login",
            "✨ Register"
        ]
    )

    with login_tab:
        show_login_form()

    with register_tab:
        show_register_form()

    st.divider()

    st.caption(
        "🔒 Passwords are securely hashed before being stored "
        "in PostgreSQL."
    )