import streamlit as st
import sys
import os

st.set_page_config(
    page_title="CRM System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'service')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))

from login import login_page
from dashboard import dashboard_page
from interactions import interaction_page
from customers import customer_page
from interact_customer import interact_customer_page
from reports import report_page
from widget import initialize_session_state, load_css, navigation

load_css()
initialize_session_state()

if not st.session_state.logged_in:
    login_page(st.session_state.user_db)
else:
    navigation()
    
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
    elif page == "Logout":
        st.session_state.logged_in = False
        st.rerun()