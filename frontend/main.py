import streamlit as st
import sys
import os

# Add paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))

from login import login_page
from dashboard import dashboard_page
from user_generator import load_user_db

st.set_page_config(page_title="CRM App", layout="wide")

# Initialize session state
if 'user_db' not in st.session_state:
    st.session_state.user_db = load_user_db()
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Show only login if not logged in
if st.session_state.get('logged_in') == False:
    login_page(st.session_state.user_db)
else:
    # Show sidebar only if logged in
    menu = ["Dashboard", "Logout"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Dashboard":
        dashboard_page()
    elif choice == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.user_db = {}
        st.session_state['logged_in'] = False
        # Rerun after logout
        st.runtime.legacy_rerun()
