import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))

from widget import CUSTOMER_API_URL, INTERACT_API_URL

def report_page():
    st.title("📊 Analytics & Reports")
    st.markdown("<p style='color: #666; margin-bottom: 20px;'>View detailed customer analytics and business intelligence</p>", unsafe_allow_html=True)
    
    # Get customer data
    try:
        cust_response = requests.get(CUSTOMER_API_URL)
        if cust_response.status_code == 200:
            customers_df = pd.DataFrame(cust_response.json())
        else:
            st.error(f"Failed to load customer data. Status code: {cust_response.status_code}")
            return
    except Exception as e:
        st.error(f"Error loading customer data: {e}")
        return
    
    # Get interaction data
    try:
        interact_response = requests.get(INTERACT_API_URL)
        if interact_response.status_code == 200:
            interactions_df = pd.DataFrame(interact_response.json())
        else:
            st.error(f"Failed to load interaction data. Status code: {interact_response.status_code}")
            return
    except Exception as e:
        st.error(f"Error loading interaction data: {e}")
        return
    
    # Report selection tabs
    tab1, tab2, tab3 = st.tabs(["📈 Overview", "👥 Customer Analysis", "📞 Interaction Analysis"])
    
    with tab1:
        st.subheader("Business Overview")
        
        # Key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_customers = customers_df.shape[0]
            st.metric("Total Customers", total_customers)
        
        with col2:
            if 'date' in interactions_df.columns or 'timestamp' in interactions_df.columns:
                date_col = 'date' if 'date' in interactions_df.columns else 'timestamp'
                interactions_df[date_col] = pd.to_datetime(interactions_df[date_col], errors='coerce')
                
                # Get interactions in last 30 days
                now = datetime.now()
                thirty_days_ago = now - pd.Timedelta(days=30)
                recent_interactions = interactions_df[interactions_df[date_col] >= thirty_days_ago].shape[0]
                
                st.metric("Monthly Interactions", recent_interactions)
            else:
                st.metric("Total Interactions", interactions_df.shape[0])
        
        with col3:
            vip_percentage = customers_df[customers_df['type'] == 'VIP'].shape[0] / max(total_customers, 1) * 100
            st.metric("VIP Customer %", f"{vip_percentage:.1f}%")
        
        # Customer distribution chart
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h4>Customer Segmentation</h4>", unsafe_allow_html=True)
        
        customer_summary = customers_df['type'].value_counts().reset_index()
        customer_summary.columns = ['Customer Type', 'Count']
        
        colors = {'VIP': '#ffd700', 'Regular': '#007bff', 'New': '#28a745'}
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pie = px.pie(
                customer_summary, 
                names='Customer Type', 
                values='Count',
                color='Customer Type',
                color_discrete_map=colors,
                hole=0.4,
            )
            fig_pie.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=300, text =)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            fig_bar = px.bar(
                customer_summary, 
                x='Customer Type', 
                y='Count', 
                color='Customer Type',
                color_discrete_map=colors,
                text='Count',
                height=300
            )

            fig_bar.update_layout(
                margin=dict(l=50, r=50, t=50, b=0),
                yaxis=dict(
                    automargin=True,
                    range=[0, max(customer_summary['Count']) * 1] 
                ),
                showlegend=False,
                uniformtext_minsize=8,  
                uniformtext_mode='hide'
            )

            fig_bar.update_traces(
                textposition='outside',
                textfont_size=14, 
                cliponaxis=False  
            )

            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Interaction trends
        if 'date' in interactions_df.columns or 'timestamp' in interactions_df.columns:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("<h4>Interaction Trends</h4>", unsafe_allow_html=True)
            
            date_col = 'date' if 'date' in interactions_df.columns else 'timestamp'
            interactions_df[date_col] = pd.to_datetime(interactions_df[date_col], errors='coerce')
            interactions_df['date_only'] = interactions_df[date_col].dt.date
            
            # Group by date and interaction type
            if 'type' in interactions_df.columns:
                interaction_counts = interactions_df.groupby(['date_only', 'type']).size().reset_index(name='count')
                
                fig = px.line(
                    interaction_counts, 
                    x='date_only', 
                    y='count', 
                    color='type',
                    markers=True,
                    line_shape='spline'
                )
                fig.update_layout(
                    margin=dict(l=20, r=20, t=0, b=20),
                    height=350,
                    xaxis_title="Date",
                    yaxis_title="Number of Interactions",
                    legend_title="Interaction Type",
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Just group by date if type not available
                interaction_counts = interactions_df.groupby('date_only').size().reset_index(name='count')
                
                fig = px.line(
                    interaction_counts, 
                    x='date_only', 
                    y='count',
                    markers=True,
                    line_shape='spline'
                )
                fig.update_layout(
                    margin=dict(l=20, r=20, t=0, b=20),
                    height=350,
                    xaxis_title="Date",
                    yaxis_title="Number of Interactions",
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Customer Analysis")
        
        # Customer type distribution over time (if datetime available)
        if 'datetime' in customers_df.columns:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("<h4>Customer Growth</h4>", unsafe_allow_html=True)
            
            # customers_df['date'] = pd.to_datetime(customers_df['datetime']).dt.date
            try:
                customers_df['date'] = pd.to_datetime(customers_df['datetime'], format='ISO8601', errors='coerce')
                if customers_df['date'].isna().any():
                    customers_df['date'] = pd.to_datetime(customers_df['datetime'], format='mixed', errors='coerce')
                customers_df['month'] = customers_df['date'].dt.month
                customers_df['date'] = customers_df['date'].dt.date
            except Exception as e:
                st.warning(f"Could not format datetime column: {str(e)}")
                customers_df['date'] = customers_df['datetime'].date
            # customers_df['month'] = pd.to_datetime(customers_df['datetime']).dt.to_period('M')
            
            # Group by month and customer type
            monthly_growth = customers_df.groupby(['month', 'type']).size().reset_index(name='count')
            monthly_growth['month'] = monthly_growth['month'].astype(str)
            
            fig = px.bar(
                monthly_growth,
                x='month',
                y='count',
                color='type',
                barmode='group',
                text='count'
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=0, b=20),
                height=350,
                xaxis_title="Month",
                yaxis_title="Number of Customers",
                legend_title="Customer Type"
            )
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Customer engagement analysis
        if not interactions_df.empty and 'customer_id' in interactions_df.columns:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("<h4>Customer Engagement Analysis</h4>", unsafe_allow_html=True)
            
            # Count interactions per customer
            customer_engagement = interactions_df['customer_id'].value_counts().reset_index()
            customer_engagement.columns = ['customer_id', 'interactions']
            
            # Merge with customer data to get customer types
            if not customers_df.empty:
                customer_engagement = customer_engagement.merge(
                    customers_df[['customer_id', 'type']], 
                    on='customer_id', 
                    how='left'
                )
                
                # Group by customer type
                engagement_by_type = customer_engagement.groupby('type')['interactions'].mean().reset_index()
                
                fig = px.bar(
                    engagement_by_type,
                    x='type',
                    y='interactions',
                    color='type',
                    title="Average Interactions per Customer Type",
                    text='interactions'
                )
                fig.update_layout(
                    margin=dict(l=20, r=20, t=30, b=20),
                    height=350,
                    xaxis_title="Customer Type",
                    yaxis_title="Average Interactions"
                )
                fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Most engaged customers
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("<h4>Most Engaged Customers</h4>", unsafe_allow_html=True)
            
            top_customers = customer_engagement.sort_values('interactions', ascending=False).head(10)
            
            # Try to get customer names
            if 'name' in customers_df.columns:
                top_customers = top_customers.merge(
                    customers_df[['customer_id', 'name']], 
                    on='customer_id', 
                    how='left'
                )
                x_col = 'name'
            else:
                x_col = 'customer_id'
            
            fig = px.bar(
                top_customers,
                x=x_col,
                y='interactions',
                color='type' if 'type' in top_customers.columns else None,
                text='interactions'
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=0, b=0),
                height=400,
                xaxis_title="Customer",
                yaxis_title="Number of Interactions",
                xaxis={'categoryorder':'total descending'}
            )
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.subheader("Interaction Analysis")
        
        if not interactions_df.empty:
            # Interaction type distribution
            if 'type' in interactions_df.columns:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.markdown("<h4>Interaction Type Distribution</h4>", unsafe_allow_html=True)
                
                interaction_types = interactions_df['type'].value_counts().reset_index()
                interaction_types.columns = ['Interaction Type', 'Count']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_pie = px.pie(
                        interaction_types, 
                        names='Interaction Type', 
                        values='Count',
                        hole=0.4
                    )
                    fig_pie.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300)
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    fig_bar = px.bar(
                        interaction_types, 
                        x='Interaction Type', 
                        y='Count',
                        color='Interaction Type',
                        text='Count'
                    )
                    fig_bar.update_layout(
                        margin=dict(l=0, r=0, t=0, b=0),
                        height=300,
                        xaxis_title="",
                        yaxis_title="Number of Interactions",
                        showlegend=False
                    )
                    fig_bar.update_traces(textposition='outside')
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Interaction trends over time
            if 'date' in interactions_df.columns or 'timestamp' in interactions_df.columns:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.markdown("<h4>Interaction Volume Over Time</h4>", unsafe_allow_html=True)
                
                date_col = 'date' if 'date' in interactions_df.columns else 'timestamp'
                interactions_df[date_col] = pd.to_datetime(interactions_df[date_col], errors='coerce')
                
                # Group by day of week
                interactions_df['day_of_week'] = interactions_df[date_col].dt.day_name()
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                day_counts = interactions_df['day_of_week'].value_counts().reindex(day_order).reset_index()
                day_counts.columns = ['Day of Week', 'Count']
                
                fig = px.bar(
                    day_counts,
                    x='Day of Week',
                    y='Count',
                    color='Day of Week',
                    text='Count'
                )
                fig.update_layout(
                    margin=dict(l=20, r=20, t=0, b=20),
                    height=350,
                    xaxis_title="",
                    yaxis_title="Number of Interactions",
                    showlegend=False
                )
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
                
                # Group by hour of day if time information available
                if interactions_df[date_col].dt.hour.nunique() > 1:
                    interactions_df['hour_of_day'] = interactions_df[date_col].dt.hour
                    hour_counts = interactions_df['hour_of_day'].value_counts().sort_index().reset_index()
                    hour_counts.columns = ['Hour of Day', 'Count']
                    
                    fig = px.line(
                        hour_counts,
                        x='Hour of Day',
                        y='Count',
                        markers=True
                    )
                    fig.update_layout(
                        margin=dict(l=20, r=20, t=30, b=20),
                        height=350,
                        xaxis_title="Hour (24-hour format)",
                        yaxis_title="Number of Interactions",
                        title="Interaction Distribution by Hour"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("</div>", unsafe_allow_html=True)