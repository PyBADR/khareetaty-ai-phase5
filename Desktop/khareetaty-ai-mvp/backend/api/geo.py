from fastapi import APIRouter, HTTPException
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.geo_lookup import GeoLookupService

router = APIRouter()

# Initialize geo service
try:
    geo_service = GeoLookupService()
except Exception as e:
    print(f"Warning: Could not initialize GeoLookupService: {e}")
    geo_service = None

@router.get("/options")
def get_geo_options():
    """
    Get all available geographic options for filters
    
    Returns:
        - governorates: List of governorates with codes and names
        - districts: List of districts with codes, names, and governorate
        - police_zones: List of police zones with codes and names
        - blocks: List of blocks with codes and names
    """
    if not geo_service:
        raise HTTPException(status_code=503, detail="Geographic service not available")
    
    try:
        # Use the get_all_zones method from GeoLookupService
        governorates = geo_service.get_all_zones('governorate')
        districts = geo_service.get_all_zones('district')
        police_zones = geo_service.get_all_zones('police_zone')
        blocks = geo_service.get_all_zones('block')
        
        return {
            "status": "success",
            "data": {
                "governorates": governorates,
                "districts": districts,
                "police_zones": police_zones,
                "blocks": blocks
            },
            "counts": {
                "governorates": len(governorates),
                "districts": len(districts),
                "police_zones": len(police_zones),
                "blocks": len(blocks)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve geographic options: {str(e)}")

@router.get("/governorates")
def get_governorates():
    """Get list of all governorates"""
    if not geo_service:
        raise HTTPException(status_code=503, detail="Geographic service not available")
    
    try:
        governorates = geo_service.get_all_zones('governorate')
        return {"status": "success", "data": governorates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/districts")
def get_districts(governorate_code: str = None):
    """Get list of districts, optionally filtered by governorate"""
    if not geo_service:
        raise HTTPException(status_code=503, detail="Geographic service not available")
    
    try:
        all_districts = geo_service.get_all_zones('district')
        
        # Filter by governorate if specified
        if governorate_code:
            districts = []
            for feature in geo_service.districts['features']:
                props = feature['properties']
                if props.get('governorate_code') == governorate_code:
                    districts.append({
                        'code': props.get('code'),
                        'name_en': props.get('name_en'),
                        'name_ar': props.get('name_ar'),
                        'governorate_code': props.get('governorate_code')
                    })
        else:
            districts = all_districts
        
        return {"status": "success", "data": districts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/police-zones")
def get_police_zones(governorate_code: str = None):
    """Get list of police zones, optionally filtered by governorate"""
    if not geo_service:
        raise HTTPException(status_code=503, detail="Geographic service not available")
    
    try:
        all_zones = geo_service.get_all_zones('police_zone')
        
        # Filter by governorate if specified
        if governorate_code:
            zones = []
            for feature in geo_service.police_zones['features']:
                props = feature['properties']
                if props.get('governorate_code') == governorate_code:
                    zones.append({
                        'code': props.get('code'),
                        'name_en': props.get('name_en'),
                        'name_ar': props.get('name_ar'),
                        'governorate_code': props.get('governorate_code')
                    })
        else:
            zones = all_zones
        
        return {"status": "success", "data": zones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blocks")
def get_blocks(district_code: str = None):
    """Get list of blocks, optionally filtered by district"""
    if not geo_service:
        raise HTTPException(status_code=503, detail="Geographic service not available")
    
    try:
        all_blocks = geo_service.get_all_zones('block')
        
        # Filter by district if specified
        if district_code:
            blocks = []
            for feature in geo_service.blocks['features']:
                props = feature['properties']
                if props.get('district_code') == district_code:
                    blocks.append({
                        'code': props.get('code'),
                        'name_en': props.get('name_en'),
                        'name_ar': props.get('name_ar'),
                        'district_code': props.get('district_code')
                    })
        else:
            blocks = all_blocks
        
        return {"status": "success", "data": blocks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resolve")
def resolve_coordinates(lat: float, lon: float):
    """
    Resolve geographic coordinates to zone information
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Zone information including governorate, district, block, police_zone
    """
    if not geo_service:
        raise HTTPException(status_code=503, detail="Geographic service not available")
    
    try:
        result = geo_service.resolve_zone(lat, lon)
        if result:
            return {
                "status": "success",
                "data": result
            }
        else:
            return {
                "status": "not_found",
                "message": "Coordinates do not match any known zone",
                "data": None
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve coordinates: {str(e)}")

@router.get("/geojson/{layer}")
def get_geojson_layer(layer: str):
    """
    Get GeoJSON data for a specific layer
    
    Args:
        layer: One of 'governorates', 'districts', 'blocks', 'police_zones'
    
    Returns:
        GeoJSON FeatureCollection
    """
    valid_layers = ['governorates', 'districts', 'blocks', 'police_zones']
    if layer not in valid_layers:
        raise HTTPException(status_code=400, detail=f"Invalid layer. Must be one of: {', '.join(valid_layers)}")
    
    try:
        # Construct path to GeoJSON file
        base_path = os.path.join(os.path.dirname(__file__), '../../data/geo/kuwait')
        geojson_path = os.path.join(base_path, f"{layer}.geojson")
        
        if not os.path.exists(geojson_path):
            raise HTTPException(status_code=404, detail=f"GeoJSON file not found for layer: {layer}")
        
        with open(geojson_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        return {
            "status": "success",
            "layer": layer,
            "data": geojson_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load GeoJSON: {str(e)}")
