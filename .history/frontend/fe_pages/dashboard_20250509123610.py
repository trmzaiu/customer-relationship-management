

import streamlit as st
import pandas as pd
import plotly.express as px
import time
import requests
import random
from datetime import datetime
import plotly.graph_objects as go

# from datetime import datetime, timedelta
# from utils.customer_generator import generate_customer_data, generate_interaction_data

CUSTOMER_API_URL = "http://localhost:5000/api/customers"
INTERACT_API_URL = "http://localhost:5000/api/interactions"


def dashboard_page(auto_refresh=False):
    while True:
        st.title("🏠 Dashboard Overview")

        # Get customer data from backend API
        try:
            response = requests.get(CUSTOMER_API_URL)
            if response.status_code == 200:
                customers_df = pd.DataFrame(response.json())
            else:
                st.error(f"Failed to load customer data. Status code: {response.status_code}")
                return
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return
        
        # Get interaction data from backend API
        try:
            response = requests.get(INTERACT_API_URL)
            if response.status_code == 200:
                interact_df = pd.DataFrame(response.json())
            else:
                st.error(f"Failed to load customer data. Status code: {response.status_code}")
                return
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return
        
        total_customers = customers_df.shape[0]
        vip_customers = customers_df[customers_df['type'] == 'VIP'].shape[0]
        regular_customers = customers_df[customers_df['type'] == 'Regular'].shape[0]
        new_customers = customers_df[customers_df['type'] == 'New'].shape[0]

        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Customers", total_customers)
        col2.metric("VIP Customers", vip_customers)
        col3.metric("Regular Customers", regular_customers)
        col4.metric("New Customers", new_customers)

        st.divider()

        # Customer Distribution
        st.header("🧠 Customer Distribution")
        customer_summary = customers_df['type'].value_counts().reset_index()
        customer_summary.columns = ['Customer Type', 'Count']

        col5, col6 = st.columns(2)
        with col5:
            fig_pie = px.pie(customer_summary, names='Customer Type', values='Count', title='Customer Distribution', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        with col6:
            fig_bar = px.bar(customer_summary, x='Customer Type', y='Count', title='Customer Count', color='Customer Type')
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # Weekly Interactions
        st.header("📈 Weekly Interaction Trends")
        interact_df['date'] = pd.to_datetime(interact_df['date'], format='%a, %d %b %Y %H:%M:%S GMT', errors='coerce')
        interact_df = interact_df.dropna(subset=['date'])

        interact_df['date'] = interact_df['date'].dt.date

        weekly_trend = interact_df.groupby('date').size().reset_index(name='Interactions')
        weekly_trend = weekly_trend.rename(columns={'date': 'Date'})

        fig_line = px.line(weekly_trend, x='Date', y='Interactions', markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

        if auto_refresh:
            time.sleep(10)
            st.rerun()
        else:
            break