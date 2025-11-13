#!/usr/bin/env python3
"""
Debug script to check table creation.
"""

import sys
import os
sys.path.insert(0, os.getcwd())

from app.database import engine, Base
from app.models import Entity, RelationshipEntity, User
from sqlalchemy import text

def debug_tables():
    """Debug table creation."""
    print("🔍 Debugging table creation...")
    
    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    
    # Check what tables exist
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables found: {tables}")
        
        # Check table structure for entities
        if "entities" in tables:
            result = conn.execute(text("PRAGMA table_info(entities)"))
            columns = result.fetchall()
            print(f"Entities table columns: {[col[1] for col in columns]}")
        else:
            print("❌ entities table not found")
        
        # Check table structure for relationships
        if "relationships" in tables:
            result = conn.execute(text("PRAGMA table_info(relationships)"))
            columns = result.fetchall()
            print(f"Relationships table columns: {[col[1] for col in columns]}")
        else:
            print("❌ relationships table not found")
        
        # Check table structure for users
        if "users" in tables:
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = result.fetchall()
            print(f"Users table columns: {[col[1] for col in columns]}")
        else:
            print("❌ users table not found")

if __name__ == "__main__":
    debug_tables()
