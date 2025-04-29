import streamlit as st

def send_email_page():
    st.title("📧 Send Email")

    # Choose customer or segment to send email to
    customer_type = st.selectbox("Choose Customer Type to Send Email", ['VIP', 'Regular', 'All'])
    
    # Compose the email
    subject = st.text_input("Email Subject")
    body = st.text_area("Email Body")
    
    # Button to send email
    if st.button("Send Email"):
        st.success(f"Email sent to {customer_type} customers with subject: {subject}")
