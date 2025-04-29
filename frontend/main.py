import streamlit as st
from pages import dashboard, customers, reports

st.set_page_config(page_title="Admin Dashboard", layout="wide")

# Sidebar
st.sidebar.title("Admin Menu")
page = st.sidebar.radio("Go to", ["Dashboard", "Customers", "Reports"])
refresh = st.sidebar.checkbox("Auto-refresh every 10 seconds")

# Router
if page == "Dashboard":
    dashboard.show(refresh)
elif page == "Customers":
    customers.show()
elif page == "Reports":
    reports.show()
