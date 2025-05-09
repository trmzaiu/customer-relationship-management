import streamlit as st
import pandas as pd
import requests
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))

from widget import CUSTOMER_API_URL

def interaction_page():
    st.title("📞 Interactions")

    st.header("Interaction History")

    try:
        res = requests.get(CUSTOMER_API_URL)
        if res.status_code == 200:
            data = res.json()

            if not data:
                st.info("No interactions found.")
            else:
                # Create DataFrame from the data
                df = pd.DataFrame(data)
                
                # Check which fields are available in the data
                available_fields = df.columns.tolist()
                
                # Define the fields we want to display (only those that exist in the data)
                possible_fields = {
                    "customer_id": "Customer ID",
                    "type": "Interaction Type",
                    "notes": "Notes",
                    "date": "Date",
                }
                
                # Select only fields that exist in the data
                display_fields = [field for field in possible_fields.keys() if field in available_fields]
                
                if not display_fields:
                    st.error("No displayable fields found in the data.")
                    return
                
                # Select and rename the fields
                df = df[display_fields].rename(columns=possible_fields)
                
                # Try to format date if present (checking for either 'date' or 'created_at')
                date_column = None
                if "Date" in df.columns:
                    date_column = "Date"
                elif "Created At" in df.columns:
                    date_column = "Created At"
                
                if date_column:
                    try:
                        df[date_column] = pd.to_datetime(df[date_column]).dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        st.warning("Could not format date column")
                
                st.dataframe(df)
        else:
            st.error(f"Failed to fetch data: {res.status_code}")
    except Exception as e:
        st.error(f"Error: {e}")

    if st.button("➕ Add New Interaction"):
        st.session_state.current_page = "Interact With Customer"
        st.rerun()