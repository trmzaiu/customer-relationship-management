from datetime import datetime
import streamlit as st
import requests
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
            color: #333;
        }
        .pagination a:hover {
            background-color: #f0f0f0;
        }
        .pagination a.active {
            background-color: #0d6efd;
            color: white;
            border-color: #0d6efd;
        }
        .main {
        padding: 1rem;
        }
        
        /* Navigation styles */
        .nav-item {
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .nav-item:hover {
            background-color: rgba(49, 51, 63, 0.1);
        }
        .nav-item.active {
            background-color: rgba(49, 51, 63, 0.2);
            font-weight: bold;
        }
        
        /* Card styles */
        .customer-card {
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }
        
        /* Form styles */
        .customer-form {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        /* Badge styles */
        .badge {
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        .badge-vip {
            background-color: #FFD700;
            color: #333;
        }
        .badge-regular {
            background-color: #B3E5FC;
            color: #0288D1;
        }
        .badge-new {
            background-color: #C8E6C9;
            color: #388E3C;
        }
        
        /* Stats card styles */
        .stats-card {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
        }
        .stats-number {
            font-size: 2rem;
            font-weight: bold;
            color: #1E88E5;
        }
        
        /* Chat styles */
        .chat-message {
            padding: 10px 15px;
            border-radius: 18px;
            margin-bottom: 10px;
            max-width: 80%;
            position: relative;
        }
        .user-message {
            background-color: #E3F2FD;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }
        .system-message {
            background-color: #F5F5F5;
            margin-right: auto;
            border-bottom-left-radius: 5px;
        }
        .message-time {
            font-size: 11px;
            color: #9E9E9E;
            margin-top: 3px;
        }
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
    if 'last_data_update' not in st.session_state:
        st.session_state.last_data_update = None
    if 'data_hash' not in st.session_state:
        st.session_state.data_hash = None

def check_email_exists(email_to_check):
    try:
        res = requests.get(CUSTOMER_API_URL)
        
        if not res.ok:
            return False, None
        
        data = res.json()
        
        for customer in data:
            if 'email' in customer and str(customer['email']).lower() == email_to_check.lower():
                return True, customer
        
        return False, None
    
    except Exception as e:
        print(f"Error checking email: {e}")
        return False, None

def check_customer_id_exist(id):
    try:
        res = requests.get(CUSTOMER_API_URL)
        
        if not res.ok:
            return False, None
        
        data = res.json()
        
        for customer in data:
            if 'customer_id' in customer and customer['customer_id'] == id:
                return True, customer
        
        return False, None
    
    except Exception as e:
        print(f"Error checking email: {e}")
        return False, None

def check_data_changes(new_data):
    """Check if data has changed since last load"""
    import hashlib
    current_hash = hashlib.md5(str(new_data).encode()).hexdigest()
    
    if st.session_state.data_hash != current_hash:
        st.session_state.last_data_update = datetime.now()
        st.session_state.data_hash = current_hash
        return True
    return False


def get_icon_for_page(page_name):
    icons = {
        "Dashboard": "🏠",
        "Customers": "👥",
        "Interactions": "📞",
        "Reports": "📊",
        "Settings": "⚙️",
        "Logout": "🚪"
    }
    return icons.get(page_name, "📄")

def navigation():
    st.markdown("""
    <style>
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
        
        pages = ["Dashboard", "Customers", "Interactions", "Reports", "Logout"]
        
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