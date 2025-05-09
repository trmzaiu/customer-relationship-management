import streamlit as st
import pandas as pd
import requests
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))

from widget import INTERACT_API_URL, check_customer_id_exist

def interaction_page():
    st.title("📞 Interactions")
    st.header("Interaction History")

    # Hiển thị loading trước khi fetch data
    with st.spinner('Loading interactions...'):
        res = requests.get(INTERACT_API_URL)
        
        if res.status_code == 200:
            data = res.json()

            if not data:
                st.info("No interactions found.")
                return  # Kết thúc sớm nếu không có data

            # Chuẩn bị dữ liệu song song
            display_fields = ["customer_id", "type", "notes", "date"]
            df = pd.DataFrame(data)[display_fields]

            # Đổi tên cột
            df = df.rename(columns={
                "customer_id": "Customer",
                "type": "Interaction Type",
                "notes": "Notes",
                "date": "Date"
            })

            # Xử lý datetime hiệu quả hơn
            df["Date"] = pd.to_datetime(df["Date"], format="%a, %d %b %Y %H:%M:%S %Z", errors='coerce')
            df["Date"] = df["Date"].dt.strftime("%b %d, %Y %H:%M")
            
            # Tối ưu việc lấy customer names
            if 'Customer' in df.columns:
                # Tạo dict ánh xạ customer_id -> customer_data để tránh lặp lại API calls
                unique_customer_ids = df['Customer'].unique()
                customer_map = {}
                
                for customer_id in unique_customer_ids:
                    _, customer_data = check_customer_id_exist(customer_id)
                    customer_map[customer_id] = customer_data
                
                # Ánh xạ nhanh bằng map
                df['Customer'] = df['Customer'].astype(str).map(customer_map)
                
            # Cache dataframe để không phải tính toán lại khi rerun
            st.dataframe(df)
        else:
            st.error(f"Failed to fetch data: {res.status_code}")

    if st.button("➕ Add New Interaction"):
        st.session_state.current_page = "Interact With Customer"
        st.rerun()