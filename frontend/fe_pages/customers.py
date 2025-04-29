import streamlit as st
from utils.customer_generator import generate_customer_data

def customer_page():
    st.title("👥 Customers")
    
    # Load customer data
    customers_df = generate_customer_data()

    # Display customer table
    st.header("Customer List")
    st.dataframe(customers_df)

    # Customer Details
    st.header("Customer Details")
    customer_id = st.selectbox("Select a Customer ID", customers_df['Customer ID'].tolist())
    selected_customer = customers_df[customers_df['Customer ID'] == customer_id].iloc[0]
    st.write(f"Name: {selected_customer['Name']}")
    st.write(f"Email: {selected_customer['Email']}")
    st.write(f"Phone: {selected_customer['Phone']}")
    st.write(f"Category: {selected_customer['Type']}")
    st.write(f"Created At: {selected_customer['Created At']}")
