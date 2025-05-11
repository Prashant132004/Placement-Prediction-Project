import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import create_engine, text

def migrate():
    with app.app_context():
        # Create a new engine for raw SQL
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        
        # Add mobile_number column
        with engine.connect() as conn:
            conn.execute(text('ALTER TABLE user ADD COLUMN mobile_number VARCHAR(15) UNIQUE'))
            conn.commit()

if __name__ == "__main__":
    migrate()
    print("Migration completed successfully!") 