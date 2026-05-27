"""Initialize database with sample data from CSV files."""

import os

from library_db_core import Database


def init_sample_data():
    """Load sample data from CSV files into database."""
    db = Database().connect()
    
    # Skip if already seeded
    if db.is_seeded():
        db.close()
        return
    
    csv_dir = os.path.join(os.path.dirname(__file__), "csv")
    if os.path.exists(csv_dir):
        db.seed_from_csv(csv_dir)
    
    db.close()