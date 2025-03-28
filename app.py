import sqlalchemy as db
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from datetime import datetime, timedelta
from sqlalchemy.dialects.sqlite import *
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from flask import Flask, render_template, request, flash, redirect, url_for, session
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt=Bcrypt(app)
app.secret_key = 'super_secret_key'

app.config['SECRET_KEY']='8a0f946f1471e113e528d927220ad977ed8b2cce63303beff10c8cb4a15e1a99'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///assignment3.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 10)
db = SQLAlchemy(app)

# Creating an engine that will connect to the SQLite database
#engine = db.create_engine('sqlite:///assignment3.db', echo = True)

# Session setup
# Session = sessionmaker(bind=engine)
# session = Session()

Base = declarative_base()

# Table for the users
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    first_name = Column(db.String(100))
    last_name = Column(db.String(100))

    # 0 = student, 1 = instructor
    user_type = Column(db.Integer, nullable=False)

    # Connecting feedback to the instructor
    instr_feedback = relationship("Feedback", back_populates="instr_to_feedback")


# Table for different types of assessments
class Assessment(db.Model):
    __tablename__ = 'assessments'
    assessment_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    mark = db.Column(db.Integer)

    # Connecting assessment with the instructor
    instructor_id = db.Column(db.Integer, ForeignKey('users.user_id'), nullable=False)

# Table with the students and their corresponding assessments
class AssessmentsStudent(db.Model):
    __tablename__ = 'student_assessments'
    student_id = db.Column(db.Integer, ForeignKey('users.user_id'), primary_key=True)
    assessment_id = db.Column(db.Integer, ForeignKey('assessments.assessment_id'), primary_key=True)
    remark_id = db.Column(db.Integer, ForeignKey('remarkrequests.remark_id'))
    marks = db.Column(db.Integer, nullable=True)
    # default is NULL, 0 = pending, 1 = approved, 2 = rejected

    # Connecting students to their assessments
    student_to_assess = relationship("User", backref="student_assessments")
    assess_to_student = relationship("Assessment", backref="student_assessments")
    remark_to_student = relationship("RemarkRequests", backref="student_assessments")


# Table for feedback (anonymous feedback from students to instructors)
class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    instructor_id = db.Column(db.Integer, ForeignKey('users.user_id'), nullable=False)
    feedback_type = db.Column(db.Integer)
    feedback = db.Column(db.String, nullable=False)
    reviewed = db.Column(db.Integer, nullable=False, default=0)

    # Connecting the feedback to an instructor
    instr_to_feedback = relationship("User", back_populates="instr_feedback")
    
class RemarkRequests(db.Model):
    __tablename__ = 'remarkrequests'
    remark_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assessment_id = db.Column(db.Integer, ForeignKey('assessments.assessment_id'), nullable=False)
    student_id = db.Column(db.String, ForeignKey('users.user_id'), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=0)
    remark_reason = db.Column(db.String(500), nullable=True)

    # Connecting the feedback to an instructor
    remark_to_user = relationship("User", backref='remarkrequests')
    remark_to_assessment = relationship("Assessment", backref='remarkrequests')


# Create the tables in the database
# Base.metadata.create_all(engine)

# Rendering the pages to make the dropdown work
@app.route('/')
def homepage():
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    return render_template('homepage.html', user=user)

@app.route('/syllabus')
def syllabus():
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    return render_template('syllabus.html', user=user)

@app.route('/assignments')
def assignments():
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    return render_template('assignments.html',user=user)

@app.route('/lab')
def lab():
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    return render_template('lab.html', user=user)

@app.route('/lecturenotes')
def lecturenotes():
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    return render_template('lecturenotes.html', user=user)

@app.route('/piazza')
def piazza():
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    return render_template('piazza.html', user=user)

@app.route('/markus')
def markus():
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    return redirect("https://markus2.utsc.utoronto.ca/", user=user)

@app.route('/anonfeedback', methods = ['GET', 'POST'])
def anonfeedback():
    username = session['name']
    user = User.query.filter_by(username=username).first()

    if not user.user_type == 0:
        return render_template('viewanonfeedback.html') #temp, add prof feedback
    
    if not user:
        return render_template('homepage.html')
    
    professors = User.query.filter_by(user_type=1).all()
    if request.method == "POST":
        professor_id = request.form.get('professor')

        if professor_id:

            instruct_feed = request.form.get('instruct_feed')
            instruct_tips = request.form.get('instruct_tips')
            lab_feed = request.form.get('lab_feed')
            lab_tips = request.form.get('lab_tips')

            if instruct_feed:
                feedback_instructor = Feedback(instructor_id=professor_id, feedback_type=0, feedback=instruct_feed)
                db.session.add(feedback_instructor)
                
            if instruct_tips:
                feedback_tips = Feedback(instructor_id=professor_id, feedback_type=1, feedback=instruct_tips)
                db.session.add(feedback_tips)
                
            if lab_feed:
                feedback_lab = Feedback(instructor_id=professor_id, feedback_type=2, feedback=lab_feed)
                db.session.add(feedback_lab)
                
            if lab_tips:
                feedback_lab_tips = Feedback(instructor_id=professor_id, feedback_type=3, feedback=lab_tips)
                db.session.add(feedback_lab_tips)

            db.session.commit()
            flash('Your feedback has been submitted successfully!', 'success')

            return render_template('anonfeedback.html', success=True, professors=professors)
        else: 
            flash('Please select a Professor.', 'warning')

    return render_template('anonfeedback.html', professors=professors, user=user)

@app.route('/courseteam')
def courseteam():
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    return render_template('courseteam.html', user=user)

