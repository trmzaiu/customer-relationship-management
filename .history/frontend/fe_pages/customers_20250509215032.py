# import streamlit as st
# import requests
# import pandas as pd
# import sys
# import os
# from datetime import datetime

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))

# from widget import CUSTOMER_API_URL, check_email_exists

# def customer_page():
#     st.markdown("<h1 class='main-header'>👥 Customer Management Dashboard</h1>", unsafe_allow_html=True)
#     length = 0
#     res = requests.get(CUSTOMER_API_URL)
#     if res.ok:
#         data = res.json()
#         length = len(data)
#     tab1, tab2, tab3 = st.tabs(["📋 Customer List", "➕ Add Customer", "🔍 Search & Modify"])
    
#     # ================ TAB 1: CUSTOMER LIST ================
#     with tab1:
#         col1, col2 = st.columns([4, 1])
#         with col1:
#             st.subheader("Customer Database")

#         filter_col1, filter_col2 = st.columns([3, 2])
#         with filter_col1:
#             search_term = st.text_input("🔍 Filter by name or email", "")
#         with filter_col2:
#             filter_type = st.selectbox("Filter by type", ["All Types", "VIP", "Regular", "New"])
        
#         try:
#             res = requests.get(CUSTOMER_API_URL)
#             if res.ok:
#                 data = res.json()
#                 display_fields = ["customer_id", "name", "type", "email", "phone", "datetime"]
#                 df = pd.DataFrame(data)
                
#                 if search_term:
#                     df = df[df['name'].str.contains(search_term, case=False) | 
#                             df['email'].str.contains(search_term, case=False)]
                
#                 if filter_type != "All Types":
#                     df = df[df['type'] == filter_type]
                
#                 if 'datetime' in df.columns:
#                     try:
#                         df['datetime'] = pd.to_datetime(df['datetime'], format='ISO8601', errors='coerce')
#                         if df['datetime'].isna().any():
#                             df['datetime'] = pd.to_datetime(df['datetime'], format='mixed', errors='coerce')
#                         df['datetime'] = df['datetime'].dt.strftime('%b %d, %Y %H:%M')
#                     except Exception as e:
#                         st.warning(f"Could not format datetime column: {str(e)}")
#                         df['datetime'] = df['datetime'].astype(str)
                
#                 if not df.empty:
#                     df = df[display_fields] if all(field in df.columns for field in display_fields) else df
#                     df = df.rename(columns={
#                         "customer_id": "Customer_id",
#                         "name": "Name",
#                         "type": "Type",
#                         "email": "Email",
#                         "phone": "Phone",
#                         "datetime": "Created At"
#                     })
#                     st.dataframe(df, use_container_width=True, height=400)
#                     st.caption(f"Showing {len(df)} customers")
#                 else:
#                     st.info("No customers match your filter criteria")
#             else:
#                 st.error(f"Error loading customers: {res.status_code}")
#         except Exception as e:
#             st.error(f"Error: {str(e)}")
            
#     # ================ TAB 2: ADD CUSTOMER ================
#     with tab2:
#         st.subheader("Create New Customer")
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             cust_id = st.text_input("Customer ID (Optional)", key="new_id", disabled=True, placeholder= "Auto to generate")
#             name = st.text_input("Full Name *", key="new_name", placeholder="John Doe")
#             email = st.text_input("Email Address *", key="new_email", placeholder="john.doe@example.com")
        
#         with col2:
#             phone = st.text_input("Phone Number", key="new_phone", placeholder="+1 (555) 123-4567")
#             cust_type = st.selectbox("Customer Type *", ["Regular", "VIP", "New"], key="new_type")
#             st.text_input("Creation Date", datetime.now().strftime("%Y-%m-%d %H:%M"), disabled=True,
#                          help="Automatically set to today")
        
#         if st.button("✅ Create Customer", key="create", use_container_width=True, type="primary"):
#             if not name or not email:
#                 st.error("Name and Email are required fields")
#             elif "@" not in email:
#                 st.error("Please enter a valid email address")
#             else:
#                 exists, _ = check_email_exists(email)
#                 if exists:
#                     st.error(f"Email exists!")
#                 else:
#                     payload = {
#                         **({"customer_id": int(cust_id)} if cust_id and cust_id.isdigit() else {}),
#                         "name": name,
#                         "email": email,
#                         "phone": phone,
#                         "type": cust_type,
#                     }
                    
