import streamlit as st
import requests
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))

from widget import CUSTOMER_API_URL

def customer_page():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .section-divider {
        margin: 2rem 0;
        border-top: 1px solid #eaeaea;
    }
    .success-msg {
        padding: 10px;
        border-radius: 5px;
        background-color: #d4edda;
        color: #155724;
    }
    .error-msg {
        padding: 10px;
        border-radius: 5px;
        background-color: #f8d7da;
        color: #721c24;
    }
    .card {
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='main-header'>👥 Customer Management Dashboard</h1>", unsafe_allow_html=True)
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["📋 Customer List", "➕ Add Customer", "🔍 Search & Modify"])
    
    # ================ TAB 1: CUSTOMER LIST ================
    with tab1:
        # st.markdown("<div class='card'>", unsafe_allow_html=True)

        st.subheader("Customer Database")

        # Add search filter above the table
        filter_col1, filter_col2 = st.columns([3, 2])
        with filter_col1:
            search_term = st.text_input("🔍 Filter by name or email", "")
        with filter_col2:
            filter_type = st.selectbox("Filter by type", ["All Types", "VIP", "Regular", "New"])
        
        try:
            res = requests.get(CUSTOMER_API_URL)
            if res.ok:
                data = res.json()
                display_fields = ["customer_id", "name", "type", "email", "phone", "datetime"]
                df = pd.DataFrame(data)
                
                # Apply filters if provided
                if search_term:
                    df = df[df['name'].str.contains(search_term, case=False) | 
                            df['email'].str.contains(search_term, case=False)]
                
                if filter_type != "All Types":
                    df = df[df['type'] == filter_type]
                
                # Format datetime for better readability
                if 'datetime' in df.columns:
                    df['datetime'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d %H:%M')
                
                # Add action buttons if needed
                if not df.empty:
                    df = df[display_fields] if all(field in df.columns for field in display_fields) else df
                    st.dataframe(df, use_container_width=True, height=400)
                    st.caption(f"Showing {len(df)} customers")
                else:
                    st.info("No customers match your filter criteria")
            else:
                st.error(f"Error loading customers: {res.status_code}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
            
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ================ TAB 2: ADD CUSTOMER ================
    with tab2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Create New Customer")
        
        # Split form into two columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
            cust_id = st.text_input("Customer ID (Optional)", key="new_id", 
                                    placeholder="Leave blank for auto-generation")
            name = st.text_input("Full Name *", key="new_name", placeholder="John Doe")
            email = st.text_input("Email Address *", key="new_email", placeholder="john.doe@example.com")
        
        with col2:
            phone = st.text_input("Phone Number", key="new_phone", placeholder="+1 (555) 123-4567")
            cust_type = st.selectbox("Customer Type *", ["Regular", "VIP", "New"], key="new_type")
            st.text_input("Creation Date", datetime.now().strftime("%Y-%m-%d"), disabled=True,
                         help="Automatically set to today")
        
        # Create button with validation
        if st.button("✅ Create Customer", key="create", use_container_width=True, type="primary"):
            # Basic validation
            if not name or not email:
                st.error("Name and Email are required fields")
            elif "@" not in email:
                st.error("Please enter a valid email address")
            else:
                payload = {
                    **({"customer_id": int(cust_id)} if cust_id and cust_id.isdigit() else {}),
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "type": cust_type,
                }
                
                try:
                    res = requests.post(CUSTOMER_API_URL, json=payload)
                    if res.status_code == 201:
                        new_id = res.json().get("customer_id") or res.json().get("_id")
                        st.success(f"✅ Customer created successfully with ID: {new_id}")
                        # Clear form fields after successful creation
                        st.session_state["new_id"] = ""
                        st.session_state["new_name"] = ""
                        st.session_state["new_email"] = ""
                        st.session_state["new_phone"] = ""
                    else:
                        st.error(f"Error {res.status_code}: {res.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ================ TAB 3: SEARCH & MODIFY ================
    with tab3:
        st.subheader("Find and Modify Customer")
        
        lookup_id = st.text_input("Customer ID *", key="lookup", placeholder="Enter ID to search")
        
        if lookup_id:
            if st.button("🔍 Find Customer", key="find_customer", use_container_width=True):
                try:
                    res = requests.get(f"{CUSTOMER_API_URL}/{lookup_id}")
                    if res.ok:
                        customer_data = res.json()
                        
                        # Display current customer info
                        st.subheader("Customer Details")
                        
                        # Create three columns for better layout
                        info_col1, info_col2, info_col3 = st.columns(3)
                        
                        with info_col1:
                            st.metric("Customer ID", customer_data.get("customer_id", "N/A"))
                            st.metric("Name", customer_data.get("name", "N/A"))
                        
                        with info_col2:
                            st.metric("Type", customer_data.get("type", "N/A"))
                            st.metric("Email", customer_data.get("email", "N/A"))
                        
                        with info_col3:
                            st.metric("Phone", customer_data.get("phone", "N/A"))
                            created_date = customer_data.get("datetime", "N/A")
                            if created_date != "N/A":
                                created_date = pd.to_datetime(created_date).strftime("%Y-%m-%d")
                            st.metric("Created On", created_date)
                        
                        # Store found customer in session state
                        st.session_state['found_customer'] = customer_data
                        
                        # Show update and delete options
                        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
                        st.subheader("Modify Customer")
                        
                        update_tab, delete_tab = st.tabs(["Update Info", "Delete Customer"])
                        
                        with update_tab:
                            # Pre-fill with current values
                            update_col1, update_col2 = st.columns(2)
                            
                            with update_col1:
                                new_name = st.text_input("Name", 
                                                         value=customer_data.get("name", ""), 
                                                         key="up_name")
                                new_email = st.text_input("Email", 
                                                          value=customer_data.get("email", ""), 
                                                          key="up_email")
                            
                            with update_col2:
                                new_phone = st.text_input("Phone", 
                                                          value=customer_data.get("phone", ""), 
                                                          key="up_phone")
                                new_type = st.selectbox("Type", 
                                                        options=["VIP", "Regular", "New"],
                                                        index=["VIP", "Regular", "New"].index(customer_data.get("type", "Regular")), 
                                                        key="up_type")
                            
                            if st.button("💾 Save Changes", key="update", use_container_width=True, type="primary"):
                                # Check what changed
                                payload = {}
                                original = st.session_state['found_customer']
                                
                                if new_name != original.get("name", ""): 
                                    payload["name"] = new_name
                                if new_email != original.get("email", ""): 
                                    payload["email"] = new_email
                                if new_phone != original.get("phone", ""): 
                                    payload["phone"] = new_phone
                                if new_type != original.get("type", ""): 
                                    payload["type"] = new_type
                                
                                if not payload:
                                    st.info("No changes detected")
                                else:
                                    try:
                                        res = requests.put(f"{CUSTOMER_API_URL}/{lookup_id}", json=payload)
                                        if res.ok:
                                            st.success("✅ Customer updated successfully")
                                        else:
                                            st.error(f"Error {res.status_code}: {res.text}")
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                        
                        with delete_tab:
                            st.warning("⚠️ This action cannot be undone!")
                            
                            confirm_delete = st.text_input("Type 'DELETE' to confirm", 
                                                          placeholder="DELETE", 
                                                          key="confirm_delete")
                            
                            if st.button("🗑️ Delete Customer", key="delete", use_container_width=True):
                                if confirm_delete != "DELETE":
                                    st.error("Please type 'DELETE' to confirm")
                                else:
                                    try:
                                        res = requests.delete(f"{CUSTOMER_API_URL}/{lookup_id}")
                                        if res.ok:
                                            st.success("✅ Customer deleted successfully")
                                            # Clear session state
                                            if 'found_customer' in st.session_state:
                                                del st.session_state['found_customer']
                                            st.session_state["lookup"] = ""
                                        else:
                                            st.error(f"Error {res.status_code}: {res.text}")
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                    else:
                        st.error(f"Customer with ID '{lookup_id}' not found")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.info("Enter a customer ID to search")
        
        st.markdown("</div>", unsafe_allow_html=True)
    