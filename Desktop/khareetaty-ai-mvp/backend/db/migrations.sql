-- Khareetaty AI Database Schema
-- PostgreSQL + PostGIS for crime analytics system

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================
-- 1. INCIDENTS TABLES
-- ============================================

-- Raw incidents table (initial data ingestion)
CREATE TABLE IF NOT EXISTS incidents_raw (
    id SERIAL PRIMARY KEY,
    incident_type TEXT NOT NULL,
    governorate TEXT,
    zone TEXT,
    lat DECIMAL(10, 8) NOT NULL,
    lon DECIMAL(11, 8) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_incidents_raw_timestamp ON incidents_raw(timestamp);
CREATE INDEX IF NOT EXISTS idx_incidents_raw_type ON incidents_raw(incident_type);
CREATE INDEX IF NOT EXISTS idx_incidents_raw_governorate ON incidents_raw(governorate);

-- Clean incidents table (processed data with derived fields)
CREATE TABLE IF NOT EXISTS incidents_clean (
    id SERIAL PRIMARY KEY,
    raw_incident_id INTEGER REFERENCES incidents_raw(id),
    incident_type TEXT NOT NULL,
    governorate TEXT,
    zone TEXT,
    lat DECIMAL(10, 8) NOT NULL,
    lon DECIMAL(11, 8) NOT NULL,
    geom GEOMETRY(Point, 4326),  -- PostGIS geometry column
    hour INTEGER,
    day TEXT,
    week INTEGER,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_incidents_clean_timestamp ON incidents_clean(timestamp);
CREATE INDEX IF NOT EXISTS idx_incidents_clean_type ON incidents_clean(incident_type);
CREATE INDEX IF NOT EXISTS idx_incidents_clean_governorate ON incidents_clean(governorate);
CREATE INDEX IF NOT EXISTS idx_incidents_clean_geom ON incidents_clean USING GIST(geom);

-- ============================================
-- 2. HOTSPOTS & PREDICTIONS
-- ============================================

-- Zones hotspots table (clustering results and forecasts)
CREATE TABLE IF NOT EXISTS zones_hotspots (
    id SERIAL PRIMARY KEY,
    zone TEXT NOT NULL,
    score DECIMAL(10, 2) NOT NULL,
    predicted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(zone, predicted)
);

CREATE INDEX IF NOT EXISTS idx_zones_hotspots_score ON zones_hotspots(score DESC);
CREATE INDEX IF NOT EXISTS idx_zones_hotspots_predicted ON zones_hotspots(predicted);

-- ============================================
-- 3. USER MANAGEMENT & AUTHENTICATION
-- ============================================

-- System users table
CREATE TABLE IF NOT EXISTS system_users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,  -- Bcrypt hashed password
    phone TEXT,
    role TEXT CHECK (role IN ('superadmin', 'analyst', 'viewer')) DEFAULT 'viewer',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_system_users_email ON system_users(email);
CREATE INDEX IF NOT EXISTS idx_system_users_role ON system_users(role);

-- ============================================
-- 4. ALERTS & NOTIFICATIONS
-- ============================================

-- Alerts log table
CREATE TABLE IF NOT EXISTS alerts_log (
    id SERIAL PRIMARY KEY,
    alert_type TEXT NOT NULL,
    severity TEXT CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')) DEFAULT 'MEDIUM',
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT NOW(),
    recipients TEXT,
    status TEXT DEFAULT 'sent'
);

CREATE INDEX IF NOT EXISTS idx_alerts_log_sent_at ON alerts_log(sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_log_severity ON alerts_log(severity);

-- ============================================
-- 5. ANALYTICS SUMMARY
-- ============================================

-- Analytics summary table (for dashboard)
CREATE TABLE IF NOT EXISTS analytics_summary (
    id SERIAL PRIMARY KEY,
    metric_name TEXT NOT NULL,
    metric_value DECIMAL(15, 2),
    governorate TEXT,
    incident_type TEXT,
    time_period TEXT,
    calculated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analytics_summary_metric ON analytics_summary(metric_name);
CREATE INDEX IF NOT EXISTS idx_analytics_summary_calculated ON analytics_summary(calculated_at DESC);

-- ============================================
-- 6. SEED DATA
-- ============================================

-- Insert default superadmin user
INSERT INTO system_users (name, email, phone, role)
VALUES ('Bader', 'bader.naser.ai.sa@gmail.com', '+96566338736', 'superadmin')
ON CONFLICT (email) DO NOTHING;

-- Insert sample analyst user
INSERT INTO system_users (name, email, phone, role)
VALUES ('Analyst User', 'analyst@khareetaty.ai', '+96512345678', 'analyst')
ON CONFLICT (email) DO NOTHING;

-- Insert sample viewer user
INSERT INTO system_users (name, email, phone, role)
VALUES ('Viewer User', 'viewer@khareetaty.ai', '+96587654321', 'viewer')
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- 7. FUNCTIONS & TRIGGERS
-- ============================================

-- Function to update geom column from lat/lon
CREATE OR REPLACE FUNCTION update_geom_from_coords()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geom = ST_SetSRID(ST_MakePoint(NEW.lon, NEW.lat), 4326);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update geom on insert/update
DROP TRIGGER IF EXISTS trigger_update_geom ON incidents_clean;
CREATE TRIGGER trigger_update_geom
    BEFORE INSERT OR UPDATE ON incidents_clean
    FOR EACH ROW
    EXECUTE FUNCTION update_geom_from_coords();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for system_users updated_at
DROP TRIGGER IF EXISTS trigger_update_users_timestamp ON system_users;
CREATE TRIGGER trigger_update_users_timestamp
    BEFORE UPDATE ON system_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
