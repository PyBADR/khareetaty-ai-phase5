#!/usr/bin/env python3
"""
Apply Phase 5 Database Migrations
This script applies the Phase 5 database schema changes to support operational intelligence
"""

import os
import sys
import psycopg2
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import DATABASE

def apply_phase5_migrations():
    """Apply Phase 5 database migrations"""
    
    migration_file = Path(__file__).parent / "phase5_migrations.sql"
    
    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    try:
        # Read migration SQL
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_commands = f.read()
        
        # Connect to database
        conn = psycopg2.connect(
            host=DATABASE.HOST,
            port=DATABASE.PORT,
            dbname=DATABASE.NAME,
            user=DATABASE.USER,
            password=DATABASE.PASSWORD
        )
        
        conn.autocommit = False
        cur = conn.cursor()
        
        print("🚀 Applying Phase 5 database migrations...")
        
        # Execute migration commands
        cur.execute(sql_commands)
        
        # Commit changes
        conn.commit()
        
        cur.close()
        conn.close()
        
        print("✅ Phase 5 migrations applied successfully!")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def verify_migration():
    """Verify that Phase 5 tables exist"""
    
    try:
        conn = psycopg2.connect(
            host=DATABASE.HOST,
            port=DATABASE.PORT,
            dbname=DATABASE.NAME,
            user=DATABASE.USER,
            password=DATABASE.PASSWORD
        )
        
        cur = conn.cursor()
        
        # Check if key tables exist
        tables_to_check = [
            'zones_hotspots',
            'geo_resolution_log', 
            'contacts',
            'analytics_summary',
            'alerts_log'
        ]
        
        missing_tables = []
        
        for table in tables_to_check:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (table,))
            
            exists = cur.fetchone()[0]
            if not exists:
                missing_tables.append(table)
        
        cur.close()
        conn.close()
        
        if missing_tables:
            print(f"❌ Missing tables: {', '.join(missing_tables)}")
            return False
        else:
            print("✅ All Phase 5 tables verified successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def main():
    """Main execution function"""
    
    print("=" * 50)
    print("KHAREETATY AI - PHASE 5 DATABASE MIGRATIONS")
    print("=" * 50)
    
    # Apply migrations
    if apply_phase5_migrations():
        print("\n🔍 Verifying migration...")
        if verify_migration():
            print("\n🎉 Phase 5 database setup complete!")
            print("✓ Extended incidents_clean table")
            print("✓ Updated zones_hotspots with geographic fields")
            print("✓ Created geo_resolution_log for tracking")
            print("✓ Added contacts table for alert routing")
            print("✓ Enhanced analytics_summary with categorization")
            print("✓ Improved alerts_log with delivery tracking")
            print("✓ Created dashboard optimization views")
            return True
        else:
            print("\n❌ Migration verification failed!")
            return False
    else:
        print("\n❌ Migration application failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
