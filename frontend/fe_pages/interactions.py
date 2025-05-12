import streamlit as st
import pandas as pd
import requests
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'service')))

from api import get_interaction

def interaction_page():
    st.title("📞 Interactions")

    st.header("Interaction History")

    try:
        data = get_interaction()

        if not data:
            st.info("No interactions found.")
        else:
            display_fields = ["customer", "type", "notes", "date"]
            df = pd.DataFrame(data)[display_fields]

            df = df.rename(columns={
                "customer": "Customer",
                "type": "Interaction Type",
                "notes": "Notes",
                "date": "Date"
            })

            df["Date"] = pd.to_datetime(df["Date"])
            df["Date"] = df["Date"].dt.strftime("%b %d %Y %H:%M")

            st.dataframe(df)
    except Exception as e:
        st.error(f"Error: {e}")

    if st.button("➕ Add New Interaction"):
        st.session_state.current_page = "Interact With Customer"
        st.rerun()
