import math
import streamlit as st
import requests
import pandas as pd
import sys
import os
from io import StringIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))

from widget import CUSTOMER_API_URL

# CSS styles
st.markdown("""
<style>
    /* Modal styles */
    .modal {
        display: none;
        position: fixed;
        z-index: 1001;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.4);
    }
    .modal-content {
        background-color: #fefefe;
        margin: 10% auto;
        padding: 20px;
        border-radius: 10px;
        width: 60%;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .close {
        color: #aaa;
        float: right;
        font-size: 28px;
        font-weight: bold;
    }
    .close:hover {
        color: black;
        cursor: pointer;
    }
    
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
    
    # Initialize session state for pagination
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
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
                        pagination_html = """
                        <div class="pagination">
                        """
                        
                        if page_number > 1:
                            pagination_html += f"""
                            <a href="#" onclick="window.streamlitSessionState.set('current_page', {page_number-1}); window.streamlitRerun()">
                                &laquo; Previous
                            </a>
                            """
                        
                        for i in range(1, total_pages + 1):
                            active = "active" if i == page_number else ""
                            pagination_html += f"""
                            <a href="#" onclick="window.streamlitSessionState.set('current_page', {i}); window.streamlitRerun()" 
                               class="{active}">
                                {i}
                            </a>
                            """
                        
                        if page_number < total_pages:
                            pagination_html += f"""
                            <a href="#" onclick="window.streamlitSessionState.set('current_page', {page_number+1}); window.streamlitRerun()">
                                Next
                            </a>
                            """
                        
                        pagination_html += "</div>"
                        st.markdown(pagination_html, unsafe_allow_html=True)
                    
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
                        # Clear form
                        for key in ["new_id", "new_name", "new_email", "new_phone"]:
                            if key in st.session_state:
                                del st.session_state[key]
                        load_customers()
                    else:
                        st.error(f"Error {res.status_code}: {res.text}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Edit customer modal
    if st.session_state.get('modal_open', False) and 'edit_customer' in st.session_state:
        show_edit_modal(st.session_state.edit_customer)