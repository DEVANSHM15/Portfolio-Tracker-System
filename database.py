# database.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Map of activity types to their fixed points
POINTS_MAP = {
    "journal_q1q2": 50,
    "journal_q3": 40,
    "journal_q4": 30,
    "best_paper_award": 50,
    "Conf_presentation_international": 40,
    "Conf_presentation_national": 25,
    "Winners_international": 50,
    "Winners_national": 40,
    "Winners_intercollege":30,
    "Winner_college":20,
    "Participation_International": 40,
    "Participation_National": 30,
    "Participation_Intercollege": 20,
    "Participation_college": 10,
    "Cultural_participation": 30,
    "Blood_donation": 20,
    "Community_service": 10,
    "Industrial_visit": 20,
    "Organize_event": 20
}   

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), nullable=True    )
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'student' or 'faculty'
    usn = db.Column(db.String(20), unique=True, nullable=True)  # Changed to nullable=True
    points = db.Column(db.Integer, default=0)
    
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    proof = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    feedback = db.Column(db.Text)  # faculty feedback
    activity_type = db.Column(db.String(50))  # e.g., 'journal_q1q2', 'blood_donation', etc.

    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student = db.relationship('User', backref=db.backref('activities', lazy=True))

class HelpDeskQA(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
