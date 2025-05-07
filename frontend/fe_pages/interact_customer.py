import streamlit as st
import requests
from datetime import datetime

API_CUSTOMERS = "http://localhost:5000/api/customers"
API_INTERACTIONS = "http://localhost:5000/api/interactions"


def interact_customer_page():
    st.title("📞 Customer Interactions")

    # Get customers
    customer_data = requests.get(API_CUSTOMERS).json()
    customer_names = [c['name'] for c in customer_data]
    customer_lookup = {c['name']: c for c in customer_data}

    # Select type of interaction
    interaction_type = st.selectbox("Choose type of interaction", ['Email', 'Meeting', 'Call'])
    selected_customer = st.selectbox("Choose customer", customer_names)

    if interaction_type == "Email":
        subject = st.text_input("Email Subject")
        body = st.text_area("Email Body")
        if st.button("Send Email"):
            payload = {
                "customer_id": customer_lookup[selected_customer]["customer_id"],
                "type": "Email",
                "subject": subject,
                "notes": body
            }
            res = requests.post(API_INTERACTIONS, json=payload)
            if res.status_code == 201:
                st.success(f"📧 Email sent to {selected_customer}")

    elif interaction_type == "Meeting":
        meeting_date = st.date_input("Meeting Date", datetime.today())
        notes = st.text_area("Meeting Notes")
        if st.button("Create Meeting"):
            payload = {
                "customer_id": customer_lookup[selected_customer]["customer_id"],
                "type": "Meeting",
                "date": str(meeting_date),
                "notes": notes
            }
            res = requests.post(API_INTERACTIONS, json=payload)
            if res.status_code == 201:
                st.success(f"📅 Meeting scheduled with {selected_customer} on {meeting_date}")

    elif interaction_type == "Call":
        phone = customer_lookup[selected_customer]["phone"]
        st.text_input("Phone Number", phone, disabled=True)
        if st.button("Call"):
            payload = {
                "customer_id": customer_lookup[selected_customer]["customer_id"],
                "type": "Call",
                "phone": phone,
                "notes": f"Called {selected_customer}"
            }
            res = requests.post(API_INTERACTIONS, json=payload)
            if res.status_code == 201:
                st.success(f"📞 Called {selected_customer} at {phone}")