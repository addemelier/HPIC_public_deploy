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
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Total Membership Growth', 'Membership by Source'),
        vertical_spacing=0.12,
        row_heights=[0.7, 0.3]
    )
    
    # Main timeline
    fig.add_trace(
        go.Scatter(
            x=filtered_df['month_start'],
            y=filtered_df['active_members'],
            mode='lines+markers',
            name='Total Members',
            line=dict(color='#2E86AB', width=3),
            hovertemplate='<b>%{x|%B %Y}</b><br>Total Members: %{y}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=filtered_df['month_start'],
            y=filtered_df['classic_members'],
            mode='lines+markers',
            name='Classic',
            line=dict(color='#A23B72', width=2),
            hovertemplate='<b>%{x|%B %Y}</b><br>Classic: %{y}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=filtered_df['month_start'],
            y=filtered_df['champion_members'],
            mode='lines+markers',
            name='Champion',
            line=dict(color='#F18F01', width=2),
            hovertemplate='<b>%{x|%B %Y}</b><br>Champion: %{y}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Data source breakdown
    fig.add_trace(
        go.Scatter(
            x=filtered_df['month_start'],
            y=filtered_df['hpic_members'],
            mode='lines+markers',
            name='HPIC System',
            line=dict(color='#2E86AB', width=2),
            hovertemplate='<b>%{x|%B %Y}</b><br>HPIC: %{y}<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=filtered_df['month_start'],
            y=filtered_df['pmp_members'],
            mode='lines+markers',
            name='PMP Legacy',
            line=dict(color='#A23B72', width=2),
            hovertemplate='<b>%{x|%B %Y}</b><br>PMP: %{y}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Add milestone markers
    covid_date = pd.to_datetime('2020-03-01')
    hpic_launch = pd.to_datetime('2024-04-01')
    
    min_date = filtered_df['month_start'].min()
    max_date = filtered_df['month_start'].max()
    
    if covid_date >= min_date and covid_date <= max_date:
        fig.add_vline(x=covid_date, line_dash="dash", line_color="red", 
                     annotation_text="COVID Impact", annotation_position="top left")
    
    if hpic_launch >= min_date and hpic_launch <= max_date:
        fig.add_vline(x=hpic_launch, line_dash="dash", line_color="green",
                     annotation_text="HPIC Launch", annotation_position="top right")
    
    fig.update_layout(
        height=600,
        showlegend=True,
        hovermode='x unified'
    )
    
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Members", row=1, col=1)
    fig.update_yaxes(title_text="Members", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Additional insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Growth Insights")
        
        # Calculate growth metrics
        total_growth = current_data['active_members'] - filtered_df.iloc[0]['active_members']
        months_span = len(filtered_df)
        avg_monthly_growth = total_growth / months_span if months_span > 0 else 0
        
        peak_membership = filtered_df['active_members'].max()
        peak_date = filtered_df.loc[filtered_df['active_members'].idxmax(), 'month_start']
        
        st.write(f"**Total Growth:** +{total_growth} members")
        st.write(f"**Average Monthly Growth:** {avg_monthly_growth:.1f} members/month")
        st.write(f"**Peak Membership:** {peak_membership} members ({peak_date.strftime('%B %Y')})")
        
        # Recent trend
        recent_months = filtered_df.tail(6)
        recent_growth = recent_months.iloc[-1]['active_members'] - recent_months.iloc[0]['active_members']
        st.write(f"**6-Month Growth:** +{recent_growth} members")
    
    with col2:
        st.subheader("📊 Current Breakdown")
        
        # Pie chart of current membership
        tier_data = pd.DataFrame({
            'Tier': ['Classic', 'Champion'],
            'Members': [current_data['classic_members'], current_data['champion_members']]
        })
        
        breakdown_fig = px.pie(
            tier_data,
            values='Members',
            names='Tier',
            title="Membership Tiers",
            color_discrete_map={'Classic': '#A23B72', 'Champion': '#F18F01'}
        )
        breakdown_fig.update_layout(height=300)
        st.plotly_chart(breakdown_fig, use_container_width=True)
        
        # Data source breakdown
        current_hpic = current_data['hpic_members']
        current_pmp = current_data['pmp_members']
        
        st.write("**Data Sources:**")
        st.write(f"• HPIC System: {current_hpic} members")
        st.write(f"• PMP Legacy: {current_pmp} members")
    
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