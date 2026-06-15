# auth.py
import streamlit as st
from auth.login import show_login
from auth.register import show_register

def show_auth():
    
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
    
    if st.session_state.auth_mode == "login":
        show_login()
    elif st.session_state.auth_mode == "register":
        show_register()