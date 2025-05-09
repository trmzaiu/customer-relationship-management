# interaction_page.py
import pandas as pd
import streamlit as st

def interaction_page():
    st.title("📞 Interactions")
    st.header("Interaction History")
    
    # Kiểm tra nếu có dữ liệu trong cache
    if 'interaction_data' not in st.session_state or st.session_state.interaction_data is None:
        st.warning("Dữ liệu đang được tải...")
        st.button("Thử lại", on_click=load_interaction_data)
        return
    
    data = st.session_state.interaction_data
    
    if not data:
        st.info("Không tìm thấy tương tác nào.")
        return

    # Tạo dataframe từ dữ liệu đã cache
    display_fields = ["customer_id", "type", "notes", "date"]
    df = pd.DataFrame(data)[display_fields]

    df = df.rename(columns={
        "customer_id": "Customer",
        "type": "Interaction Type",
        "notes": "Notes",
        "date": "Date"
    })

    # Xử lý datetime
    df["Date"] = pd.to_datetime(df["Date"], format="%a, %d %b %Y %H:%M:%S %Z", errors='coerce')
    df["Date"] = df["Date"].dt.strftime("%b %d, %Y %H:%M")
    
    # Lấy thông tin khách hàng từ cache
    if 'Customer' in df.columns and 'customer_cache' in st.session_state:
        df['Customer'] = df['Customer'].map(st.session_state.customer_cache)
    
    # Hiển thị dataframe
    st.dataframe(df)

    # Nút refresh dữ liệu
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Làm mới dữ liệu"):
            load_interaction_data()
            st.rerun()
    
    with col2:
        if st.button("➕ Thêm Tương Tác Mới"):
            st.session_state.current_page = "Interact With Customer"
            st.rerun()