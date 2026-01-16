"""
Geographic Lookup Service for Khareetaty-AI
Resolves lat/lon coordinates to Kuwait administrative zones
"""

import json
import os
from typing import Dict, Optional, List, Tuple
from functools import lru_cache
import logging

try:
    from shapely.geometry import Point, shape
    from shapely.prepared import prep
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False
    logging.warning("Shapely not available. Install with: pip install shapely>=2.0.0")

logger = logging.getLogger(__name__)

# Path to geo data
GEO_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'data', 'geo', 'kuwait'
)


class GeoLookupService:
    """
    Service for resolving coordinates to geographic zones in Kuwait
    """
    
    def __init__(self, data_path: str = GEO_DATA_PATH):
        self.data_path = data_path
        self.governorates = None
        self.districts = None
        self.blocks = None
        self.police_zones = None
        self.index = None
        self.prepared_geometries = {}
        
        # Load data on initialization
        self._load_geo_data()
    
    def _load_geo_data(self):
        """Load all GeoJSON files and index"""
        try:
            # Load index
            index_path = os.path.join(self.data_path, 'index.json')
            with open(index_path, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
            
            # Load governorates
            gov_path = os.path.join(self.data_path, 'governorates.geojson')
            with open(gov_path, 'r', encoding='utf-8') as f:
                self.governorates = json.load(f)
            
            # Load districts
            dist_path = os.path.join(self.data_path, 'districts.geojson')
            with open(dist_path, 'r', encoding='utf-8') as f:
                self.districts = json.load(f)
            
            # Load blocks
            blocks_path = os.path.join(self.data_path, 'blocks.geojson')
            with open(blocks_path, 'r', encoding='utf-8') as f:
                self.blocks = json.load(f)
            
            # Load police zones
            pz_path = os.path.join(self.data_path, 'police_zones.geojson')
            with open(pz_path, 'r', encoding='utf-8') as f:
                self.police_zones = json.load(f)
            
            # Prepare geometries for faster lookup if Shapely available
            if SHAPELY_AVAILABLE:
                self._prepare_geometries()
            
            logger.info(f"Loaded geo data from {self.data_path}")
            logger.info(f"Governorates: {len(self.governorates['features'])}")
            logger.info(f"Districts: {len(self.districts['features'])}")
            logger.info(f"Blocks: {len(self.blocks['features'])}")
            logger.info(f"Police Zones: {len(self.police_zones['features'])}")
            
        except FileNotFoundError as e:
            logger.error(f"Geo data files not found: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in geo data files: {e}")
            raise
    
    def _prepare_geometries(self):
        """Prepare geometries for faster point-in-polygon queries"""
        if not SHAPELY_AVAILABLE:
            return
        
        self.prepared_geometries['governorates'] = []
        for feature in self.governorates['features']:
            geom = shape(feature['geometry'])
            self.prepared_geometries['governorates'].append({
                'geometry': prep(geom),
                'properties': feature['properties']
            })
        
        self.prepared_geometries['districts'] = []
        for feature in self.districts['features']:
            geom = shape(feature['geometry'])
            self.prepared_geometries['districts'].append({
                'geometry': prep(geom),
                'properties': feature['properties']
            })
        
        self.prepared_geometries['police_zones'] = []
        for feature in self.police_zones['features']:
            geom = shape(feature['geometry'])
            self.prepared_geometries['police_zones'].append({
                'geometry': prep(geom),
                'properties': feature['properties']
            })
        
        logger.info("Prepared geometries for fast lookup")
    
    def resolve_zone(self, lat: float, lon: float) -> Dict[str, Optional[str]]:
        """
        Resolve lat/lon to all administrative zones
        
        Args:
            lat: Latitude in WGS84
            lon: Longitude in WGS84
        
        Returns:
            Dictionary with governorate, district, block, police_zone
        """
        result = {
            'governorate': None,
            'governorate_code': None,
            'district': None,
            'district_code': None,
            'block': None,
            'block_code': None,
            'police_zone': None,
            'police_zone_code': None,
            'resolved': False
        }
        
        # Validate coordinates are in Kuwait bounds
        if not (46.5 <= lon <= 49.0 and 28.5 <= lat <= 30.5):
            logger.warning(f"Coordinates outside Kuwait bounds: lat={lat}, lon={lon}")
            return result
        
        if not SHAPELY_AVAILABLE:
            logger.warning("Shapely not available, using fallback method")
            return self._resolve_zone_fallback(lat, lon)
        
        try:
            point = Point(lon, lat)
            
            # Find governorate
            for item in self.prepared_geometries['governorates']:
                if item['geometry'].contains(point):
                    result['governorate'] = item['properties']['name_en']
                    result['governorate_code'] = item['properties']['code']
                    break
            
            # Find district
            for item in self.prepared_geometries['districts']:
                if item['geometry'].contains(point):
                    result['district'] = item['properties']['name_en']
                    result['district_code'] = item['properties']['code']
                    break
            
            # Find nearest block (using distance since blocks are points)
            min_distance = float('inf')
            nearest_block = None
            for feature in self.blocks['features']:
                block_point = Point(feature['geometry']['coordinates'])
                distance = point.distance(block_point)
                if distance < min_distance:
                    min_distance = distance
                    nearest_block = feature['properties']
            
            if nearest_block and min_distance < 0.05:  # ~5km threshold
                result['block'] = nearest_block.get('block_number')
                result['block_code'] = nearest_block.get('code')
            
            # Find police zone
            for item in self.prepared_geometries['police_zones']:
                if item['geometry'].contains(point):
                    result['police_zone'] = item['properties']['name_en']
                    result['police_zone_code'] = item['properties']['code']
                    break
            
            # Mark as resolved if at least district was found
            result['resolved'] = result['district'] is not None
            
        except Exception as e:
            logger.error(f"Error resolving zone for lat={lat}, lon={lon}: {e}")
        
        return result
    
    def _resolve_zone_fallback(self, lat: float, lon: float) -> Dict[str, Optional[str]]:
        """
        Fallback method when Shapely is not available
        Uses simple bounding box checks
        """
        result = {
            'governorate': None,
            'governorate_code': None,
            'district': None,
            'district_code': None,
            'block': None,
            'block_code': None,
            'police_zone': None,
            'police_zone_code': None,
            'resolved': False
        }
        
        # Simple bounding box check for districts
        for feature in self.districts['features']:
            coords = feature['geometry']['coordinates'][0]
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            
            if (min(lons) <= lon <= max(lons) and 
                min(lats) <= lat <= max(lats)):
                result['district'] = feature['properties']['name_en']
                result['district_code'] = feature['properties']['code']
                result['governorate'] = feature['properties'].get('governorate')
                result['governorate_code'] = feature['properties'].get('governorate_code')
                result['resolved'] = True
                break
        
        # Find police zone from district
        if result['district_code']:
            result['police_zone_code'] = self._district_to_police_zone(result['district_code'])
            if result['police_zone_code']:
                for feature in self.police_zones['features']:
                    if feature['properties']['code'] == result['police_zone_code']:
                        result['police_zone'] = feature['properties']['name_en']
                        break
        
        return result
    
    def to_governorate(self, zone: str) -> Optional[str]:
        """
        Map any zone identifier to its governorate
        
        Args:
            zone: District code, block code, or police zone code
        
        Returns:
            Governorate name or None
        """
        # Check if it's a district code
        for feature in self.districts['features']:
            if feature['properties']['code'] == zone:
                return feature['properties'].get('governorate')
        
        # Check if it's a block code
        for feature in self.blocks['features']:
            if feature['properties']['code'] == zone:
                district_code = feature['properties'].get('district_code')
                return self.to_governorate(district_code)
        
        # Check if it's a governorate code
        for feature in self.governorates['features']:
            if feature['properties']['code'] == zone:
                return feature['properties']['name_en']
        
        return None
    
    def to_police_area(self, zone: str) -> Optional[str]:
        """
        Map zone to police jurisdiction
        
        Args:
            zone: District code, governorate code, or zone name
        
        Returns:
            Police zone name or None
        """
        # Check if it's a district code
        district_code = zone
        
        # Find which police zone contains this district
        for feature in self.police_zones['features']:
            districts = feature['properties'].get('districts', [])
            if district_code in districts:
                return feature['properties']['name_en']
        
        # Try to find by governorate
        governorate = self.to_governorate(zone)
        if governorate:
            # Police zones typically align with governorates
            for feature in self.police_zones['features']:
                if governorate.lower() in feature['properties']['name_en'].lower():
                    return feature['properties']['name_en']
        
        return None
    
    def _district_to_police_zone(self, district_code: str) -> Optional[str]:
        """Helper to map district code to police zone code"""
        for feature in self.police_zones['features']:
            districts = feature['properties'].get('districts', [])
            if district_code in districts:
                return feature['properties']['code']
        return None
    
    def zone_stats(self, zone: str, zone_type: str = 'district') -> Dict:
        """
        Get statistics and metadata for a zone
        
        Args:
            zone: Zone code or name
            zone_type: 'governorate', 'district', 'block', or 'police_zone'
        
        Returns:
            Dictionary with zone information
        """
        result = {
            'zone': zone,
            'zone_type': zone_type,
            'found': False
        }
        
        # Select appropriate dataset
        if zone_type == 'governorate':
            features = self.governorates['features']
        elif zone_type == 'district':
            features = self.districts['features']
        elif zone_type == 'block':
            features = self.blocks['features']
        elif zone_type == 'police_zone':
            features = self.police_zones['features']
        else:
            return result
        
        # Find the zone
        for feature in features:
            props = feature['properties']
            if props.get('code') == zone or props.get('name_en') == zone:
                result['found'] = True
                result['code'] = props.get('code')
                result['name_en'] = props.get('name_en')
                result['name_ar'] = props.get('name_ar')
                result['properties'] = props
                
                # Add parent zone info
                if zone_type == 'district':
                    result['governorate'] = props.get('governorate')
                    result['governorate_code'] = props.get('governorate_code')
                elif zone_type == 'block':
                    result['district'] = props.get('district')
                    result['district_code'] = props.get('district_code')
                
                break
        
        return result
    
    def get_all_zones(self, zone_type: str = 'district') -> List[Dict]:
        """
        Get list of all zones of a specific type
        
        Args:
            zone_type: 'governorate', 'district', 'block', or 'police_zone'
        
        Returns:
            List of zone dictionaries
        """
        if zone_type == 'governorate':
            features = self.governorates['features']
        elif zone_type == 'district':
            features = self.districts['features']
        elif zone_type == 'block':
            features = self.blocks['features']
        elif zone_type == 'police_zone':
            features = self.police_zones['features']
        else:
            return []
        
        return [{
            'code': f['properties'].get('code'),
            'name_en': f['properties'].get('name_en'),
            'name_ar': f['properties'].get('name_ar')
        } for f in features]


# Singleton instance
_geo_service = None

def get_geo_service() -> GeoLookupService:
    """Get or create singleton GeoLookupService instance"""
    global _geo_service
    if _geo_service is None:
        _geo_service = GeoLookupService()
    return _geo_service


# Convenience functions
def resolve_zone(lat: float, lon: float) -> Dict[str, Optional[str]]:
    """Resolve coordinates to zones"""
    service = get_geo_service()
    return service.resolve_zone(lat, lon)


def to_governorate(zone: str) -> Optional[str]:
    """Map zone to governorate"""
    service = get_geo_service()
    return service.to_governorate(zone)


def to_police_area(zone: str) -> Optional[str]:
    """Map zone to police area"""
    service = get_geo_service()
    return service.to_police_area(zone)


def zone_stats(zone: str, zone_type: str = 'district') -> Dict:
    """Get zone statistics"""
    service = get_geo_service()
    return service.zone_stats(zone, zone_type)


if __name__ == "__main__":
    # Test the service
    import sys
    logging.basicConfig(level=logging.INFO)
    
    print("Testing GeoLookupService...")
    print("=" * 60)
    
    service = GeoLookupService()
    
    # Test coordinates in Kuwait City
    test_coords = [
        (29.3759, 47.9774, "Kuwait City"),
        (29.3375, 48.0758, "Salmiya"),
        (29.2769, 47.9583, "Farwaniya"),
    ]
    
    for lat, lon, expected in test_coords:
        print(f"\nTesting: {expected} (lat={lat}, lon={lon})")
        result = service.resolve_zone(lat, lon)
        print(f"  Governorate: {result['governorate']}")
        print(f"  District: {result['district']}")
        print(f"  Police Zone: {result['police_zone']}")
        print(f"  Resolved: {result['resolved']}")
    
    print("\n" + "=" * 60)
    print("All zones:")
    districts = service.get_all_zones('district')
    print(f"  Total districts: {len(districts)}")
    for d in districts[:5]:
        print(f"    - {d['name_en']} ({d['code']})")
