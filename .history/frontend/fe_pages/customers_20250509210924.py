import streamlit as st
import requests
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))

from widget import CUSTOMER_API_URL, check_email_exists

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
    .button {
        display: inline-block;
        padding: 0.5rem 1rem;
        background-color: #4e73df;
        color: white;
        text-decoration: none;
        border-radius: 0.25rem;
        font-weight: 500;
        margin-top: 0.5rem;
        text-align: center;
    }
    .button:hover {
        background-color: #2e59d9;
        color: white;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='main-header'>👥 Customer Management Dashboard</h1>", unsafe_allow_html=True)
    length = 0
    res = requests.get(CUSTOMER_API_URL)
    if res.ok:
        data = res.json()
        length = len(data)
    tab1, tab2, tab3 = st.tabs(["📋 Customer List", "➕ Add Customer", "🔍 Search & Modify"])
    
    # ================ TAB 1: CUSTOMER LIST ================
    with tab1:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.subheader("Customer Database")

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
                
                if search_term:
                    df = df[df['name'].str.contains(search_term, case=False) | 
                            df['email'].str.contains(search_term, case=False)]
                
                if filter_type != "All Types":
                    df = df[df['type'] == filter_type]
                
                if 'datetime' in df.columns:
                    try:
                        df['datetime'] = pd.to_datetime(df['datetime'], format='ISO8601', errors='coerce')
                        if df['datetime'].isna().any():
                            df['datetime'] = pd.to_datetime(df['datetime'], format='mixed', errors='coerce')
                        df['datetime'] = df['datetime'].dt.strftime('%b %d, %Y %H:%M')
                    except Exception as e:
                        st.warning(f"Could not format datetime column: {str(e)}")
                        df['datetime'] = df['datetime'].astype(str)
                
                if not df.empty:
                    df = df[display_fields] if all(field in df.columns for field in display_fields) else df
                    df = df.rename(columns={
                        "customer_id": "Customer_id",
                        "name": "Name",
                        "type": "Type",
                        "email": "Email",
                        "phone": "Phone",
                        "datetime": "Created At"
                    })
                    st.dataframe(df, use_container_width=True, height=400)
                    st.caption(f"Showing {len(df)} customers")
                else:
                    st.info("No customers match your filter criteria")
            else:
                st.error(f"Error loading customers: {res.status_code}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
            
    # ================ TAB 2: ADD CUSTOMER ================
    with tab2:
        st.subheader("Create New Customer")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cust_id = st.text_input("Customer ID (Optional)", key="new_id", disabled=True, placeholder= "Auto to generate")
            name = st.text_input("Full Name *", key="new_name", placeholder="John Doe")
            email = st.text_input("Email Address *", key="new_email", placeholder="john.doe@example.com")
        
        with col2:
            phone = st.text_input("Phone Number", key="new_phone", placeholder="+1 (555) 123-4567")
            cust_type = st.selectbox("Customer Type *", ["Regular", "VIP", "New"], key="new_type")
            st.text_input("Creation Date", datetime.now().strftime("%Y-%m-%d %H:%M"), disabled=True,
                         help="Automatically set to today")
        
        if st.button("✅ Create Customer", key="create", use_container_width=True, type="primary"):
            if not name or not email:
                st.error("Name and Email are required fields")
            elif "@" not in email:
                st.error("Please enter a valid email address")
            else:
                exists, _ = check_email_exists(email)
                if exists:
                    st.error(f"Email exists!")
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
                        else:
                            st.error(f"Error {res.status_code}: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        st.subheader("Import Customers from File")
        
        uploaded_file = st.file_uploader("Choose a CSV or Excel file", 
                                        type=["csv", "xlsx", "xls"], 
                                        help="Your file should contain columns for customer data")
        
        if uploaded_file is not None:
            file_size = uploaded_file.size / 1024  
            st.info(f"File: {uploaded_file.name} ({file_size:.2f} KB)")
            
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:  
                    df = pd.read_excel(uploaded_file)
                
                if df.empty:
                    st.error("The uploaded file is empty.")
                else:
                    st.subheader("Data Preview")
                    st.dataframe(df.head(5), use_container_width=True)
                    
                    st.subheader("Map Columns")
                    st.write("Match your file columns to our system fields:")
                    
                    col_map = {}
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        col_map["name"] = st.selectbox(
                            "Name Column", 
                            options=["-- Select --"] + list(df.columns),
                            help="Required field"
                        )
                        
                        col_map["email"] = st.selectbox(
                            "Email Column", 
                            options=["-- Select --"] + list(df.columns),
                            help="Required field"
                        )
                    
                    with col2:
                        col_map["phone"] = st.selectbox(
                            "Phone Column", 
                            options=["-- None --"] + list(df.columns)
                        )
                        
                        col_map["type"] = st.selectbox(
                            "Customer Type Column", 
                            options=["-- None --"] + list(df.columns),
                            help="If not selected, all imported customers will be set as 'Regular'"
                        )
                    
                    if col_map["type"] == "-- None --":
                        default_type = st.selectbox(
                            "Default Customer Type", 
                            options=["Regular", "VIP", "New"]
                        )
                    
                    duplicate_action = st.radio(
                        "If duplicate customer email is found:",
                        options=["Skip", "Update existing record"],
                        horizontal=True
                    )
                    
                    if st.button("🚀 Process Import", type="primary", use_container_width=True):
                        if col_map["name"] == "-- Select --" or col_map["email"] == "-- Select --":
                            st.error("Name and Email columns are required")
                        else:
                            progress_bar = st.progress(0)
                            import_status = st.empty()
                            import_status.info("Starting import...")
                            
                            success_count = 0
                            error_count = 0
                            skip_count = 0
                            
                            for i, row in enumerate(df.itertuples()):
                                progress = (i + 1) / len(df)
                                progress_bar.progress(progress)
                                import_status.info(f"Processing row {i+1} of {len(df)}...")
                                
                                try:
                                    name = getattr(row, col_map["name"]) if col_map["name"] != "-- Select --" else ""
                                    email = getattr(row, col_map["email"]) if col_map["email"] != "-- Select --" else ""
                                    phone = getattr(row, col_map["phone"]) if col_map["phone"] != "-- None --" else ""
                                    
                                    if col_map["type"] != "-- None --":
                                        cust_type = getattr(row, col_map["type"])
                                        if cust_type not in ["VIP", "Regular", "New"]:
                                            cust_type = "New"  
                                    else:
                                        cust_type = default_type
                                    
                                    if not name or not email:
                                        skip_count += 1
                                        continue
                                    
                                    payload = {
                                        "name": str(name),
                                        "email": str(email),
                                        "phone": str(phone) if phone else "",
                                        "type": str(cust_type)
                                    }
                                    
                                    if duplicate_action == "Skip":
                                        exist, _ = check_email_exists(payload["email"])
                                        
                                        if exist:
                                            skip_count += 1
                                            continue
                                        
                                        res = requests.post(CUSTOMER_API_URL, json=payload)
                                        if res.status_code == 201:
                                            success_count += 1
                                        else:
                                            error_count += 1
                                            
                                    else:  
                                        exist, customer = check_email_exists(payload["email"])
                                        
                                        if exist:
                                            existing_id = customer['customer_id']
                                            update_res = requests.put(f"{CUSTOMER_API_URL}/{existing_id}", json=payload)
                                            if update_res.ok:
                                                success_count += 1
                                            else:
                                                error_count += 1
                                        else:
                                            res = requests.post(CUSTOMER_API_URL, json=payload)
                                            if res.status_code == 201:
                                                success_count += 1
                                            else:
                                                error_count += 1
                                
                                except Exception as e:
                                    error_count += 1
                                    continue
                            
                            import_status.success(f"Import complete! Successfully processed {success_count} customers.")
                            st.write(f"🟢 Added/Updated: {success_count} | 🟠 Skipped: {skip_count} | 🔴 Errors: {error_count}")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

    # ================ TAB 3: SEARCH & MODIFY ================
    with tab3:
        st.subheader("Find and Modify Customer")
        
        lookup_id = st.text_input("Customer ID *", key="lookup", placeholder="Enter ID to search")
        
        if st.button("🔍 Find Customer", key="find_customer", use_container_width=True):
            try:
                if lookup_id =='':
                    st.info("Enter a customer ID to search")
                    return
                res = requests.get(f"{CUSTOMER_API_URL}/{lookup_id}")
                if res.ok:
                    customer_data = res.json()
                    
                    st.subheader("Customer Details")
                    
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
                    
                    st.session_state['found_customer'] = customer_data
                    
                    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
                    st.subheader("Modify Customer")
                    
                    update_tab, delete_tab = st.tabs(["Update Info", "Delete Customer"])
                    
                    with update_tab:
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
                        confirm_delete = st.text_input("Type 'DELETE' to confirm", placeholder="DELETE", key="confirm_delete")
                        
                        if st.button("🗑️ Delete Customer", key="update", use_container_width=True):
                            if confirm_delete != "DELETE":
                                st.error("Please type 'DELETE' to confirm")
                            else:
                                try:
                                    res = requests.delete(f"{CUSTOMER_API_URL}/{lookup_id}")
                                    
                                    if res.status_code == 200:
                                        st.success("✅ Customer deleted successfully!")
                                        
                                        if 'found_customer' in st.session_state:
                                            del st.session_state['found_customer']
                                        
                                        st.experimental_rerun()
                                    
                                    else:
                                        st.error(f"❌ Failed to delete customer. Error: {res.text}")
                                
                                except Exception as e:
                                    st.error(f"🚨 Connection error: {str(e)}")
                else:
                    st.error(f"Customer with ID '{lookup_id}' not found")
            except Exception as e:
                st.error(f"Error: {str(e)}")      
