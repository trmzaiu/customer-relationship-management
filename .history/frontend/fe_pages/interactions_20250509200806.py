import streamlit as st
import pandas as pd
import requests
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))

from widget import INTERACT_API_URL, check_customer_id_exist

def interaction_page():
    st.title("📞 Interactions")
    st.header("Interaction History")

    try:
        
    except Exception as e:
        st.error(f"Error: {e}")

    if st.button("➕ Add New Interaction"):
        st.session_state.current_page = "Interact With Customer"
        st.rerun()
