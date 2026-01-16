"""
Predictive Patrol Allocation Service
Uses ML predictions to recommend optimal patrol routes and resource allocation
"""

import psycopg2
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)

DB_CONN = {
    "host": "postgres",
    "dbname": "khareetaty_ai",
    "user": "bader",
    "password": "secret123"
}

class PatrolAllocationEngine:
    """
    Predictive patrol allocation engine that:
    - Predicts tomorrow's high-risk zones
    - Recommends patrol routes
    - Assigns teams based on risk scores
    - Detects overwork and undercoverage
    - Optimizes resource distribution
    """
    
    def __init__(self):
        self.conn = None
    
    def _get_connection(self):
        """Get database connection"""
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(**DB_CONN)
        return self.conn
    
    def predict_tomorrows_hotspots(self) -> List[Dict]:
        """
        Predict tomorrow's high-risk zones based on:
        - Historical patterns (day of week)
        - Recent trends
        - Forecasting model predictions
        
        Returns:
            List of predicted hotspots with risk scores
        """
        try:
            conn = self._get_connection()
            
            # Get tomorrow's day of week
            tomorrow = datetime.now() + timedelta(days=1)
            day_name = tomorrow.strftime('%A')
            hour = tomorrow.hour
            
            # Get historical patterns for this day
            query = """
                SELECT 
                    zone,
                    governorate,
                    COUNT(*) as incident_count,
                    AVG(lat) as avg_lat,
                    AVG(lon) as avg_lon
                FROM incidents_clean
                WHERE day = %s
                AND timestamp > NOW() - INTERVAL '90 days'
                GROUP BY zone, governorate
                HAVING COUNT(*) > 3
                ORDER BY incident_count DESC
                LIMIT 20
            """
            
            df = pd.read_sql(query, conn, params=(day_name,))
            
            if df.empty:
                logger.warning("No historical data for prediction")
                return []
            
            # Get recent hotspots from zones_hotspots
            cur = conn.cursor()
            cur.execute("""
                SELECT zone, score, predicted
                FROM zones_hotspots
                WHERE predicted = true
                ORDER BY created_at DESC
                LIMIT 10
            """)
            
            forecast_zones = {row[0]: row[1] for row in cur.fetchall()}
            
            # Combine historical and forecast data
            predictions = []
            for _, row in df.iterrows():
                zone = row['zone']
                base_score = float(row['incident_count'])
                
                # Boost score if in forecast
                if zone in forecast_zones:
                    base_score *= 1.3
                
                predictions.append({
                    "zone": zone,
                    "governorate": row['governorate'],
                    "risk_score": round(base_score, 2),
                    "lat": float(row['avg_lat']),
                    "lon": float(row['avg_lon']),
                    "predicted_for": tomorrow.strftime('%Y-%m-%d'),
                    "day": day_name
                })
            
            # Sort by risk score
            predictions.sort(key=lambda x: x['risk_score'], reverse=True)
            
            logger.info(f"Predicted {len(predictions)} hotspots for {day_name}")
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to predict tomorrow's hotspots: {e}")
            return []
    
    def recommend_patrol_routes(self, num_teams: int = 5) -> List[Dict]:
        """
        Recommend patrol routes based on predicted hotspots
        
        Args:
            num_teams: Number of patrol teams available
            
        Returns:
            List of recommended routes for each team
        """
        try:
            hotspots = self.predict_tomorrows_hotspots()
            
            if not hotspots:
                return []
            
            # Distribute hotspots across teams
            routes = []
            hotspots_per_team = max(1, len(hotspots) // num_teams)
            
            for team_id in range(num_teams):
                start_idx = team_id * hotspots_per_team
                end_idx = start_idx + hotspots_per_team
                
                team_hotspots = hotspots[start_idx:end_idx]
                
                if not team_hotspots:
                    continue
                
                # Calculate route priority
                total_risk = sum(h['risk_score'] for h in team_hotspots)
                
                routes.append({
                    "team_id": f"Team-{chr(65 + team_id)}",  # Team-A, Team-B, etc.
                    "priority": "high" if total_risk > 50 else "medium" if total_risk > 25 else "low",
                    "total_risk_score": round(total_risk, 2),
                    "zones": team_hotspots,
                    "zone_count": len(team_hotspots),
                    "recommended_start_time": "08:00",
                    "estimated_duration_hours": len(team_hotspots) * 1.5
                })
            
            logger.info(f"Generated {len(routes)} patrol routes")
            return routes
            
        except Exception as e:
            logger.error(f"Failed to recommend patrol routes: {e}")
            return []
    
    def assign_teams_to_zones(self, available_teams: List[str]) -> List[Dict]:
        """
        Assign available teams to high-risk zones
        
        Args:
            available_teams: List of team identifiers
            
        Returns:
            List of team assignments
        """
        try:
            hotspots = self.predict_tomorrows_hotspots()
            
            if not hotspots or not available_teams:
                return []
            
            assignments = []
            
            # Assign teams to highest risk zones first
            for i, team in enumerate(available_teams):
                if i < len(hotspots):
                    zone = hotspots[i]
                    
                    assignments.append({
                        "team_id": team,
                        "zone": zone['zone'],
                        "governorate": zone['governorate'],
                        "risk_score": zone['risk_score'],
                        "lat": zone['lat'],
                        "lon": zone['lon'],
                        "assignment_time": datetime.now().isoformat(),
                        "status": "assigned"
                    })
            
            logger.info(f"Assigned {len(assignments)} teams to zones")
            return assignments
            
        except Exception as e:
            logger.error(f"Failed to assign teams: {e}")
            return []
    
    def detect_coverage_gaps(self) -> Dict:
        """
        Detect areas with insufficient patrol coverage
        
        Returns:
            Coverage analysis
        """
        try:
            conn = self._get_connection()
            
            # Get all governorates
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT governorate, COUNT(*) as incident_count
                FROM incidents_clean
                WHERE timestamp > NOW() - INTERVAL '30 days'
                GROUP BY governorate
                ORDER BY incident_count DESC
            """)
            
            governorate_incidents = cur.fetchall()
            
            # Check assigned tasks
            cur.execute("""
                SELECT zone, COUNT(*) as task_count
                FROM assigned_tasks
                WHERE status IN ('pending', 'on_route')
                GROUP BY zone
            """)
            
            assigned_zones = {row[0]: row[1] for row in cur.fetchall()}
            
            # Identify gaps
            gaps = []
            for gov, count in governorate_incidents:
                # High incident count but no assignments
                if count > 10 and gov not in assigned_zones:
                    gaps.append({
                        "governorate": gov,
                        "incident_count": count,
                        "assigned_teams": 0,
                        "severity": "high" if count > 20 else "medium"
                    })
            
            return {
                "gaps_detected": len(gaps),
                "coverage_gaps": gaps,
                "recommendation": "Increase patrol presence in identified areas"
            }
            
        except Exception as e:
            logger.error(f"Failed to detect coverage gaps: {e}")
            return {}
    
    def detect_team_overwork(self, team_id: str, days: int = 7) -> Dict:
        """
        Detect if a team is overworked
        
        Args:
            team_id: Team identifier
            days: Number of days to analyze
            
        Returns:
            Overwork analysis
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            # Count tasks assigned to team in last N days
            cur.execute("""
                SELECT COUNT(*) as task_count
                FROM assigned_tasks
                WHERE assigned_to = %s
                AND created_at > NOW() - INTERVAL '%s days'
            """, (team_id, days))
            
            task_count = cur.fetchone()[0]
            
            # Threshold: more than 2 tasks per day = overworked
            threshold = days * 2
            overworked = task_count > threshold
            
            return {
                "team_id": team_id,
                "task_count": task_count,
                "days_analyzed": days,
                "threshold": threshold,
                "overworked": overworked,
                "recommendation": "Reduce workload" if overworked else "Normal workload"
            }
            
        except Exception as e:
            logger.error(f"Failed to detect team overwork: {e}")
            return {}
    
    def optimize_resource_distribution(self) -> Dict:
        """
        Optimize patrol resource distribution across governorates
        
        Returns:
            Optimization recommendations
        """
        try:
            conn = self._get_connection()
            
            # Get incident distribution by governorate
            query = """
                SELECT 
                    governorate,
                    COUNT(*) as incident_count,
                    COUNT(DISTINCT zone) as zone_count
                FROM incidents_clean
                WHERE timestamp > NOW() - INTERVAL '30 days'
                GROUP BY governorate
                ORDER BY incident_count DESC
            """
            
            df = pd.read_sql(query, conn)
            
            if df.empty:
                return {}
            
            # Calculate recommended team allocation
            total_incidents = df['incident_count'].sum()
            
            recommendations = []
            for _, row in df.iterrows():
                gov = row['governorate']
                incidents = row['incident_count']
                zones = row['zone_count']
                
                # Allocate teams proportional to incidents
                percentage = (incidents / total_incidents) * 100
                recommended_teams = max(1, int(percentage / 10))  # 1 team per 10%
                
                recommendations.append({
                    "governorate": gov,
                    "incident_count": int(incidents),
                    "zone_count": int(zones),
                    "incident_percentage": round(percentage, 2),
                    "recommended_teams": recommended_teams,
                    "priority": "high" if percentage > 30 else "medium" if percentage > 15 else "low"
                })
            
            return {
                "total_incidents": int(total_incidents),
                "governorate_count": len(recommendations),
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize resource distribution: {e}")
            return {}
    
    def generate_patrol_report(self) -> Dict:
        """
        Generate comprehensive patrol allocation report
        
        Returns:
            Complete patrol report
        """
        try:
            report = {
                "generated_at": datetime.now().isoformat(),
                "predicted_hotspots": self.predict_tomorrows_hotspots()[:10],
                "recommended_routes": self.recommend_patrol_routes(num_teams=5),
                "coverage_gaps": self.detect_coverage_gaps(),
                "resource_optimization": self.optimize_resource_distribution()
            }
            
            logger.info("Generated patrol allocation report")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate patrol report: {e}")
            return {}


if __name__ == "__main__":
    engine = PatrolAllocationEngine()
    report = engine.generate_patrol_report()
    print("Patrol Allocation Report:")
    print(f"Predicted Hotspots: {len(report.get('predicted_hotspots', []))}")
    print(f"Recommended Routes: {len(report.get('recommended_routes', []))}")
