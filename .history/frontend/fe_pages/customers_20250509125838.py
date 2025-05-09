import streamlit as st
import requests
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))

from widget import CUSTOMER_API_URL

def customer_page():
    st.title("👥 Customer Management")
    st.markdown("<p style='color: #666; margin-bottom: 20px;'>Add, view, edit and delete customer information</p>", unsafe_allow_html=True)
    
    # Tabs for different customer operations
    tab1, tab2 = st.tabs(["📋 Customer List", "➕ Add Customer"])
    
    with tab1:
        # Search and Filter Section
        st.markdown("<div class='customer-form'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            search_term = st.text_input("Search by name or email", placeholder="Enter search term")
        
        with col2:
            filter_type = st.selectbox("Filter by type", ["All Types", "VIP", "Regular", "New"])
        
        with col3:
            st.write("")
            st.write("")
            load_btn = st.button("🔍 Search", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Table of customers with actions
        if load_btn or 'customer_data' in st.session_state:
            with st.spinner("Loading customers..."):
                try:
                    res = requests.get(CUSTOMER_API_URL)
                    if res.ok:
                        data = res.json()
                        st.session_state.customer_data = data
                        
                        # Apply filters
                        if search_term:
                            data = [c for c in data if search_term.lower() in c.get('name', '').lower() or 
                                    search_term.lower() in c.get('email', '').lower()]
                        
                        if filter_type != "All Types":
                            data = [c for c in data if c.get('type') == filter_type]
                        
                        if not data:
                            st.info("No customers match your search criteria.")
                        else:
                            # Convert to DataFrame for display
                            display_fields = ["customer_id", "name", "type", "email", "phone"]
                            df = pd.DataFrame(data)[display_fields]
                            
                            # Format the dataframe
                            df = df.rename(columns={
                                "customer_id": "ID",
                                "name": "Name",
                                "type": "Type",
                                "email": "Email",
                                "phone": "Phone"
                            })
                            
                            # Display customer cards with actions
                            for i, customer in enumerate(data):
                                col1, col2, col3 = st.columns([3, 2, 1])
                                
                                with col1:
                                    st.markdown(f"""
                                    <div class='customer-card'>
                                        <h3 style='margin:0;'>{customer.get('name', 'Unknown')}</h3>
                                        <div style='margin:5px 0;'>
                                            <span class='badge badge-{customer.get('type', '').lower()}'>{customer.get('type', '')}</span>
                                            <span style='color:#666; margin-left:10px;'>ID: {customer.get('customer_id', 'N/A')}</span>
                                        </div>
                                        <div style='margin-top:8px;'>
                                            <span style='color:#666;'>📧 {customer.get('email', 'No email')}</span><br>
                                            <span style='color:#666;'>📱 {customer.get('phone', 'No phone')}</span>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                with col2:
                                    st.markdown(f"<div style='height:30px;'></div>", unsafe_allow_html=True)
                                    if st.button("✏️ Edit", key=f"edit_{i}"):
                                        st.session_state.edit_customer = customer
                                        st.rerun()
                                    
                                    if st.button("📞 Contact", key=f"contact_{i}"):
                                        st.session_state.current_page = "Interact With Customer"
                                        st.session_state.selected_customer = customer.get('name')
                                        st.rerun()
                                
                                with col3:
                                    st.markdown(f"<div style='height:30px;'></div>", unsafe_allow_html=True)
                                    if st.button("🗑️ Delete", key=f"delete_{i}"):
                                        cust_id = customer.get('customer_id')
                                        res = requests.delete(f"{CUSTOMER_API_URL}/{cust_id}")
                                        if res.ok:
                                            st.session_state.pop('customer_data', None)
                                            st.success("Customer deleted successfully!")
                                            st.rerun()
                                        else:
                                            st.error(f"Error {res.status_code}: {res.text}")
                    else:
                        st.error(f"Failed to load customer data. Status code: {res.status_code}")
                except Exception as e:
                    st.error(f"Error loading data: {e}")
        else:
            st.info("Click 'Search' to load customer data")
    
    with tab2:
        st.markdown("<div class='customer-form'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            cust_id = st.text_input("Customer ID", key="new_id", placeholder="Leave blank for auto-generation")
            name = st.text_input("Full Name", key="new_name", placeholder="John Doe")
            email = st.text_input("Email Address", key="new_email", placeholder="john.doe@example.com")
        
        with col2:
            phone = st.text_input("Phone Number", key="new_phone", placeholder="+1 (555) 123-4567")
            cust_type = st.selectbox("Customer Type", ["VIP", "Regular", "New"], key="new_type")
        
        notes = st.text_area("Additional Notes", placeholder="Enter any additional information about this customer")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("")
        with col2:
            if st.button("➕ Create Customer", use_container_width=True):
                payload = {
                    **({"customer_id": int(cust_id)} if cust_id else {}),
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "type": cust_type,
                    "notes": notes
                }
                
                if not name or not email:
                    st.warning("Please enter at least name and email")
                else:
                    res = requests.post(CUSTOMER_API_URL, json=payload)
                    if res.status_code == 201:
                        new_id = res.json().get("customer_id") or res.json().get("_id")
                        st.success(f"✅ Customer created successfully with ID: {new_id}")
                        # Clear the form
                        st.session_state.new_id = ""
                        st.session_state.new_name = ""
                        st.session_state.new_email = ""
                        st.session_state.new_phone = ""
                    else:
                        st.error(f"Error {res.status_code}: {res.text}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Edit customer modal (using expander as a workaround)
    if 'edit_customer' in st.session_state:
        customer = st.session_state.edit_customer
        
        st.markdown("---")
        st.subheader("✏️ Edit Customer")
        
        st.markdown("<div class='customer-form'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            cust_id = st.text_input("Customer ID", value=customer.get('customer_id', ''), disabled=True)
            up_name = st.text_input("Name", value=customer.get('name', ''), key="up_name")
            up_email = st.text_input("Email", value=customer.get('email', ''), key="up_email")
        
        with col2:
            up_phone = st.text_input("Phone", value=customer.get('phone', ''), key="up_phone")
            up_type = st.selectbox("Type", ["VIP", "Regular", "New"], 
                                 index=["VIP", "Regular", "New"].index(customer.get('type', 'Regular')), 
                                 key="up_type")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write("")
        with col2:
            if st.button("✅ Save Changes", use_container_width=True):
                payload = {
                    "name": up_name,
                    "email": up_email,
                    "phone": up_phone,
                    "type": up_type
                }
                
                res = requests.put(f"{CUSTOMER_API_URL}/{cust_id}", json=payload)
                if res.ok:
                    st.success("Customer updated successfully!")
                    st.session_state.pop('edit_customer', None)
                    st.session_state.pop('customer_data', None)
                    st.rerun()
                else:
                    st.error(f"Error {res.status_code}: {res.text}")
        
        with col3:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.pop('edit_customer', None)
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
