# register.py
import streamlit as st
import re
from services.user_service import register_user
from services.validation_service import validate_email, validate_password

def show_register():
 
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #1a2a2a 0%, #2a1f1f 50%, #1a1a1a 100%) !important;
        } 
        .register-title {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(120deg, #4ecdc4, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .register-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 30px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .password-strength {
            margin-top: 5px;
            font-size: 0.8rem;
        }
        
        .strength-weak { color: #ff6b6b; }
        .strength-medium { color: #feca57; }
        .strength-strong { color: #48dbfb; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="register-title">🎵 Create Account</p>', unsafe_allow_html=True)
    st.caption("Join Songlytics and discover music insights")
    
    # ==========================================
    # 注册表单
    # ==========================================
    with st.form("register_form", clear_on_submit=False):
        
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input(
                "👤 Username",
                placeholder="Choose a unique username",
                help="Username can contain letters, numbers, and underscores"
            )
        
        with col2:
            email = st.text_input(
                "📧 Email",
                placeholder="your@email.com",
                help="We'll never share your email"
            )
        
        st.markdown("---")
        
        password = st.text_input(
            "🔒 Password",
            type="password",
            placeholder="Create a strong password",
            help="Minimum 8 characters, include uppercase, lowercase, and numbers"
        )
        
        # 实时密码强度显示
        if password:
            strength, strength_text, strength_class = check_password_strength(password)
            st.markdown(f"""
                <div class="password-strength">
                    Password strength: <span class="{strength_class}">{strength_text}</span>
                </div>
            """, unsafe_allow_html=True)
        
        confirm_password = st.text_input(
            "✓ Confirm Password",
            type="password",
            placeholder="Re-enter your password"
        )
        
        # 密码匹配提示
        if password and confirm_password:
            if password != confirm_password:
                st.error("❌ Passwords do not match")
            else:
                st.success("✅ Passwords match")
        
        st.markdown("---")
        
        # 条款同意
        agree_terms = st.checkbox(
            "I agree to the Terms of Service and Privacy Policy",
            value=False
        )
        
        
        submitted = st.form_submit_button("🚀 Create Account", type="primary", use_container_width=True)
        
        if submitted:
            
            if not username or not email or not password:
                st.warning("⚠️ Please fill in all fields")
                return
            
            if not agree_terms:
                st.warning("⚠️ Please agree to the Terms of Service")
                return
            
            
            if not validate_username(username):
                st.error("❌ Username must be 3-20 characters and contain only letters, numbers, and underscores")
                return

            if not validate_email(email):
                st.error("❌ Please enter a valid email address")
                return

            valid, msg = validate_password(password)
            if not valid:
                st.error(f"❌ {msg}")
                return
            
            if password != confirm_password:
                st.error("❌ Passwords do not match")
                return
  
            try:
                with st.spinner("Creating your account..."):
                    user_id, message = register_user(username, email, password)
                
                if user_id:
                    st.success("✅ Registration successful!")
                    st.info("🎉 Welcome to Songlytics! Please login to continue.")
                
                    import time
                    time.sleep(1.5)
                    st.session_state.auth_mode = "login"
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
                    
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Already have an account? Login here", use_container_width=True):
            st.session_state.auth_mode = "login"
            st.rerun()
    
    st.markdown("---")
    st.caption("🔒 Your data is secure with bcrypt encryption")

def check_password_strength(password):
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("At least 8 characters")
    
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Uppercase letter")
    
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Lowercase letter")
    
    if re.search(r'[0-9]', password):
        score += 1
    else:
        feedback.append("Number")
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append("Special character")
    
    if score <= 2:
        return "weak", "Weak - " + ", ".join(feedback[:2]) + "...", "strength-weak"
    elif score <= 4:
        return "medium", "Medium - Could be stronger", "strength-medium"
    else:
        return "strong", "Strong - Good password!", "strength-strong"

def validate_username(username):
    if not username:
        return False
    if len(username) < 3 or len(username) > 20:
        return False
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False
    return True