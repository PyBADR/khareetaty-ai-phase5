-- Geographic Enhancement Migrations for Khareetaty-AI
-- Adds geographic reference tables and updates incidents_clean schema

-- ============================================
-- 1. GEOGRAPHIC REFERENCE TABLES
-- ============================================

-- Governorates reference table
CREATE TABLE IF NOT EXISTS geo_governorates (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name_en TEXT NOT NULL,
    name_ar TEXT NOT NULL,
    geom GEOMETRY(MultiPolygon, 4326),
    population INTEGER,
    area_km2 DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_geo_governorates_code ON geo_governorates(code);
CREATE INDEX IF NOT EXISTS idx_geo_governorates_geom ON geo_governorates USING GIST(geom);

COMMENT ON TABLE geo_governorates IS 'Kuwait governorate boundaries and metadata';

-- Districts reference table
CREATE TABLE IF NOT EXISTS geo_districts (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name_en TEXT NOT NULL,
    name_ar TEXT NOT NULL,
    governorate_code TEXT REFERENCES geo_governorates(code),
    geom GEOMETRY(MultiPolygon, 4326),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_geo_districts_code ON geo_districts(code);
CREATE INDEX IF NOT EXISTS idx_geo_districts_governorate ON geo_districts(governorate_code);
CREATE INDEX IF NOT EXISTS idx_geo_districts_geom ON geo_districts USING GIST(geom);

COMMENT ON TABLE geo_districts IS 'Kuwait district boundaries within governorates';

-- Blocks reference table (centroids)
CREATE TABLE IF NOT EXISTS geo_blocks (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name_en TEXT NOT NULL,
    name_ar TEXT NOT NULL,
    district_code TEXT REFERENCES geo_districts(code),
    block_number TEXT,
    geom GEOMETRY(Point, 4326),  -- Centroid point
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_geo_blocks_code ON geo_blocks(code);
CREATE INDEX IF NOT EXISTS idx_geo_blocks_district ON geo_blocks(district_code);
CREATE INDEX IF NOT EXISTS idx_geo_blocks_geom ON geo_blocks USING GIST(geom);

COMMENT ON TABLE geo_blocks IS 'Kuwait block centroids (point geometries)';

-- Police zones reference table
CREATE TABLE IF NOT EXISTS geo_police_zones (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name_en TEXT NOT NULL,
    name_ar TEXT NOT NULL,
    districts TEXT[],  -- Array of district codes
    headquarters TEXT,
    phone TEXT,
    geom GEOMETRY(MultiPolygon, 4326),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_geo_police_zones_code ON geo_police_zones(code);
CREATE INDEX IF NOT EXISTS idx_geo_police_zones_geom ON geo_police_zones USING GIST(geom);

COMMENT ON TABLE geo_police_zones IS 'Police jurisdiction areas in Kuwait';

-- ============================================
-- 2. GEO RESOLUTION LOG
-- ============================================

-- Log table for tracking geo resolution success/failures
CREATE TABLE IF NOT EXISTS geo_resolution_log (
    id SERIAL PRIMARY KEY,
    lat DECIMAL(10, 8),
    lon DECIMAL(11, 8),
    resolved BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_geo_resolution_log_resolved ON geo_resolution_log(resolved);
CREATE INDEX IF NOT EXISTS idx_geo_resolution_log_timestamp ON geo_resolution_log(timestamp);

COMMENT ON TABLE geo_resolution_log IS 'Tracks geographic resolution attempts and failures';

-- ============================================
-- 3. UPDATE INCIDENTS_CLEAN TABLE
-- ============================================

-- Add new geographic columns to incidents_clean
ALTER TABLE incidents_clean ADD COLUMN IF NOT EXISTS district TEXT;
ALTER TABLE incidents_clean ADD COLUMN IF NOT EXISTS block TEXT;
ALTER TABLE incidents_clean ADD COLUMN IF NOT EXISTS police_zone TEXT;

-- Create indexes on new columns
CREATE INDEX IF NOT EXISTS idx_incidents_clean_district ON incidents_clean(district);
CREATE INDEX IF NOT EXISTS idx_incidents_clean_block ON incidents_clean(block);
CREATE INDEX IF NOT EXISTS idx_incidents_clean_police_zone ON incidents_clean(police_zone);

-- Add comments
COMMENT ON COLUMN incidents_clean.district IS 'District name resolved from lat/lon';
COMMENT ON COLUMN incidents_clean.block IS 'Block number resolved from lat/lon';
COMMENT ON COLUMN incidents_clean.police_zone IS 'Police jurisdiction area';

-- ============================================
-- 4. UPDATE ZONES_HOTSPOTS TABLE
-- ============================================

-- Add zone_type column to distinguish between cluster IDs and real zones
ALTER TABLE zones_hotspots ADD COLUMN IF NOT EXISTS zone_type TEXT DEFAULT 'cluster';
ALTER TABLE zones_hotspots ADD COLUMN IF NOT EXISTS district TEXT;
ALTER TABLE zones_hotspots ADD COLUMN IF NOT EXISTS police_zone TEXT;
ALTER TABLE zones_hotspots ADD COLUMN IF NOT EXISTS forecast_count INTEGER;
ALTER TABLE zones_hotspots ADD COLUMN IF NOT EXISTS forecast_timestamp TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_zones_hotspots_zone_type ON zones_hotspots(zone_type);
CREATE INDEX IF NOT EXISTS idx_zones_hotspots_district ON zones_hotspots(district);

COMMENT ON COLUMN zones_hotspots.zone_type IS 'Type of zone: cluster, district, police_zone';
COMMENT ON COLUMN zones_hotspots.district IS 'District name for geographic hotspots';
COMMENT ON COLUMN zones_hotspots.police_zone IS 'Police zone for geographic hotspots';
COMMENT ON COLUMN zones_hotspots.forecast_count IS 'Predicted incident count for next 24h';

-- ============================================
-- 5. HELPER FUNCTIONS
-- ============================================

-- Function to get district from coordinates
CREATE OR REPLACE FUNCTION get_district_from_coords(p_lat DECIMAL, p_lon DECIMAL)
RETURNS TEXT AS $$
DECLARE
    v_district TEXT;
BEGIN
    SELECT name_en INTO v_district
    FROM geo_districts
    WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(p_lon, p_lat), 4326))
    LIMIT 1;
    
    RETURN v_district;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_district_from_coords IS 'Resolve lat/lon to district name using PostGIS';

-- Function to get police zone from district
CREATE OR REPLACE FUNCTION get_police_zone_from_district(p_district_code TEXT)
RETURNS TEXT AS $$
DECLARE
    v_police_zone TEXT;
BEGIN
    SELECT name_en INTO v_police_zone
    FROM geo_police_zones
    WHERE p_district_code = ANY(districts)
    LIMIT 1;
    
    RETURN v_police_zone;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_police_zone_from_district IS 'Map district code to police zone';

-- ============================================
-- 6. VIEWS FOR ANALYTICS
-- ============================================

-- View: Incidents with full geographic context
CREATE OR REPLACE VIEW incidents_geo_view AS
SELECT 
    ic.id,
    ic.incident_type,
    ic.governorate,
    ic.district,
    ic.block,
    ic.police_zone,
    ic.lat,
    ic.lon,
    ic.timestamp,
    ic.hour,
    ic.day,
    ic.week,
    gd.name_ar as district_ar,
    gg.name_ar as governorate_ar,
    gpz.headquarters as police_headquarters
FROM incidents_clean ic
LEFT JOIN geo_districts gd ON ic.district = gd.name_en
LEFT JOIN geo_governorates gg ON ic.governorate = gg.name_en
LEFT JOIN geo_police_zones gpz ON ic.police_zone = gpz.name_en;

COMMENT ON VIEW incidents_geo_view IS 'Incidents with enriched geographic information';

-- View: District-level incident statistics
CREATE OR REPLACE VIEW district_stats_view AS
SELECT 
    district,
    governorate,
    police_zone,
    COUNT(*) as total_incidents,
    COUNT(DISTINCT incident_type) as incident_types,
    MIN(timestamp) as first_incident,
    MAX(timestamp) as last_incident,
    AVG(EXTRACT(HOUR FROM timestamp)) as avg_hour
FROM incidents_clean
WHERE district IS NOT NULL
GROUP BY district, governorate, police_zone;

COMMENT ON VIEW district_stats_view IS 'Aggregated statistics per district';

-- ============================================
-- 7. DATA QUALITY CHECKS
-- ============================================

-- View: Incidents without geographic resolution
CREATE OR REPLACE VIEW unresolved_incidents_view AS
SELECT 
    id,
    incident_type,
    lat,
    lon,
    timestamp,
    governorate
FROM incidents_clean
WHERE district IS NULL
ORDER BY timestamp DESC;

COMMENT ON VIEW unresolved_incidents_view IS 'Incidents that failed geographic resolution';

-- ============================================
-- 8. GRANT PERMISSIONS
-- ============================================

-- Grant read access to all geo tables (adjust user as needed)
-- GRANT SELECT ON geo_governorates, geo_districts, geo_blocks, geo_police_zones TO readonly_user;
-- GRANT SELECT, INSERT ON geo_resolution_log TO app_user;

-- ============================================
-- MIGRATION COMPLETE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE 'Geographic enhancement migrations completed successfully';
    RAISE NOTICE 'Tables created: geo_governorates, geo_districts, geo_blocks, geo_police_zones, geo_resolution_log';
    RAISE NOTICE 'incidents_clean updated with district, block, police_zone columns';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Load GeoJSON data into geo_* tables';
    RAISE NOTICE '  2. Run ETL pipeline to populate geographic fields';
    RAISE NOTICE '  3. Verify data with: SELECT * FROM district_stats_view;';
END $$;
