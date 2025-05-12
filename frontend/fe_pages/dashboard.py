import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'service')))

from api import get_metrics_from_api, get_customer_name, get_interaction

def dashboard_page():
    st.title("🏠 Dashboard Overview")
    st.markdown("<p style='color: #666;'>Welcome to your customer management dashboard</p>", unsafe_allow_html=True)

    metrics = get_metrics_from_api()
    interactions = get_interaction()

    if not metrics:
        return  # Dừng nếu không có dữ liệu

    st.markdown("### 📌 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Customers", metrics["customer_count"])
    with col2:
        st.metric("VIP", metrics["customer_by_type"].get("VIP", 0))
    with col3:
        st.metric("Regular", metrics["customer_by_type"].get("Regular", 0))
    with col4:
        st.metric("New", metrics["customer_by_type"].get("New", 0))

    st.markdown("---")

    # ==== Pie chart: Customer by type ====
    st.subheader("📊 Customer Type Distribution")
    customer_type_data = pd.DataFrame({
        "Type": list(metrics["customer_by_type"].keys()),
        "Count": list(metrics["customer_by_type"].values())
    })

    fig_pie = px.pie(
        customer_type_data,
        names="Type",
        values="Count",
        hole=0.4,
        color="Type",
        color_discrete_map={"VIP": "#ffd700", "Regular": "#007bff", "New": "#28a745"}
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_pie, use_container_width=True)

    # ==== Line chart: Customer growth ====
    st.subheader("📈 Customer Growth")
    if "customer_growth" in metrics:
        growth_df = pd.DataFrame(metrics["customer_growth"])
        growth_df["date"] = pd.to_datetime(growth_df["date"]).dt.date  

        fig_growth = px.line(growth_df, x="date", y="count", markers=True)
        fig_growth.update_layout(height=300, xaxis_title="Date", yaxis_title="New Customers")
        st.plotly_chart(fig_growth, use_container_width=True)
    else:
        st.info("Customer growth data not available.")

    # # ==== Line chart: Interaction trends ====
    # st.subheader("📞 Interaction Trends")
    # if "interaction_trend" in metrics:
    #     trend_df = pd.DataFrame(metrics["interaction_trend"])
    #     st.info(trend_df)
    #     trend_df["date"] = pd.to_datetime(trend_df["date"]).dt.date
    #     st.info(trend_df["date"])

    #     fig_line = px.line(trend_df, x="date", y="count", markers=True, line_shape="spline")
    #     fig_line.update_layout(height=300, xaxis_title="Date", yaxis_title="Interactions")
    #     fig_line.update_traces(line=dict(width=3, color="#0f52ba"))
    #     st.plotly_chart(fig_line, use_container_width=True)
    # else:
    #     st.info("Interaction trend data not available.")

    # ==== Bar chart: Interaction by type ====
    st.subheader("📑 Interaction by Type")
    if "interaction_by_type" in metrics:
        interaction_type_df = pd.DataFrame({
            "Type": list(metrics["interaction_by_type"].keys()),
            "Count": list(metrics["interaction_by_type"].values())
        })
        fig_bar = px.bar(interaction_type_df, x="Type", y="Count", color="Type", text="Count")
        fig_bar.update_layout(height=300)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No interaction type data available.")
    
    recent_activities = interactions[:5]

    st.markdown("---")
    st.subheader("📝 Recent Activities")

    for activity in recent_activities:
        col1, col2 = st.columns([1, 25])
        
        with col1:
            icon = {
                "Email": "📧",
                "Call": "📞",
                "Meeting": "🤝"
            }.get(activity.get('type'), "🔔")
            
            st.markdown(f"<div style='font-size:24px; text-align:center;'>{icon}</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='border-left:1px solid #eee; padding-left:15px;'>
                <div style='font-weight:500;'>{activity.get('type', 'Unknown')} with {activity.get('customer', 'Unknown')}</div>
                <div style='color:#666; font-size:0.9em;'>{activity.get('notes', 'No notes')}</div>
                <div style='color:#999; font-size:0.8em;'>{activity.get('date', 'Unknown date')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
    
