import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime, timedelta

def home_page():
    # --- Title ---
    st.title("🏠 Admin Dashboard")

    # --- Mock Data ---
    total_customers = 1200
    vip_customers = 300
    regular_customers = 800
    new_customers = 100
    emails_sent = 850
    interactions_logged = 2000
    weekly_interactions = random.randint(150, 300)

    # --- Overview Metrics ---
    st.header("📊 Overview")
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Customers", f"{total_customers}")
    col2.metric("VIP Customers", f"{vip_customers}")
    col3.metric("Regular Customers", f"{regular_customers}")
    col4.metric("New Customers (This Month)", f"{new_customers}")
    col5.metric("Interactions This Week", f"{weekly_interactions}")

    st.divider()

    # --- Customer Insights ---
    st.header("🧠 Customer Insights")
    df_customers = pd.DataFrame({
        'Customer Type': ['VIP', 'Regular', 'New'],
        'Count': [vip_customers, regular_customers, new_customers]
    })

    col6, col7 = st.columns(2)
    with col6:
        fig_pie = px.pie(
            df_customers, names='Customer Type', values='Count',
            title='Customer Distribution', color_discrete_sequence=px.colors.sequential.Aggrnyl
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col7:
        fig_bar = px.bar(
            df_customers, x='Customer Type', y='Count',
            title='Customer Count by Type', color='Customer Type',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # --- Weekly Interactions Trend ---
    st.header("📈 Weekly Interactions Trends")
    days = [(datetime.now() - timedelta(days=i)).strftime('%A') for i in range(6, -1, -1)]
    interactions = [random.randint(10, 70) for _ in range(7)]
    df_weekly = pd.DataFrame({'Day': days, 'Interactions': interactions})

    fig_line = px.line(
        df_weekly, x='Day', y='Interactions',
        title='Interactions Over the Past Week',
        markers=True, line_shape='spline'
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    # --- Top VIP Customers and Recent Interactions ---
    col8, col9 = st.columns(2)
    with col8:
        st.subheader("🏅 Top 5 VIP Customers")
        vip_customers_df = pd.DataFrame({
            'Name': [f"VIP Customer {i}" for i in range(1, 6)],
            'Total Interactions': [random.randint(20, 100) for _ in range(5)],
            'Last Interaction': [(datetime.now() - timedelta(days=random.randint(1, 10))).strftime('%Y-%m-%d') for _ in range(5)]
        })
        st.dataframe(vip_customers_df, use_container_width=True)

    with col9:
        st.subheader("🕑 Recent Interactions")
        recent_interactions_df = pd.DataFrame({
            'Customer': [f"Customer {random.randint(1, 50)}" for _ in range(5)],
            'Type': random.choices(['Email', 'Call', 'Meeting'], k=5),
            'Date': [(datetime.now() - timedelta(hours=random.randint(1, 72))).strftime('%Y-%m-%d %H:%M') for _ in range(5)]
        })
        st.dataframe(recent_interactions_df, use_container_width=True)

if __name__ == "__main__":
    home_page()
