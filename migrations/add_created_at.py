import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import create_engine, Column, DateTime
from sqlalchemy.ext.declarative import declarative_base

def migrate():
    with app.app_context():
        # Create a new engine for raw SQL
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        
        # Add created_at column
        with engine.connect() as conn:
            conn.execute('ALTER TABLE user ADD COLUMN created_at DATETIME')
            conn.commit()

if __name__ == "__main__":
    migrate()
    print("Migration completed successfully!") 