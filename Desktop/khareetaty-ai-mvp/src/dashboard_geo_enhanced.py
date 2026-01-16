"""
Geo-Enhanced Dashboard Module for Khareetaty-AI
Adds choropleth maps with district/governorate polygons and zone filters
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import Config
from src.database import db_manager

# Path to geo data
GEO_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'data', 'geo', 'kuwait'
)

class GeoEnhancedDashboard:
    """
    Enhanced dashboard with geographic polygon visualization
    """
    
    def __init__(self):
        self.geo_data = {}
        self._load_geo_data()
    
    def _load_geo_data(self):
        """Load GeoJSON files for map visualization"""
        try:
            # Load governorates
            gov_path = os.path.join(GEO_DATA_PATH, 'governorates.geojson')
            with open(gov_path, 'r', encoding='utf-8') as f:
                self.geo_data['governorates'] = json.load(f)
            
            # Load districts
            dist_path = os.path.join(GEO_DATA_PATH, 'districts.geojson')
            with open(dist_path, 'r', encoding='utf-8') as f:
                self.geo_data['districts'] = json.load(f)
            
            # Load police zones
            pz_path = os.path.join(GEO_DATA_PATH, 'police_zones.geojson')
            with open(pz_path, 'r', encoding='utf-8') as f:
                self.geo_data['police_zones'] = json.load(f)
            
            # Load index
            index_path = os.path.join(GEO_DATA_PATH, 'index.json')
            with open(index_path, 'r', encoding='utf-8') as f:
                self.geo_data['index'] = json.load(f)
            
            st.success("✅ Geographic data loaded successfully")
            
        except FileNotFoundError as e:
            st.error(f"❌ Geographic data files not found: {e}")
            self.geo_data = {}
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid GeoJSON format: {e}")
            self.geo_data = {}
    
    def render_geo_filters(self):
        """Render geographic filter sidebar"""
        st.sidebar.header("🗺️ Geographic Filters")
        
        # Get available zones from geo data
        governorates = []
        districts = []
        police_zones = []
        
        if 'governorates' in self.geo_data:
            governorates = [f['properties']['name_en'] 
                          for f in self.geo_data['governorates']['features']]
        
        if 'districts' in self.geo_data:
            districts = [f['properties']['name_en'] 
                       for f in self.geo_data['districts']['features']]
        
        if 'police_zones' in self.geo_data:
            police_zones = [f['properties']['name_en'] 
                          for f in self.geo_data['police_zones']['features']]
        
        # Governorate filter
        selected_governorates = st.sidebar.multiselect(
            "Governorate",
            options=governorates,
            default=[]
        )
        
        # District filter (filtered by governorate if selected)
        if selected_governorates:
            filtered_districts = [
                f['properties']['name_en']
                for f in self.geo_data.get('districts', {}).get('features', [])
                if f['properties'].get('governorate') in selected_governorates
            ]
        else:
            filtered_districts = districts
        
        selected_districts = st.sidebar.multiselect(
            "District",
            options=filtered_districts,
            default=[]
        )
        
        # Police zone filter
        selected_police_zones = st.sidebar.multiselect(
            "Police Zone",
            options=police_zones,
            default=[]
        )
        
        return {
            'governorates': selected_governorates,
            'districts': selected_districts,
            'police_zones': selected_police_zones
        }
    
    def render_choropleth_map(self, incidents_df, hotspots_df, zone_level='district'):
        """
        Render choropleth map with incident density by zone
        
        Args:
            incidents_df: DataFrame with incident data
            hotspots_df: DataFrame with hotspot data
            zone_level: 'governorate', 'district', or 'police_zone'
        """
        st.subheader(f"🗺️ Hotspot Intensity Map - {zone_level.title()} Level")
        
        if zone_level not in self.geo_data:
            st.warning(f"Geographic data for {zone_level} not available")
            return
        
        # Calculate incident counts per zone
        if zone_level == 'district' and 'district' in incidents_df.columns:
            zone_counts = incidents_df['district'].value_counts().to_dict()
        elif zone_level == 'governorate' and 'governorate' in incidents_df.columns:
            zone_counts = incidents_df['governorate'].value_counts().to_dict()
        elif zone_level == 'police_zone' and 'police_zone' in incidents_df.columns:
            zone_counts = incidents_df['police_zone'].value_counts().to_dict()
        else:
            st.info(f"No {zone_level} data available in incidents")
            return
        
        # Create figure
        fig = go.Figure()
        
        # Add polygons with color intensity
        for feature in self.geo_data[zone_level]['features']:
            zone_name = feature['properties']['name_en']
            count = zone_counts.get(zone_name, 0)
            
            # Normalize intensity (0-1)
            max_count = max(zone_counts.values()) if zone_counts else 1
            intensity = count / max_count if max_count > 0 else 0
            
            # Color scale: white -> yellow -> orange -> red
            if intensity == 0:
                color = 'rgba(200, 200, 200, 0.3)'
            elif intensity < 0.25:
                color = f'rgba(255, 255, 0, {0.3 + intensity})'
            elif intensity < 0.5:
                color = f'rgba(255, 200, 0, {0.4 + intensity})'
            elif intensity < 0.75:
                color = f'rgba(255, 150, 0, {0.5 + intensity})'
            else:
                color = f'rgba(255, 0, 0, {0.6 + intensity})'
            
            # Extract coordinates
            if feature['geometry']['type'] == 'Polygon':
                coords = feature['geometry']['coordinates'][0]
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                
                fig.add_trace(go.Scattermapbox(
                    lon=lons,
                    lat=lats,
                    mode='lines',
                    fill='toself',
                    fillcolor=color,
                    line=dict(width=1, color='rgba(0, 0, 0, 0.5)'),
                    name=zone_name,
                    hovertemplate=f"<b>{zone_name}</b><br>Incidents: {count}<extra></extra>"
                ))
        
        # Add incident markers
        if not incidents_df.empty and 'lat' in incidents_df.columns:
            fig.add_trace(go.Scattermapbox(
                lat=incidents_df['lat'],
                lon=incidents_df['lon'],
                mode='markers',
                marker=dict(
                    size=4,
                    color='blue',
                    opacity=0.6
                ),
                name='Incidents',
                hovertemplate='<b>Incident</b><br>Type: %{text}<extra></extra>',
                text=incidents_df.get('incident_type', '')
            ))
        
        # Add hotspot markers if available
        if not hotspots_df.empty and 'lat' in hotspots_df.columns:
            fig.add_trace(go.Scattermapbox(
                lat=hotspots_df['lat'],
                lon=hotspots_df['lon'],
                mode='markers',
                marker=dict(
                    size=12,
                    color='red',
                    symbol='star',
                    opacity=0.8
                ),
                name='Hotspots',
                hovertemplate='<b>Hotspot</b><br>Score: %{text}<extra></extra>',
                text=hotspots_df.get('score', '')
            ))
        
        # Update layout
        fig.update_layout(
            mapbox=dict(
                style='open-street-map',
                center=dict(lat=29.3759, lon=47.9774),  # Kuwait City
                zoom=8
            ),
            height=600,
            showlegend=True,
            margin=dict(r=0, t=0, l=0, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_forecast_overlay(self, forecast_df):
        """
        Render forecast predictions as overlay markers
        
        Args:
            forecast_df: DataFrame with forecast data (district, predicted_count, etc.)
        """
        st.subheader("🔮 24-Hour Forecast Overlay")
        
        if forecast_df.empty:
            st.info("No forecast data available")
            return
        
        # Create map with forecast markers
        fig = go.Figure()
        
        # Add district polygons (light background)
        if 'districts' in self.geo_data:
            for feature in self.geo_data['districts']['features']:
                coords = feature['geometry']['coordinates'][0]
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                
                fig.add_trace(go.Scattermapbox(
                    lon=lons,
                    lat=lats,
                    mode='lines',
                    fill='toself',
                    fillcolor='rgba(200, 200, 200, 0.2)',
                    line=dict(width=1, color='rgba(0, 0, 0, 0.3)'),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        # Add forecast markers
        for _, row in forecast_df.iterrows():
            # Get district center (approximate)
            district_name = row.get('district', row.get('zone', 'Unknown'))
            predicted_count = row.get('forecast_count', row.get('predicted_count', 0))
            trend = row.get('score', 0)  # Trend percentage
            
            # Find district center from geo data
            district_center = self._get_district_center(district_name)
            if not district_center:
                continue
            
            # Marker size based on predicted count
            marker_size = min(30, 10 + predicted_count)
            
            # Color based on trend
            if trend > 10:
                color = 'red'
            elif trend > 0:
                color = 'orange'
            elif trend < -10:
                color = 'green'
            else:
                color = 'yellow'
            
            fig.add_trace(go.Scattermapbox(
                lat=[district_center['lat']],
                lon=[district_center['lon']],
                mode='markers+text',
                marker=dict(
                    size=marker_size,
                    color=color,
                    opacity=0.7
                ),
                text=[str(predicted_count)],
                textposition='middle center',
                textfont=dict(size=10, color='white', family='Arial Black'),
                name=district_name,
                hovertemplate=f"<b>{district_name}</b><br>" +
                             f"Forecast: {predicted_count} incidents<br>" +
                             f"Trend: {trend:+.1f}%<extra></extra>"
            ))
        
        fig.update_layout(
            mapbox=dict(
                style='open-street-map',
                center=dict(lat=29.3759, lon=47.9774),
                zoom=8
            ),
            height=600,
            showlegend=False,
            margin=dict(r=0, t=0, l=0, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _get_district_center(self, district_name):
        """Get approximate center of a district"""
        if 'districts' not in self.geo_data:
            return None
        
        for feature in self.geo_data['districts']['features']:
            if feature['properties']['name_en'] == district_name:
                coords = feature['geometry']['coordinates'][0]
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                return {
                    'lat': sum(lats) / len(lats),
                    'lon': sum(lons) / len(lons)
                }
        return None
    
    def render_zone_statistics(self, incidents_df):
        """Render statistics table by zone"""
        st.subheader("📊 Zone Statistics")
        
        if incidents_df.empty:
            st.info("No incident data available")
            return
        
        # Create tabs for different zone levels
        tab1, tab2, tab3 = st.tabs(["By District", "By Governorate", "By Police Zone"])
        
        with tab1:
            if 'district' in incidents_df.columns:
                stats = incidents_df.groupby('district').agg({
                    'id': 'count',
                    'incident_type': lambda x: x.mode()[0] if len(x) > 0 else 'N/A',
                    'timestamp': ['min', 'max']
                }).round(2)
                stats.columns = ['Total Incidents', 'Most Common Type', 'First Incident', 'Last Incident']
                stats = stats.sort_values('Total Incidents', ascending=False)
                st.dataframe(stats, use_container_width=True)
            else:
                st.info("District data not available")
        
        with tab2:
            if 'governorate' in incidents_df.columns:
                stats = incidents_df.groupby('governorate').agg({
                    'id': 'count',
                    'incident_type': lambda x: x.mode()[0] if len(x) > 0 else 'N/A'
                }).round(2)
                stats.columns = ['Total Incidents', 'Most Common Type']
                stats = stats.sort_values('Total Incidents', ascending=False)
                st.dataframe(stats, use_container_width=True)
            else:
                st.info("Governorate data not available")
        
        with tab3:
            if 'police_zone' in incidents_df.columns:
                stats = incidents_df.groupby('police_zone').agg({
                    'id': 'count',
                    'district': 'nunique'
                }).round(2)
                stats.columns = ['Total Incidents', 'Districts Covered']
                stats = stats.sort_values('Total Incidents', ascending=False)
                st.dataframe(stats, use_container_width=True)
            else:
                st.info("Police zone data not available")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Khareetaty AI - Geo Enhanced",
        page_icon="🗺️",
        layout="wide"
    )
    
    st.title("🗺️ Khareetaty AI - Geographic Intelligence Dashboard")
    
    dashboard = GeoEnhancedDashboard()
    
    # Render filters
    filters = dashboard.render_geo_filters()
    
    st.write("Selected filters:", filters)
