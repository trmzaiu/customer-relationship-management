# import streamlit as st

# def register_page(user_db):
#     st.title("Register")

#     with st.form("register_form"):
#         new_username = st.text_input("Choose a username")
#         new_password = st.text_input("Choose a password", type="password")
#         confirm_password = st.text_input("Confirm password", type="password")
#         register_button = st.form_submit_button("Register")

#         if register_button:
#             if new_username in user_db:
#                 st.error("Username already exists. Please choose another one.")
#             elif new_password != confirm_password:
#                 st.error("Passwords do not match.")
#             elif not new_username or not new_password:
#                 st.error("Please fill in all fields.")
#             else:
#                 user_db[new_username] = new_password
#                 st.success("Registration successful! Please go to the Login page.")
