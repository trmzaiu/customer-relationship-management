import streamlit as st
import pandas as pd
import plotly.express as px
import time
import requests
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))

from widget import CUSTOMER_API_URL, INTERACT_API_URL, check_customer_id_exist

def dashboard_page(auto_refresh=False):
    st.title("🏠 Dashboard Overview")
    st.markdown("<p style='color: #666; margin-bottom: 20px;'>Welcome to your customer management dashboard</p>", unsafe_allow_html=True)
    
    try:
        response = requests.get(CUSTOMER_API_URL)
        if response.status_code == 200:
            customers_df = pd.DataFrame(response.json())
        else:
            st.error(f"Failed to load customer data. Status code: {response.status_code}")
            return
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    try:
        response = requests.get(INTERACT_API_URL)
        if response.status_code == 200:
            interact_df = pd.DataFrame(response.json())
        else:
            st.error(f"Failed to load interaction data. Status code: {response.status_code}")
            return
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    total_customers = customers_df.shape[0]
    vip_customers = customers_df[customers_df['type'] == 'VIP'].shape[0]
    regular_customers = customers_df[customers_df['type'] == 'Regular'].shape[0]
    new_customers = customers_df[customers_df['type'] == 'New'].shape[0]
    
    # KPIs with improved styling
    st.markdown("<div style='margin-bottom: 10px;'><strong>Key Customer Metrics</strong></div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Customers", total_customers, delta=None)
    with col2:
        st.metric("VIP Customers", vip_customers, delta=None)
    with col3:
        st.metric("Regular Customers", regular_customers, delta=None)
    with col4:
        st.metric("New Customers", new_customers, delta=None)

    st.markdown("---")
    st.subheader("📊 Customer Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h4>Customer Distribution</h4>", unsafe_allow_html=True)
        customer_summary = customers_df['type'].value_counts().reset_index()
        customer_summary.columns = ['Customer Type', 'Count']
        
        colors = {'VIP': '#ffd700', 'Regular': '#007bff', 'New': '#28a745'}
        
        fig_pie = px.pie(
            customer_summary, 
            names='Customer Type', 
            values='Count',
            hole=0.4,
            color='Customer Type',
            color_discrete_map=colors
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            height=300
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h4>Customer Growth</h4>", unsafe_allow_html=True)
        
        if 'datetime' in customers_df.columns:
            try:
                customers_df['date'] = pd.to_datetime(customers_df['datetime'], format='ISO8601', errors='coerce')
                if customers_df['date'].isna().any():
                    customers_df['date'] = pd.to_datetime(customers_df['datetime'], format='mixed', errors='coerce')
                customers_df['date'] = customers_df['date'].dt.date
            except Exception as e:
                st.warning(f"Could not format datetime column: {str(e)}")
                customers_df['date'] = customers_df['datetime'].date

            growth_data = customers_df.groupby('date').size().reset_index(name='New Customers')
            growth_data = growth_data.sort_values('date')
            
            fig_growth = px.line(
                growth_data, 
                x='date', 
                y='New Customers',
                markers=True
            )
            fig_growth.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                height=300,
                xaxis_title="Date",
                yaxis_title="New Customers"
            )
            st.plotly_chart(fig_growth, use_container_width=True)
        else:
            st.info("Customer growth data not available")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Interaction Analytics
    st.markdown("---")
    st.subheader("📈 Interaction Analytics")
    
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    # Process interaction data - FIXED THIS PART
    if 'date' not in interact_df.columns:
        # Use timestamp column if available, otherwise try date column
        date_column = 'timestamp' if 'timestamp' in interact_df.columns else 'date'
        if date_column in interact_df.columns:
            interact_df['date'] = pd.to_datetime(interact_df[date_column], errors='coerce')
        else:
            interact_df['date'] = None
    else:
        # Convert existing date column to datetime
        interact_df['date'] = pd.to_datetime(interact_df['date'], errors='coerce')
    
    if not interact_df['date'].isnull().all():
        # Only try to extract .dt.date if we have datetime values
        interact_df['date'] = interact_df['date'].dt.date
        weekly_trend = interact_df.groupby('date').size().reset_index(name='Interactions')
        
        fig_line = px.line(
            weekly_trend, 
            x='date', 
            y='Interactions', 
            markers=True,
            line_shape='spline'
        )
        fig_line.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            height=350,
            title="Weekly Interaction Trends",
            xaxis_title="Date",
            yaxis_title="Number of Interactions",
            hovermode="x unified"
        )
        fig_line.update_traces(line=dict(width=3, color='#0f52ba'))
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Interaction trend data not available")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📝 Recent Activities")
    
    if not interact_df.empty and 'type' in interact_df.columns:
        if 'date' in interact_df.columns and not interact_df['date'].isnull().all():
            recent_activities = interact_df.sort_values('date', ascending=False).head(5)
        else:
            recent_activities = interact_df.head(5)
        
        for _, activity in recent_activities.iterrows():
            col1, col2 = st.columns([1, 25])
            
            with col1:
                if activity['type'] == 'Email':
                    icon = "📧"
                elif activity['type'] == 'Call':
                    icon = "📞"
                elif activity['type'] == 'Meeting':
                    icon = "🤝"
                else:
                    icon = "🔔"
                
                st.markdown(f"<div style='font-size:24px; text-align:center;'>{icon}</div>", unsafe_allow_html=True)
            
            with col2:
                activity_date = activity.get('date', 'Unknown date')
                check_customer_id_exist(activity['customer_id'])
                st.markdown(f"""
                <div style='border-left:1px solid #eee; padding-left:15px;'>
                    <div style='font-weight:500;'>{activity['type']} with Customer #{activity['customer_id']}</div>
                    <div style='color:#666; font-size:0.9em;'>{activity.get('notes', 'No notes')[:50]}...</div>
                    <div style='color:#999; font-size:0.8em;'>{activity_date}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
    else:
        st.info("No recent activities available")
    
    # Auto refresh option
    st.sidebar.markdown("---")
    auto_refresh = st.sidebar.checkbox("Auto refresh dashboard", value=False)
    
    if auto_refresh:
        time.sleep(10)
        st.rerun()