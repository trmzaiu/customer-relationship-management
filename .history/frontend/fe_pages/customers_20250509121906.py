import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import requests
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# API endpoints
CUSTOMER_API_URL = "http://localhost:5000/api/customers"
INTERACT_API_URL = "http://localhost:5000/api/interactions"

# Cache the API data to reduce redundant calls
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_customer_data():
    """Fetch customer data from the backend API."""
    try:
        response = requests.get(CUSTOMER_API_URL, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching customer data: {e}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_interaction_data():
    """Fetch interaction data from the backend API."""
    try:
        response = requests.get(INTERACT_API_URL, timeout=10)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching interaction data: {e}")
        return None

def process_interaction_data(df):
    """Process and clean interaction data."""
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Convert date strings to datetime
    df['date'] = pd.to_datetime(df['date'], format='%a, %d %b %Y %H:%M:%S GMT', errors='coerce')
    df = df.dropna(subset=['date'])
    
    # Extract date components
    df['date_only'] = df['date'].dt.date
    df['hour'] = df['date'].dt.hour
    df['day_of_week'] = df['date'].dt.day_name()
    
    return df

def create_customer_distribution_charts(df):
    """Create customer distribution visualizations."""
    if df is None or df.empty:
        return None, None
    
    customer_summary = df['type'].value_counts().reset_index()
    customer_summary.columns = ['Customer Type', 'Count']
    
    # Create pie chart
    pie_fig = px.pie(
        customer_summary, 
        names='Customer Type', 
        values='Count',
        title='Customer Distribution',
        hole=0.4,
        color='Customer Type',
        color_discrete_map={
            'VIP': '#FF6B6B',
            'Regular': '#4ECDC4',
            'New': '#FFD166'
        }
    )
    pie_fig.update_traces(textposition='inside', textinfo='percent+label')
    
    # Create bar chart
    bar_fig = px.bar(
        customer_summary, 
        x='Customer Type', 
        y='Count',
        title='Customer Count by Type',
        color='Customer Type',
        color_discrete_map={
            'VIP': '#FF6B6B',
            'Regular': '#4ECDC4',
            'New': '#FFD166'
        }
    )
    bar_fig.update_layout(xaxis_title="Customer Type", yaxis_title="Count")
    
    return pie_fig, bar_fig

def create_interaction_trends(df):
    """Create interaction trend visualizations."""
    if df is None or df.empty:
        return None, None
    
    # Weekly trend
    weekly_trend = df.groupby('date_only').size().reset_index(name='Interactions')
    weekly_trend.columns = ['Date', 'Interactions']
    
    # Calculate rolling average (7-day)
    weekly_trend['Rolling_Avg'] = weekly_trend['Interactions'].rolling(window=7, min_periods=1).mean()
    
    # Create line chart
    line_fig = px.line(
        weekly_trend, 
        x='Date', 
        y=['Interactions', 'Rolling_Avg'],
        markers=True,
        title='Daily Interactions with 7-Day Rolling Average',
        labels={'value': 'Count', 'variable': 'Metric'}
    )
    
    line_fig.update_layout(legend_title_text='')
    
    # Create hourly distribution
    hourly_dist = df.groupby('hour').size().reset_index(name='Interactions')
    hour_fig = px.bar(
        hourly_dist,
        x='hour',
        y='Interactions',
        title='Interactions by Hour of Day',
        labels={'hour': 'Hour of Day', 'Interactions': 'Number of Interactions'},
        color_discrete_sequence=['#4ECDC4']
    )
    
    return line_fig, hour_fig

def create_day_of_week_chart(df):
    """Create day of week distribution chart."""
    if df is None or df.empty:
        return None
    
    # Order days of week correctly
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = df['day_of_week'].value_counts().reindex(days_order).reset_index()
    day_counts.columns = ['Day', 'Interactions']
    
    fig = px.bar(
        day_counts,
        x='Day',
        y='Interactions',
        title='Interactions by Day of Week',
        color_discrete_sequence=['#FFD166']
    )
    
    return fig

def display_kpi_metrics(customers_df):
    """Display KPI metrics."""
    if customers_df is None or customers_df.empty:
        st.error("No customer data available to display KPIs.")
        return
    
    total_customers = customers_df.shape[0]
    vip_customers = customers_df[customers_df['type'] == 'VIP'].shape[0]
    regular_customers = customers_df[customers_df['type'] == 'Regular'].shape[0]
    new_customers = customers_df[customers_df['type'] == 'New'].shape[0]
    
    # Calculate percentages for delta values
    vip_pct = round((vip_customers / total_customers) * 100, 1) if total_customers > 0 else 0
    regular_pct = round((regular_customers / total_customers) * 100, 1) if total_customers > 0 else 0
    new_pct = round((new_customers / total_customers) * 100, 1) if total_customers > 0 else 0
    
    # Display metrics with percentages
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", f"{total_customers:,}")
    col2.metric("VIP Customers", f"{vip_customers:,}", f"{vip_pct}% of total")
    col3.metric("Regular Customers", f"{regular_customers:,}", f"{regular_pct}% of total")
    col4.metric("New Customers", f"{new_customers:,}", f"{new_pct}% of total")

def dashboard_page(auto_refresh=False, refresh_interval=60):
    """Main dashboard function."""
    
    st.set_page_config(
        page_title="Customer Dashboard",
        page_icon="🏠",
        layout="wide",
    )
    
    while True:
        # Add title with current timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.title("🏠 Customer Dashboard")
        st.caption(f"Last updated: {current_time}")
        
        # Add refresh button
        if not auto_refresh:
            if st.button("🔄 Refresh Data"):
                st.cache_data.clear()
                st.success("Data refreshed!")
                
        # Fetch data
        with st.spinner("Loading customer data..."):
            customers_df = fetch_customer_data()
        
        with st.spinner("Loading interaction data..."):
            raw_interact_df = fetch_interaction_data()
            interact_df = process_interaction_data(raw_interact_df)
        
        # Check if data is available
        if customers_df is None or customers_df.empty:
            st.error("❌ Failed to load customer data. Please check the API connection.")
            if auto_refresh:
                time.sleep(refresh_interval)
                st.rerun()
            return
            
        if interact_df is None or interact_df.empty:
            st.warning("⚠️ No interaction data available.")
        
        # Display KPI metrics
        st.subheader("📊 Key Performance Indicators")
        display_kpi_metrics(customers_df)
        
        st.divider()
        
        # Customer Distribution section
        st.header("🧠 Customer Distribution")
        
        pie_fig, bar_fig = create_customer_distribution_charts(customers_df)
        if pie_fig and bar_fig:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(pie_fig, use_container_width=True)
            with col2:
                st.plotly_chart(bar_fig, use_container_width=True)
        else:
            st.error("Failed to create customer distribution charts.")
        
        st.divider()
        
        # Interaction Trends section
        if not interact_df.empty:
            st.header("📈 Interaction Analysis")
            
            trend_fig, hour_fig = create_interaction_trends(interact_df)
            if trend_fig:
                st.plotly_chart(trend_fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if hour_fig:
                    st.plotly_chart(hour_fig, use_container_width=True)
            
            with col2:
                day_fig = create_day_of_week_chart(interact_df)
                if day_fig:
                    st.plotly_chart(day_fig, use_container_width=True)
            
            # Show recent interactions in expandable section
            with st.expander("View Recent Interactions"):
                if not interact_df.empty:
                    recent = interact_df.sort_values('date', ascending=False).head(10)
                    st.dataframe(
                        recent[['customer_id', 'channel', 'type', 'date']].rename(
                            columns={
                                'customer_id': 'Customer ID',
                                'channel': 'Channel',
                                'type': 'Type',
                                'date': 'Date'
                            }
                        ),
                        use_container_width=True
                    )
                else:
                    st.info("No interaction data available.")
        
        # Auto-refresh logic
        if auto_refresh:
            st.info(f"Dashboard will refresh in {refresh_interval} seconds.")
            time.sleep(refresh_interval)
            st.rerun()
        else:
            break

if __name__ == "__main__":
    # Create sidebar for settings
    st.sidebar.title("Dashboard Settings")
    
    auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=False)
    refresh_interval = 60
    
    if auto_refresh:
        refresh_interval = st.sidebar.slider(
            "Refresh Interval (seconds)", 
            min_value=10, 
            max_value=300, 
            value=60,
            step=10
        )
    
    # Start the dashboard
    dashboard_page(auto_refresh, refresh_interval)