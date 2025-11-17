#!/usr/bin/env python
"""
Simple database sync script.

Auto-generates and runs migrations based on model changes.
Just update your models and run this script - it handles everything.

Usage:
    python scripts/sync_db.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.migrate import sync_db


def main():
    """Sync database with models."""
    print("🔄 Syncing database with models...")
    print("   This will auto-generate migrations and apply them.\n")
    
    success = sync_db()
    
    if success:
        print("\n✅ Database sync completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Database sync failed. Check the logs above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()