@app.route('/viewstudentgrades')
def viewstudentgrades():
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    try:
        assignments = (
            db.session.query(AssessmentsStudent, Assessment)
            .join(Assessment, AssessmentsStudent.assessment_id == Assessment.assessment_id)
            .all()
        )
        #assignments = AssessmentsStudent.query.all()
        print("Query executed successfully")  # Debugging statement
        for assignment in assignments:
            print(f"Assessment ID: {assignment.AssessmentsStudent.assessment_id}, Student ID: {assignment.AssessmentsStudent.student_id}, Mark: {assignment.AssessmentsStudent.marks} Type: {assignment.Assessment.type}")
        return render_template('viewstudentgrades.html', assignments=assignments, user=user)
    except Exception as e:
        print("Error:", e)  # This will print any database errors
        return "An error occurred", 500
    
@app.route('/updatestudentgrades')
def updatestudentgrades():
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    try:
        assignments = (
            db.session.query(AssessmentsStudent, Assessment)
            .join(Assessment, AssessmentsStudent.assessment_id == Assessment.id)
            .all()
        )
        #assignments = AssessmentsStudent.query.all()
        print("Query executed successfully")  # Debugging statement
        for assignment in assignments:
            print(f"Assessment ID: {assignment.AssessmentsStudent.assessment_id}, Student ID: {assignment.AssessmentsStudent.student_id}, Mark: {assignment.AssessmentsStudent.marks} Type: {assignment.Assessment.type}")
        return render_template('updatestudentgrades.html', assignments=assignments, user=user)
    except Exception as e:
        print("Error:", e)  # This will print any database errors
        return "An error occurred", 500
    
@app.route('/viewanonfeedback', methods=['GET', 'POST'])
def viewanonfeedback():
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    # Handling POST request
    if request.method == 'POST':
        print("Received POST request")
        print("Form Data:", request.form)  # Debugging: print the form data
        
        # Process checkboxes and update the 'reviewed' field for each feedback
        for feedback in Feedback.query.all():
            checkbox_name = f"reviewed_{feedback.id}"
            if checkbox_name in request.form:
                print("reviewed")
                feedback.reviewed = 1  # Mark as reviewed if checked
            else:
                print("not reviewed")
                feedback.reviewed = 0  # Mark as not reviewed if unchecked
        
        db.session.commit()  # Save changes to the database
        print("Database updated with reviewed status")
    
    # Handling GET request (or after POST)
    feedbacks = Feedback.query.all()
    print("Query executed successfully")  # Debugging: check if query works
    for feedback in feedbacks:
        print(f"Feedback: {feedback.feedback}")
    
    # Always return the template with feedback data
    return render_template('viewanonfeedback.html', feedbacks=feedbacks, user=user)

@app.route('/viewremarkrequests', methods=['GET', 'POST'])
def viewremarkrequests():
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    return render_template('viewremarkrequests.html', user=user)

@app.route('/index')
def index():
    pagename='index'
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    print(username)
    print(user.user_id)
    print(user.user_type)
    print(user)
    return render_template('index.html', user=user)

# Registration, Login, and Logout
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method=='GET':
        return render_template('register.html')
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        user_name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # generating the hashed password
        hashed_password=bcrypt.generate_password_hash(password).decode('utf-8')
        user_type = int(request.form['user_type'])
        new_user = User(first_name=first_name, last_name=last_name, username=user_name, email=email, password=hashed_password, user_type=user_type)
        
        db.session.add_all([new_user])
        db.session.commit()
        # db.session.close()
        return redirect(url_for('login'))
    
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username = username).first()

        if not user or not bcrypt.check_password_hash(user.password, password):
            flash('Please check your login details and try again.', 'error')
            return render_template('login.html')
        else:
            session['name'] = user.username
            session.permanent=True
            if (user.user_type == 0 ): 
                flash(f"Welcome {user.first_name}! Click the Menu button to navigate to your grades.", 'succes')
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('name', default = None)
    return redirect(url_for('index'))

# Hannas Section
@app.route('/studentgrades')
def studentgrades():
    username = session['name']
    user = User.query.filter_by(username=username).first()

    if not user.user_type == 0:
        return render_template('viewstudentgrades.html') #temp, add prof grades
    
    if not user:
        return render_template('homepage.html')
    
    user_id = user.user_id

    r1 = (
        db.session.query(Assessment, AssessmentsStudent)
        .join(AssessmentsStudent, Assessment.assessment_id == AssessmentsStudent.assessment_id)
    )
    r2 = r1.filter(AssessmentsStudent.student_id == user_id)
    r3 = r2.all()

    grades= []
    labs = []
    exams = []

    for assessment, student_assessment in r3:
        grade_info = {
            'assessment_name': assessment.name,
            'grade': student_assessment.marks if student_assessment.marks is not None else 'Not Graded'
        }
        if "Midterm" in assessment.name or "Final" in assessment.name:
            exams.append(grade_info)
        elif "Lab" in assessment.name:
            labs.append(grade_info)
        else:
            grades.append(grade_info)

    return render_template('studentgrades.html', grades=grades, labs = labs, exams = exams, user=user)

# # NOTEE: DELETE EVERYTHING AFTER THIS BEFORE SUBMISSION
# # Inserting new users into the database
# instructor = User(username='jane_doe', email='jane@example.com', password='securepassword', user_type=1)  # INSTRUCTOR = 1
# student = User(username='john_doe', email='john@example.com', password='securepassword', user_type=0)  # STUDENT = 0
# session.add_all([instructor, student])
# session.commit()

# # Example: Add a new assessment
# assessment = Assessment(name="Math Exam", mark=100, instructor_id=instructor.id)
# session.add(assessment)
# session.commit()

# # Example: Add feedback from a student about the instructor
# feedback = Feedback(instructor_id=instructor.id, feedback="Great teacher, very clear explanations!")
# session.add(feedback)
# session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

