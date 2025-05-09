import streamlit as st
import requests
import pandas as pd
import sys
import os
from io import StringIO
from streamlit_modal import Modal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))

from widget import CUSTOMER_API_URL

# CSS styles
st.markdown("""
<style>
    
    /* Pagination styles */
    .pagination {
        display: flex;
        justify-content: center;
        gap: 5px;
        margin: 15px 0;
    }
    .pagination a {
        padding: 5px 10px;
        border-radius: 5px;
        border: 1px solid #ddd;
        text-decoration: none;
    }
    .pagination a:hover {
        background-color: #f0f0f0;
    }
    .pagination a.active {
        background-color: #0d6efd;
        color: white;
        border-color: #0d6efd;
    }
    
    /* Customer card styles */
    .customer-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
    }
    .badge-vip {
        background-color: #ffd700;
        color: #333;
    }
    .badge-regular {
        background-color: #007bff;
        color: white;
    }
    .badge-new {
        background-color: #28a745;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def show_edit_modal(customer):
    # Initialize the streamlit-modal
    modal = Modal(
        "Edit Customer", 
        key="edit_customer_modal",
        padding=20,
        max_width=800
    )
    
    # Open the modal
    open_modal = modal.open()
    
    if open_modal:
        st.markdown("### ✏️ Edit Customer")
        
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
                    modal.close()
                    st.rerun()
                else:
                    st.error(f"Error {res.status_code}: {res.text}")
        
        with col2:
            if st.button("❌ Cancel", key="modal_cancel"):
                st.session_state.modal_open = False
                modal.close()
                st.rerun()

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

def customer_page():
    st.title("👥 Customer Management")
    st.markdown("<p style='color: #666; margin-bottom: 20px;'>Add, view, edit and delete customer information</p>", unsafe_allow_html=True)
    
    # Initialize session states if not already present
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'customer_data' not in st.session_state:
        load_customers()
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "customer_list"
    if 'modal_open' not in st.session_state:
        st.session_state.modal_open = False
    
    # Handle tab selection
    tab_options = ["📋 Customer List", "➕ Add Customer"]
    tab_index = 0 if st.session_state.active_tab == "customer_list" else 1
    
    # Create tabs with the selected tab active
    tab1, tab2 = st.tabs(tab_options)
    
    # Function to set active tab
    def set_active_tab(tab_name):
        st.session_state.active_tab = tab_name
    
    # Handle different tabs/pages based on active_tab state
    if st.session_state.active_tab == "customer_list":
        with tab1:
            # Search and Filter Section
            st.markdown("<div class='customer-form'>", unsafe_allow_html=True)
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
                st.session_state.current_page = 1
            else:
                if view_type == "Table":
                    # Table view implementation
                    display_fields = ["customer_id", "name", "type", "email", "phone"]
                    df = pd.DataFrame(data)[display_fields]
                    
                    df = df.rename(columns={
                        "customer_id": "ID",
                        "name": "Name",
                        "type": "Type",
                        "email": "Email",
                        "phone": "Phone"
                    })
                    
                    col1, col2 = st.columns([9, 1])
                    with col2:
                        csv = convert_df_to_csv(df)
                        st.download_button(
                            label="📥 CSV",
                            data=csv,
                            file_name="customers.csv",
                            mime="text/csv"
                        )
                    
                    st.dataframe(df, use_container_width=True)
                    
                    st.markdown("### Actions")
                    selected_id = st.selectbox("Select customer ID for actions:", 
                                             options=df["ID"].tolist(),
                                             format_func=lambda x: f"{x} - {df[df['ID']==x]['Name'].values[0]}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✏️ Edit Customer", use_container_width=True):
                            selected_customer = next((c for c in data if c.get('customer_id') == selected_id), None)
                            if selected_customer:
                                st.session_state.edit_customer = selected_customer
                                st.session_state.modal_open = True
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
                
                else:  # Cards view
                    items_per_page = 10
                    total_pages = max(1, math.ceil(len(data) / items_per_page))
                    
                    # Ensure page_number is valid
                    try:
                        page_number = int(st.session_state.current_page)
                        page_number = max(1, min(page_number, total_pages))
                        st.session_state.current_page = page_number
                    except:
                        page_number = 1
                        st.session_state.current_page = 1
                    
                    # Pagination controls
                    col1, col2, col3 = st.columns([1, 6, 1])
                    with col2:
                        # Fixed pagination with proper event handlers for Streamlit
                        st.markdown(f"<p style='text-align:center'>Page {page_number} of {total_pages}</p>", unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col1:
                            if page_number > 1:
                                if st.button("⬅️ Previous", key="prev_page"):
                                    st.session_state.current_page = page_number - 1
                                    st.rerun()
                        
                        with col3:
                            if page_number < total_pages:
                                if st.button("Next ➡️", key="next_page"):
                                    st.session_state.current_page = page_number + 1
                                    st.rerun()
                        
                        # Page number input
                        with col2:
                            new_page = st.number_input("Go to page", min_value=1, max_value=total_pages, 
                                                      value=page_number, key="go_to_page")
                            if new_page != page_number:
                                st.session_state.current_page = new_page
                                st.rerun()
                    
                    # Display customers for current page
                    start_idx = (page_number - 1) * items_per_page
                    end_idx = start_idx + items_per_page
                    paginated_data = data[start_idx:end_idx]
                    
                    for i, customer in enumerate(paginated_data):
                        col1, col2 = st.columns([10, 2])
                        
                        with col1:
                            badge_class = f"badge-{customer.get('type', '').lower()}"
                            st.markdown(f"""
                            <div class='customer-card'>
                                <h3 style='margin:0;'>{customer.get('name', 'Unknown')}</h3>
                                <div style='margin:5px 0;'>
                                    <span class='badge {badge_class}'>{customer.get('type', '')}</span>
                                    <span style='color:#666; margin-left:10px;'>ID: {customer.get('customer_id', 'N/A')}</span>
                                </div>
                                <div style='margin-top:8px;'>
                                    <span style='color:#666;'>📧 {customer.get('email', 'No email')}</span><br>
                                    <span style='color:#666;'>📱 {customer.get('phone', 'No phone')}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            if st.button("✏️ Edit", key=f"edit_{i}_{customer.get('customer_id')}"):
                                st.session_state.edit_customer = customer
                                st.session_state.modal_open = True
                                st.rerun()
                            
                            if st.button("📞 Contact", key=f"contact_{i}_{customer.get('customer_id')}"):
                                st.session_state.active_tab = "contact_customer"
                                st.session_state.selected_customer = customer.get('name')
                                st.rerun()
                                
                            if st.button("🗑️ Delete", key=f"delete_{i}_{customer.get('customer_id')}"):
                                delete_confirm = st.checkbox(f"Confirm delete", key=f"confirm_{i}_{customer.get('customer_id')}")
                                if delete_confirm:
                                    delete_customer(customer.get('customer_id'))
        else:
            st.info("Loading customer data...")
            load_customers()
            st.rerun()
    
    elif st.session_state.active_tab == "add_customer":
        with tab2:
            # Add Customer form
            st.markdown("<div class='customer-form'>", unsafe_allow_html=True)
        # Add Customer form
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
                    **({"customer_id": int(cust_id)} if cust_id and cust_id.isdigit() else {}),
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
                        # Clear form
                        for key in ["new_id", "new_name", "new_email", "new_phone"]:
                            if key in st.session_state:
                                del st.session_state[key]
                        load_customers()
                    else:
                        st.error(f"Error {res.status_code}: {res.text}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Contact customer tab
    elif st.session_state.active_tab == "contact_customer":
        render_contact_customer()
    
    # Edit customer modal
    if st.session_state.get('modal_open', False) and 'edit_customer' in st.session_state:
        show_edit_modal(st.session_state.edit_customer)
        
    # Add a check to ensure modal_open is initialized in session state
    if 'modal_open' not in st.session_state:
        st.session_state.modal_open = False

def render_contact_customer():
    if 'selected_customer' not in st.session_state:
        st.error("No customer selected")
        if st.button("Back to Customer List"):
            st.session_state.active_tab = "customer_list"
            st.rerun()
        return
    
    customer_name = st.session_state.selected_customer
    st.title(f"📞 Contact {customer_name}")
    
    st.markdown("### Contact Options")
    
    contact_option = st.radio(
        "How would you like to contact this customer?",
        options=["Email", "Phone Call", "SMS", "Meeting"],
        horizontal=True
    )
    
    if contact_option == "Email":
        st.text_area("Email Subject", key="email_subject", placeholder="Enter email subject...")
        st.text_area("Email Body", height=200, key="email_body", 
                    placeholder="Compose your email message here...")
        
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("Include company logo", value=True)
            st.checkbox("Request read receipt")
        with col2:
            st.checkbox("Mark as important")
            st.checkbox("Save as template")
        
        if st.button("Send Email", type="primary"):
            st.success(f"Email sent to {customer_name}!")
    
    elif contact_option == "Phone Call":
        st.text_area("Call Notes", height=100, placeholder="Enter notes about the call purpose...")
        
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("Record call")
        with col2:
            st.checkbox("Set follow-up reminder")
        
        if st.button("Start Call", type="primary"):
            st.success(f"Calling {customer_name}...")
    
    elif contact_option == "SMS":
        st.text_area("Message", height=100, placeholder="Type your SMS message...")
        
        if st.button("Send SMS", type="primary"):
            st.success(f"SMS sent to {customer_name}!")
    
    else:  # Meeting
        st.date_input("Meeting Date")
        st.time_input("Meeting Time")
        st.text_input("Meeting Location/Link")
        st.text_area("Agenda", height=100, placeholder="Enter meeting agenda...")
        
        if st.button("Schedule Meeting", type="primary"):
            st.success(f"Meeting scheduled with {customer_name}!")
    
    if st.button("Back to Customer List"):
        st.session_state.active_tab = "customer_list"
        st.rerun()import math