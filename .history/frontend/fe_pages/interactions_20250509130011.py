import streamlit as st
import requests
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))

from widget import INTERACT_API_URL

def interaction_page():
    st.title("📞 Interaction History")
    st.markdown("<p style='color: #666; margin-bottom: 20px;'>View all customer interactions and communication history</p>", unsafe_allow_html=True)
    
    try:
        with st.spinner("Loading interactions..."):
            res = requests.get(INTERACT_API_URL)
            if res.status_code == 200:
                data = res.json()
                
                if not data:
                    st.info("No interactions found in the system.")
                else:
                    # Filter and search options
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        interaction_filter = st.selectbox(
                            "Filter by type",
                            ["All Types", "Email", "Call", "Meeting"]
                        )
                    
                    with col2:
                        search_term = st.text_input("Search by customer ID or notes", placeholder="Enter search term")
                    
                    with col3:
                        st.write("")
                        st.write("")
                        filter_button = st.button("🔍 Filter", use_container_width=True)
                    
                    # Apply filters
                    if filter_button or 'filtered_interactions' in st.session_state:
                        filtered_data = data.copy()
                        
                        if interaction_filter != "All Types":
                            filtered_data = [i for i in filtered_data if i.get('type') == interaction_filter]
                        
                        if search_term:
                            filtered_data = [i for i in filtered_data if 
                                            search_term.lower() in str(i.get('customer_id', '')).lower() or 
                                            search_term.lower() in i.get('notes', '').lower()]
                        
                        st.session_state.filtered_interactions = filtered_data
                    else:
                        filtered_data = data
                        st.session_state.filtered_interactions = filtered_data
                    
                    # Display interactions
                    st.markdown("### Interaction List")
                    
                    for i, interaction in enumerate(filtered_data):
                        col1, col2 = st.columns([1, 3])
                        
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
                            <div style='background-color: #f8f9fa; border-radius: 10px; padding: 15px; text-align: center;'>
                                <div style='font-size: 24px;'>{icon}</div>
                                <div style='font-weight: 500; margin-top: 5px;'>{interaction.get('type', 'Unknown')}</div>
                                <div style='font-size: 0.8em; color: #666;'>Customer #{interaction.get('customer_id', 'N/A')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div style='background-color: white; border-radius: 10px; padding: 15px; height: 100%; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>
                                <div style='display: flex; justify-content: space-between;'>
                                    <div style='font-weight: 500;'>{interaction.get('subject', interaction.get('type', 'Interaction'))}</div>
                                    <div style='color: #666; font-size: 0.9em;'>{interaction.get('timestamp', interaction.get('date', 'Unknown date'))}</div>
                                </div>
                                <div style='margin-top: 10px; color: #333;'>{interaction.get('notes', 'No notes available')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                    
                    # Add New Interaction button
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col3:
                        if st.button("➕ New Interaction", use_container_width=True):
                            st.session_state.current_page = "Interact With Customer"
                            st.rerun()
            else:
                st.error(f"Failed to fetch interaction data: {res.status_code}")
    except Exception as e:
        st.error(f"Error: {e}")
