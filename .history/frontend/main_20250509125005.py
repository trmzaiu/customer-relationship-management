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

def main():
    st.set_page_config(page_title="CRM App", layout="wide")
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

if __name__ == "__main__":
    main()