#                     try:
#                         res = requests.post(CUSTOMER_API_URL, json=payload)
#                         if res.status_code == 201:
#                             new_id = res.json().get("customer_id") or res.json().get("_id")
#                             st.success(f"✅ Customer created successfully with ID: {new_id}")
#                         else:
#                             st.error(f"Error {res.status_code}: {res.text}")
#                     except Exception as e:
#                         st.error(f"Error: {str(e)}")
        
#         st.subheader("Import Customers from File")
        
#         uploaded_file = st.file_uploader("Choose a CSV or Excel file", 
#                                         type=["csv", "xlsx", "xls"], 
#                                         help="Your file should contain columns for customer data")
        
#         if uploaded_file is not None:
#             file_size = uploaded_file.size / 1024  
#             st.info(f"File: {uploaded_file.name} ({file_size:.2f} KB)")
            
#             try:
#                 if uploaded_file.name.endswith('.csv'):
#                     df = pd.read_csv(uploaded_file)
#                 else:  
#                     df = pd.read_excel(uploaded_file)
                
#                 if df.empty:
#                     st.error("The uploaded file is empty.")
#                 else:
#                     st.subheader("Data Preview")
#                     st.dataframe(df.head(5), use_container_width=True)
                    
#                     st.subheader("Map Columns")
#                     st.write("Match your file columns to our system fields:")
                    
#                     col_map = {}
#                     col1, col2 = st.columns(2)
                    
#                     with col1:
#                         col_map["name"] = st.selectbox(
#                             "Name Column", 
#                             options=["-- Select --"] + list(df.columns),
#                             help="Required field"
#                         )
                        
#                         col_map["email"] = st.selectbox(
#                             "Email Column", 
#                             options=["-- Select --"] + list(df.columns),
#                             help="Required field"
#                         )
                    
#                     with col2:
#                         col_map["phone"] = st.selectbox(
#                             "Phone Column", 
#                             options=["-- None --"] + list(df.columns)
#                         )
                        
#                         col_map["type"] = st.selectbox(
#                             "Customer Type Column", 
#                             options=["-- None --"] + list(df.columns),
#                             help="If not selected, all imported customers will be set as 'Regular'"
#                         )
                    
#                     if col_map["type"] == "-- None --":
#                         default_type = st.selectbox(
#                             "Default Customer Type", 
#                             options=["Regular", "VIP", "New"]
#                         )
                    
#                     duplicate_action = st.radio(
#                         "If duplicate customer email is found:",
#                         options=["Skip", "Update existing record"],
#                         horizontal=True
#                     )
                    
#                     if st.button("🚀 Process Import", type="primary", use_container_width=True):
#                         if col_map["name"] == "-- Select --" or col_map["email"] == "-- Select --":
#                             st.error("Name and Email columns are required")
#                         else:
#                             progress_bar = st.progress(0)
#                             import_status = st.empty()
#                             import_status.info("Starting import...")
                            
#                             success_count = 0
#                             error_count = 0
#                             skip_count = 0
                            
#                             for i, row in enumerate(df.itertuples()):
#                                 progress = (i + 1) / len(df)
#                                 progress_bar.progress(progress)
#                                 import_status.info(f"Processing row {i+1} of {len(df)}...")
                                
#                                 try:
#                                     name = getattr(row, col_map["name"]) if col_map["name"] != "-- Select --" else ""
#                                     email = getattr(row, col_map["email"]) if col_map["email"] != "-- Select --" else ""
#                                     phone = getattr(row, col_map["phone"]) if col_map["phone"] != "-- None --" else ""
                                    
#                                     if col_map["type"] != "-- None --":
#                                         cust_type = getattr(row, col_map["type"])
#                                         if cust_type not in ["VIP", "Regular", "New"]:
#                                             cust_type = "New"  
#                                     else:
#                                         cust_type = default_type
                                    
#                                     if not name or not email:
#                                         skip_count += 1
#                                         continue
                                    
#                                     payload = {
#                                         "name": str(name),
#                                         "email": str(email),
#                                         "phone": str(phone) if phone else "",
#                                         "type": str(cust_type)
#                                     }
                                    
#                                     if duplicate_action == "Skip":
#                                         exist, _ = check_email_exists(payload["email"])
                                        
