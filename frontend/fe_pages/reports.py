import streamlit as st
import plotly.express as px
from utils.customer_generator import generate_customer_data, generate_interaction_data

def report_page():
    st.title("📊 Reports")

    # Load data
    customers_df = generate_customer_data()
    interactions_df = generate_interaction_data()

    # Customer Distribution Chart
    st.header("Customer Distribution")
    customer_summary = customers_df['Type'].value_counts().reset_index()
    customer_summary.columns = ['Customer Type', 'Count']
    fig_pie = px.pie(customer_summary, names='Customer Type', values='Count', title='Customer Distribution')
    st.plotly_chart(fig_pie)

    # Interaction Trends Chart
    st.header("Weekly Interaction Trends")
    weekly_trend = interactions_df.groupby('Date').size().reset_index(name='Interactions')
    fig_line = px.line(weekly_trend, x='Date', y='Interactions', markers=True)
    st.plotly_chart(fig_line)
