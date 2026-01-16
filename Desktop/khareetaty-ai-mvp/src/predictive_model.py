"""
Predictive model module for Khareetaty AI MVP Crime Analytics System
Implements Prophet time series forecasting and clustering algorithms for hotspot detection
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import warnings

# Suppress Prophet warnings
warnings.filterwarnings("ignore")

try:
    from prophet import Prophet
except ImportError:
    Prophet = None
    print("Warning: Prophet not installed. Install with 'pip install prophet'")

from geopy.distance import geodesic
from src.config import Config
from src.database import db_manager

logger = logging.getLogger(__name__)

class PredictiveModel:
    def __init__(self):
        self.forecast_periods = Config.DEFAULT_FORECAST_PERIODS
        self.cluster_epsilon_km = Config.CLUSTER_EPSILON_KM
        self.min_samples_cluster = Config.MIN_SAMPLES_CLUSTER
        
    def prepare_prophet_data(self, df: pd.DataFrame, date_col: str = 'timestamp', 
                           target_col: str = 'incident_count') -> pd.DataFrame:
        """Prepare data for Prophet forecasting"""
        if df.empty:
            return pd.DataFrame()
            
        # Create the required Prophet format: ds (date) and y (target)
        prophet_df = pd.DataFrame({
            'ds': df[date_col],
            'y': df[target_col] if target_col in df.columns else 1  # Default to 1 if counting events
        })
        
        # Ensure ds is datetime and y is numeric
        prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
        prophet_df['y'] = pd.to_numeric(prophet_df['y'], errors='coerce')
        
        # Remove any NaN values
        prophet_df = prophet_df.dropna()
        
        return prophet_df
        
    def forecast_by_zone(self, df: pd.DataFrame, zone_column: str = 'governorate', 
                        date_col: str = 'timestamp', target_col: str = 'incident_count') -> Dict:
        """Generate forecasts for each zone"""
        if df.empty:
            return {}
            
        if Prophet is None:
            logger.error("Prophet library not available. Please install with 'pip install prophet'")
            return {}
            
        forecasts = {}
        
        # Group by zone
        grouped = df.groupby(zone_column)
        
        for zone, zone_data in grouped:
            logger.info(f"Forecasting for zone: {zone}")
            
            # Prepare data for Prophet
            if target_col in zone_data.columns:
                prophet_data = self.prepare_prophet_data(zone_data, date_col, target_col)
            else:
                # If no target column, count incidents per day
                daily_counts = zone_data.groupby(zone_data[date_col].dt.date).size().reset_index(name='incident_count')
                daily_counts.columns = ['timestamp', 'incident_count']
                prophet_data = self.prepare_prophet_data(daily_counts, 'timestamp', 'incident_count')
            
            if len(prophet_data) < 10:  # Need minimum data points for Prophet
                logger.warning(f"Not enough data points for zone {zone} (need at least 10)")
                continue
                
            try:
                # Create and fit Prophet model
                model = Prophet(
                    yearly_seasonality=True,
                    weekly_seasonality=True,
                    daily_seasonality=False,
                    interval_width=0.95
                )
                model.fit(prophet_data)
                
                # Create future dataframe
                future = model.make_future_dataframe(periods=self.forecast_periods)
                
                # Make predictions
                forecast = model.predict(future)
                
                # Store results
                forecasts[zone] = {
                    'model': model,
                    'forecast': forecast,
                    'historical_data': prophet_data,
                    'prediction_dates': forecast.tail(self.forecast_periods)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records')
                }
                
                logger.info(f"Generated forecast for {zone} with {self.forecast_periods} periods")
                
            except Exception as e:
                logger.error(f"Error forecasting for zone {zone}: {e}")
                continue
                
        return forecasts
        
    def forecast_by_crime_type(self, df: pd.DataFrame, crime_column: str = 'normalized_type', 
                              date_col: str = 'timestamp') -> Dict:
        """Generate forecasts for each crime type"""
        if df.empty:
            return {}
            
        if Prophet is None:
            logger.error("Prophet library not available. Please install with 'pip install prophet'")
            return {}
            
        forecasts = {}
        
        # Group by crime type
        grouped = df.groupby(crime_column)
        
        for crime_type, crime_data in grouped:
            logger.info(f"Forecasting for crime type: {crime_type}")
            
            # Count incidents per day for this crime type
            daily_counts = crime_data.groupby(crime_data[date_col].dt.date).size().reset_index(name='incident_count')
            daily_counts.columns = ['timestamp', 'incident_count']
            
            prophet_data = self.prepare_prophet_data(daily_counts, 'timestamp', 'incident_count')
            
            if len(prophet_data) < 10:  # Need minimum data points for Prophet
                logger.warning(f"Not enough data points for crime type {crime_type} (need at least 10)")
                continue
                
            try:
                # Create and fit Prophet model
                model = Prophet(
                    yearly_seasonality=True,
                    weekly_seasonality=True,
                    daily_seasonality=False,
                    interval_width=0.95
                )
                model.fit(prophet_data)
                
                # Create future dataframe
                future = model.make_future_dataframe(periods=self.forecast_periods)
                
                # Make predictions
                forecast = model.predict(future)
                
                # Store results
                forecasts[crime_type] = {
                    'model': model,
                    'forecast': forecast,
                    'historical_data': prophet_data,
                    'prediction_dates': forecast.tail(self.forecast_periods)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records')
                }
                
                logger.info(f"Generated forecast for {crime_type} with {self.forecast_periods} periods")
                
            except Exception as e:
                logger.error(f"Error forecasting for crime type {crime_type}: {e}")
                continue
                
        return forecasts
        
    def detect_hotspots_dbscan(self, df: pd.DataFrame) -> List[Dict]:
        """Detect crime hotspots using DBSCAN clustering algorithm"""
        if df.empty:
            return []
            
        # Prepare coordinates for clustering
        coords = df[['latitude', 'longitude']].values
        
        if len(coords) < 2:
            logger.warning("Not enough data points for clustering")
            return []
            
        # Convert epsilon from km to approximate degree difference
        # Rough conversion: 1 degree ~ 111 km at equator (adjustment needed for Kuwait's latitude)
        epsilon_degrees = self.cluster_epsilon_km / 111.0
        
        # Apply DBSCAN clustering
        dbscan = DBSCAN(eps=epsilon_degrees, min_samples=self.min_samples_cluster, metric='euclidean')
        cluster_labels = dbscan.fit_predict(coords)
        
        # Count points in each cluster
        unique_labels, counts = np.unique(cluster_labels, return_counts=True)
        
        hotspots = []
        
        for label, count in zip(unique_labels, counts):
            if label == -1:  # Noise points, skip
                continue
                
            # Get coordinates for this cluster
            cluster_mask = cluster_labels == label
            cluster_coords = coords[cluster_mask]
            
            # Calculate centroid
            centroid_lat = np.mean(cluster_coords[:, 0])
            centroid_lon = np.mean(cluster_coords[:, 1])
            
            # Determine severity based on incident count
            severity = self._determine_hotspot_severity(count)
            
            hotspots.append({
                'zone_name': f'Hotspot_{label}',
                'latitude': float(centroid_lat),
                'longitude': float(centroid_lon),
                'severity': severity,
                'cluster_id': int(label),
                'incident_count': int(count),
                'risk_score': float(min(count * 2, 10))  # Scale risk score 0-10
            })
            
        logger.info(f"Detected {len(hotspots)} DBSCAN hotspots")
        return hotspots
        
    def detect_hotspots_kmeans(self, df: pd.DataFrame, n_clusters: int = 5) -> List[Dict]:
        """Detect crime hotspots using KMeans clustering algorithm"""
        if df.empty:
            return []
            
        # Prepare coordinates for clustering
        coords = df[['latitude', 'longitude']].values
        
        if len(coords) < n_clusters:
            logger.warning(f"Not enough data points for {n_clusters} clusters, reducing to {len(coords)}")
            n_clusters = max(1, len(coords))
            
        if n_clusters < 1:
            logger.warning("Not enough data points for clustering")
            return []
            
        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(coords)
        
        # Get cluster centers
        cluster_centers = kmeans.cluster_centers_
        
        # Count points in each cluster
        unique_labels, counts = np.unique(cluster_labels, return_counts=True)
        
        hotspots = []
        
        for label, count in zip(unique_labels, counts):
            center = cluster_centers[label]
            
            # Determine severity based on incident count
            severity = self._determine_hotspot_severity(count)
            
            hotspots.append({
                'zone_name': f'KMeans_Hotspot_{label}',
                'latitude': float(center[0]),
                'longitude': float(center[1]),
                'severity': severity,
                'cluster_id': int(label),
                'incident_count': int(count),
                'risk_score': float(min(count * 2, 10))  # Scale risk score 0-10
            })
            
        logger.info(f"Detected {len(hotspots)} KMeans hotspots")
        return hotspots
        
    def _determine_hotspot_severity(self, incident_count: int) -> str:
        """Determine severity level based on incident count"""
        if incident_count >= 20:
            return 'CRITICAL'
        elif incident_count >= 10:
            return 'HIGH'
        elif incident_count >= 5:
            return 'MEDIUM'
        else:
            return 'LOW'
            
    def optimize_cluster_number(self, df: pd.DataFrame, max_clusters: int = 10) -> int:
        """Optimize the number of clusters using silhouette analysis"""
        if df.empty or len(df) < 2:
            return 1
            
        coords = df[['latitude', 'longitude']].values
        max_clusters = min(max_clusters, len(df) - 1)
        
        if max_clusters < 2:
            return 1
            
        best_n_clusters = 2
        best_silhouette = -1
        
        for n_clusters in range(2, max_clusters + 1):
            try:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(coords)
                
                if len(np.unique(cluster_labels)) > 1:  # Need at least 2 clusters for silhouette
                    silhouette_avg = silhouette_score(coords, cluster_labels)
                    
                    if silhouette_avg > best_silhouette:
                        best_silhouette = silhouette_avg
                        best_n_clusters = n_clusters
                        
            except Exception:
                continue
                
        return best_n_clusters
        
    def save_hotspots_to_db(self, hotspots: List[Dict], prediction_date: datetime = None) -> int:
        """Save detected hotspots to database"""
        if not hotspots:
            logger.info("No hotspots to save")
            return 0
            
        if prediction_date is None:
            prediction_date = datetime.now().date()
            
        # Prepare data for insertion
        hotspot_records = []
        
        for hotspot in hotspots:
            hotspot_records.append((
                hotspot['zone_name'],
                hotspot['latitude'],
                hotspot['longitude'],
                hotspot['severity'],
                prediction_date,
                hotspot['cluster_id'],
                hotspot['incident_count'],
                hotspot['risk_score']
            ))
            
        # Create query
        query = """
            INSERT INTO zones_hotspots 
            (zone_name, latitude, longitude, severity, prediction_date, cluster_id, incident_count, risk_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            with db_manager.connection.cursor() as cursor:
                cursor.executemany(query, hotspot_records)
                rows_inserted = cursor.rowcount
                logger.info(f"Saved {rows_inserted} hotspots to database")
                return rows_inserted
        except Exception as e:
            logger.error(f"Failed to save hotspots to database: {e}")
            raise
            
    def predict_incidents(self, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """Generate comprehensive predictions including forecasts and hotspots"""
        logger.info("Starting comprehensive prediction process...")
        
        if start_date is None:
            start_date = datetime.now() - timedelta(days=90)  # Last 3 months of data
        if end_date is None:
            end_date = datetime.now()
            
        # Get data from database
        query = """
            SELECT timestamp, normalized_type, latitude, longitude, governorate, district
            FROM incidents_clean 
            WHERE timestamp BETWEEN %s AND %s
            ORDER BY timestamp
        """
        
        incidents_data = db_manager.execute_query(query, (start_date, end_date))
        
        if not incidents_data:
            logger.warning("No incidents found for prediction")
            return {}
            
        df = pd.DataFrame(incidents_data)
        
        results = {}
        
        # Generate forecasts by zone
        logger.info("Generating forecasts by zone...")
        zone_forecasts = self.forecast_by_zone(df)
        results['zone_forecasts'] = zone_forecasts
        
        # Generate forecasts by crime type
        logger.info("Generating forecasts by crime type...")
        crime_forecasts = self.forecast_by_crime_type(df)
        results['crime_forecasts'] = crime_forecasts
        
        # Detect hotspots using DBSCAN
        logger.info("Detecting hotspots using DBSCAN...")
        dbscan_hotspots = self.detect_hotspots_dbscan(df)
        results['dbscan_hotspots'] = dbscan_hotspots
        
        # Detect hotspots using KMeans with optimized cluster number
        logger.info("Detecting hotspots using KMeans...")
        optimal_clusters = self.optimize_cluster_number(df)
        kmeans_hotspots = self.detect_hotspots_kmeans(df, optimal_clusters)
        results['kmeans_hotspots'] = kmeans_hotspots
        
        # Combine all hotspots
        all_hotspots = dbscan_hotspots + kmeans_hotspots
        
        # Save hotspots to database
        if all_hotspots:
            rows_saved = self.save_hotspots_to_db(all_hotspots)
            logger.info(f"Saved {rows_saved} total hotspots to database")
        
        # Generate summary
        summary = {
            'prediction_date': datetime.now().isoformat(),
            'total_incidents_analyzed': len(df),
            'zones_forecasted': len(zone_forecasts),
            'crime_types_forecasted': len(crime_forecasts),
            'dbscan_hotspots_detected': len(dbscan_hotspots),
            'kmeans_hotspots_detected': len(kmeans_hotspots),
            'results': results
        }
        
        logger.info("Prediction process completed successfully")
        return summary
        
    def get_predictions_for_zone(self, governorate: str, days_ahead: int = 7) -> Dict:
        """Get specific predictions for a zone"""
        query = """
            SELECT timestamp, normalized_type, latitude, longitude
            FROM incidents_clean 
            WHERE governorate = %s
            ORDER BY timestamp
        """
        
        incidents_data = db_manager.execute_query(query, (governorate,))
        
        if not incidents_data:
            logger.warning(f"No incidents found for governorate: {governorate}")
            return {}
            
        df = pd.DataFrame(incidents_data)
        
        # Generate forecast for this specific zone
        if Prophet is not None:
            # Count incidents per day
            daily_counts = df.groupby(df['timestamp'].dt.date).size().reset_index(name='incident_count')
            daily_counts.columns = ['timestamp', 'incident_count']
            
            prophet_data = self.prepare_prophet_data(daily_counts, 'timestamp', 'incident_count')
            
            if len(prophet_data) >= 10:
                try:
                    model = Prophet(yearly_seasonality=True, weekly_seasonality=True, interval_width=0.95)
                    model.fit(prophet_data)
                    
                    future = model.make_future_dataframe(periods=days_ahead)
                    forecast = model.predict(future)
                    
                    # Get predictions for the next days_ahead days
                    predictions = forecast.tail(days_ahead)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records')
                    
                    return {
                        'zone': governorate,
                        'predictions': predictions,
                        'model_performance': 'good' if len(prophet_data) > 30 else 'limited_data'
                    }
                except Exception as e:
                    logger.error(f"Error generating prediction for {governorate}: {e}")
                    return {}
            else:
                logger.warning(f"Not enough data for {governorate} (only {len(prophet_data)} data points)")
                return {}
        else:
            logger.error("Prophet not available")
            return {}
            
    def evaluate_clustering_quality(self, df: pd.DataFrame) -> Dict:
        """Evaluate the quality of different clustering approaches"""
        if df.empty or len(df) < 2:
            return {}
            
        coords = df[['latitude', 'longitude']].values
        results = {}
        
        # DBSCAN evaluation
        try:
            epsilon_degrees = self.cluster_epsilon_km / 111.0
            dbscan = DBSCAN(eps=epsilon_degrees, min_samples=self.min_samples_cluster)
            dbscan_labels = dbscan.fit_predict(coords)
            
            n_clusters_dbscan = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
            n_noise_dbscan = list(dbscan_labels).count(-1)
            
            results['dbscan'] = {
                'n_clusters': n_clusters_dbscan,
                'n_noise_points': n_noise_dbscan,
                'cluster_ratio': n_clusters_dbscan / len(set(dbscan_labels)) if len(set(dbscan_labels)) > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error evaluating DBSCAN: {e}")
            results['dbscan'] = {'error': str(e)}
            
        # KMeans evaluation with different cluster numbers
        try:
            kmeans_results = {}
            for n_clusters in [3, 5, 8, 10]:
                if len(coords) >= n_clusters:
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                    kmeans_labels = kmeans.fit_predict(coords)
                    
                    if len(set(kmeans_labels)) > 1:
                        silhouette = silhouette_score(coords, kmeans_labels)
                    else:
                        silhouette = -1  # Invalid silhouette score
                    
                    kmeans_results[n_clusters] = {
                        'silhouette_score': silhouette,
                        'inertia': kmeans.inertia_
                    }
                    
            results['kmeans'] = kmeans_results
        except Exception as e:
            logger.error(f"Error evaluating KMeans: {e}")
            results['kmeans'] = {'error': str(e)}
            
        return results