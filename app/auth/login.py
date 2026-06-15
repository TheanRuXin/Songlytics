import streamlit as st
from services.user_service import authenticate_user

def show_login():
    
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #1a2a2a 0%, #2a1f1f 50%, #1a1a1a 100%) !important;
        }

        .login-title {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(120deg, #4ecdc4, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 20px;
        }

        .stForm {
            background: rgba(30, 30, 40, 0.6);
            border-radius: 20px;
            padding: 10px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(78, 205, 196, 0.2);
        }

        .stButton button {
            background: linear-gradient(135deg, #2d2d2d) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
        }

        .stMarkdown, .stMarkdown p, .stCaption {
            color: #e0e0e0 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="login-title">🎵 Welcome to Songlytics</p>', unsafe_allow_html=True)
    st.caption("Login to access your music analytics dashboard")
  
    with st.form("login_form", clear_on_submit=False):
        
        email = st.text_input(
            "📧 Email",
            placeholder="your@email.com",
            help="Enter your registered email address"
        )
        
        password = st.text_input(
            "🔒 Password",
            type="password",
            placeholder="Enter your password",
            help="Your password is encrypted with bcrypt"
        )
        
        col1, col2 = st.columns(2)
        
        submitted = st.form_submit_button("🔐 Login", type="primary", use_container_width=True)
        
        if submitted:
            if not email or not password:
                st.warning("⚠️ Please enter both email and password")
            else:
                with st.spinner("Authenticating..."):
                    user = authenticate_user(email, password)
                
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user["id"]
                    st.session_state.username = user["username"]
                    st.session_state.email = user["email"]
                    st.session_state.auth_mode = None
                    
                    st.success(f"✅ Welcome back, {user['username']}!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password")
    

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<p style="text-align: center;">Don\'t have an account?</p>', unsafe_allow_html=True)
        if st.button("📝 Create New Account", use_container_width=True):
            st.session_state.auth_mode = "register"
            st.rerun()
    