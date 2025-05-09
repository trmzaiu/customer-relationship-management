from frontend.fe_pages.widget import CUSTOMER_API_URL, INTERACT_API_URL
import streamlit as st
import requests
from datetime import datetime

def interact_customer_page():
    st.title("🤝 New Customer Interaction")
    st.markdown("<p style='color: #666; margin-bottom: 20px;'>Create a new interaction with your customers</p>", unsafe_allow_html=True)
    
    # Get customers
    try:
        customer_response = requests.get(CUSTOMER_API_URL)
        if customer_response.status_code == 200:
            customer_data = customer_response.json()
            if not customer_data:
                st.info("No customers found. Please add customers first.")
                return
            
            customer_names = [c['name'] for c in customer_data]
            customer_lookup = {c['name']: c for c in customer_data}
            
            # Interaction form
            st.markdown("<div class='customer-form'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Use the stored selected customer if available
                default_index = 0
                if 'selected_customer' in st.session_state and st.session_state.selected_customer in customer_names:
                    default_index = customer_names.index(st.session_state.selected_customer)
                
                selected_customer = st.selectbox(
                    "Select Customer", 
                    customer_names,
                    index=default_index
                )
            
            with col2:
                interaction_type = st.selectbox(
                    "Type of Interaction",
                    ['Email', 'Call', 'Meeting']
                )
            
            # Customer info display
            customer = customer_lookup[selected_customer]
            
            st.markdown(f"""
            <div style='background-color: #f8f9fa; border-radius: 10px; padding: 15px; margin: 15px 0;'>
                <h4 style='margin-top: 0;'>Customer Information</h4>
                <div style='display: flex; gap: 20px;'>
                    <div>
                        <div style='color: #666;'>Name:</div>
                        <div style='font-weight: 500;'>{customer.get('name', 'Unknown')}</div>
                    </div>
                    <div>
                        <div style='color: #666;'>Customer ID:</div>
                        <div style='font-weight: 500;'>{customer.get('customer_id', 'N/A')}</div>
                    </div>
                    <div>
                        <div style='color: #666;'>Customer Type:</div>
                        <div><span class='badge badge-{customer.get('type', '').lower()}'>{customer.get('type', 'Regular')}</span></div>
                    </div>
                </div>
                <div style='margin-top: 10px; display: flex; gap: 20px;'>
                    <div>
                        <div style='color: #666;'>Email:</div>
                        <div>{customer.get('email', 'No email available')}</div>
                    </div>
                    <div>
                        <div style='color: #666;'>Phone:</div>
                        <div>{customer.get('phone', 'No phone available')}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Interaction form based on type
            if interaction_type == "Email":
                st.markdown("<h4>📧 Send Email</h4>", unsafe_allow_html=True)
                
                subject = st.text_input("Email Subject", placeholder="Type the subject of your email")
                body = st.text_area("Email Body", height=200, placeholder="Type your email content here...")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col3:
                    if st.button("📤 Send Email", use_container_width=True):
                        if not subject or not body:
                            st.warning("Please fill all the fields")
                        else:
                            payload = {
                                "customer_id": customer["customer_id"],
                                "type": "Email",
                                "subject": subject,
                                "notes": body,
                                "timestamp": datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
                            }
                            
                            res = requests.post(INTERACT_API_URL, json=payload)
                            if res.status_code == 201:
                                st.success(f"📧 Email sent to {selected_customer}")
                                # Clear form fields
                                st.rerun()
                            else:
                                st.error(f"Error {res.status_code}: {res.text}")
            
            elif interaction_type == "Call":
                st.markdown("<h4>📞 Make a Call</h4>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    phone = st.text_input("Phone Number", value=customer["phone"], disabled=True)
                with col2:
                    call_duration = st.slider("Estimated Call Duration (minutes)", 5, 60, 15)
                
                call_notes = st.text_area("Call Notes", height=150, placeholder="Enter notes about the call...")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col3:
                    if st.button("📞 Make Call", use_container_width=True):
                        payload = {
                            "customer_id": customer["customer_id"],
                            "type": "Call",
                            "phone": phone,
                            "notes": call_notes or f"Called {selected_customer} for {call_duration} minutes",
                            "timestamp": datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
                        }
                        
                        res = requests.post(INTERACT_API_URL, json=payload)
                        if res.status_code == 201:
                            st.success(f"📞 Call logged with {selected_customer}")
                            # Clear form
                            st.rerun()
                        else:
                            st.error(f"Error {res.status_code}: {res.text}")
            
            elif interaction_type == "Meeting":
                st.markdown("<h4>🤝 Schedule Meeting</h4>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    meeting_date = st.date_input("Meeting Date", datetime.today())
                with col2:
                    meeting_time = st.time_input("Meeting Time", datetime.now().time())
                
                meeting_subject = st.text_input("Meeting Subject", placeholder="Brief description of meeting purpose")
                meeting_notes = st.text_area("Meeting Notes/Agenda", height=150, placeholder="Enter meeting agenda items...")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col3:
                    if st.button("📅 Schedule Meeting", use_container_width=True):
                        if not meeting_subject:
                            st.warning("Please enter a meeting subject")
                        else:
                            meeting_datetime = datetime.combine(meeting_date, meeting_time)
                            formatted_date = meeting_datetime.strftime("%a, %d %b %Y %H:%M:%S GMT")
                            
                            payload = {
                                "customer_id": customer["customer_id"],
                                "type": "Meeting",
                                "date": formatted_date,
                                "subject": meeting_subject,
                                "notes": meeting_notes or f"Meeting scheduled with {selected_customer}",
                                "timestamp": datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
                            }
                            
                            res = requests.post(INTERACT_API_URL, json=payload)
                            if res.status_code == 201:
                                st.success(f"📅 Meeting scheduled with {selected_customer} on {meeting_date}")
                                # Clear form
                                st.rerun()
                            else:
                                st.error(f"Error {res.status_code}: {res.text}")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Previous interactions with this customer
            st.markdown("---")
            st.markdown("<h3>Previous Interactions</h3>", unsafe_allow_html=True)
            
            try:
                interactions_response = requests.get(INTERACT_API_URL)
                if interactions_response.status_code == 200:
                    all_interactions = interactions_response.json()
                    customer_interactions = [i for i in all_interactions if str(i.get('customer_id')) == str(customer.get('customer_id'))]
                    
                    if not customer_interactions:
                        st.info(f"No previous interactions with {selected_customer}")
                    else:
                        # Sort by date descending
                        customer_interactions.sort(key=lambda x: x.get('timestamp', x.get('date', '')), reverse=True)
                        
                        for interaction in customer_interactions[:5]:  # Show last 5 interactions
                            col1, col2 = st.columns([1, 4])
                            
                            with col1:
                                if interaction.get('type') == 'Email':
                                    icon = "📧"
                                elif interaction.get('type') == 'Call':
                                    icon = "📞"
                                elif interaction.get('type') == 'Meeting':
                                    icon = "🤝"
                                else:
                                    icon = "🔔"
                                
                                st.markdown(f"""
                                <div style='text-align: center;'>
                                    <div style='font-size: 24px;'>{icon}</div>
                                    <div style='font-size: 0.8em; color: #666;'>{interaction.get('type')}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown(f"""
                                <div style='background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>
                                    <div style='display: flex; justify-content: space-between;'>
                                        <div style='font-weight: 500;'>{interaction.get('subject', interaction.get('type', 'Interaction'))}</div>
                                        <div style='color: #666; font-size: 0.9em;'>{interaction.get('timestamp', interaction.get('date', 'Unknown date'))}</div>
                                    </div>
                                    <div style='margin-top: 10px; color: #333;'>{interaction.get('notes', 'No notes available')}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error loading previous interactions: {e}")
        else:
            st.error(f"Failed to load customer data: {customer_response.status_code}")
    except Exception as e:
        st.error(f"Error: {e}")
