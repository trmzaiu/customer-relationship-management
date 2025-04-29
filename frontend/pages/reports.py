import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_generator import generate_interaction_data

def show():
    st.title("📑 Reports & Analytics")

    interactions_df = generate_interaction_data()

    st.subheader("Overall Interaction Types")
    interaction_summary = interactions_df['Type'].value_counts().reset_index()
    interaction_summary.columns = ['Interaction Type', 'Count']

    fig = px.bar(interaction_summary, x='Interaction Type', y='Count', color='Interaction Type')
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(interactions_df, use_container_width=True)
