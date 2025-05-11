from app import app, db
from models import User

def update_database():
    with app.app_context():
        # Add created_at column to existing users
        users = User.query.all()
        for user in users:
            if not hasattr(user, 'created_at'):
                user.created_at = db.func.now()
        db.session.commit()

if __name__ == "__main__":
    update_database()
    print("Database updated successfully!") 