# Khareetaty-AI Geographic Awareness Gap Report
**Generated:** January 16, 2026
**Workflow:** Geo Upgrade Implementation

---

## EXECUTIVE SUMMARY

The current Khareetaty-AI system lacks true geographic awareness. While it uses governorate-level data and lat/lon coordinates, it cannot:
- Resolve coordinates to specific districts, blocks, or police zones
- Cluster incidents within meaningful geographic boundaries
- Provide zone-specific forecasts and alerts
- Display geographic polygons on the dashboard

This report identifies all gaps and provides a prioritized action plan.

---

## CRITICAL BLOCKERS (Must Fix)

### 1. **Missing Geographic Data Layer**
**Location:** `data/geo/kuwait/` (currently empty)
**Impact:** Cannot resolve lat/lon to administrative zones
**Required Files:**
- `governorates.geojson` - 6 Kuwait governorates with polygons
- `districts.geojson` - ~130 districts with polygons
- `blocks.geojson` - Block-level data (or centroid fallback)
- `police_zones.geojson` - Police jurisdiction areas
- `index.json` - Metadata and zone hierarchy

**Attributes Needed:**
- `name_en` - English name
- `name_ar` - Arabic name
- `code` - Unique identifier
- `parent_zone` - Hierarchical reference
- `geometry` - WGS84 polygon/point

---

### 2. **Missing Geo Lookup Service**
**Location:** `backend/services/geo_lookup.py` (does not exist)
**Impact:** No way to convert coordinates to zones
**Required Functions:**
```python
def resolve_zone(lat: float, lon: float) -> dict:
    """Returns {governorate, district, block, police_zone}"""
    
def to_governorate(zone: str) -> str:
    """Maps any zone to its governorate"""
    
def to_police_area(zone: str) -> str:
    """Maps zone to police jurisdiction"""
    
def zone_stats(zone: str) -> dict:
    """Returns incident statistics for a zone"""
```

**Dependencies:**
- Shapely for point-in-polygon operations
- GeoJSON loading utilities
- Caching for performance

---

### 3. **ETL Pipeline Missing Geo Resolution**
**Location:** `automation/etl_job.py`
**Current State:** Lines 34-37 define VALID_GOVERNORATES but no resolution logic
**Impact:** incidents_clean table lacks district/block/police_zone data

**Required Changes:**
```python
# After line 50, add:
from backend.services.geo_lookup import resolve_zone

# In clean_data() function, add:
for idx, row in df.iterrows():
    zone_info = resolve_zone(row['lat'], row['lon'])
    df.at[idx, 'district'] = zone_info.get('district')
    df.at[idx, 'block'] = zone_info.get('block')
    df.at[idx, 'police_zone'] = zone_info.get('police_zone')
    # Log failures to geo_resolution_log
```

---

### 4. **Database Schema Missing Geo Tables**
**Location:** `backend/db/migrations.sql`
**Current State:** Has incidents_raw, incidents_clean, zones_hotspots
**Impact:** No persistent storage for geographic boundaries

**Required Tables:**
```sql
-- Geographic reference tables
CREATE TABLE geo_governorates (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name_en TEXT NOT NULL,
    name_ar TEXT NOT NULL,
    geom GEOMETRY(MultiPolygon, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE geo_districts (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name_en TEXT NOT NULL,
    name_ar TEXT NOT NULL,
    governorate_code TEXT REFERENCES geo_governorates(code),
    geom GEOMETRY(MultiPolygon, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE geo_blocks (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name_en TEXT NOT NULL,
    name_ar TEXT NOT NULL,
    district_code TEXT REFERENCES geo_districts(code),
    geom GEOMETRY(Point, 4326),  -- Centroid if full polygon unavailable
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE geo_police_zones (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name_en TEXT NOT NULL,
    name_ar TEXT NOT NULL,
    districts TEXT[],  -- Array of district codes
    geom GEOMETRY(MultiPolygon, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE geo_resolution_log (
    id SERIAL PRIMARY KEY,
    lat DECIMAL(10, 8),
    lon DECIMAL(11, 8),
    resolved BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Modify incidents_clean
ALTER TABLE incidents_clean ADD COLUMN IF NOT EXISTS district TEXT;
ALTER TABLE incidents_clean ADD COLUMN IF NOT EXISTS block TEXT;
ALTER TABLE incidents_clean ADD COLUMN IF NOT EXISTS police_zone TEXT;

CREATE INDEX idx_incidents_clean_district ON incidents_clean(district);
CREATE INDEX idx_incidents_clean_police_zone ON incidents_clean(police_zone);
```

---

### 5. **Clustering Logic Not Zone-Aware**
**Location:** `services/clustering.py`
**Current State:** Line 27 queries all incidents, clusters globally
**Impact:** Hotspots don't respect administrative boundaries

