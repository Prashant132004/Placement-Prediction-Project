from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    predictions = db.relationship('Prediction', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def validate_username(username):
        return bool(re.match('^[a-zA-Z]+$', username))

    @staticmethod
    def validate_email(email):
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{3,}$', email))

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Input parameters
    cgpa = db.Column(db.Float)
    projects = db.Column(db.Integer)
    workshops = db.Column(db.Integer)
    mini_projects = db.Column(db.Integer)
    skills = db.Column(db.String(500))
    communication_skills = db.Column(db.Integer)
    internship = db.Column(db.Integer)
    hackathon = db.Column(db.Integer)
    tw_percentage = db.Column(db.Float)
    te_percentage = db.Column(db.Float)
    backlogs = db.Column(db.Integer)
    
    # Prediction results
    placement_prediction = db.Column(db.String(20))
    salary_prediction = db.Column(db.Float)
    
    # Scenario comparison
    scenario_name = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'cgpa': self.cgpa,
            'projects': self.projects,
            'workshops': self.workshops,
            'mini_projects': self.mini_projects,
            'skills': self.skills,
            'communication_skills': self.communication_skills,
            'internship': self.internship,
            'hackathon': self.hackathon,
            'tw_percentage': self.tw_percentage,
            'te_percentage': self.te_percentage,
            'backlogs': self.backlogs,
            'placement_prediction': self.placement_prediction,
            'salary_prediction': self.salary_prediction,
            'scenario_name': self.scenario_name
        }

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prediction_id = db.Column(db.Integer, db.ForeignKey('prediction.id'), nullable=False)
    skill_area = db.Column(db.String(100))
    recommendation = db.Column(db.String(500))
    priority = db.Column(db.Integer)  # 1-5, where 5 is highest priority
    
    prediction = db.relationship('Prediction', backref='recommendations')

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    notification_type = db.Column(db.String(50))  # e.g., 'update', 'recommendation', 'system' 