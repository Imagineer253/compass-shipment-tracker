#!/usr/bin/env python3
"""
Simple script to check the database structure and verify migration
"""

import sqlite3
import os

def check_database():
    """Check database structure"""
    # Check both possible locations
    db_paths = ['compass.db', 'instance/compass.db']
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Database file not found in any expected location!")
        return
    
    print(f"📁 Database file: {db_path}")
    print(f"📊 File size: {os.path.getsize(db_path)} bytes")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📋 Tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if signing_authority table exists
        table_names = [t[0] for t in tables]
        if 'signing_authority' in table_names:
            print("\n✅ SigningAuthority table exists")
            
            # Get signing authority count
            cursor.execute("SELECT COUNT(*) FROM signing_authority")
            sa_count = cursor.fetchone()[0]
            print(f"📊 Signing authorities: {sa_count}")
            
            if sa_count > 0:
                cursor.execute("SELECT name, name_hindi, designation, designation_hindi, department, department_hindi, is_default FROM signing_authority")
                authorities = cursor.fetchall()
                for auth in authorities:
                    default_mark = " (DEFAULT)" if auth[6] else ""
                    print(f"  - {auth[0]} / {auth[1] or 'N/A'}")
                    print(f"    {auth[2]} / {auth[3] or 'N/A'}")
                    print(f"    {auth[4]} / {auth[5] or 'N/A'}{default_mark}")
                    print()
                    
                # Check if Hindi fields exist
                cursor.execute("PRAGMA table_info(signing_authority)")
                sa_columns = [col[1] for col in cursor.fetchall()]
                hindi_fields = ['name_hindi', 'designation_hindi', 'department_hindi']
                missing_hindi = [field for field in hindi_fields if field not in sa_columns]
                
                if missing_hindi:
                    print(f"⚠️ Missing Hindi fields: {missing_hindi}")
                else:
                    print("✅ All Hindi fields present in signing authority table")
        else:
            print("❌ SigningAuthority table missing")
        
        # Check shipment table columns
        if 'shipment' in table_names:
            print("\n📋 Shipment table columns:")
            cursor.execute("PRAGMA table_info(shipment)")
            columns = cursor.fetchall()
            
            signing_authority_column_exists = False
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
                if col[1] == 'signing_authority_id':
                    signing_authority_column_exists = True
            
            if signing_authority_column_exists:
                print("\n✅ signing_authority_id column exists in shipment table")
            else:
                print("\n❌ signing_authority_id column missing from shipment table")
                
            # Check shipment count
            cursor.execute("SELECT COUNT(*) FROM shipment")
            shipment_count = cursor.fetchone()[0]
            print(f"📊 Total shipments: {shipment_count}")
        else:
            print("❌ Shipment table missing")
        
        conn.close()
        
        # Migration status
        if 'signing_authority' in table_names and 'shipment' in table_names:
            cursor = sqlite3.connect(db_path).cursor()
            cursor.execute("PRAGMA table_info(shipment)")
            shipment_cols = [col[1] for col in cursor.fetchall()]
            if 'signing_authority_id' in shipment_cols:
                print("\n🎉 Migration appears to be successful!")
            else:
                print("\n⚠️ Migration incomplete - missing signing_authority_id column")
        else:
            print("\n❌ Migration failed - missing tables")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == '__main__':
    check_database() 