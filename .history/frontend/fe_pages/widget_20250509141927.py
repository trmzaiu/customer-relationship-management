import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
from user_generator import load_user_db


# Apply custom CSS
def load_css():
    st.markdown("""
    <style>
        .main .block-container {padding-top: 2rem;}
        h1, h2, h3 {margin-bottom: 0.5rem;}
        .stMetric {background-color: #f8f9fa; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);}
        .stMetric label {font-weight: 500; color: #555;}
        .stMetric [data-testid="stMetricValue"] {font-size: 1.8rem !important; font-weight: 600 !important; color: #0f52ba;}
        div.stButton > button {
            width: 100%;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 5px;
        }
        div.stButton > button:first-child {
            background-color: #0f52ba;
            color: white;
        }
        .css-1544g2n {padding: 2rem 1rem 1.5rem;}
        .st-emotion-cache-13ln4jk {padding: 2rem 1rem 1.5rem;}
        .css-1544g2n h1 {
            color: #0f52ba;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 20px;
        }
        .chart-container {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        .dataframe {width: 100% !important;}
        .dataframe td {white-space: nowrap;}
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
            border-right: 1px solid #eaeaea;
        }
        [data-testid="stSidebarNav"] {
            padding-top: 1rem;
        }
        [data-testid="stSidebarNavItems"] {
            gap: 0.5rem;
        }
        .customer-form {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        [data-testid="stExpander"] {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        .success-msg {
            padding: 10px;
            background-color: #d4edda;
            color: #155724;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .error-msg {
            padding: 10px;
            background-color: #f8d7da;
            color: #721c24;
            border-radius: 5px;
            margin-bottom: 15px;
        }
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
        hr {margin: 1.5rem 0;}
    </style>
    """, unsafe_allow_html=True)

# --- Constants ---
CUSTOMER_API_URL = "http://localhost:5000/api/customers"
INTERACT_API_URL = "http://localhost:5000/api/interactions"

# --- App Navigation ---
def initialize_session_state():
    if 'user_db' not in st.session_state:
        st.session_state.user_db = load_user_db()
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_page' not in st.session_state and st.session_state.logged_in:
        st.session_state.current_page = "Dashboard"
    if 'sidebar_state' not in st.session_state:
        st.session_state.sidebar_state = "expanded"

def get_icon_for_page(page_name):
    icons = {
        "Dashboard": "🏠",
        "Customers": "👥",
        "Interactions": "📞",
        "Interact With Customer": "🤝",
        "Reports": "📊",
        "Settings": "⚙️",
        "Logout": "🚪"
    }
    return icons.get(page_name, "📄")

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
def navigation():
    st.markdown("""
    <style>
        /* CSS mạnh với selector cụ thể và !important */
        section[data-testid="stSidebar"] div.stButton > button {
            width: 100% !important;
            border: none !important;
            text-align: left !important;
            padding: 10px 15px !important;
            margin: 0 !important;
            border-radius: 0 !important;
            justify-content: flex-start !important;
            background: transparent !important;
            box-shadow: none !important;
            transition: background 0.3s !important;
            color: black;
        }
        
        section[data-testid="stSidebar"] div.stButton > button:hover {
            background: #f0f2f6 !important;
        }
        
        section[data-testid="stSidebar"] div.stButton > button:focus {
            outline: none !important;
            box-shadow: none !important;
        }
        
        /* Active state */
        section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
            background: #e1e8f0 !important;
            font-weight: 600 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("🏢 CRM System")
        st.markdown("---")
        
        pages = ["Dashboard", "Customers", "Interactions", "Interact With Customer", "Reports", "Logout"]
        
        for page in pages:
            icon = get_icon_for_page(page)
            is_active = st.session_state.get("current_page") == page
            if st.button(
                f"{icon} {page}",
                key=f"nav_{page}",
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        st.write("© 2025 CRM System")