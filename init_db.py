from app import app, db
from models import User, Prediction, Recommendation, Notification

def init_database():
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_database() 