#                                         if exist:
#                                             skip_count += 1
#                                             continue
                                        
#                                         res = requests.post(CUSTOMER_API_URL, json=payload)
#                                         if res.status_code == 201:
#                                             success_count += 1
#                                         else:
#                                             error_count += 1
                                            
#                                     else:  
#                                         exist, customer = check_email_exists(payload["email"])
                                        
#                                         if exist:
#                                             existing_id = customer['customer_id']
#                                             update_res = requests.put(f"{CUSTOMER_API_URL}/{existing_id}", json=payload)
#                                             if update_res.ok:
#                                                 success_count += 1
#                                             else:
#                                                 error_count += 1
#                                         else:
#                                             res = requests.post(CUSTOMER_API_URL, json=payload)
#                                             if res.status_code == 201:
#                                                 success_count += 1
#                                             else:
#                                                 error_count += 1
                                
#                                 except Exception as e:
#                                     error_count += 1
#                                     continue
                            
#                             import_status.success(f"Import complete! Successfully processed {success_count} customers.")
#                             st.write(f"🟢 Added/Updated: {success_count} | 🟠 Skipped: {skip_count} | 🔴 Errors: {error_count}")
#             except Exception as e:
#                 st.error(f"Error processing file: {str(e)}")

#     # ================ TAB 3: SEARCH & MODIFY ================
#     with tab3:
#         st.subheader("Find and Modify Customer")
        
#         lookup_id = st.text_input("Customer ID *", key="lookup", placeholder="Enter ID to search")
        
#         try:
#             if lookup_id =='':
#                 st.info("Enter a customer ID to search")
#                 return
#             res = requests.get(f"{CUSTOMER_API_URL}/{lookup_id}")
#             if res.ok:
#                 customer_data = res.json()
                
#                 st.subheader("Customer Details")
                
#                 info_col1, info_col2, info_col3 = st.columns(3)
                
#                 with info_col1:
#                     st.metric("Customer ID", customer_data.get("customer_id", "N/A"))
#                     st.metric("Name", customer_data.get("name", "N/A"))
                
#                 with info_col2:
#                     st.metric("Type", customer_data.get("type", "N/A"))
#                     st.metric("Email", customer_data.get("email", "N/A"))
                
#                 with info_col3:
#                     st.metric("Phone", customer_data.get("phone", "N/A"))
#                     created_date = customer_data.get("datetime", "N/A")
#                     if created_date != "N/A":
#                         created_date = pd.to_datetime(created_date).strftime("%Y-%m-%d")
#                     st.metric("Created On", created_date)
                
#                 st.session_state['found_customer'] = customer_data
                
#                 st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
#                 st.subheader("Modify Customer")
                
#                 update_tab, delete_tab = st.tabs(["Update Info", "Delete Customer"])
                
#                 with update_tab:
#                     update_col1, update_col2 = st.columns(2)
                    
#                     with update_col1:
#                         new_name = st.text_input("Name", 
#                                                     value=customer_data.get("name", ""), 
#                                                     key="up_name")
#                         new_email = st.text_input("Email", 
#                                                     value=customer_data.get("email", ""), 
#                                                     key="up_email")
                    
#                     with update_col2:
#                         new_phone = st.text_input("Phone", 
#                                                     value=customer_data.get("phone", ""), 
#                                                     key="up_phone")
#                         new_type = st.selectbox("Type", 
#                                                 options=["VIP", "Regular", "New"],
#                                                 index=["VIP", "Regular", "New"].index(customer_data.get("type", "Regular")), 
#                                                 key="up_type")
                    
#                     if st.button("💾 Save Changes", key="update", use_container_width=True, type="primary"):
#                         payload = {}
#                         original = st.session_state['found_customer']
                        
#                         if new_name != original.get("name", ""): 
#                             payload["name"] = new_name
#                         if new_email != original.get("email", ""): 
#                             payload["email"] = new_email
#                         if new_phone != original.get("phone", ""): 
#                             payload["phone"] = new_phone
#                         if new_type != original.get("type", ""): 
#                             payload["type"] = new_type
                        
