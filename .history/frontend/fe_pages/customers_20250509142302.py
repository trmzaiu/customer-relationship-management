import math
import streamlit as st
import requests
import pandas as pd
import sys
import os
from io import StringIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))

from widget import CUSTOMER_API_URL

def show_edit_modal(customer):
    modal_html = f"""
    <div id="editModal" class="modal" style="display: block;">
        <div class="modal-content">
            <span class="close" onclick="document.getElementById('editModal').style.display='none'">&times;</span>
            <h2>✏️ Edit Customer</h2>
            <div id="modalContent"></div>
        </div>
    </div>
    <script>
        function closeModal() {{
            document.getElementById('editModal').style.display = 'none';
        }}
    </script>
    """
    st.markdown(modal_html, unsafe_allow_html=True)
    
    # Nội dung form edit
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            cust_id = st.text_input("Customer ID", value=customer.get('customer_id', ''), disabled=True, key="modal_id")
            up_name = st.text_input("Name", value=customer.get('name', ''), key="modal_name")
            up_email = st.text_input("Email", value=customer.get('email', ''), key="modal_email")
        
        with col2:
            up_phone = st.text_input("Phone", value=customer.get('phone', ''), key="modal_phone")
            up_type = st.selectbox("Type", ["VIP", "Regular", "New"], 
                                 index=["VIP", "Regular", "New"].index(customer.get('type', 'Regular')), 
                                 key="modal_type")
            up_notes = st.text_area("Notes", value=customer.get('notes', ''), key="modal_notes")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Update", key="modal_update"):
                payload = {
                    "name": up_name,
                    "email": up_email,
                    "phone": up_phone,
                    "type": up_type,
                    "notes": up_notes
                }
                
                res = requests.put(f"{CUSTOMER_API_URL}/{cust_id}", json=payload)
                if res.ok:
                    st.success("Customer updated successfully!")
                    st.session_state.modal_open = False
                    load_customers()
                    st.experimental_rerun()
                else:
                    st.error(f"Error {res.status_code}: {res.text}")
        
        with col2:
            if st.button("❌ Cancel", key="modal_cancel"):
                st.session_state.modal_open = False
                st.experimental_rerun()

