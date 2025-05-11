import numpy as np
from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify, send_file
import pickle
import warnings
import pandas as pd
from io import BytesIO
from models import db, User, Prediction, Recommendation, Notification
from datetime import datetime
import secrets
import os
import re
warnings.filterwarnings('ignore')

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Handle PostgreSQL URL for Render
database_url = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Load models with error handling
try:
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('model1.pkl', 'rb') as f:
        model1 = pickle.load(f)
except Exception as e:
    print(f"Error loading models: {e}")
    model = None
    model1 = None

# Admin credentials (in production, these should be stored securely)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')  # In production, use a secure password hash

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        mobile_number = request.form.get('mobile_number')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        security_answer1 = request.form.get('security_answer1')  # Get security answer 1
        security_answer2 = request.form.get('security_answer2')  # Get security answer 2
        
        if not User.validate_username(username):
            flash('Username should contain only alphabets')
            return redirect(url_for('register'))
            
        if not User.validate_email(email):
            flash('Invalid email format')
            return redirect(url_for('register'))
            
        if not mobile_number or not mobile_number.isdigit() or len(mobile_number) != 10:
            flash('Please enter a valid 10-digit mobile number')
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
            
        if User.query.filter_by(username=username).first():
            flash('Username already taken')
            return redirect(url_for('register'))
            
        if User.query.filter_by(mobile_number=mobile_number).first():
            flash('Mobile number already registered')
            return redirect(url_for('register'))
            
        user = User(username=username, email=email, mobile_number=mobile_number)  # Removed security question arguments
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'scenario_name', 'cgpa', 'projects', 'workshops', 'mini_projects', 
                             'skills', 'communication_skills', 'internship', 'hackathon', 
                             'tw_percentage', 'te_percentage', 'backlogs']
            
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Extract features from the request
            features = [
                float(data['cgpa']),
                int(data['projects']),
                int(data['workshops']),
                int(data['mini_projects']),
                1 + data['skills'].count(','),
                int(data['communication_skills']),
                int(data['internship']),
                int(data['hackathon']),
                float(data['tw_percentage']),
                float(data['te_percentage']),
                int(data['backlogs'])
            ]
            
            arr = np.array(features, dtype=float)
            
            # Make predictions
            placement_pred = model.predict([arr])[0] if model else 'Not Placed'
            salary_pred = 0
            
            if model1 and placement_pred == 'Placed':
                salary_features = np.append(arr, 1.0)
                salary_pred = model1.predict([salary_features])[0]
            
            # Store prediction in database
            prediction = Prediction(
                user_id=session['user_id'],
                cgpa=features[0],
                projects=features[1],
                workshops=features[2],
                mini_projects=features[3],
                skills=data['skills'],
                communication_skills=features[5],
                internship=features[6],
                hackathon=features[7],
                tw_percentage=features[8],
                te_percentage=features[9],
                backlogs=features[10],
                placement_prediction=placement_pred,
                salary_prediction=salary_pred,
                scenario_name=data['scenario_name']
            )
            
            db.session.add(prediction)
            db.session.commit()
            
            # Generate recommendations
            recommendations = generate_recommendations(prediction)
            for rec in recommendations:
                db.session.add(rec)
            db.session.commit()
            
            return jsonify({
                'name': data['name'],
                'placement_prediction': placement_pred,
                'salary_prediction': salary_pred,
                'recommendations': [{'skill_area': r.skill_area, 'recommendation': r.recommendation, 'priority': r.priority} 
                                  for r in recommendations]
            })
            
        except ValueError as e:
            return jsonify({'error': f'Invalid input value: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('index.html')

@app.route('/notifications')
@login_required
def get_notifications():
    try:
        notifications = Notification.query.filter_by(
            user_id=session['user_id'],
            is_read=False
        ).order_by(Notification.timestamp.desc()).all()
        
        return jsonify([{
            'id': n.id,
            'message': n.message,
            'timestamp': n.timestamp.isoformat(),
            'type': n.notification_type
        } for n in notifications])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/mark_notification_read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    try:
        notification = Notification.query.get_or_404(notification_id)
        if notification.user_id != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
            
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def generate_recommendations(prediction):
    recommendations = []
    
    # Academic Performance Recommendations
    if prediction.cgpa < 7.0:
        recommendations.append(Recommendation(
            prediction_id=prediction.id,
            skill_area='Academic Performance',
            recommendation='Your CGPA is below the competitive threshold. Focus on improving your academic performance by:\n'
                         '1. Attending all classes regularly\n'
                         '2. Seeking help from professors during office hours\n'
                         '3. Forming study groups with peers\n'
                         '4. Taking additional courses in your weak areas\n\n'
                         'Recommended Resources:\n'
                         '- Brilliant (https://brilliant.org/) for interactive learning\n'
                         '- Study.com (https://study.com/) for academic courses\n'
                         '- Academic Earth (https://academicearth.org/) for free courses\n'
                         '- OpenStax (https://openstax.org/) for free textbooks',
            priority=5
        ))
    elif prediction.cgpa < 8.0:
        recommendations.append(Recommendation(
            prediction_id=prediction.id,
            skill_area='Academic Performance',
            recommendation='Your CGPA is good but could be improved. Consider:\n'
                         '1. Taking advanced courses in your field\n'
                         '2. Participating in academic competitions\n'
                         '3. Publishing research papers or technical articles\n\n'
                         'Recommended Resources:\n'
                         '- Academia.edu (https://www.academia.edu/) for research papers\n'
                         '- ResearchGate (https://www.researchgate.net/) for academic collaboration\n'
                         '- ScienceDirect (https://www.sciencedirect.com/) for scientific articles\n'
                         '- JSTOR (https://www.jstor.org/) for academic journals',
            priority=4
        ))
    
    # Project Experience Recommendations
    if prediction.projects < 2:
        recommendations.append(Recommendation(
            prediction_id=prediction.id,
            skill_area='Project Experience',
            recommendation='Limited project experience detected. Enhance your profile by:\n'
                         '1. Starting personal projects in your area of interest\n'
                         '2. Contributing to open-source projects on GitHub\n'
                         '3. Participating in hackathons and coding competitions\n'
                         '4. Building a portfolio website to showcase your work\n\n'
                         'Recommended Resources:\n'
                         '- GitLab (https://gitlab.com/) for project hosting\n'
                         '- Bitbucket (https://bitbucket.org/) for code collaboration\n'
                         '- Glitch (https://glitch.com/) for web projects\n'
                         '- CodeSandbox (https://codesandbox.io/) for web development',
            priority=5
        ))
    elif prediction.projects < 4:
        recommendations.append(Recommendation(
            prediction_id=prediction.id,
            skill_area='Project Experience',
            recommendation='Good project experience, but room for improvement:\n'
                         '1. Focus on complex, real-world projects\n'
                         '2. Document your projects with proper README files\n'
                         '3. Add unit tests and documentation to your code\n'
                         '4. Consider publishing your projects on GitHub\n\n'
                         'Recommended Resources:\n'
                         '- GitBook (https://www.gitbook.com/) for documentation\n'
                         '- SonarQube (https://www.sonarqube.org/) for code quality\n'
                         '- Snyk (https://snyk.io/) for security scanning\n'
                         '- CircleCI (https://circleci.com/) for continuous integration',
            priority=4
        ))
    
    # Communication Skills Recommendations
    if prediction.communication_skills < 3:
        recommendations.append(Recommendation(
            prediction_id=prediction.id,
            skill_area='Communication Skills',
            recommendation='Communication skills need improvement. Consider:\n'
                         '1. Joining a public speaking club (e.g., Toastmasters)\n'
                         '2. Participating in group discussions and debates\n'
                         '3. Practicing mock interviews with career services\n'
                         '4. Taking online courses on business communication\n\n'
                         'Recommended Resources:\n'
                         '- MasterClass (https://www.masterclass.com/) for expert-led courses\n'
                         '- Skillshare (https://www.skillshare.com/) for creative skills\n'
                         '- Udacity (https://www.udacity.com/) for tech communication\n'
                         '- Pluralsight (https://www.pluralsight.com/) for professional development',
            priority=5
        ))
    elif prediction.communication_skills < 4:
        recommendations.append(Recommendation(
            prediction_id=prediction.id,
            skill_area='Communication Skills',
            recommendation='Good communication skills, but could be enhanced:\n'
                         '1. Practice technical presentation skills\n'
                         '2. Work on writing technical documentation\n'
                         '3. Participate in technical meetups and conferences\n'
                         '4. Learn to explain complex concepts simply\n\n'
                         'Recommended Resources:\n'
                         '- Hashnode (https://hashnode.com/) for tech blogging\n'
                         '- Dev Community (https://dev.to/) for tech discussions\n'
                         '- Stack Overflow Blog (https://stackoverflow.blog/) for tech insights\n'
                         '- TechCrunch (https://techcrunch.com/) for tech news',
            priority=4
        ))
    
    # Internship Experience Recommendations
    if prediction.internship < 1:
        recommendations.append(Recommendation(
            prediction_id=prediction.id,
            skill_area='Internship Experience',
            recommendation='No internship experience detected. Critical to:\n'
                         '1. Apply for summer internships in your field\n'
                         '2. Look for virtual internship opportunities\n'
                         '3. Consider part-time internships during semester\n'
                         '4. Network with alumni for internship referrals\n\n'
                         'Recommended Resources:\n'
                         '- Handshake (https://joinhandshake.com/) for student opportunities\n'
                         '- WayUp (https://www.wayup.com/) for entry-level jobs\n'
                         '- RippleMatch (https://www.ripplematch.com/) for career matching\n'
                         '- ZipRecruiter (https://www.ziprecruiter.com/) for job search',
            priority=5
        ))
    
    # Hackathon Participation Recommendations
    if prediction.hackathon < 1:
        recommendations.append(Recommendation(
            prediction_id=prediction.id,
            skill_area='Hackathon Experience',
            recommendation='No hackathon experience. Consider:\n'
                         '1. Participating in local hackathons\n'
                         '2. Joining online hackathon platforms\n'
                         '3. Forming a team with classmates\n'
                         '4. Building a portfolio of hackathon projects\n\n'
                         'Recommended Resources:\n'
                         '- Major League Hacking (https://mlh.io/) for student hackathons\n'
                         '- Devfolio (https://devfolio.co/) for hackathons\n'
                         '- Unstop (https://unstop.com/) for competitions\n'
                         '- HackerEarth (https://www.hackerearth.com/) for coding challenges',
            priority=4
        ))
    
    # Skills Development Recommendations
    skills_count = len(prediction.skills.split(','))
    if skills_count < 3:
        recommendations.append(Recommendation(
            prediction_id=prediction.id,
            skill_area='Technical Skills',
            recommendation='Limited technical skills detected. Focus on:\n'
                         '1. Learning core programming languages (Python, Java, C++)\n'
                         '2. Mastering data structures and algorithms\n'
                         '3. Learning version control (Git)\n'
                         '4. Taking online courses on platforms like Coursera, Udemy\n\n'
                         'Recommended Resources:\n'
                         '- Exercism (https://exercism.org/) for coding practice\n'
                         '- Codewars (https://www.codewars.com/) for coding challenges\n'
                         '- Frontend Mentor (https://www.frontendmentor.io/) for frontend projects\n'
                         '- Scrimba (https://scrimba.com/) for interactive coding',
            priority=5
        ))
    
    # Backlog Management Recommendations
    if prediction.backlogs > 0:
        recommendations.append(Recommendation(
            prediction_id=prediction.id,
            skill_area='Backlog Management',
            recommendation='Backlogs detected. Important to:\n'
                         '1. Clear all backlogs as soon as possible\n'
                         '2. Create a study plan for backlog subjects\n'
                         '3. Seek help from professors and peers\n'
                         '4. Consider taking additional classes if needed\n\n'
                         'Recommended Resources:\n'
                         '- StudySmarter (https://www.studysmarter.us/) for study planning\n'
                         '- Quizlet (https://quizlet.com/) for flashcards\n'
                         '- Anki (https://apps.ankiweb.net/) for spaced repetition\n'
                         '- Wolfram Alpha (https://www.wolframalpha.com/) for problem solving',
            priority=5
        ))
    
    # Placement Preparation Recommendations
    if prediction.placement_prediction == 'Not Placed':
        recommendations.append(Recommendation(
            prediction_id=prediction.id,
            skill_area='Placement Preparation',
            recommendation='Based on your profile, focus on:\n'
                         '1. Strengthening core technical concepts\n'
                         '2. Practicing coding problems daily\n'
                         '3. Building a strong resume and LinkedIn profile\n'
                         '4. Networking with industry professionals\n'
                         '5. Preparing for technical and HR interviews\n\n'
                         'Recommended Resources:\n'
                         '- Pramp (https://www.pramp.com/) for mock interviews\n'
                         '- Interview Cake (https://www.interviewcake.com/) for interview prep\n'
                         '- Resume.io (https://resume.io/) for resume building\n'
                         '- Levels.fyi (https://www.levels.fyi/) for salary research',
            priority=5
        ))
    else:
        recommendations.append(Recommendation(
            prediction_id=prediction.id,
            skill_area='Placement Preparation',
            recommendation='Good placement chances! Prepare by:\n'
                         '1. Researching target companies and roles\n'
                         '2. Practicing company-specific interview questions\n'
                         '3. Preparing for technical and behavioral interviews\n'
                         '4. Building a strong professional network\n\n'
                         'Recommended Resources:\n'
                         '- Blind (https://www.teamblind.com/) for company insights\n'
                         '- LeetCode Premium (https://leetcode.com/premium/) for company questions\n'
                         '- Interviewing.io (https://interviewing.io/) for practice interviews\n'
                         '- Repvue (https://www.repvue.com/) for sales careers',
            priority=4
        ))
    
    return recommendations

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        flash('Please login as admin first', 'warning')
        return redirect(url_for('admin_login'))
    
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash('Admin logged out successfully', 'success')
    return redirect(url_for('home'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    user = User.query.get_or_404(user_id)
    try:
        # Delete related predictions first
        predictions = Prediction.query.filter_by(user_id=user_id).all()
        for prediction in predictions:
            # Delete related recommendations
            Recommendation.query.filter_by(prediction_id=prediction.id).delete()
            # Delete the prediction
            db.session.delete(prediction)
        
        # Delete related notifications
        Notification.query.filter_by(user_id=user_id).delete()
        
        # Finally delete the user
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)