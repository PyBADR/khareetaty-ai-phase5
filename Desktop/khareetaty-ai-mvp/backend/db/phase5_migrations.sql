-- Khareetaty AI - Phase 5 Database Migrations
-- Extending tables for operational intelligence

-- ============================================
-- 1. EXTEND INCIDENTS_CLEAN TABLE
-- ============================================

-- Add missing geographic columns
ALTER TABLE incidents_clean 
ADD COLUMN IF NOT EXISTS district TEXT,
ADD COLUMN IF NOT EXISTS block TEXT,
ADD COLUMN IF NOT EXISTS police_zone TEXT;

-- Create indexes for new columns
CREATE INDEX IF NOT EXISTS idx_incidents_clean_district ON incidents_clean(district);
CREATE INDEX IF NOT EXISTS idx_incidents_clean_block ON incidents_clean(block);
CREATE INDEX IF NOT EXISTS idx_incidents_clean_police_zone ON incidents_clean(police_zone);

-- ============================================
-- 2. UPDATE ZONES_HOTSPOTS TABLE
-- ============================================

-- Drop existing table and recreate with proper structure
DROP TABLE IF EXISTS zones_hotspots CASCADE;

CREATE TABLE zones_hotspots (
    id SERIAL PRIMARY KEY,
    zone TEXT NOT NULL,
    governorate TEXT,
    district TEXT,
    police_zone TEXT,
    score DECIMAL(10, 2) NOT NULL,
    forecast DECIMAL(10, 2) DEFAULT 0.00,
    last_seen TIMESTAMP DEFAULT NOW(),
    zone_type TEXT CHECK (zone_type IN ('district', 'governorate', 'police_zone', 'block')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(zone, zone_type, created_at)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_zones_hotspots_zone ON zones_hotspots(zone);
CREATE INDEX IF NOT EXISTS idx_zones_hotspots_score ON zones_hotspots(score DESC);
CREATE INDEX IF NOT EXISTS idx_zones_hotspots_last_seen ON zones_hotspots(last_seen DESC);
CREATE INDEX IF NOT EXISTS idx_zones_hotspots_zone_type ON zones_hotspots(zone_type);

-- ============================================
-- 3. CREATE GEO_RESOLUTION_LOG TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS geo_resolution_log (
    id SERIAL PRIMARY KEY,
    lat DECIMAL(10, 8) NOT NULL,
    lon DECIMAL(11, 8) NOT NULL,
    governorate TEXT,
    district TEXT,
    block TEXT,
    police_zone TEXT,
    resolution_method TEXT CHECK (resolution_method IN ('manual', 'auto', 'api')),
    confidence_level DECIMAL(3, 2) DEFAULT 1.00,
    resolved_at TIMESTAMP DEFAULT NOW(),
    processing_time_ms INTEGER
);

CREATE INDEX IF NOT EXISTS idx_geo_resolution_lat_lon ON geo_resolution_log(lat, lon);
CREATE INDEX IF NOT EXISTS idx_geo_resolution_resolved_at ON geo_resolution_log(resolved_at DESC);

-- ============================================
-- 4. CREATE CONTACTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    role TEXT CHECK (role IN ('analyst', 'officer', 'commander', 'admin')),
    zone TEXT,
    governorate TEXT,
    district TEXT,
    police_zone TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
CREATE INDEX IF NOT EXISTS idx_contacts_zone ON contacts(zone);
CREATE INDEX IF NOT EXISTS idx_contacts_active ON contacts(active);

-- Seed default contacts
INSERT INTO contacts (name, phone, email, role, zone, governorate)
VALUES 
    ('Bader Naser', '+96566338736', 'bader.naser.ai.sa@gmail.com', 'admin', 'Capital', 'Al Asimah'),
    ('MOI Command Center', '+9651818181', 'command@moi.gov.kw', 'commander', 'Capital', 'Al Asimah')
ON CONFLICT (phone) DO NOTHING;

-- ============================================
-- 5. CREATE ANALYTICS_SUMMARY TABLE (Extended)
-- ============================================

DROP TABLE IF EXISTS analytics_summary CASCADE;

CREATE TABLE analytics_summary (
    id SERIAL PRIMARY KEY,
    metric_name TEXT NOT NULL,
    metric_value DECIMAL(15, 2),
    metric_category TEXT CHECK (metric_category IN ('incidents', 'hotspots', 'forecasts', 'alerts', 'performance')),
    governorate TEXT,
    district TEXT,
    police_zone TEXT,
    zone_type TEXT,
    time_period TEXT,
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    calculated_at TIMESTAMP DEFAULT NOW(),
    calculation_duration_ms INTEGER
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_analytics_summary_metric_name ON analytics_summary(metric_name);
CREATE INDEX IF NOT EXISTS idx_analytics_summary_calculated_at ON analytics_summary(calculated_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_summary_zone_type ON analytics_summary(zone_type);

-- ============================================
-- 6. CREATE ALERTS_LOG TABLE (Extended)
-- ============================================

DROP TABLE IF EXISTS alerts_log CASCADE;

CREATE TABLE alerts_log (
    id SERIAL PRIMARY KEY,
    alert_type TEXT NOT NULL CHECK (alert_type IN ('hotspot', 'forecast', 'manual', 'system')),
    severity TEXT CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')) DEFAULT 'MEDIUM',
    zone TEXT,
    governorate TEXT,
    district TEXT,
    police_zone TEXT,
    message TEXT NOT NULL,
    phone TEXT,
    status TEXT CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'acknowledged')) DEFAULT 'pending',
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    acknowledged_at TIMESTAMP,
    failure_reason TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_alerts_log_created_at ON alerts_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_log_status ON alerts_log(status);
CREATE INDEX IF NOT EXISTS idx_alerts_log_alert_type ON alerts_log(alert_type);
CREATE INDEX IF NOT EXISTS idx_alerts_log_zone ON alerts_log(zone);

-- ============================================
-- 7. CREATE TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for tables with updated_at
DROP TRIGGER IF EXISTS trigger_update_contacts_timestamp ON contacts;
CREATE TRIGGER trigger_update_contacts_timestamp
    BEFORE UPDATE ON contacts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trigger_update_alerts_timestamp ON alerts_log;
CREATE TRIGGER trigger_update_alerts_timestamp
    BEFORE UPDATE ON alerts_log
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 8. CREATE VIEWS FOR DASHBOARD QUERIES
-- ============================================

-- Current hotspots view
CREATE OR REPLACE VIEW current_hotspots AS
SELECT 
    zone,
    governorate,
    district,
    police_zone,
    score,
    forecast,
    last_seen,
    zone_type,
    EXTRACT(EPOCH FROM (NOW() - last_seen))/3600 as hours_since_last_seen
FROM zones_hotspots
WHERE last_seen >= NOW() - INTERVAL '24 hours'
ORDER BY score DESC;

-- Daily analytics summary view
CREATE OR REPLACE VIEW daily_analytics AS
SELECT 
    metric_name,
    metric_category,
    AVG(metric_value) as avg_value,
    MAX(metric_value) as max_value,
    MIN(metric_value) as min_value,
    COUNT(*) as data_points,
    DATE(calculated_at) as calculation_date
FROM analytics_summary
WHERE calculated_at >= NOW() - INTERVAL '7 days'
GROUP BY metric_name, metric_category, DATE(calculated_at)
ORDER BY calculation_date DESC, metric_name;

-- Alert effectiveness view
CREATE OR REPLACE VIEW alert_effectiveness AS
SELECT 
    alert_type,
    severity,
    COUNT(*) as total_sent,
    COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
    ROUND(
        COUNT(CASE WHEN status = 'delivered' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(*), 0), 2
    ) as delivery_rate_percent
FROM alerts_log
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY alert_type, severity
ORDER BY delivery_rate_percent DESC;

-- ============================================
-- 9. INSERT SAMPLE DATA FOR TESTING
-- ============================================

-- Sample analytics data
INSERT INTO analytics_summary (
    metric_name, metric_value, metric_category, 
    governorate, zone_type, time_period, 
    period_start, period_end
) VALUES
    ('total_incidents', 1247, 'incidents', 'Al Asimah', 'governorate', 'daily', 
     NOW() - INTERVAL '1 day', NOW()),
    ('active_hotspots', 23, 'hotspots', 'Al Asimah', 'governorate', 'daily',
     NOW() - INTERVAL '1 day', NOW()),
    ('forecast_accuracy', 87.5, 'forecasts', 'Al Asimah', 'governorate', 'daily',
     NOW() - INTERVAL '1 day', NOW())
ON CONFLICT DO NOTHING;

-- Sample alerts data
INSERT INTO alerts_log (
    alert_type, severity, zone, governorate, district,
    message, phone, status, sent_at
) VALUES
    ('hotspot', 'HIGH', 'Salmiya', 'Hawalli', 'Salmiya',
     '🚨 Hotspot Detected\nZone: Salmiya\nScore: 45.2\nGovernorate: Hawalli', 
     'whatsapp:+96566338736', 'sent', NOW() - INTERVAL '2 hours'),
    ('forecast', 'MEDIUM', 'Jaber Al Ahmad', 'Al Farwaniyah', 'Jaber Al Ahmad',
     '📈 Forecast Alert\nZone: Jaber Al Ahmad\nPredicted increase: 15%\nNext 24h forecast: 32 incidents',
     'whatsapp:+96566338736', 'sent', NOW() - INTERVAL '4 hours')
ON CONFLICT DO NOTHING;

-- ============================================
-- 10. GRANT PERMISSIONS
-- ============================================

-- Grant necessary permissions (adjust as needed for your setup)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO bdr.ai;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO bdr.ai;

-- Refresh materialized views if any
REFRESH MATERIALIZED VIEW IF EXISTS current_hotspots;
REFRESH MATERIALIZED VIEW IF EXISTS daily_analytics;
REFRESH MATERIALIZED VIEW IF EXISTS alert_effectiveness;
