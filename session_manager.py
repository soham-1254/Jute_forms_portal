import streamlit as st
from datetime import datetime, timedelta

TIMEOUT_MINUTES = 5  # Auto logout after 5 mins of inactivity

def init_session():
    if "user" not in st.session_state:
        st.session_state.user = None
        st.session_state.role = None
        st.session_state.last_active = datetime.now()
        st.session_state.logged_in = False
        st.session_state.login_error = False

def login_user(username, role):
    st.session_state.user = username
    st.session_state.role = role
    st.session_state.last_active = datetime.now()
    st.session_state.logged_in = True
    # ✅ NO st.rerun() here

def logout_user():
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.last_active = datetime.now()
    st.session_state.logged_in = False
    # ✅ NO st.rerun() here

def check_timeout():
    if st.session_state.get("logged_in", False):
        last = st.session_state.get("last_active", datetime.now())
        if datetime.now() - last > timedelta(minutes=TIMEOUT_MINUTES):
            st.warning("⚠️ Session expired due to inactivity. Please log in again.")
            logout_user()
        else:
            st.session_state.last_active = datetime.now()