**Required Changes:**
```python
# Replace global clustering with per-zone clustering
def compute_hotspots():
    conn = psycopg2.connect(**DB_CONN)
    
    # Get unique districts
    districts = pd.read_sql(
        "SELECT DISTINCT district FROM incidents_clean WHERE district IS NOT NULL",
        conn
    )['district'].tolist()
    
    cur = conn.cursor()
    
    for district in districts:
        # Cluster within each district
        df = pd.read_sql(
            """SELECT lat, lon, incident_type 
               FROM incidents_clean 
               WHERE district = %s 
               AND timestamp >= NOW() - INTERVAL '30 days'""",
            conn,
            params=(district,)
        )
        
        if len(df) < 5:
            continue
            
        coords = df[["lat","lon"]].values
        model = DBSCAN(eps=0.01, min_samples=3, metric='euclidean')
        labels = model.fit_predict(coords)
        
        # Store results per district
        cluster_counts = pd.Series(labels).value_counts()
        for cluster_id, count in cluster_counts.items():
            if cluster_id == -1:
                continue
            zone_key = f"{district}_cluster_{cluster_id}"
            cur.execute(
                """INSERT INTO zones_hotspots (zone, score, predicted)
                   VALUES (%s, %s, FALSE)
                   ON CONFLICT (zone, predicted) DO UPDATE
                   SET score = EXCLUDED.score""",
                (zone_key, float(count))
            )
    
    conn.commit()
    conn.close()
```

---

## PRIORITY FIXES (High Importance)

### 6. **Forecasting Not Zone-Specific**
**Location:** `services/modeling.py`
**Current State:** Has `predict_by_governorate()` but not per-district
**Impact:** Cannot provide 24h forecasts for specific zones

**Required Function:**
```python
def predict_by_zone(zone_type='district', forecast_hours=24):
    """
    Predict incident counts for next 24h per zone
    zone_type: 'district' or 'police_zone'
    """
    conn = psycopg2.connect(**DB_CONN)
    
    zones = pd.read_sql(
        f"SELECT DISTINCT {zone_type} FROM incidents_clean WHERE {zone_type} IS NOT NULL",
        conn
    )[zone_type].tolist()
    
    predictions = []
    for zone in zones:
        # Time series analysis per zone
        df = pd.read_sql(
            f"""SELECT timestamp, COUNT(*) as count
               FROM incidents_clean
               WHERE {zone_type} = %s
               AND timestamp >= NOW() - INTERVAL '90 days'
               GROUP BY DATE_TRUNC('hour', timestamp)
               ORDER BY timestamp""",
            conn,
            params=(zone,)
        )
        
        if len(df) < 24:
            continue
            
        # Simple moving average or ARIMA
        recent_avg = df.tail(24)['count'].mean()
        predicted_count = int(recent_avg * 1.1)  # 10% buffer
        
        predictions.append({
            'zone': zone,
            'zone_type': zone_type,
            'predicted_count': predicted_count,
            'forecast_hours': forecast_hours
        })
    
    conn.close()
    return predictions
```

---

### 7. **Dashboard Missing Geographic Visualization**
**Location:** `src/dashboard.py`
**Current State:** Uses plotly scatter maps (line 8-9 imports)
**Impact:** No polygon shading, no zone filters

**Required Changes:**
```python
# Add to imports
import json
from shapely.geometry import shape, Point

# Add function to load GeoJSON
def load_geo_boundaries():
    with open('../data/geo/kuwait/governorates.geojson') as f:
        governorates = json.load(f)
    with open('../data/geo/kuwait/districts.geojson') as f:
        districts = json.load(f)
    return governorates, districts

# Add choropleth map
def render_hotspot_map(incidents_df, hotspots_df):
    governorates, districts = load_geo_boundaries()
    
    # Merge hotspot scores with district geometries
    district_scores = hotspots_df.groupby('district')['score'].sum().to_dict()
    
    fig = go.Figure()
    
    # Add district polygons with color intensity
    for feature in districts['features']:
        district_name = feature['properties']['name_en']
        score = district_scores.get(district_name, 0)
        
        # Color based on score
        color = f'rgba(255, 0, 0, {min(score/100, 1)})'
        
        fig.add_trace(go.Scattermapbox(
            mode='lines',
            fill='toself',
            fillcolor=color,
            # ... polygon coordinates
        ))
    
    # Add incident markers
    fig.add_trace(go.Scattermapbox(
        lat=incidents_df['lat'],
        lon=incidents_df['lon'],
        mode='markers',
        marker=dict(size=5, color='blue')
    ))
    
    return fig

# Add filters in sidebar
def render_filters():
    st.sidebar.header("Geographic Filters")
    
    governorates = st.sidebar.multiselect(
        "Governorate",
        options=KUWAIT_GOVERNORATES
    )
    
    # Load districts for selected governorates
    districts = get_districts_for_governorates(governorates)
    selected_districts = st.sidebar.multiselect(
        "District",
        options=districts
    )
    
    police_areas = st.sidebar.multiselect(
        "Police Area",
        options=get_police_areas()
    )
    
    return {
        'governorates': governorates,
        'districts': selected_districts,
        'police_areas': police_areas
    }
```

