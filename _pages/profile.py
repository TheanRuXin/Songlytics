# profile.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from services.history_service import get_user_predictions, get_user_simulations
from services.user_service import get_user_by_id, update_user_profile

def show_profile():
    st.markdown("""
        <style>
        .profile-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(120deg, #4ecdc4, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
        }
        
        .profile-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 25px;
            color: white;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
        }
        
        .stat-label {
            font-size: 0.9rem;
        }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="profile-title">👤 My Profile</p>', unsafe_allow_html=True)
    st.caption("Manage your account information")
    
    user_id = st.session_state.get("user_id", 1)
    user = get_user_by_id(user_id)

    if user is None:
        st.error("User not found. Please login again.")
        if st.button("Go to Login"):
            st.session_state.clear()
            st.rerun()
        return
    
    username = user.get("username", "N/A")
    email = user.get("email", "N/A")
    created_at = user.get("created_at", "N/A")
    
    # 获取统计数据
    df_pred = get_user_predictions(user_id)
    df_sim = get_user_simulations(user_id)
    
    # 统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(df_pred)}</div>
                <div class="stat-label">Total Predictions</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(df_sim)}</div>
                <div class="stat-label">Total Simulations</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        high_count = len(df_pred[df_pred["prediction"] == "High Popularity"]) if not df_pred.empty else 0
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{high_count}</div>
                <div class="stat-label">High Popularity Songs</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # 计算平均置信度
        avg_conf = df_pred['probability'].mean() if not df_pred.empty else 0
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{avg_conf:.0f}%</div>
                <div class="stat-label">Avg Confidence</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 账户信息
    st.subheader("📋 Account Information")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 显示当前信息
        st.markdown(f"""
            <div class="info-row">
                <span style="font-weight: bold;">👤 Username</span>
                <span>{username}</span>
            </div>
            <div class="info-row">
                <span style="font-weight: bold;">📧 Email</span>
                <span>{email}</span>
            </div>
            <div class="info-row">
                <span style="font-weight: bold;">📅 Member Since</span>
                <span>{created_at}</span>
            </div>
            <div class="info-row">
                <span style="font-weight: bold;">🕐 Last Active</span>
                <span>{datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # 简单图表：最近7天活动
        if not df_pred.empty and 'created_at' in df_pred.columns:
            df_pred['date'] = pd.to_datetime(df_pred['created_at'])
            weekly_activity = df_pred.groupby(df_pred['date'].dt.date).size().tail(7)
            st.caption("Last 7 days activity")
            st.line_chart(weekly_activity, height=150)
    
    st.markdown("---")
    
    # 编辑设置
    st.subheader("⚙️ Edit Profile")
    
    with st.expander("✏️ Edit Account Information", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            new_username = st.text_input("New Username", value=username)
            new_email = st.text_input("New Email", value=email)
        
        with col2:
            new_password = st.text_input("New Password", type="password", placeholder="Leave blank to keep current")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm new password")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            if st.button("💾 Save Changes", type="primary"):
                if new_password and new_password != confirm_password:
                    st.error("❌ Passwords do not match!")
                elif new_password and len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters!")
                else:
                    success = update_user_profile(
                        user_id, 
                        new_username, 
                        new_email, 
                        new_password if new_password else None
                    )
                    if success:
                        st.success("✅ Profile updated successfully!")
                        st.session_state.username = new_username
                        st.rerun()
                    else:
                        st.error("❌ Failed to update profile")
        
        with col_btn2:
            if st.button("🔄 Reset"):
                st.rerun()
    
    st.markdown("---")
    st.caption(f"🎵 Songlytics | Member since {created_at.strftime('%Y-%m-%d')}")