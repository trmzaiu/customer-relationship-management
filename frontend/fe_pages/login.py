import streamlit as st
from utils.user_generator import hash_password

def login_page(user_db):
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.title("Login")

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("Login")

            if login_button:
                if authenticate(username, password, user_db):
                    st.success(f"Welcome, {username}!")
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.session_state['user_db'] = user_db
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

def authenticate(username, password, user_db):
    hashed_pw = hash_password(password)
    return user_db.get(username) == hashed_pw
