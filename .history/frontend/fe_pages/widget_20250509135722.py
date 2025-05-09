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

def navigation():
    with st.sidebar:
        st.title("🏢 CRM System")
        st.markdown("---")
        
        pages = ["Dashboard", "Customers", "Interactions", "Interact With Customer", "Reports", "Logout"]
        
        for page in pages:
            icon = get_icon_for_page(page)
            if st.sidebar.button(f"{icon} {page}", key=f"nav_{page}"):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        st.write("© 2025 CRM System")