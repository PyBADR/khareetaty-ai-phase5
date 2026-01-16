#!/usr/bin/env python3
"""
Load GeoJSON data into PostgreSQL database tables
"""
import json
import psycopg2
import os
from pathlib import Path

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'khareetaty_ai'),
    'user': os.getenv('DB_USER', 'bdr.ai'),
    'password': os.getenv('DB_PASSWORD', 'secret123')
}

GEO_DATA_DIR = Path(__file__).parent / 'data' / 'geo' / 'kuwait'

def load_geojson(filepath):
    """Load and parse a GeoJSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_governorates(conn):
    """Load governorates into geo_governorates table"""
    print("Loading governorates...")
    data = load_geojson(GEO_DATA_DIR / 'governorates.geojson')
    
    with conn.cursor() as cur:
        for feature in data['features']:
            props = feature['properties']
            geom = json.dumps(feature['geometry'])
            
            cur.execute("""
                INSERT INTO geo_governorates (code, name_en, name_ar, geom)
                VALUES (%s, %s, %s, ST_GeomFromGeoJSON(%s))
                ON CONFLICT (code) DO UPDATE SET
                    name_en = EXCLUDED.name_en,
                    name_ar = EXCLUDED.name_ar,
                    geom = EXCLUDED.geom
            """, (props['code'], props['name_en'], props['name_ar'], geom))
    
    conn.commit()
    print(f"✓ Loaded {len(data['features'])} governorates")

def load_districts(conn):
    """Load districts into geo_districts table"""
    print("Loading districts...")
    data = load_geojson(GEO_DATA_DIR / 'districts.geojson')
    
    with conn.cursor() as cur:
        for feature in data['features']:
            props = feature['properties']
            geom = json.dumps(feature['geometry'])
            
            cur.execute("""
                INSERT INTO geo_districts (code, name_en, name_ar, governorate_code, geom)
                VALUES (%s, %s, %s, %s, ST_GeomFromGeoJSON(%s))
                ON CONFLICT (code) DO UPDATE SET
                    name_en = EXCLUDED.name_en,
                    name_ar = EXCLUDED.name_ar,
                    governorate_code = EXCLUDED.governorate_code,
                    geom = EXCLUDED.geom
            """, (props['code'], props['name_en'], props['name_ar'], props['governorate_code'], geom))
    
    conn.commit()
    print(f"✓ Loaded {len(data['features'])} districts")

def load_blocks(conn):
    """Load blocks into geo_blocks table"""
    print("Loading blocks...")
    data = load_geojson(GEO_DATA_DIR / 'blocks.geojson')
    
    with conn.cursor() as cur:
        for feature in data['features']:
            props = feature['properties']
            geom = json.dumps(feature['geometry'])
            
            cur.execute("""
                INSERT INTO geo_blocks (code, name_en, name_ar, district_code, block_number, geom)
                VALUES (%s, %s, %s, %s, %s, ST_GeomFromGeoJSON(%s))
                ON CONFLICT (code) DO UPDATE SET
                    name_en = EXCLUDED.name_en,
                    name_ar = EXCLUDED.name_ar,
                    district_code = EXCLUDED.district_code,
                    block_number = EXCLUDED.block_number,
                    geom = EXCLUDED.geom
            """, (props['code'], props['name_en'], props['name_ar'], props['district_code'], props.get('block_number', ''), geom))
    
    conn.commit()
    print(f"✓ Loaded {len(data['features'])} blocks")

def load_police_zones(conn):
    """Load police zones into geo_police_zones table"""
    print("Loading police zones...")
    data = load_geojson(GEO_DATA_DIR / 'police_zones.geojson')
    
    with conn.cursor() as cur:
        for feature in data['features']:
            props = feature['properties']
            geom = json.dumps(feature['geometry'])
            districts_list = props.get('districts', [])
            
            cur.execute("""
                INSERT INTO geo_police_zones (code, name_en, name_ar, districts, headquarters, phone, geom)
                VALUES (%s, %s, %s, %s, %s, %s, ST_GeomFromGeoJSON(%s))
                ON CONFLICT (code) DO UPDATE SET
                    name_en = EXCLUDED.name_en,
                    name_ar = EXCLUDED.name_ar,
                    districts = EXCLUDED.districts,
                    headquarters = EXCLUDED.headquarters,
                    phone = EXCLUDED.phone,
                    geom = EXCLUDED.geom
            """, (props['code'], props['name_en'], props['name_ar'], districts_list, 
                  props.get('headquarters', ''), props.get('phone', ''), geom))
    
    conn.commit()
    print(f"✓ Loaded {len(data['features'])} police zones")

def verify_data(conn):
    """Verify data was loaded correctly"""
    print("\nVerifying loaded data...")
    
    with conn.cursor() as cur:
        tables = ['geo_governorates', 'geo_districts', 'geo_blocks', 'geo_police_zones']
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"  {table}: {count} records")

def main():
    """Main execution"""
    print("=" * 60)
    print("Loading GeoJSON data into PostgreSQL")
    print("=" * 60)
    
    try:
        # Connect to database
        print(f"\nConnecting to database: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ Connected successfully")
        
        # Load data
        load_governorates(conn)
        load_districts(conn)
        load_blocks(conn)
        load_police_zones(conn)
        
        # Verify
        verify_data(conn)
        
        print("\n" + "=" * 60)
        print("✓ All geographic data loaded successfully!")
        print("=" * 60)
        
        conn.close()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