def customer_page():
    st.title("👥 Customer Management")
    st.markdown("<p style='color: #666; margin-bottom: 20px;'>Add, view, edit and delete customer information</p>", unsafe_allow_html=True)
    
    # Tabs for different customer operations
    tab1, tab2 = st.tabs(["📋 Customer List", "➕ Add Customer"])
    
    # Initialize session state for customers data if not already present
    if 'customer_data' not in st.session_state:
        load_customers()
    
    with tab1:
        # Search and Filter Section
        st.markdown("<div class='customer-form'>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        
        with col1:
            search_term = st.text_input("Search by name or email", placeholder="Enter search term")
        
        with col2:
            filter_type = st.selectbox("Filter by type", ["All Types", "VIP", "Regular", "New"])
        
        with col3:
            st.write("")
            st.write("")
            load_btn = st.button("🔍 Search", use_container_width=True)
            if load_btn:
                load_customers()
        
        with col4:
            st.write("")
            st.write("")
            # Toggle between card and table view
            view_type = st.radio("View as:", ["Cards", "Table"], horizontal=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display customers with filters applied
        if 'customer_data' in st.session_state:
            data = st.session_state.customer_data
            
            # Apply filters
            if search_term:
                data = [c for c in data if search_term.lower() in c.get('name', '').lower() or 
                        search_term.lower() in c.get('email', '').lower()]
            
            if filter_type != "All Types":
                data = [c for c in data if c.get('type') == filter_type]
            
            if not data:
                st.info("No customers match your search criteria.")
            else:
                if view_type == "Table":
                    # Convert to DataFrame for table display
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
                    
                    # Display table with download button
                    col1, col2 = st.columns([9, 1])
                    with col2:
                        csv = convert_df_to_csv(df)
                        st.download_button(
                            label="📥 CSV",
                            data=csv,
                            file_name="customers.csv",
                            mime="text/csv"
                        )
                    
                    # Add action buttons to the table
                    df_with_actions = df.copy()
                    st.dataframe(df, use_container_width=True)
                    
                    # Separate action buttons below the table
                    st.markdown("### Actions")
                    selected_id = st.selectbox("Select customer ID for actions:", 
                                             options=df["ID"].tolist(),
                                             format_func=lambda x: f"{x} - {df[df['ID']==x]['Name'].values[0]}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✏️ Edit Customer", use_container_width=True):
                            # Find selected customer by ID
                            selected_customer = next((c for c in data if c.get('customer_id') == selected_id), None)
                            if selected_customer:
                                st.session_state.edit_customer = selected_customer
                                st.session_state.show_edit_modal = True
                                st.rerun()
                    
                    with col2:
                        if st.button("📞 Contact Customer", use_container_width=True):
                            selected_customer = next((c for c in data if c.get('customer_id') == selected_id), None)
                            if selected_customer:
                                st.session_state.current_page = "Interact With Customer"
                                st.session_state.selected_customer = selected_customer.get('name')
                                st.rerun()
                    
                    with col3:
                        if st.button("🗑️ Delete Customer", use_container_width=True):
                            selected_customer = next((c for c in data if c.get('customer_id') == selected_id), None)
                            if selected_customer:
                                delete_customer(selected_customer.get('customer_id'))
                
                else: 
                    # Phân trang
                    items_per_page = 10
                    total_pages = math.ceil(len(data) / items_per_page)
                    page_number = st.session_state.get('current_page', 1)
                    
                    # Hiển thị pagination control
                    pagination_html = """
                    <div class="pagination">
                    """
                    for i in range(1, total_pages + 1):
                        active = "active" if i == page_number else ""
                        pagination_html += f"""
                        <div class="page-item">
                            <a class="page-link {active}" href="#" onclick="streamlitSessionState.set('current_page', {i}); streamlitRerun()">{i}</a>
                        </div>
                        """
                    pagination_html += "</div>"
                    st.markdown(pagination_html, unsafe_allow_html=True)
                    
                    # Hiển thị customers cho trang hiện tại
                    start_idx = (page_number - 1) * items_per_page
                    end_idx = start_idx + items_per_page
                    paginated_data = data[start_idx:end_idx]
                    
                    for i, customer in enumerate(paginated_data):
                        col1, col2 = st.columns([10, 2])
                        
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
                            if st.button("✏️ Edit", key=f"edit_{i}"):
                                st.session_state.edit_customer = customer
                                st.session_state.modal_open = True
                                st.experimental_rerun()
                            
                            if st.button("📞 Contact", key=f"contact_{i}"):
                                st.session_state.current_page = "Interact With Customer"
                                st.session_state.selected_customer = customer.get('name')
                                st.experimental_rerun()
                                
                            if st.button("🗑️ Delete", key=f"delete_{i}"):
                                delete_customer(customer.get('customer_id'))
                            else:
                                st.info("Loading customer data...")
                                load_customers()
                                st.rerun()
    
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
                        # Refresh the customer data
                        load_customers()
                    else:
                        st.error(f"Error {res.status_code}: {res.text}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Edit customer modal
    if st.session_state.get('modal_open', False) and 'edit_customer' in st.session_state:
        show_edit_modal(st.session_state.edit_customer)

def load_customers():
    """Load customer data from API and store in session state"""
    try:
        res = requests.get(CUSTOMER_API_URL)
        if res.ok:
            data = res.json()
            st.session_state.customer_data = data
        else:
            st.error(f"Failed to load customer data. Status code: {res.status_code}")
    except Exception as e:
        st.error(f"Error loading data: {e}")

def delete_customer(customer_id):
    """Delete a customer by ID"""
    res = requests.delete(f"{CUSTOMER_API_URL}/{customer_id}")
    if res.ok:
        # Remove from session state if present
        if 'customer_data' in st.session_state:
            st.session_state.customer_data = [c for c in st.session_state.customer_data 
                                             if c.get('customer_id') != customer_id]
        st.success("Customer deleted successfully!")
        st.rerun()
    else:
        st.error(f"Error {res.status_code}: {res.text}")

def convert_df_to_csv(df):
    """Convert dataframe to CSV for download"""
    return df.to_csv(index=False).encode('utf-8')

def show_edit_modal():
    """Display the edit customer modal"""
    customer = st.session_state.edit_customer
    
    # Create a modal-like interface
    with st.container():
        st.markdown("""
        <style>
        .modal-container {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='modal-container'>", unsafe_allow_html=True)
        st.subheader("✏️ Edit Customer")
        
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
            up_notes = st.text_area("Notes", value=customer.get('notes', ''), key="up_notes")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write("")
        with col2:
            if st.button("✅ Update", use_container_width=True):
                payload = {
                    "name": up_name,
                    "email": up_email,
                    "phone": up_phone,
                    "type": up_type,
                    "notes": up_notes
                }
                
                res = requests.put(f"{CUSTOMER_API_URL}/{cust_id}", json=payload)
                if res.ok:
                    st.success("Customer updated successfully!")
                    # Close modal and refresh data
                    st.session_state.pop('edit_customer', None)
                    st.session_state.pop('show_edit_modal', None)
                    load_customers()
                    st.rerun()
                else:
                    st.error(f"Error {res.status_code}: {res.text}")
        
        with col3:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.pop('edit_customer', None)
                st.session_state.pop('show_edit_modal', None)
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)