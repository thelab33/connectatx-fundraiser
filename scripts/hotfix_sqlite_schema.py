#!/usr/bin/env python3
"""
hotfix_sqlite_schema.py — Safe schema patcher for FundChamps SQLite DB.
Run this to add missing columns or adjust schema without nuking data.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("app/data/app.db")

# List of patches: (table, column, SQL)
PATCHES = [
    (
        "campaign_goals",
        "total",
        "ALTER TABLE campaign_goals ADD COLUMN total INTEGER DEFAULT 0",
    ),
    # Add future patches here as tuples
]

def apply_patches():
    if not DB_PATH.exists():
        print(f"❌ DB not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for table, column, sql in PATCHES:
        try:
            # Check if column exists
            c.execute(f"PRAGMA table_info({table});")
            cols = [row[1] for row in c.fetchall()]
            if column in cols:
                print(f"ℹ️ {table}.{column} already exists, skipping")
                continue

            # Apply patch
            print(f"➕ Adding {table}.{column} …")
            c.execute(sql)
            print(f"✅ Added {table}.{column}")

        except Exception as e:
            print(f"⚠️ Error while patching {table}.{column}: {e}")

    conn.commit()
    conn.close()
    print("🎉 Schema hotfix complete.")

if __name__ == "__main__":
    apply_patches()

