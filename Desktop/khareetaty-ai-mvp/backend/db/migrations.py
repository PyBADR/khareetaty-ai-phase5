import psycopg2
import os

DB_CONN = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME", "khareetaty_ai"),
    "user": os.getenv("DB_USER", "bader"),
    "password": os.getenv("DB_PASSWORD", "secret123")
}

def create_tables():
    """Create all required database tables"""
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    
    # Create incidents_raw table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS incidents_raw (
            id SERIAL PRIMARY KEY,
            incident_type VARCHAR(100) NOT NULL,
            governorate VARCHAR(100),
            zone VARCHAR(100),
            lat DECIMAL(10, 8) NOT NULL,
            lon DECIMAL(11, 8) NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create incidents_clean table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS incidents_clean (
            id SERIAL PRIMARY KEY,
            raw_incident_id INTEGER REFERENCES incidents_raw(id),
            incident_type VARCHAR(100) NOT NULL,
            governorate VARCHAR(100),
            zone VARCHAR(100),
            lat DECIMAL(10, 8) NOT NULL,
            lon DECIMAL(11, 8) NOT NULL,
            hour INTEGER,
            day VARCHAR(10),
            week INTEGER,
            timestamp TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create zones_hotspots table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS zones_hotspots (
            id SERIAL PRIMARY KEY,
            zone VARCHAR(200) NOT NULL UNIQUE,
            score DECIMAL(10, 2),
            predicted BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create alerts_log table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alerts_log (
            id SERIAL PRIMARY KEY,
            alert_type VARCHAR(50) NOT NULL,
            severity VARCHAR(20) NOT NULL,
            message TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            recipients TEXT
        );
    """)
    
    # Create system_users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS system_users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            role TEXT CHECK (role IN ('superadmin', 'analyst', 'viewer')) DEFAULT 'viewer',
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create indexes for performance
    cur.execute("CREATE INDEX IF NOT EXISTS idx_incidents_raw_timestamp ON incidents_raw(timestamp);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_incidents_raw_location ON incidents_raw(lat, lon);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_incidents_clean_timestamp ON incidents_clean(timestamp);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_incidents_clean_gov ON incidents_clean(governorate);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_zones_hotspots_predicted ON zones_hotspots(predicted);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_alerts_log_sent_at ON alerts_log(sent_at);")
    
    conn.commit()
    conn.close()
    print("Database tables created successfully!")

def seed_initial_data():
    """Seed initial data for the system"""
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    
    # Insert initial admin user
    try:
        cur.execute("""
            INSERT INTO system_users (name, email, phone, role, active)
            VALUES ('Bader Admin', 'bader.naser.ai.sa@gmail.com', '+96566338736', 'superadmin', TRUE)
            ON CONFLICT (email) DO NOTHING;
        """)
        conn.commit()
        print("Initial admin user created (if not exists)")
    except Exception as e:
        print(f"Error seeding initial data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_tables()
    seed_initial_data()
    print("Database setup completed!")