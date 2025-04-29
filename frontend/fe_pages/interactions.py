import streamlit as st
from utils.customer_generator import generate_interaction_data

def interaction_page():
    st.title("📞 Interactions")

    # Load interaction data
    interactions_df = generate_interaction_data()

    # Display interaction table
    st.header("Interaction History")
    st.dataframe(interactions_df)
