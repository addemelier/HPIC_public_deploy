#!/usr/bin/env python3
"""
HPIC Membership Dashboard - Public Version
Reads from CSV files for Streamlit Community Cloud deployment

Run: streamlit run hpic_dashboard_public.py
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="HPIC Membership Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data from CSV
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_membership_data():
    try:
        # Try to load from public_data directory first (local development)
        if os.path.exists('public_data/membership_timeline.csv'):
            timeline_df = pd.read_csv('public_data/membership_timeline.csv')
        # Fallback to same directory (Streamlit Cloud deployment)
        elif os.path.exists('membership_timeline.csv'):
            timeline_df = pd.read_csv('membership_timeline.csv')
        else:
            st.error("❌ Membership data file not found")
            st.stop()
        
        # Convert dates
        timeline_df['month_start'] = pd.to_datetime(timeline_df['month_start'])
        
        return timeline_df
        
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.stop()

# Main dashboard
def main():
    # Header
    st.title("🏠 HPIC Membership Dashboard")
    st.markdown("*Highland Park Improvement Club - Membership Analytics*")
    st.info("📊 This dashboard shows aggregated membership data only - no individual member information is displayed or stored.")
    
    # Load data
    timeline_df = load_membership_data()
    
    # Sidebar filters
    st.sidebar.header("📅 Filters")
    
    # Date range selector
    min_date = timeline_df['month_start'].min().date()
    max_date = timeline_df['month_start'].max().date()
    
    start_date = st.sidebar.date_input(
        "Start Date",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )
    
    end_date = st.sidebar.date_input(
        "End Date", 
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )
    
    # Filter data
    mask = (timeline_df['month_start'].dt.date >= start_date) & (timeline_df['month_start'].dt.date <= end_date)
    filtered_df = timeline_df[mask]
    
    if filtered_df.empty:
        st.warning("No data available for selected date range")
        return
    
    # Key Metrics Row
    current_data = filtered_df.iloc[-1]
    previous_data = filtered_df.iloc[-2] if len(filtered_df) > 1 else current_data
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_change = current_data['active_members'] - previous_data['active_members']
        st.metric(
            "Total Members",
            f"{current_data['active_members']:,}",
            delta=f"{total_change:+d}" if total_change != 0 else None
        )
    
    with col2:
        classic_pct = (current_data['classic_members'] / current_data['active_members']) * 100
        st.metric(
            "Classic Members",
            f"{current_data['classic_members']:,}",
            delta=f"{classic_pct:.1f}% of total"
        )
    
    with col3:
        champion_pct = (current_data['champion_members'] / current_data['active_members']) * 100
        st.metric(
            "Champion Members", 
            f"{current_data['champion_members']:,}",
            delta=f"{champion_pct:.1f}% of total"
        )
    
    with col4:
        hpic_pct = (current_data['hpic_members'] / current_data['active_members']) * 100
        st.metric(
            "HPIC System",
            f"{current_data['hpic_members']:,}",
            delta=f"{hpic_pct:.1f}% of total"
        )
    
    # Main Charts
    st.markdown("---")
    
    # Timeline Chart
    st.subheader("📈 Membership Timeline")
    
    # Create interactive timeline
    fig = go.Figure()
    
    # Main timeline
    fig.add_trace(
        go.Scatter(
            x=filtered_df['month_start'],
            y=filtered_df['active_members'],
            mode='lines+markers',
            name='Total Members',
            line=dict(color='#2E86AB', width=3),
            hovertemplate='<b>%{x|%B %Y}</b><br>Total Members: %{y}<extra></extra>'
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=filtered_df['month_start'],
            y=filtered_df['classic_members'],
            mode='lines+markers',
            name='Classic',
            line=dict(color='#A23B72', width=2),
            hovertemplate='<b>%{x|%B %Y}</b><br>Classic: %{y}<extra></extra>'
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=filtered_df['month_start'],
            y=filtered_df['champion_members'],
            mode='lines+markers',
            name='Champion',
            line=dict(color='#F18F01', width=2),
            hovertemplate='<b>%{x|%B %Y}</b><br>Champion: %{y}<extra></extra>'
        )
    )
    
    # Milestone markers temporarily removed due to Plotly timestamp issues
    
    fig.update_layout(
        height=400,
        showlegend=True,
        hovermode='x unified',
        title="Membership Growth Over Time"
    )
    
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Members")
    
    st.plotly_chart(fig, use_container_width=True)
    
    
    # About section
    with st.expander("ℹ️ About This Dashboard"):
        st.markdown("""
        **Highland Park Improvement Club (HPIC)** is a 100+ year old neighborhood nonprofit serving 
        the Highland Park and Riverview communities in Pittsburgh, PA.
        
        **Data Privacy:**
        - This dashboard displays only aggregated monthly totals
        - No individual member information is shown or stored
        - All data is anonymized for public transparency
        
        **Data Sources:**
        - Little Green Light CRM (current membership system)
        - PMP Legacy System (historical data from previous platform)
        
        **Membership Tiers:**
        - **Classic**: Standard membership ($20 individual, $40 family)
        - **Champion**: Premium supporter level ($100 individual, $200 family)
        """)
    
    # Footer
    st.markdown("---")
    st.caption(f"📅 Data through {max_date} | Last updated: {datetime.now().strftime('%Y-%m-%d')}")
    st.caption("🏠 Highland Park Improvement Club | Built with Streamlit")

if __name__ == "__main__":
    main()