#                         if not payload:
#                             st.info("No changes detected")
#                         else:
#                             try:
#                                 res = requests.put(f"{CUSTOMER_API_URL}/{lookup_id}", json=payload)
#                                 if res.ok:
#                                     st.success("✅ Customer updated successfully")
#                                 else:
#                                     st.error(f"Error {res.status_code}: {res.text}")
#                             except Exception as e:
#                                 st.error(f"Error: {str(e)}")
                                
#                     if st.button("🗑️ Delete Customer", key="delete", use_container_width=True):
#                         try:
#                             res = requests.delete(f"{CUSTOMER_API_URL}/{lookup_id}")
#                             if res.status_code == 200:
#                                 st.success("✅ Customer deleted successfully!")
#                                 if 'found_customer' in st.session_state:
#                                     del st.session_state['found_customer']
#                                 st.rerun()
#                             else:
#                                 st.error(f"❌ Failed to delete customer. Error: {res.text}")
#                         except Exception as e:
#                             st.error(f"🚨 Connection error: {str(e)}")                    
#             else:
#                 st.error(f"Customer with ID '{lookup_id}' not found")
#         except Exception as e:
#             st.error(f"Error: {str(e)}")      
            
import streamlit as st
import requests
import pandas as pd
import sys
import os
from datetime import datetime
from functools import lru_cache
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))

from widget import CUSTOMER_API_URL, check_email_exists

# Cache API results with a TTL (time to live) of 30 seconds
@lru_cache(maxsize=32)
def fetch_customers(timestamp_minute):
    """Fetch customers with caching by minute timestamp to avoid excessive API calls"""
    try:
        res = requests.get(CUSTOMER_API_URL)
        if res.ok:
            return res.json()
        return []
    except Exception as e:
        st.error(f"Error fetching customer data: {str(e)}")
        return []

def get_cached_customers():
    """Get customers with a cache that refreshes every minute"""
    # Using the current minute as cache key ensures refresh every minute
    current_minute = int(time.time() / 60)
    return fetch_customers(current_minute)

def format_datetime(df):
    """Format datetime column for display"""
    if 'datetime' in df.columns:
        try:
            df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
            df['datetime'] = df['datetime'].dt.strftime('%b %d, %Y %H:%M')
        except Exception:
            df['datetime'] = df['datetime'].astype(str)
    return df

def filter_dataframe(df, search_term="", filter_type="All Types"):
    """Filter dataframe based on search term and customer type"""
    filtered_df = df.copy()
    
    if search_term:
        name_mask = filtered_df['name'].str.contains(search_term, case=False, na=False)
        email_mask = filtered_df['email'].str.contains(search_term, case=False, na=False)
        filtered_df = filtered_df[name_mask | email_mask]
    
    if filter_type != "All Types":
        filtered_df = filtered_df[filtered_df['type'] == filter_type]
        
    return filtered_df

