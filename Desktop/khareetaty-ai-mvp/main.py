"""
Main orchestrator for Khareetaty AI MVP Crime Analytics System
Coordinates the complete data pipeline: loading, cleaning, analytics, predictions, and alerts
"""
import sys
import os
import logging
from datetime import datetime, timedelta
import argparse

# Add src directory to path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.database import db_manager, DatabaseManager
from src.data_loader import DataLoader
from src.data_cleaner import DataCleaner
from src.analytics import AnalyticsEngine
from src.predictive_model import PredictiveModel
from src.alert_system import AlertSystem

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    def __init__(self):
        self.db_manager = db_manager
        self.data_loader = DataLoader()
        self.data_cleaner = DataCleaner()
        self.analytics_engine = AnalyticsEngine()
        self.predictive_model = PredictiveModel()
        self.alert_system = AlertSystem()
        
    def initialize_database(self):
        """Initialize database tables"""
        logger.info("Initializing database...")
        try:
            self.db_manager.create_tables()
            logger.info("Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False
            
    def load_data_from_staging(self):
        """Load data from staging directory"""
        logger.info("Starting data loading from staging directory...")
        try:
            rows_loaded = self.data_loader.validate_and_load_directory()
            logger.info(f"Data loading completed. Rows loaded: {rows_loaded}")
            return rows_loaded
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return 0
            
    def clean_raw_data(self):
        """Clean and process raw data"""
        logger.info("Starting data cleaning process...")
        try:
            rows_processed = self.data_cleaner.run_full_cleaning_pipeline()
            logger.info(f"Data cleaning completed. Rows processed: {rows_processed}")
            return rows_processed
        except Exception as e:
            logger.error(f"Failed to clean data: {e}")
            return 0
            
    def run_analytics(self):
        """Run analytics calculations"""
        logger.info("Starting analytics calculations...")
        try:
            # Generate analytics for the last 30 days
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()
            
            report = self.analytics_engine.generate_analytics_report(start_date, end_date)
            logger.info(f"Analytics completed. Report: {report}")
            return report
        except Exception as e:
            logger.error(f"Failed to run analytics: {e}")
            return {}
            
    def run_predictions(self):
        """Run predictive modeling"""
        logger.info("Starting predictive modeling...")
        try:
            predictions = self.predictive_model.predict_incidents()
            logger.info(f"Predictions completed. Summary: {predictions}")
            return predictions
        except Exception as e:
            logger.error(f"Failed to run predictions: {e}")
            return {}
            
    def run_alert_detection(self):
        """Run alert detection system"""
        logger.info("Starting alert detection...")
        try:
            results = self.alert_system.run_alert_detection_cycle()
            logger.info(f"Alert detection completed. Results: {results}")
            return results
        except Exception as e:
            logger.error(f"Failed to run alert detection: {e}")
            return {}
            
    def run_full_pipeline(self, run_load: bool = True, run_clean: bool = True, 
                         run_analytics: bool = True, run_predictions: bool = True, 
                         run_alerts: bool = True):
        """Run the complete data pipeline"""
        logger.info("Starting complete pipeline execution...")
        
        results = {}
        
        # Step 1: Initialize database
        if not self.initialize_database():
            logger.error("Database initialization failed. Aborting pipeline.")
            return results
            
        # Step 2: Load data
        if run_load:
            results['load_data'] = self.load_data_from_staging()
            
        # Step 3: Clean data
        if run_clean:
            results['clean_data'] = self.clean_raw_data()
            
        # Step 4: Run analytics
        if run_analytics:
            results['analytics'] = self.run_analytics()
            
        # Step 5: Run predictions
        if run_predictions:
            results['predictions'] = self.run_predictions()
            
        # Step 6: Run alerts
        if run_alerts:
            results['alerts'] = self.run_alert_detection()
            
        logger.info("Pipeline execution completed")
        return results
        
    def run_incremental_pipeline(self):
        """Run incremental updates to the pipeline"""
        logger.info("Starting incremental pipeline update...")
        
        results = {}
        
        # Load new data
        results['load_data'] = self.load_data_from_staging()
        
        # Process any new raw data
        results['clean_data'] = self.clean_raw_data()
        
        # Run analytics on recent data
        results['analytics'] = self.run_analytics()
        
        # Run predictions
        results['predictions'] = self.run_predictions()
        
        # Run alert detection
        results['alerts'] = self.run_alert_detection()
        
        logger.info("Incremental pipeline completed")
        return results
        
    def cleanup_old_data(self):
        """Clean up old data based on retention policies"""
        logger.info("Starting data cleanup...")
        try:
            self.db_manager.cleanup_old_data()
            logger.info("Data cleanup completed")
            return True
        except Exception as e:
            logger.error(f"Failed to clean up data: {e}")
            return False
            
    def health_check(self):
        """Perform health check of the system"""
        logger.info("Performing system health check...")
        
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Check database connection
        try:
            with self.db_manager.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status['checks']['database'] = 'OK'
        except Exception as e:
            health_status['checks']['database'] = f'ERROR: {e}'
            
        # Check if required tables exist
        try:
            tables = ['incidents_raw', 'incidents_clean', 'zones_hotspots', 'analytics_summary', 'alerts_log']
            missing_tables = []
            
            for table in tables:
                cursor = self.db_manager.connection.cursor()
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table}'
                    );
                """)
                exists = cursor.fetchone()[0]
                if not exists:
                    missing_tables.append(table)
                    
            if missing_tables:
                health_status['checks']['tables'] = f'MISSING: {missing_tables}'
            else:
                health_status['checks']['tables'] = 'OK'
                
        except Exception as e:
            health_status['checks']['tables'] = f'ERROR: {e}'
            
        # Check recent data
        try:
            query = "SELECT COUNT(*) as count FROM incidents_clean WHERE timestamp >= NOW() - INTERVAL '7 days'"
            result = self.db_manager.execute_query(query)
            recent_count = result[0]['count'] if result else 0
            health_status['checks']['recent_data'] = f'{recent_count} records in last 7 days'
        except Exception as e:
            health_status['checks']['recent_data'] = f'ERROR: {e}'
            
        logger.info(f"Health check completed: {health_status}")
        return health_status


def main():
    parser = argparse.ArgumentParser(description='Khareetaty AI Crime Analytics Pipeline')
    parser.add_argument('--mode', choices=['full', 'incremental', 'load', 'clean', 'analytics', 'predictions', 'alerts', 'health'], 
                       default='full', help='Pipeline mode to run')
    parser.add_argument('--no-load', action='store_true', help='Skip data loading step')
    parser.add_argument('--no-clean', action='store_true', help='Skip data cleaning step')
    parser.add_argument('--no-analytics', action='store_true', help='Skip analytics step')
    parser.add_argument('--no-predictions', action='store_true', help='Skip predictions step')
    parser.add_argument('--no-alerts', action='store_true', help='Skip alerts step')
    
    args = parser.parse_args()
    
    orchestrator = PipelineOrchestrator()
    
    if args.mode == 'health':
        # Run health check only
        health_status = orchestrator.health_check()
        print(f"Health Status: {health_status}")
        return
        
    # Determine which steps to run
    run_load = not args.no_load
    run_clean = not args.no_clean
    run_analytics = not args.no_analytics
    run_predictions = not args.no_predictions
    run_alerts = not args.no_alerts
    
    if args.mode == 'full':
        results = orchestrator.run_full_pipeline(run_load, run_clean, run_analytics, run_predictions, run_alerts)
    elif args.mode == 'incremental':
        results = orchestrator.run_incremental_pipeline()
    elif args.mode == 'load':
        results = {'load_data': orchestrator.load_data_from_staging()}
    elif args.mode == 'clean':
        results = {'clean_data': orchestrator.clean_raw_data()}
    elif args.mode == 'analytics':
        results = {'analytics': orchestrator.run_analytics()}
    elif args.mode == 'predictions':
        results = {'predictions': orchestrator.run_predictions()}
    elif args.mode == 'alerts':
        results = {'alerts': orchestrator.run_alert_detection()}
    else:
        # Default to full pipeline
        results = orchestrator.run_full_pipeline(run_load, run_clean, run_analytics, run_predictions, run_alerts)
    
    print(f"Pipeline completed with results: {results}")
    
    # Cleanup old data after successful pipeline run
    orchestrator.cleanup_old_data()


if __name__ == "__main__":
    main()