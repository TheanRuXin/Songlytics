# app/main.py
import streamlit as st
import os
import sys
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

st.set_page_config(
    page_title="Songlytics - AI Music Analytics Platform",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/songlytics',
        'Report a bug': "mailto:support@songlytics.com",
        'About': """
            ### Songlytics
            
            **AI-Powered Music Analytics Platform**
            
            - XGBoost Machine Learning Model
            - SHAP Explainable AI
            - Real-time Spotify API Integration
        """
    }
)

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
 
    .sidebar-user {
        padding: 10px;
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        color: white;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 10px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
        text-align: center;
    }
    
    .stMarkdown, .stMarkdown p, .stMarkdown div,
    .stMetric, .stMetric label, .stMetric div,
    p, span, div, label, .stText, .stCaption,
    .stSelectbox label, .stMultiSelect label {
        color: white !important;
    }
            
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    .stRadio label, .stRadio span, div[role="radiogroup"] label {
        color: white !important;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        background-color: #1e1e2e !important;
        color: white !important;
    }
    
    .stAlert, .stInfo, .stWarning, .stSuccess, .stError {
        color: #333 !important;
    }
    
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        text-align: center;
        padding: 10px;
        background: #1a1a2e;
        color: #888;
        font-size: 0.8rem;
        z-index: 999;
    }
    </style>
""", unsafe_allow_html=True)

def init_session():
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "email" not in st.session_state:
        st.session_state.email = None
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"
    if "previous_page" not in st.session_state:
        st.session_state.previous_page = None
    if "prediction_done" not in st.session_state:
        st.session_state.prediction_done = False
    if "temp_features_df" not in st.session_state:
        st.session_state.temp_features_df = None
    if "last_prediction_result" not in st.session_state:
        st.session_state.last_prediction_result = None
    if "last_explanation" not in st.session_state:
        st.session_state.last_explanation = None
    if "return_from_simulation" not in st.session_state:
        st.session_state.return_from_simulation = False
    if "sim_features" not in st.session_state:
        st.session_state.sim_features = None
    if "search_term" not in st.session_state:
        st.session_state.search_term = ""
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"

init_session()

from auth.login import show_login
from auth.register import show_register
from _pages.dashboard import show_dashboard
from _pages.prediction import show_prediction
from _pages.history import show_history
from _pages.profile import show_profile

def check_auth():
    if st.session_state.user_id is None or not st.session_state.logged_in:
        return False
    return True

def show_auth_page():
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.auth_mode == "login":
            show_login()
        else:
            show_register()

def main():
    if not check_auth():
        show_auth_page()
        return
     
    with st.sidebar:
        st.markdown(f"""
            <div class="sidebar-user">
                <div style="font-size: 2rem;">🎵</div>
                <div style="font-weight: bold;">{st.session_state.username}</div>
                <div style="font-size: 0.8rem; opacity: 0.7;">{st.session_state.email}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        menu_options = {
            "📊 Analytics": "dashboard",
            "🤖 Prediction": "prediction",
            "📜 History": "history",
            "👤 Profile": "profile"
        }
        
        selected_label = st.radio(
            "Navigation",
            list(menu_options.keys()),
            index=list(menu_options.values()).index(st.session_state.page) if st.session_state.page in menu_options.values() else 0,
            key="nav_menu"
        )
        
        selected_page = menu_options[selected_label]
        
        if selected_page != st.session_state.page:
            st.session_state.previous_page = st.session_state.page
            st.session_state.page = selected_page
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📊 Quick Stats")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Predictions", "0", delta=None)
        with col2:
            st.metric("Simulations", "0", delta=None)
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.markdown("---")

    st.markdown(f"""
        <div class="main-header">
            <h1>🎵 Songlytics</h1>
            <p>AI-Powered Music Analytics Platform</p>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.page == "dashboard":
        show_dashboard()
    elif st.session_state.page == "prediction":
        show_prediction()
    elif st.session_state.page == "history":
        show_history()
    elif st.session_state.page == "profile":
        show_profile()
    
    st.markdown("""
        <div class="footer">
            🎵 Songlytics | AI-Powered Music Analytics | XGBoost | SHAP | Spotify API
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()