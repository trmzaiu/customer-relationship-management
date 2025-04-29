import streamlit as st
from login_page import login_page
from register_page import register_page

if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "admin": "admin123"
    }

menu = ["Login", "Register"]
if st.session_state.get('logged_in'):
    menu = ["Dashboard", "Logout"]

choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Login":
    if st.session_state.get('logged_in'):
        st.success("Already logged in.")
    else:
        login_page(st.session_state.user_db)

elif choice == "Register":
    register_page(st.session_state.user_db)

elif choice == "Dashboard":
    st.title("🎯 CRM Dashboard")
    st.write(f"Hello, {st.session_state['username']} 👋")

elif choice == "Logout":
    st.session_state['logged_in'] = False
    st.session_state['username'] = ""
    st.experimental_rerun()
