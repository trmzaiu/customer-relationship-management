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
        res = requests.get(INTERACT_API_URL)
        if res.status_code == 200:
            data = res.json()

            if not data:
                st.info("No interactions found.")
            else:
                display_fields = ["customer_id", "type", "notes", "date"]
                df = pd.DataFrame(data)[display_fields]

                df = df.rename(columns={
                    "customer_id": "Customer",
                    "type": "Interaction Type",
                    "notes": "Notes",
                    "date": "Date"
                })

                df["Date"] = pd.to_datetime(df["Date"], format="%a, %d %b %Y %H:%M:%S %Z")
                df["Date"] = df["Date"].dt.strftime("%b %d, %Y %H:%M")
                
                if 'Customer' in df.columns:
                    df['Customer'] = df['Customer'].astype(str)
                    
                    customer_names = []
                    for customer_id in df['Customer']:
                        _, customer_data = check_customer_id_exist(customer_id)
                        customer_names.append(customer_data)
                        print(c)
                    df['Customer'] = customer_names
                    
                st.dataframe(df)
        else:
            st.error(f"Failed to fetch data: {res.status_code}")
    except Exception as e:
        st.error(f"Error: {e}")

    if st.button("➕ Add New Interaction"):
        st.session_state.current_page = "Interact With Customer"
        st.rerun()
