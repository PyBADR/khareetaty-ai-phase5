"""
Analytics engine for Khareetaty AI MVP Crime Analytics System
Handles hourly/daily/zone frequency calculations and statistical analysis
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
from collections import Counter
import calendar

from src.config import Config
from src.database import db_manager

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    def __init__(self):
        self.timezone = Config.TIMEZONE
        
    def calculate_hourly_frequency(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate hourly incident frequency"""
        if df.empty:
            return pd.DataFrame()
            
        # Extract hour from timestamp
        df_copy = df.copy()
        df_copy['hour'] = df_copy['timestamp'].dt.hour
        df_copy['date'] = df_copy['timestamp'].dt.date
        
        # Group by date and hour
        hourly_freq = df_copy.groupby(['date', 'hour', 'governorate', 'crime_type']).size().reset_index(name='incident_count')
        
        # Add period information for analytics table
        hourly_freq['period_type'] = 'HOURLY'
        hourly_freq['period_value'] = hourly_freq.apply(
            lambda row: f"{row['date']} {row['hour']:02d}:00:00", axis=1
        )
        
        return hourly_freq
        
    def calculate_daily_frequency(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate daily incident frequency"""
        if df.empty:
            return pd.DataFrame()
            
        # Extract date from timestamp
        df_copy = df.copy()
        df_copy['date'] = df_copy['timestamp'].dt.date
        
        # Group by date
        daily_freq = df_copy.groupby(['date', 'governorate', 'crime_type']).size().reset_index(name='incident_count')
        
        # Add period information for analytics table
        daily_freq['period_type'] = 'DAILY'
        daily_freq['period_value'] = daily_freq['date'].astype(str)
        
        return daily_freq
        
    def calculate_weekly_frequency(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate weekly incident frequency"""
        if df.empty:
            return pd.DataFrame()
            
        # Extract week from timestamp
        df_copy = df.copy()
        df_copy['year'] = df_copy['timestamp'].dt.year
        df_copy['week'] = df_copy['timestamp'].dt.isocalendar().week
        
        # Group by year and week
        weekly_freq = df_copy.groupby(['year', 'week', 'governorate', 'crime_type']).size().reset_index(name='incident_count')
        
        # Add period information for analytics table
        weekly_freq['period_type'] = 'WEEKLY'
        weekly_freq['period_value'] = weekly_freq.apply(
            lambda row: f"{row['year']}-W{row['week']:02d}", axis=1
        )
        
        return weekly_freq
        
    def calculate_monthly_frequency(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate monthly incident frequency"""
        if df.empty:
            return pd.DataFrame()
            
        # Extract month from timestamp
        df_copy = df.copy()
        df_copy['year'] = df_copy['timestamp'].dt.year
        df_copy['month'] = df_copy['timestamp'].dt.month
        
        # Group by year and month
        monthly_freq = df_copy.groupby(['year', 'month', 'governorate', 'crime_type']).size().reset_index(name='incident_count')
        
        # Add period information for analytics table
        monthly_freq['period_type'] = 'MONTHLY'
        monthly_freq['period_value'] = monthly_freq.apply(
            lambda row: f"{row['year']}-{row['month']:02d}", axis=1
        )
        
        return monthly_freq
        
    def calculate_zone_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate statistics by zone (governorate/district)"""
        if df.empty:
            return pd.DataFrame()
            
        # Group by zone
        zone_stats = df.groupby(['governorate', 'district', 'crime_type']).agg({
            'id': 'count',
            'timestamp': ['min', 'max']
        }).reset_index()
        
        # Flatten column names
        zone_stats.columns = ['governorate', 'district', 'crime_type', 'incident_count', 'first_incident', 'last_incident']
        
        return zone_stats
        
    def calculate_crime_type_distribution(self, df: pd.DataFrame) -> Dict:
        """Calculate distribution of crime types"""
        if df.empty:
            return {}
            
        distribution = df['normalized_type'].value_counts().to_dict()
        total = sum(distribution.values())
        
        # Calculate percentages
        percentages = {k: (v / total) * 100 for k, v in distribution.items()}
        
        return {
            'counts': distribution,
            'percentages': percentages,
            'total_incidents': total
        }
        
    def calculate_time_patterns(self, df: pd.DataFrame) -> Dict:
        """Calculate time-based patterns (hourly, daily, monthly)"""
        if df.empty:
            return {}
            
        # Hourly patterns
        hourly_pattern = df.groupby(df['timestamp'].dt.hour)['id'].count().to_dict()
        
        # Daily of week patterns (0=Monday, 6=Sunday)
        daily_pattern = df.groupby(df['timestamp'].dt.dayofweek)['id'].count().to_dict()
        
        # Monthly patterns
        monthly_pattern = df.groupby(df['timestamp'].dt.month)['id'].count().to_dict()
        
        return {
            'hourly': hourly_pattern,
            'daily_of_week': daily_pattern,
            'monthly': monthly_pattern
        }
        
    def calculate_hotspot_zones(self, df: pd.DataFrame, threshold: int = 5) -> List[Dict]:
        """Identify hotspot zones based on incident concentration"""
        if df.empty:
            return []
            
        # Group by location (rounded coordinates for clustering)
        df_copy = df.copy()
        df_copy['lat_rounded'] = df_copy['latitude'].round(3)
        df_copy['lon_rounded'] = df_copy['longitude'].round(3)
        
        location_counts = df_copy.groupby(['lat_rounded', 'lon_rounded', 'governorate']).size().reset_index(name='incident_count')
        
        # Filter for hotspots (above threshold)
        hotspots = location_counts[location_counts['incident_count'] >= threshold].to_dict('records')
        
        # Convert to proper format
        hotspot_list = []
        for hotspot in hotspots:
            hotspot_list.append({
                'latitude': float(hotspot['lat_rounded']),
                'longitude': float(hotspot['lon_rounded']),
                'governorate': hotspot['governorate'],
                'incident_count': int(hotspot['incident_count']),
                'severity': self._calculate_severity(hotspot['incident_count'])
            })
            
        return hotspot_list
        
    def _calculate_severity(self, incident_count: int) -> str:
        """Calculate severity level based on incident count"""
        if incident_count >= 20:
            return 'CRITICAL'
        elif incident_count >= 10:
            return 'HIGH'
        elif incident_count >= 5:
            return 'MEDIUM'
        else:
            return 'LOW'
            
    def calculate_trend_analysis(self, df: pd.DataFrame, days: int = 30) -> Dict:
        """Calculate trend analysis for recent days"""
        if df.empty:
            return {}
            
        # Get recent data
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_df = df[df['timestamp'] >= cutoff_date].copy()
        
        if recent_df.empty:
            return {}
            
        # Calculate daily trends
        recent_df['date'] = recent_df['timestamp'].dt.date
        daily_trends = recent_df.groupby('date').size().reset_index(name='daily_count')
        
        # Calculate moving average
        daily_trends['moving_avg'] = daily_trends['daily_count'].rolling(window=7, min_periods=1).mean()
        
        # Calculate trend direction
        if len(daily_trends) >= 2:
            recent_avg = daily_trends['daily_count'].tail(7).mean()
            older_avg = daily_trends['daily_count'].head(7).mean()
            
            if recent_avg > older_avg * 1.1:
                trend_direction = 'INCREASING'
            elif recent_avg < older_avg * 0.9:
                trend_direction = 'DECREASING'
            else:
                trend_direction = 'STABLE'
        else:
            trend_direction = 'INSUFFICIENT_DATA'
            
        return {
            'trend_direction': trend_direction,
            'recent_average': daily_trends['daily_count'].tail(7).mean(),
            'overall_average': daily_trends['daily_count'].mean(),
            'daily_trends': daily_trends.to_dict('records'),
            'total_recent_incidents': daily_trends['daily_count'].sum()
        }
        
    def aggregate_analytics(self, df: pd.DataFrame) -> Dict:
        """Perform comprehensive aggregation of analytics"""
        logger.info("Starting comprehensive analytics aggregation...")
        
        if df.empty:
            return {}
            
        results = {}
        
        # Calculate various frequency metrics
        results['hourly'] = self.calculate_hourly_frequency(df)
        results['daily'] = self.calculate_daily_frequency(df)
        results['weekly'] = self.calculate_weekly_frequency(df)
        results['monthly'] = self.calculate_monthly_frequency(df)
        results['zone_stats'] = self.calculate_zone_statistics(df)
        results['crime_distribution'] = self.calculate_crime_type_distribution(df)
        results['time_patterns'] = self.calculate_time_patterns(df)
        results['hotspots'] = self.calculate_hotspot_zones(df)
        results['trends'] = self.calculate_trend_analysis(df)
        
        logger.info("Analytics aggregation completed")
        return results
        
    def save_analytics_to_db(self, analytics_data: Dict):
        """Save analytics results to database"""
        logger.info("Saving analytics to database...")
        
        all_records = []
        
        # Combine all frequency data
        for freq_type in ['hourly', 'daily', 'weekly', 'monthly']:
            if freq_type in analytics_data and not analytics_data[freq_type].empty:
                freq_df = analytics_data[freq_type]
                
                for _, row in freq_df.iterrows():
                    all_records.append({
                        'period_type': row['period_type'],
                        'period_value': row['period_value'],
                        'zone': row.get('governorate', 'Unknown'),
                        'crime_type': row.get('crime_type', 'ALL'),
                        'incident_count': int(row['incident_count']),
                        'average_severity': 3.0  # Placeholder - would be calculated in a real system
                    })
        
        if all_records:
            # Convert to DataFrame and save
            analytics_df = pd.DataFrame(all_records)
            rows_saved = db_manager.insert_dataframe(analytics_df, 'analytics_summary')
            logger.info(f"Saved {rows_saved} analytics records to database")
            return rows_saved
        else:
            logger.info("No analytics records to save")
            return 0
            
    def generate_analytics_report(self, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """Generate comprehensive analytics report"""
        logger.info("Generating analytics report...")
        
        # Get data from database
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)  # Last 30 days by default
        if end_date is None:
            end_date = datetime.now()
            
        # Query incidents from clean table
        query = """
            SELECT * FROM incidents_clean 
            WHERE timestamp BETWEEN %s AND %s
            ORDER BY timestamp
        """
        
        incidents_data = db_manager.execute_query(query, (start_date, end_date))
        
        if not incidents_data:
            logger.warning("No incidents found for the specified date range")
            return {}
            
        df = pd.DataFrame(incidents_data)
        
        # Perform analytics
        analytics_results = self.aggregate_analytics(df)
        
        # Generate summary statistics
        summary = {
            'report_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total_incidents': len(df),
            'unique_governorates': df['governorate'].nunique(),
            'unique_crime_types': df['normalized_type'].nunique(),
            'analytics_generated': analytics_results
        }
        
        # Save to database
        self.save_analytics_to_db(analytics_results)
        
        logger.info("Analytics report generated successfully")
        return summary
        
    def get_analytics_summary(self, period_type: str = 'DAILY', governorate: str = None, 
                             crime_type: str = None, limit: int = 100) -> pd.DataFrame:
        """Retrieve analytics summary from database"""
        query = "SELECT * FROM analytics_summary WHERE period_type = %s"
        params = [period_type]
        
        if governorate:
            query += " AND zone = %s"
            params.append(governorate)
            
        if crime_type:
            query += " AND crime_type = %s"
            params.append(crime_type)
            
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        results = db_manager.execute_query(query, tuple(params))
        
        if results:
            return pd.DataFrame(results)
        else:
            return pd.DataFrame()
            
    def calculate_risk_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate risk scores for different zones and crime types"""
        if df.empty:
            return pd.DataFrame()
            
        # Group by zone and crime type to calculate risk factors
        risk_df = df.groupby(['governorate', 'district', 'normalized_type']).agg({
            'id': 'count',
            'timestamp': ['min', 'max']
        }).reset_index()
        
        # Flatten column names
        risk_df.columns = ['governorate', 'district', 'normalized_type', 'incident_count', 'first_incident', 'last_incident']
        
        # Calculate time span in days
        risk_df['time_span_days'] = (risk_df['last_incident'] - risk_df['first_incident']).dt.days
        risk_df['time_span_days'] = risk_df['time_span_days'].replace(0, 1)  # Avoid division by zero
        
        # Calculate rate of incidents per day
        risk_df['incident_rate_per_day'] = risk_df['incident_count'] / risk_df['time_span_days']
        
        # Calculate risk score (higher is riskier)
        # Weight by recency (more recent incidents = higher risk)
        max_rate = risk_df['incident_rate_per_day'].max()
        risk_df['risk_score'] = np.where(
            max_rate > 0,
            (risk_df['incident_rate_per_day'] / max_rate) * 10,  # Scale to 0-10
            0
        )
        
        # Add severity classification
        conditions = [
            risk_df['risk_score'] >= 7.5,
            risk_df['risk_score'] >= 5.0,
            risk_df['risk_score'] >= 2.5,
            risk_df['risk_score'] < 2.5
        ]
        choices = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        risk_df['severity_level'] = np.select(conditions, choices)
        
        return risk_df[['governorate', 'district', 'normalized_type', 'incident_count', 
                       'incident_rate_per_day', 'risk_score', 'severity_level']]