def customer_page():
    st.markdown("<h1 class='main-header'>👥 Customer Management Dashboard</h1>", unsafe_allow_html=True)
    
    # Initialize session state for data caching if needed
    if 'last_refresh' not in st.session_state:
        st.session_state['last_refresh'] = 0
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📋 Customer List", "➕ Add Customer", "🔍 Search & Modify"])
    
    # ================ TAB 1: CUSTOMER LIST ================
    with tab1:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.subheader("Customer Database")
        with col2:
            if st.button("🔄 Refresh"):
                st.session_state['last_refresh'] = time.time()
                # Clear cache by forcing a new timestamp
                fetch_customers.cache_clear()
                st.experimental_rerun()

        filter_col1, filter_col2 = st.columns([3, 2])
        with filter_col1:
            search_term = st.text_input("🔍 Filter by name or email", "")
        with filter_col2:
            filter_type = st.selectbox("Filter by type", ["All Types", "VIP", "Regular", "New"])
        
        # Get customer data using the caching function
        customers_data = get_cached_customers()
        
        if customers_data:
            # Convert to dataframe once
            df = pd.DataFrame(customers_data)
            
            # Apply filters
            filtered_df = filter_dataframe(df, search_term, filter_type)
            
            # Format datetime only if we have matching records
            if not filtered_df.empty:
                filtered_df = format_datetime(filtered_df)
                
                # Display dataframe with selected columns
                display_fields = ["customer_id", "name", "type", "email", "phone", "datetime"]
                if all(field in filtered_df.columns for field in display_fields):
                    display_df = filtered_df[display_fields].rename(columns={
                        "customer_id": "Customer_id",
                        "name": "Name",
                        "type": "Type",
                        "email": "Email",
                        "phone": "Phone",
                        "datetime": "Created At"
                    })
                    st.dataframe(display_df, use_container_width=True, height=400)
                else:
                    st.dataframe(filtered_df, use_container_width=True, height=400)
                
                st.caption(f"Showing {len(filtered_df)} of {len(df)} customers")
            else:
                st.info("No customers match your filter criteria")
        else:
            st.error("Unable to load customer data")
            
    # ================ TAB 2: ADD CUSTOMER ================
    with tab2:
        st.subheader("Create New Customer")
        
        # Use form for better performance with form submission
        with st.form(key="new_customer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                cust_id = st.text_input("Customer ID (Optional)", disabled=True, placeholder="Auto to generate")
                name = st.text_input("Full Name *", placeholder="John Doe")
                email = st.text_input("Email Address *", placeholder="john.doe@example.com")
            
            with col2:
                phone = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")
                cust_type = st.selectbox("Customer Type *", ["Regular", "VIP", "New"])
                st.text_input("Creation Date", datetime.now().strftime("%Y-%m-%d %H:%M"), disabled=True,
                            help="Automatically set to today")
            
            submit_button = st.form_submit_button(label="✅ Create Customer", use_container_width=True, type="primary")
            
        if submit_button:
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
                            # Clear the cache to refresh customer list
                            fetch_customers.cache_clear()
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
                # Read file more efficiently based on size
                try:
                    if uploaded_file.name.endswith('.csv'):
                        # For CSV, use chunksize if file is large
                        if file_size > 1000:  # If larger than ~1MB
                            df = pd.read_csv(uploaded_file, nrows=5)  # Just read preview rows
                            st.warning("Large file detected. Only previewing first 5 rows.")
                        else:
                            df = pd.read_csv(uploaded_file)
                    else:  
                        # For Excel files
                        if file_size > 2000:  # If larger than ~2MB
                            df = pd.read_excel(uploaded_file, nrows=5)
                            st.warning("Large file detected. Only previewing first 5 rows.")
                        else:
                            df = pd.read_excel(uploaded_file)
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
                    return
                
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
                    
                    # Process in batches for better performance
                    if st.button("🚀 Process Import", type="primary", use_container_width=True):
                        if col_map["name"] == "-- Select --" or col_map["email"] == "-- Select --":
                            st.error("Name and Email columns are required")
                        else:
                            # Get the full dataframe now if we were only previewing
                            if file_size > 1000 and uploaded_file.name.endswith('.csv'):
                                uploaded_file.seek(0)  # Reset file pointer
                                df = pd.read_csv(uploaded_file)
                            elif file_size > 2000 and not uploaded_file.name.endswith('.csv'):
                                uploaded_file.seek(0)  
                                df = pd.read_excel(uploaded_file)
                                
                            progress_bar = st.progress(0)
                            import_status = st.empty()
                            import_status.info("Starting import...")
                            
                            # Process in batches of 50 for better performance
                            BATCH_SIZE = 50
                            total_rows = len(df)
                            success_count = 0
                            error_count = 0
                            skip_count = 0
                            
                            if duplicate_action == "Skip":
                                all_emails = df[col_map["email"]].dropna().astype(str).tolist()
                                import_status.info(f"Checking for existing emails...")
                                
                                existing_emails = set()
                                for i in range(0, len(all_emails), 100):  
                                    batch_emails = all_emails[i:i+100]
                                    for email in batch_emails:
                                        exists, _ = check_email_exists(email)
                                        if exists:
                                            existing_emails.add(email)
                            
                            for batch_start in range(0, total_rows, BATCH_SIZE):
                                batch_end = min(batch_start + BATCH_SIZE, total_rows)
                                batch = df.iloc[batch_start:batch_end]
                                
                                progress = batch_end / total_rows
                                progress_bar.progress(progress)
                                import_status.info(f"Processing rows {batch_start+1} to {batch_end} of {total_rows}...")
                                
                                batch_payloads = []
                                batch_updates = []
                                
                                for _, row in batch.iterrows():
                                    try:
                                        name = str(row[col_map["name"]]) if col_map["name"] != "-- Select --" else ""
                                        email = str(row[col_map["email"]]) if col_map["email"] != "-- Select --" else ""
                                        phone = str(row[col_map["phone"]]) if col_map["phone"] != "-- None --" else ""
                                        
                                        if col_map["type"] != "-- None --":
                                            cust_type = str(row[col_map["type"]])
                                            if cust_type not in ["VIP", "Regular", "New"]:
                                                cust_type = "New"  
                                        else:
                                            cust_type = default_type
                                        
                                        if not name or not email:
                                            skip_count += 1
                                            continue
                                        
                                        payload = {
                                            "name": name,
                                            "email": email,
                                            "phone": phone,
                                            "type": cust_type
                                        }
                                        
                                        if duplicate_action == "Skip":
                                            if email in existing_emails:
                                                skip_count += 1
                                                continue
                                            
                                            batch_payloads.append(payload)
                                        else: 
                                            exists, customer = check_email_exists(email)
                                            
                                            if exists:
                                                existing_id = customer['customer_id']
                                                batch_updates.append((existing_id, payload))
                                            else:
                                                batch_payloads.append(payload)
                                    
                                    except Exception as e:
                                        error_count += 1
                                        continue
                                
                                if batch_payloads:
                                    for payload in batch_payloads:
                                        try:
                                            res = requests.post(CUSTOMER_API_URL, json=payload)
                                            if res.status_code == 201:
                                                success_count += 1
                                            else:
                                                error_count += 1
                                        except Exception:
                                            error_count += 1
                                
                                if batch_updates:
                                    for customer_id, payload in batch_updates:
                                        try:
                                            update_res = requests.put(f"{CUSTOMER_API_URL}/{customer_id}", json=payload)
                                            if update_res.ok:
                                                success_count += 1
                                            else:
                                                error_count += 1
                                        except Exception:
                                            error_count += 1
                            
                            fetch_customers.cache_clear()
                            
                            import_status.success(f"Import complete! Successfully processed {success_count} customers.")
                            st.write(f"🟢 Added/Updated: {success_count} | 🟠 Skipped: {skip_count} | 🔴 Errors: {error_count}")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

    # ================ TAB 3: SEARCH & MODIFY ================
    with tab3:
        st.subheader("Find and Modify Customer")
        
        lookup_id = st.text_input("Customer ID *", key="lookup", placeholder="Enter ID to search")
        
        if not lookup_id:
            st.info("Enter a customer ID to search")
            return
            
        try:
            @st.cache_data(ttl=60)
            def get_customer(customer_id):
                res = requests.get(f"{CUSTOMER_API_URL}/{customer_id}")
                if res.ok:
                    return res.json()
                return None
            
            customer_data = get_customer(lookup_id)
            
            if customer_data:
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
                    with st.form(key="update_customer_form"):
                        update_col1, update_col2 = st.columns(2)
                        
                        with update_col1:
                            new_name = st.text_input("Name", 
                                                    value=customer_data.get("name", ""))
                            new_email = st.text_input("Email", 
                                                    value=customer_data.get("email", ""))
                        
                        with update_col2:
                            new_phone = st.text_input("Phone", 
                                                    value=customer_data.get("phone", ""))
                            new_type = st.selectbox("Type", 
                                                    options=["VIP", "Regular", "New"],
                                                    index=["VIP", "Regular", "New"].index(customer_data.get("type", "Regular")))
                        
                        update_submit = st.form_submit_button(label="💾 Save Changes", use_container_width=True, type="primary")
                    
                    if update_submit:
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
                                    fetch_customers.cache_clear()
                                    get_customer.clear()
                                else:
                                    st.error(f"Error {res.status_code}: {res.text}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                
                with delete_tab:
                    st.warning("⚠️ This action cannot be undone!")
                    if st.button("🗑️ Delete Customer", key="delete", use_container_width=True):
                        try:
                            res = requests.delete(f"{CUSTOMER_API_URL}/{lookup_id}")
                            if res.status_code == 200:
                                st.success("✅ Customer deleted successfully!")
                                fetch_customers.cache_clear()
                                get_customer.clear()
                                if 'found_customer' in st.session_state:
                                    del st.session_state['found_customer']
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to delete customer. Error: {res.text}")
                        except Exception as e:
                            st.error(f"🚨 Connection error: {str(e)}")                    
            else:
                st.error(f"Customer with ID '{lookup_id}' not found")
        except Exception as e:
            st.error(f"Error: {str(e)}")