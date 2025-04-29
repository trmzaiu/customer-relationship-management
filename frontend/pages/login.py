import streamlit as st

def login_page(user_db):
    st.title("Login Page")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            if authenticate(username, password, user_db):
                st.success(f"Welcome, {username}!")
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
            else:
                st.error("Invalid username or password.")

def authenticate(username, password, user_db):
    return user_db.get(username) == password
