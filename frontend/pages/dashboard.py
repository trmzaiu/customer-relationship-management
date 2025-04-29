import streamlit as st
import pandas as pd
import plotly.express as px
import time
from utils.data_generator import generate_customer_data, generate_interaction_data

def show(auto_refresh=False):
    while True:
        st.title("🏠 Dashboard Overview")

        # Load fake data
        customers_df = generate_customer_data()
        interactions_df = generate_interaction_data()

        total_customers = customers_df.shape[0]
        vip_customers = customers_df[customers_df['Type'] == 'VIP'].shape[0]
        regular_customers = customers_df[customers_df['Type'] == 'Regular'].shape[0]
        new_customers = customers_df[customers_df['Type'] == 'New'].shape[0]

        weekly_interactions = interactions_df.shape[0]

        # KPIs
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Customers", total_customers)
        col2.metric("VIP Customers", vip_customers)
        col3.metric("Regular Customers", regular_customers)
        col4.metric("New Customers", new_customers)
        col5.metric("Interactions This Week", weekly_interactions)

        st.divider()

        # Customer Distribution
        st.header("🧠 Customer Distribution")
        customer_summary = customers_df['Type'].value_counts().reset_index()
        customer_summary.columns = ['Customer Type', 'Count']

        col6, col7 = st.columns(2)
        with col6:
            fig_pie = px.pie(customer_summary, names='Customer Type', values='Count',
                             title='Customer Distribution', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        with col7:
            fig_bar = px.bar(customer_summary, x='Customer Type', y='Count',
                             title='Customer Count', color='Customer Type')
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # Weekly Interactions
        st.header("📈 Weekly Interaction Trends")
        weekly_trend = interactions_df.groupby('Date').size().reset_index(name='Interactions')
        fig_line = px.line(weekly_trend, x='Date', y='Interactions', markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

        if auto_refresh:
            time.sleep(10)
            st.experimental_rerun()
        else:
            break
