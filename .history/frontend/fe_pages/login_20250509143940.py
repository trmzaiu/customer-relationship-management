import streamlit as st
from utils.user_generator import hash_password
import requests

def login_page(user_db):
    col1, col2, col3 = st.columns([3, 3, 3])
    with col2:
        st.title("Login")

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("Login")

            if login_button:
                if authenticate_with_flask(username, password):
                    st.success(f"Welcome, {username}!")
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

def authenticate(username, password, user_db):
    hashed_pw = hash_password(password)
    return user_db.get(username) == hashed_pw

def authenticate_with_flask(username, password):
    """Authenticate by making a request to Flask backend."""
    try:
        # Configure your Flask API URL here
        flask_api_url = "http://localhost:5000/api/login"
        
        # Send POST request to Flask API
        response = requests.post(
            flask_api_url,
            json={"username": username, "password": password}
        )
        # Check if authentication was successful
        if response.status_code == 200:
            user_data = response.json().get('user_data', {})
            if user_data:
                if 'is_admin' in user_data:
                    st.session_state['is_admin'] = user_data['is_admin']
                if 'user_id' in user_data:
                    st.session_state['user_id'] = user_data['user_id']
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return False