import streamlit as st
import requests
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))

from widget import CUSTOMER_API_URL, 

def customer_page():
    st.header("👥 Customers Management")

    # ─────────────── Add new customer ───────────────
    with st.expander("➕ Add new Customer"):
        cust_id  = st.text_input("Customer ID", key="new_id")
        name     = st.text_input("Name", key="new_name")
        email    = st.text_input("Email", key="new_email")
        phone    = st.text_input("Phone", key="new_phone")
        cust_type = st.selectbox("Type", ["VIP", "Regular", "New"], key="new_type")

        if st.button("Create Customer", key="create"):
            payload = {
                # cast to int if you want numeric IDs
                **({"customer_id": int(cust_id)} if cust_id else {}),
                "name": name,
                "email": email,
                "phone": phone,
                "type": cust_type,
            }
            res = requests.post(API_URL, json=payload)
            if res.status_code == 201:
                new_id = res.json().get("customer_id") or res.json().get("_id")
                st.success(f"Created successfully with ID: {new_id}")
            else:
                st.error(f"Error {res.status_code}: {res.text}")

    st.markdown("---")

    # ─────────────── Load customers ───────────────
    if st.button("🔄 Load Customers list"):
        res = requests.get(API_URL)
        if res.ok:
                data = res.json()
                display_fields = ["customer_id", "name", "type", "email", "phone", "datetime"]
                df = pd.DataFrame(data)[display_fields]

                st.dataframe(df)
        else:
            st.error("Cannot load customers list")

    st.markdown("---")

    # ───────── Search / Update / Delete ─────────
    st.subheader("🔍 Search, Update, Delete by ID")
    lookup_id = st.text_input("Input customer_id", key="lookup")

    # --- View detail ---
    if st.button("See detail", key="view"):
        if lookup_id:
            res = requests.get(f"{API_URL}/{lookup_id}")
            if res.ok:
                st.json(res.json())
            else:
                st.error("Cannot find customer")

    # --- Update ---
    st.write("**Update**")
    new_name  = st.text_input("New Name", key="up_name")
    new_email = st.text_input("New Email", key="up_email")
    new_phone = st.text_input("New Phone", key="up_phone")
    new_type  = st.selectbox("New Type", ["", "VIP", "Regular", "New"], key="up_type")

    if st.button("Update Information", key="update"):
        if not lookup_id:
            st.error("Please enter an ID to update.")
        else:
            payload = {}
            if new_name:  payload["name"]  = new_name
            if new_email: payload["email"] = new_email
            if new_phone: payload["phone"] = new_phone
            if new_type:  payload["type"]  = new_type

            if not payload:
                st.warning("No fields to update!")
            else:
                res = requests.put(f"{API_URL}/{lookup_id}", json=payload)
                if res.ok:
                    st.success("Updated successfully")
                else:
                    st.error(f"Error {res.status_code}: {res.text}")

    # --- Delete ---
    if st.button("Delete Customer", key="delete"):
        if not lookup_id:
            st.error("Please enter an ID to delete.")
        else:
            res = requests.delete(f"{API_URL}/{lookup_id}")
            if res.ok:
                st.success("Deleted successfully")
            else:
                st.error(f"Error {res.status_code}: {res.text}")