---

### 8. **Alert System Using Test Messages**
**Location:** `automation/trigger_alerts.py`
**Current State:** Sends generic test alerts
**Impact:** Not production-ready, lacks zone context

**Required Format:**
```python
def send_hotspot_alert(zone_info, trend_data, forecast_data):
    """
    Send production-ready hotspot alert
    """
    message = f"""
🚨 Hotspot Activation Alert

Zone: {zone_info['district']} Block {zone_info['block']}
Trend: +{trend_data['pct_change']}% WoW
Forecast: {forecast_data['predicted_count']} incidents next 24h
Sector: {zone_info['police_area']}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Source: Khareetaty-AI
"""
    
    # Send to multiple contacts
    contacts = os.getenv('WHATSAPP_CONTACTS', '').split(',')
    for contact in contacts:
        send_whatsapp_message(contact.strip(), message)

# Support multiple WhatsApp contacts
def send_whatsapp_message(phone_number, message):
    # Use Twilio or WhatsApp Business API
    from twilio.rest import Client
    
    client = Client(
        os.getenv('TWILIO_ACCOUNT_SID'),
        os.getenv('TWILIO_AUTH_TOKEN')
    )
    
    client.messages.create(
        from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
        to=f"whatsapp:{phone_number}",
        body=message
    )
```

---

## OPTIONAL ENHANCEMENTS

### 9. **Performance Optimization**
- Add spatial indexes on all geometry columns
- Cache geo lookup results in Redis
- Pre-compute zone boundaries for faster queries

### 10. **Data Quality**
- Add validation for zone resolution accuracy
- Track resolution success rate in geo_resolution_log
- Alert on low resolution rates

### 11. **Advanced Analytics**
- Cross-zone incident correlation
- Zone-to-zone incident migration patterns
- Temporal patterns per zone type

---

## MISSING FILES SUMMARY

### New Files to Create:
1. `backend/services/geo_lookup.py` - Geographic resolution service
2. `data/geo/kuwait/governorates.geojson` - Governorate boundaries
3. `data/geo/kuwait/districts.geojson` - District boundaries
4. `data/geo/kuwait/blocks.geojson` - Block centroids
5. `data/geo/kuwait/police_zones.geojson` - Police jurisdictions
6. `data/geo/kuwait/index.json` - Zone metadata
7. `backend/db/geo_migrations.sql` - Geographic table migrations

### Files to Modify:
1. `automation/etl_job.py` - Add geo resolution
2. `services/clustering.py` - Per-zone clustering
3. `services/modeling.py` - Add predict_by_zone()
4. `src/dashboard.py` - Add choropleth maps and filters
5. `automation/trigger_alerts.py` - Production alert format
6. `backend/db/migrations.sql` - Add geo tables
7. `backend/app.py` - Import geo_lookup service

---

## BROKEN IMPORTS / EMPTY MODULES

### Current Issues:
- `data/geo/kuwait/` folder exists but is empty
- No import errors detected in current codebase
- All referenced modules exist

### Potential Issues After Implementation:
- `backend/services/geo_lookup.py` will be imported by etl_job.py
- Dashboard will need to import GeoJSON loading utilities
- Ensure Shapely is in requirements.txt

---

## IMPLEMENTATION PRIORITY

### Phase 1 (Critical - Week 1):
1. Create geo data layer (governorates, districts, blocks, police_zones)
2. Build geo_lookup.py service
3. Update database schema with geo tables
4. Modify ETL pipeline for geo resolution

### Phase 2 (High Priority - Week 2):
5. Update clustering for per-zone operation
6. Add zone-specific forecasting
7. Enhance dashboard with choropleth maps
8. Add geographic filters

### Phase 3 (Production Ready - Week 3):
9. Upgrade alert system with production format
10. Add multiple WhatsApp contact support
11. End-to-end testing
12. Documentation and handoff

---

## DEPENDENCIES TO ADD

Add to `requirements.txt`:
```
shapely>=2.0.0
geojson>=3.0.0
rtree>=1.0.0  # For spatial indexing
```

---

## CONCLUSION

The system has a solid foundation but lacks geographic awareness at the district/block level. The main blockers are:
1. Missing geographic data files
2. No geo resolution service
3. Database schema gaps
4. Services not zone-aware

All gaps are addressable with the implementation plan outlined above. No major architectural changes required - this is primarily additive work that extends existing functionality.

**Estimated Effort:** 3-4 weeks for full implementation
**Risk Level:** Low (additive changes, no breaking modifications)
**Impact:** High (enables true geographic intelligence)
