import streamlit as st
import sys
import os

# Add paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))

from login import login_page
from dashboard import dashboard_page
from interactions import interaction_page
from customers import customer_page
from interact_customer import interact_customer_page
from reports import report_page
from user_generator import load_user_db 

st.set_page_config(page_title="CRM App", layout="wide")

if 'user_db' not in st.session_state:
    st.session_state.user_db = load_user_db()
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page(st.session_state.user_db)
else:
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"

    # Sidebar UI
    st.sidebar.title("Admin Dashboard")
    if st.sidebar.button("🏠 Dashboard"):
        st.session_state.current_page = "Dashboard"
    if st.sidebar.button("👥 Customers"):
        st.session_state.current_page = "Customers"
    if st.sidebar.button("💬 Interactions"):
        st.session_state.current_page = "Interactions"
    if st.sidebar.button("📊 Reports"):
        st.session_state.current_page = "Reports"
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.pop("username", None)
        st.session_state.pop("current_page", None)
        st.rerun()

    # Render selected page
    page = st.session_state.current_page
    if page == "Dashboard":
        dashboard_page()
    elif page == "Customers":
        customer_page()
    elif page == "Interactions":
        interaction_page()
    elif page == "Interact With Customer":
        interact_customer_page()
    elif page == "Reports":
        report_page()

def main():
    load_css()
    initialize_session_state()
    navigation()
    
    current_page = st.session_state.current_page
    
    if current_page == "Dashboard":
        dashboard_page()
    elif current_page == "Customers":
        customer_page()
    elif current_page == "Interactions":
        interaction_page()
    elif current_page == "Interact With Customer":
        interact_customer_page()
    elif current_page == "Reports":
        report_page()
    elif current_page == "Logout":

if __name__ == "__main__":
    main()