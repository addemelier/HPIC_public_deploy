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

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_revenue_data():
    try:
        # Try to load from public_data directory first (local development)
        if os.path.exists('public_data/revenue_analysis.csv'):
            revenue_df = pd.read_csv('public_data/revenue_analysis.csv')
        # Fallback to same directory (Streamlit Cloud deployment)
        elif os.path.exists('revenue_analysis.csv'):
            revenue_df = pd.read_csv('revenue_analysis.csv')
        else:
            st.error("❌ Revenue data file not found")
            st.stop()
        
        return revenue_df
        
    except Exception as e:
        st.error(f"❌ Error loading revenue data: {e}")
        st.stop()

# Main dashboard
def main():
    # Header
    st.title("🏠 HPIC Membership Dashboard")
    st.markdown("*Highland Park Improvement Club - Membership Analytics*")
    st.info("📊 This dashboard shows aggregated membership data only - no individual member information is displayed or stored.")
    
    # Load data
    timeline_df = load_membership_data()
    revenue_df = load_revenue_data()
    
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
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
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
    
    # Revenue Analysis Section
    st.markdown("---")
    st.subheader("💰 Revenue Analysis")
    
    # Revenue Overview Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = revenue_df['total_revenue'].sum()
        st.metric(
            "Total Revenue",
            f"${total_revenue:,.0f}",
            delta=f"${revenue_df['revenue_2025'].sum():,.0f} in 2025"
        )
    
    with col2:
        grant_revenue = revenue_df[revenue_df['category'] == 'grant']['total_revenue'].sum()
        grant_pct = (grant_revenue / total_revenue) * 100
        st.metric(
            "Grant Revenue",
            f"${grant_revenue:,.0f}",
            delta=f"{grant_pct:.1f}% of total"
        )
    
    with col3:
        total_transactions = revenue_df['transaction_count'].sum()
        unique_contributors = revenue_df['unique_contributors'].sum()
        st.metric(
            "Total Transactions",
            f"{total_transactions:,}",
            delta=f"{unique_contributors:,} unique contributors"
        )
    
    with col4:
        avg_transaction = revenue_df['total_revenue'].sum() / revenue_df['transaction_count'].sum()
        st.metric(
            "Avg Transaction",
            f"${avg_transaction:.2f}",
            delta=None
        )
    
    # Add separator line
    st.markdown("---")
    
    # Revenue Distribution Chart
    st.subheader("📊 Non-Grant Revenue Distribution")
    
    # Filter out grants for pie chart
    non_grant_df = revenue_df[revenue_df['category'] != 'grant']
    
    # Revenue pie chart (excluding grants)
    fig_pie = px.pie(
        non_grant_df, 
        values='total_revenue', 
        names='category',
        title="Revenue Distribution (Excluding Grants)",
        color_discrete_map={
            'membership': '#4ECDC4', 
            'donation': '#45B7D1',
            'other': '#96CEB4',
            'building_booster': '#FFEAA7'
        }
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)
    
    
    # Detailed Revenue Table
    st.subheader("📋 Detailed Revenue Breakdown")
    
    # Format revenue data for display
    display_df = revenue_df.copy()
    display_df['Total Revenue'] = display_df['total_revenue'].apply(lambda x: f"${x:,.2f}")
    display_df['% of Total'] = display_df['percentage_of_total'].apply(lambda x: f"{x:.1f}%")
    display_df['2025 Revenue'] = display_df['revenue_2025'].apply(lambda x: f"${x:,.2f}")
    display_df['Avg Transaction'] = display_df['avg_transaction_amount'].apply(lambda x: f"${x:.2f}")
    
    columns_to_show = ['category', 'transaction_count', 'unique_contributors', 'Total Revenue', '% of Total', '2025 Revenue', 'Avg Transaction']
    display_df = display_df[columns_to_show]
    display_df.columns = ['Category', 'Transactions', 'Contributors', 'Total Revenue', '% of Total', '2025 Revenue', 'Avg Transaction']
    
    st.dataframe(display_df, use_container_width=True)
    
    # Key Insights
    st.subheader("🔍 Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Grant Detection:**")
        st.info("WA Dept of Commerce grant automatically categorized as 'grant' revenue")
        
        st.markdown("**💵 Membership Calculation:**")
        membership_revenue = revenue_df[revenue_df['category'] == 'membership']['total_revenue'].sum()
        membership_transactions = revenue_df[revenue_df['category'] == 'membership']['transaction_count'].sum()
        st.info(f"${membership_revenue:,.0f} from {membership_transactions:,} membership transactions")
        
        st.markdown("**🏗️ Building Booster Tracking:**")
        booster_revenue = revenue_df[revenue_df['category'] == 'building_booster']['total_revenue'].sum()
        booster_contributors = revenue_df[revenue_df['category'] == 'building_booster']['unique_contributors'].sum()
        st.info(f"${booster_revenue:,.0f} from {booster_contributors:,} recurring facility donors")
    
    with col2:
        st.markdown("**📊 Comprehensive Stats:**")
        total_stats = f"""
        - Total transactions: {revenue_df['transaction_count'].sum():,}
        - Unique contributors: {revenue_df['unique_contributors'].sum():,}
        - Categories tracked: {len(revenue_df):,}
        - Grant percentage: {(grant_revenue/total_revenue)*100:.1f}%
        """
        st.info(total_stats)
        
        st.markdown("**🗓️ 2025 Revenue Summary:**")
        revenue_2025_summary = f"""
        - Total 2025: ${revenue_df['revenue_2025'].sum():,.0f}
        - Grant portion: ${revenue_df[revenue_df['category'] == 'grant']['revenue_2025'].sum():,.0f}
        - Non-grant portion: ${revenue_df[revenue_df['category'] != 'grant']['revenue_2025'].sum():,.0f}
        """
        st.info(revenue_2025_summary)
    
    
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