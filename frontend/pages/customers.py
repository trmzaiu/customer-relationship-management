import streamlit as st
import pandas as pd
from utils.data_generator import generate_customer_data

def show():
    st.title("👥 Customer Management")

    customers_df = generate_customer_data()

    # Filter by Type
    customer_type = st.selectbox("Filter by Customer Type", options=["All", "VIP", "Regular", "New"])
    if customer_type != "All":
        customers_df = customers_df[customers_df['Type'] == customer_type]

    st.dataframe(customers_df, use_container_width=True)
