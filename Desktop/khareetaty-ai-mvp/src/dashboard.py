"""
Dashboard module for Khareetaty AI MVP Crime Analytics System
Streamlit dashboard with maps and visualizations
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import calendar
import pytz

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import Config, KUWAIT_GOVERNORATES
from src.database import db_manager
from src.analytics import AnalyticsEngine
from src.predictive_model import PredictiveModel

# Set page configuration
st.set_page_config(
    page_title="Khareetaty AI - Crime Analytics Dashboard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

class DashboardApp:
    def __init__(self):
        self.analytics_engine = AnalyticsEngine()
        self.predictive_model = PredictiveModel()
        self.setup_session_state()
        
    def setup_session_state(self):
        """Initialize session state variables"""
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
        if 'incidents_df' not in st.session_state:
            st.session_state.incidents_df = pd.DataFrame()
        if 'hotspots_df' not in st.session_state:
            st.session_state.hotspots_df = pd.DataFrame()
        if 'analytics_df' not in st.session_state:
            st.session_state.analytics_df = pd.DataFrame()
            
    def load_data(self):
        """Load data from database"""
        with st.spinner("Loading data from database..."):
            try:
                # Load recent incidents
                cutoff_date = datetime.now() - timedelta(days=90)  # Last 3 months
                query = """
                    SELECT timestamp, normalized_type as crime_type, latitude, longitude, 
                           governorate, district, description
                    FROM incidents_clean 
                    WHERE timestamp >= %s
                    ORDER BY timestamp DESC
                """
                
                incidents_data = db_manager.execute_query(query, (cutoff_date,))
                if incidents_data:
                    st.session_state.incidents_df = pd.DataFrame(incidents_data)
                else:
                    st.session_state.incidents_df = pd.DataFrame()
                
                # Load hotspots
                hotspot_query = """
                    SELECT zone_name, latitude, longitude, severity, incident_count, risk_score, created_at
                    FROM zones_hotspots
                    ORDER BY risk_score DESC
                    LIMIT 100
                """
                
                hotspot_data = db_manager.execute_query(hotspot_query)
                if hotspot_data:
                    st.session_state.hotspots_df = pd.DataFrame(hotspot_data)
                else:
                    st.session_state.hotspots_df = pd.DataFrame()
                
                # Load analytics
                analytics_query = """
                    SELECT period_type, period_value, zone, crime_type, incident_count, created_at
                    FROM analytics_summary
                    WHERE created_at >= %s
                    ORDER BY created_at DESC
                    LIMIT 1000
                """
                
                analytics_data = db_manager.execute_query(analytics_query, (cutoff_date,))
                if analytics_data:
                    st.session_state.analytics_df = pd.DataFrame(analytics_data)
                else:
                    st.session_state.analytics_df = pd.DataFrame()
                
                st.session_state.data_loaded = True
                st.success("Data loaded successfully!")
                
            except Exception as e:
                st.error(f"Error loading data: {e}")
                st.session_state.data_loaded = False
                
    def display_header(self):
        """Display dashboard header"""
        st.title("🚨 Khareetaty AI - Crime Analytics Dashboard")
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        if st.session_state.data_loaded and not st.session_state.incidents_df.empty:
            total_incidents = len(st.session_state.incidents_df)
            unique_crimes = st.session_state.incidents_df['crime_type'].nunique()
            unique_zones = st.session_state.incidents_df['governorate'].nunique()
            recent_incidents = len(st.session_state.incidents_df[
                st.session_state.incidents_df['timestamp'] >= datetime.now() - timedelta(days=7)
            ])
            
            col1.metric("Total Incidents", total_incidents)
            col2.metric("Crime Types", unique_crimes)
            col3.metric("Zones", unique_zones)
            col4.metric("Last 7 Days", recent_incidents)
        else:
            col1.metric("Total Incidents", "Loading...")
            col2.metric("Crime Types", "Loading...")
            col3.metric("Zones", "Loading...")
            col4.metric("Last 7 Days", "Loading...")
    
    def display_map_view(self):
        """Display map view of incidents and hotspots"""
        st.subheader("🗺️ Geographic View")
        
        if not st.session_state.data_loaded:
            st.warning("Data not loaded. Click 'Load Data' first.")
            return
            
        # Create tabs for different map views
        tab1, tab2, tab3 = st.tabs(["Incidents Map", "Hotspots Map", "Combined View"])
        
        with tab1:
            if not st.session_state.incidents_df.empty:
                # Prepare data for map
                map_data = st.session_state.incidents_df.copy()
                map_data = map_data.dropna(subset=['latitude', 'longitude'])
                
                # Create scatter mapbox
                fig = px.scatter_mapbox(
                    map_data,
                    lat='latitude',
                    lon='longitude',
                    color='crime_type',
                    size='incident_count' if 'incident_count' in map_data.columns else None,
                    hover_name='governorate',
                    hover_data={'district': True, 'description': True, 'timestamp': True},
                    zoom=9,
                    height=600,
                    title="Crime Incidents Map"
                )
                
                fig.update_layout(mapbox_style="open-street-map")
                fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No incident data available to display on map.")
        
        with tab2:
            if not st.session_state.hotspots_df.empty:
                # Create hotspot map
                fig = px.scatter_mapbox(
                    st.session_state.hotspots_df,
                    lat='latitude',
                    lon='longitude',
                    color='severity',
                    size='risk_score',
                    hover_name='zone_name',
                    hover_data={'incident_count': True, 'created_at': True},
                    zoom=9,
                    height=600,
                    title="Crime Hotspots Map"
                )
                
                fig.update_layout(mapbox_style="open-street-map")
                fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hotspot data available to display on map.")
        
        with tab3:
            if not st.session_state.incidents_df.empty and not st.session_state.hotspots_df.empty:
                # Combine incidents and hotspots for comparison
                combined_data = []
                
                # Add incidents
                for _, row in st.session_state.incidents_df.head(1000).iterrows():
                    combined_data.append({
                        'lat': row['latitude'],
                        'lon': row['longitude'],
                        'type': 'Incident',
                        'category': row['crime_type'],
                        'zone': row['governorate'],
                        'size': 5
                    })
                
                # Add hotspots
                for _, row in st.session_state.hotspots_df.head(100).iterrows():
                    combined_data.append({
                        'lat': row['latitude'],
                        'lon': row['longitude'],
                        'type': 'Hotspot',
                        'category': row['severity'],
                        'zone': row['zone_name'],
                        'size': row['risk_score'] * 3 if row['risk_score'] else 10
                    })
                
                combined_df = pd.DataFrame(combined_data)
                
                if not combined_df.empty:
                    fig = px.scatter_mapbox(
                        combined_df,
                        lat='lat',
                        lon='lon',
                        color='type',
                        size='size',
                        symbol='type',
                        hover_name='zone',
                        hover_data={'category': True, 'type': True},
                        zoom=9,
                        height=600,
                        title="Combined Incidents and Hotspots Map"
                    )
                    
                    fig.update_layout(mapbox_style="open-street-map")
                    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Need both incident and hotspot data to show combined view.")
    
    def display_time_series(self):
        """Display time series analysis"""
        st.subheader("📅 Time Series Analysis")
        
        if not st.session_state.data_loaded:
            st.warning("Data not loaded. Click 'Load Data' first.")
            return
            
        if st.session_state.incidents_df.empty:
            st.info("No incident data available for time series analysis.")
            return
            
        # Prepare time series data
        df = st.session_state.incidents_df.copy()
        df['date'] = df['timestamp'].dt.date
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()
        
        # Create tabs for different time views
        tab1, tab2, tab3 = st.tabs(["Daily Trend", "Hourly Pattern", "Weekly Pattern"])
        
        with tab1:
            # Daily trend
            daily_counts = df.groupby('date').size().reset_index(name='incident_count')
            
            fig = px.line(
                daily_counts,
                x='date',
                y='incident_count',
                title="Daily Incident Trend",
                labels={'date': 'Date', 'incident_count': 'Number of Incidents'}
            )
            
            fig.update_traces(mode='lines+markers')
            fig.update_layout(height=400)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Hourly pattern
            hourly_counts = df.groupby('hour').size().reset_index(name='incident_count')
            
            fig = px.bar(
                hourly_counts,
                x='hour',
                y='incident_count',
                title="Incident Distribution by Hour of Day",
                labels={'hour': 'Hour of Day', 'incident_count': 'Number of Incidents'},
                range_x=[0, 23]
            )
            
            fig.update_layout(height=400)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Weekly pattern
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=day_order, ordered=True)
            
            weekly_counts = df.groupby('day_of_week', observed=True).size().reset_index(name='incident_count')
            
            fig = px.bar(
                weekly_counts,
                x='day_of_week',
                y='incident_count',
                title="Incident Distribution by Day of Week",
                labels={'day_of_week': 'Day of Week', 'incident_count': 'Number of Incidents'}
            )
            
            fig.update_layout(height=400)
            
            st.plotly_chart(fig, use_container_width=True)
    
    def display_crime_analysis(self):
        """Display crime type analysis"""
        st.subheader("🔍 Crime Type Analysis")
        
        if not st.session_state.data_loaded:
            st.warning("Data not loaded. Click 'Load Data' first.")
            return
            
        if st.session_state.incidents_df.empty:
            st.info("No incident data available for crime analysis.")
            return
            
        # Create tabs for different crime views
        tab1, tab2, tab3 = st.tabs(["By Type", "By Zone", "By Severity"])
        
        with tab1:
            # Crime type distribution
            crime_counts = st.session_state.incidents_df['crime_type'].value_counts().reset_index()
            crime_counts.columns = ['crime_type', 'count']
            
            fig = px.pie(
                crime_counts,
                values='count',
                names='crime_type',
                title="Distribution of Crime Types"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Crime by zone/governorate
            zone_counts = st.session_state.incidents_df['governorate'].value_counts().reset_index()
            zone_counts.columns = ['governorate', 'count']
            
            fig = px.bar(
                zone_counts,
                x='governorate',
                y='count',
                title="Incident Distribution by Governorate",
                labels={'governorate': 'Governorate', 'count': 'Number of Incidents'}
            )
            
            fig.update_layout(xaxis_tickangle=-45, height=400)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Crime trends by type over time
            df = st.session_state.incidents_df.copy()
            df['date'] = df['timestamp'].dt.date
            
            # Top 5 crime types
            top_crimes = df['crime_type'].value_counts().head(5).index
            filtered_df = df[df['crime_type'].isin(top_crimes)]
            
            daily_crime_trends = filtered_df.groupby(['date', 'crime_type']).size().reset_index(name='count')
            
            fig = px.line(
                daily_crime_trends,
                x='date',
                y='count',
                color='crime_type',
                title="Top 5 Crime Types Trend Over Time"
            )
            
            fig.update_layout(height=500)
            
            st.plotly_chart(fig, use_container_width=True)
    
    def display_hotspot_analysis(self):
        """Display hotspot analysis"""
        st.subheader("🔥 Hotspot Analysis")
        
        if not st.session_state.data_loaded:
            st.warning("Data not loaded. Click 'Load Data' first.")
            return
            
        if st.session_state.hotspots_df.empty:
            st.info("No hotspot data available.")
            return
            
        # Create tabs for different hotspot views
        tab1, tab2, tab3 = st.tabs(["Risk Levels", "Location Details", "Severity Map"])
        
        with tab1:
            # Risk level distribution
            severity_counts = st.session_state.hotspots_df['severity'].value_counts().reset_index()
            severity_counts.columns = ['severity', 'count']
            
            fig = px.bar(
                severity_counts,
                x='severity',
                y='count',
                title="Hotspot Distribution by Risk Level",
                color='severity',
                color_discrete_map={'LOW': '#2ECC71', 'MEDIUM': '#F39C12', 'HIGH': '#E67E22', 'CRITICAL': '#E74C3C'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Show hotspot details in a table
            st.dataframe(
                st.session_state.hotspots_df[['zone_name', 'latitude', 'longitude', 'severity', 'incident_count', 'risk_score']].sort_values('risk_score', ascending=False),
                use_container_width=True
            )
        
        with tab3:
            # Risk score vs incident count scatter
            if 'risk_score' in st.session_state.hotspots_df.columns:
                fig = px.scatter(
                    st.session_state.hotspots_df,
                    x='incident_count',
                    y='risk_score',
                    color='severity',
                    size='risk_score',
                    hover_name='zone_name',
                    title="Risk Score vs Incident Count",
                    labels={'incident_count': 'Incident Count', 'risk_score': 'Risk Score'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    def display_predictions(self):
        """Display predictive analytics"""
        st.subheader("🔮 Predictive Analytics")
        
        if not st.session_state.data_loaded:
            st.warning("Data not loaded. Click 'Load Data' first.")
            return
            
        if st.session_state.incidents_df.empty:
            st.info("No incident data available for predictions.")
            return
            
        # Create tabs for different prediction views
        tab1, tab2 = st.tabs(["Zone Forecasts", "Pattern Recognition"])
        
        with tab1:
            st.write("Coming soon: Zone-based crime forecasts using Prophet model")
            # In a real implementation, this would show forecasts
            # For now, we'll just show placeholder information
            st.info("""
            The predictive model analyzes historical crime patterns to forecast:
            - Future crime rates by zone
            - Peak crime times
            - Emerging crime trends
            """)
        
        with tab2:
            st.write("Coming soon: Pattern recognition and anomaly detection")
            st.info("""
            Advanced analytics to identify:
            - Unusual crime spikes
            - Seasonal patterns
            - Geographic clustering trends
            """)
    
    def display_alerts(self):
        """Display recent alerts"""
        st.subheader("🔔 Recent Alerts")
        
        try:
            recent_alerts = db_manager.get_recent_alerts(hours=168)  # Last 7 days
            
            if recent_alerts:
                alerts_df = pd.DataFrame(recent_alerts)
                
                # Show alerts in a table
                st.dataframe(
                    alerts_df[['alert_type', 'severity', 'message', 'sent_at']].sort_values('sent_at', ascending=False),
                    use_container_width=True
                )
                
                # Alert type distribution
                if 'alert_type' in alerts_df.columns:
                    alert_counts = alerts_df['alert_type'].value_counts().reset_index()
                    alert_counts.columns = ['alert_type', 'count']
                    
                    fig = px.pie(
                        alert_counts,
                        values='count',
                        names='alert_type',
                        title="Distribution of Alert Types"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No recent alerts available.")
                
        except Exception as e:
            st.error(f"Error loading alerts: {e}")
    
    def display_sidebar_controls(self):
        """Display sidebar controls"""
        with st.sidebar:
            st.header("⚙️ Controls")
            
            # Data refresh
            if st.button("🔄 Refresh Data", type="secondary"):
                self.load_data()
            
            # Date range selector
            st.subheader("📅 Date Range")
            date_range = st.date_input(
                "Select date range",
                value=(
                    datetime.now() - timedelta(days=30),
                    datetime.now()
                ),
                max_value=datetime.now()
            )
            
            # Filter options
            st.subheader("筛选器")
            
            # Crime type filter
            if not st.session_state.incidents_df.empty:
                crime_types = st.session_state.incidents_df['crime_type'].unique().tolist()
                selected_crimes = st.multiselect("Select Crime Types", options=crime_types, default=crime_types)
            else:
                selected_crimes = []
            
            # Zone filter
            if not st.session_state.incidents_df.empty:
                zones = st.session_state.incidents_df['governorate'].unique().tolist()
                selected_zones = st.multiselect("Select Zones", options=zones, default=zones)
            else:
                selected_zones = []
            
            # Severity filter for hotspots
            if not st.session_state.hotspots_df.empty:
                severities = st.session_state.hotspots_df['severity'].unique().tolist()
                selected_severities = st.multiselect("Select Severity Levels", options=severities, default=severities)
            else:
                selected_severities = []
            
            # Auto-refresh toggle
            auto_refresh = st.checkbox("Enable Auto Refresh", value=False)
            
            if auto_refresh:
                st.experimental_rerun()
    
    def run_dashboard(self):
        """Run the main dashboard application"""
        # Display header
        self.display_header()
        
        # Load data if not already loaded
        if not st.session_state.data_loaded:
            with st.expander("Load Data", expanded=True):
                if st.button("📥 Load Data from Database"):
                    self.load_data()
        
        # Create main tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🗺️ Map View", "📊 Time Series", "🔍 Crime Analysis", 
            "🔥 Hotspots", "🔮 Predictions", "🔔 Alerts"
        ])
        
        # Sidebar controls
        self.display_sidebar_controls()
        
        # Populate tabs
        with tab1:
            self.display_map_view()
            
        with tab2:
            self.display_time_series()
            
        with tab3:
            self.display_crime_analysis()
            
        with tab4:
            self.display_hotspot_analysis()
            
        with tab5:
            self.display_predictions()
            
        with tab6:
            self.display_alerts()
        
        # Footer
        st.markdown("---")
        st.markdown("*Khareetaty AI - Crime Analytics System | Last updated: {}*".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

# Main execution
def main():
    app = DashboardApp()
    app.run_dashboard()

if __name__ == "__main__":
    main()