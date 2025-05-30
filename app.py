# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory,abort,request, jsonify
from flask_migrate import Migrate
from database import db, init_db, User, Activity, HelpDeskQA,POINTS_MAP
import os
import re
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

migrate = Migrate(app, db)
init_db(app)

def is_rvu_email(email):
    return re.match(r"^[a-zA-Z0-9._%+-]+@rvu\.edu\.in$", email)

@app.route('/')
def home():
    return render_template('home.html', user=session.get('user_id'), role=session.get('role'))

@app.route('/events')
def upcoming_events():
    return render_template('events.html', user=session.get('user_id'), role=session.get('role'))

@app.route('/register', methods=['GET', 'POST'])


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name= request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        role = request.form['role']
        usn = request.form.get('usn', '').strip().upper()  # Normalize to uppercase

        # Validate RVU email
        if not is_rvu_email(email):
            flash('Only @rvu.edu.in emails are allowed!', 'error')
            return redirect(url_for('register'))

        # Validate USN if student
        if role == 'student':
            if not usn:
                flash('USN is required for students', 'error')
                return redirect(url_for('register'))
            if not re.match(r'^1RVU\d{2}[A-Z]{3}\d{3}$', usn):
                flash('Invalid USN format. Example: 1RVU23CSE140 (Year: 23, Branch: CSE, ID: 140)', 'error')
                return redirect(url_for('register'))

        # Check for existing email or USN
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        if role == 'student' and User.query.filter_by(usn=usn).first():
            flash('USN already registered!', 'error')
            return redirect(url_for('register'))

        try:
            # Create new user with hashed password
            new_user = User(
                name=name,
                email=email,
                password=generate_password_hash(password),
                role=role,
                usn=usn if role == 'student' else None,
                points=0
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            # Check if user is already logged in
            if 'user_id' in session:
                flash('Already logged in.', 'info')
                return redirect(url_for('home'))
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            # Redirect based on role
            return redirect(url_for('student_dashboard') if user.role == 'student' else url_for('faculty_dashboard'))
        else:
            flash('Invalid email or password! Not registered? <a href="{}">Sign up here</a>.'.format(url_for('register')), 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/student')
def student_dashboard():
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    db.session.refresh(user)  # Refresh user data
    if user.points >= 100:
        flash('You have reached 100 points and cannot submit more activities.', 'info')
    
    activities = Activity.query.filter_by(student_id=user.id).all()
    return render_template('student.html', user=user, activities=activities)

@app.route('/helpdesk/qa')
def helpdesk_qa():
    qa_data = HelpDeskQA.query.all()
    return jsonify([{
        'id': qa.id,
        'question': qa.question,
        'answer': qa.answer,
        'category': qa.category
    } for qa in qa_data])

@app.route('/submit', methods=['POST'])
def submit_activity():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.points >= 100:
        flash('You have reached the maximum points.', 'error')
        return redirect(url_for('student_dashboard'))

    # Handle file upload
    file = request.files['proof']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Create new activity
    new_activity = Activity(
        title=request.form['title'],
        description=request.form['description'],
        proof=filename,
        activity_type=request.form['activity_type'],
        student_id=session['user_id'],
        status='pending'
    )
    db.session.add(new_activity)
    db.session.commit()
    flash('Activity submitted successfully! Awaiting approval.', 'success')
    return redirect(url_for('student_dashboard'))
app.config['UPLOAD_FOLDER'] = 'uploads'  
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB limit

@app.route('/uploads/<user_id>/<filename>')
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
@app.errorhandler(RequestEntityTooLarge)
def handle_large_file_error(error):
    flash('File is too large. Maximum size is 2MB.', 'error')
    return redirect(url_for('student_dashboard'))  # Redirect to a page (like the dashboard) where the user can try again.
@app.route('/faculty', methods=['GET', 'POST'])
def faculty_dashboard():
    if 'role' not in session or session['role'] != 'faculty':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login'))
    

    if request.method == 'POST':
        action = request.form.get('action')
        activity_id = request.form.get('activity_id')
        feedback = request.form.get('feedback', '')

        activity = Activity.query.get(activity_id)
        if activity:
            student = User.query.get(activity.student_id)

            if action == 'approve':
                activity.status = 'approved'
                allocated_points = POINTS_MAP.get(activity.activity_type, 0)

                if student:
                    print(f"Before Update: Student {student.id} Points = {student.points}")
                    student.points = (student.points or 0) + allocated_points
                    activity.points = allocated_points
                    db.session.commit()
                    db.session.refresh(student)
                    print(f"After Update: Student {student.id} Points = {student.points}")

                activity.feedback = feedback
                db.session.commit()
                flash(f'Activity approved! {allocated_points} points awarded.', 'success')

            elif action == 'reject':
                activity.status = 'rejected'
                activity.feedback = feedback
                db.session.commit()
                flash('Activity rejected.', 'error')

    # --- Filtering Logic ---
    search_query = request.args.get('search_usn', '').strip().upper()
    from_usn = request.args.get('from_usn', '').strip().upper()
    to_usn = request.args.get('to_usn', '').strip().upper()

    all_activities = Activity.query.all()
    filtered_activities = []

    for activity in all_activities:
        student = User.query.get(activity.student_id)
        if not student:
            continue
        
        usn = student.usn.upper()
        last_three = usn[-3:] if len(usn) >= 3 else usn

        # --- Exact Match or Last 3 Digits Match for Search ---
        match_search = False
        if not search_query:  # No search query, match all
            match_search = True
        elif len(search_query) == 3:  # Last 3 digits match
            match_search = last_three == search_query
        else:  # Full USN match
            match_search = usn == search_query

        # --- From USN filter (Exact or Last 3 Digits) ---
        match_from = False
        if not from_usn:  # No "from" filter
            match_from = True
        elif len(from_usn) == 3:  # From USN is last 3 digits
            match_from = last_three >= from_usn
        else:  # Full "from" USN match
            match_from = usn >= from_usn

        # --- To USN filter (Exact or Last 3 Digits) ---
        match_to = False
        if not to_usn:  # No "to" filter
            match_to = True
        elif len(to_usn) == 3:  # To USN is last 3 digits
            match_to = last_three <= to_usn
        else:  # Full "to" USN match
            match_to = usn <= to_usn

        # If all conditions match, add activity to filtered list
        if match_search and match_from and match_to:
            activity.student = student  # Attach student for template
            activity.student_points = student.points or 0
            filtered_activities.append(activity)

    if not filtered_activities:
        flash('No records found matching the filter criteria.', 'info')

    return render_template('faculty.html', activities=filtered_activities)


@app.route('/delete_activity/<int:activity_id>', methods=['POST'])
def delete_activity(activity_id):
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))

    activity = Activity.query.get(activity_id)
    
    if activity and activity.student_id == session['user_id']:
        student = User.query.get(activity.student_id)

        if student:
            # Get allocated points for this activity
            allocated_points = POINTS_MAP.get(activity.activity_type, 0)
            
            # Deduct points (ensure it doesn't go negative)
            student.points = max(0, (student.points or 0) - allocated_points)

            # Commit point update before deleting activity
            db.session.commit()

        # Now delete the activity
        db.session.delete(activity)
        db.session.commit()

        flash('Activity deleted successfully. Points updated.', 'success')
    else:
        flash('Unauthorized action.', 'error')

    return redirect(url_for('student_dashboard'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)