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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    first_name = Column(db.String(100))
    # 0 = student, 1 = instructor
    user_type = Column(db.Integer, nullable=False)

    # Connecting feedback to the instructor
    instr_feedback = relationship("Feedback", back_populates="instr_to_feedback")


# Table for different types of assessments
class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    mark = db.Column(db.Integer)

    # Connecting assessment with the instructor
    instructor_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)

# Table with the students and their corresponding assessments
class AssessmentsStudent(db.Model):
    __tablename__ = 'student_assessments'
    student_id = db.Column(db.Integer, ForeignKey('users.id'), primary_key=True)
    assessment_id = db.Column(db.Integer, ForeignKey('assessments.id'), primary_key=True)
    marks = db.Column(db.Integer, nullable=True)
    # default is NULL, 0 = pending, 1 = approved, 2 = rejected
    remark_status = db.Column(db.Integer, nullable=True)
    remark_reason = db.Column(db.String(500), nullable=True)

    # Connecting students to their assessments
    student_to_assess = relationship("User", backref="student_assessments")
    assess_to_student = relationship("Assessment", backref="student_assessments")


# Table for feedback (anonymous feedback from students to instructors)
class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    instructor_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    feedback = db.Column(db.String, nullable=False)
    reviewed = db.Column(db.Integer, nullable=False, default=0)

    # Connecting the feedback to an instructor
    instr_to_feedback = relationship("User", back_populates="instr_feedback")


# Create the tables in the database
# Base.metadata.create_all(engine)

# REndering the pages to make the dropdown work
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/syllabus')
def syllabus():
    return render_template('syllabus.html')

@app.route('/assignments')
def assignments():
    return render_template('assignments.html')

@app.route('/lab')
def lab():
    return render_template('lab.html')

@app.route('/lecturenotes')
def lecturenotes():
    return render_template('lecturenotes.html')

@app.route('/piazza')
def piazza():
    return render_template('piazza.html')

@app.route('/markus')
def markus():
    return redirect("https://markus2.utsc.utoronto.ca/")

@app.route('/anonfeedback')
def anonfeedback():
    return render_template('anonfeedback.html')

@app.route('/courseteam')
def courseteam():
    return render_template('courseteam.html')

@app.route('/viewstudentgrades')
def viewstudentgrades():
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
        return render_template('viewstudentgrades.html', assignments=assignments)
    except Exception as e:
        print("Error:", e)  # This will print any database errors
        return "An error occurred", 500
    
@app.route('/updatestudentgrades')
def updatestudentgrades():
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
        return render_template('updatestudentgrades.html', assignments=assignments)
    except Exception as e:
        print("Error:", e)  # This will print any database errors
        return "An error occurred", 500
    
@app.route('/viewanonfeedback', methods=['GET', 'POST'])
def viewanonfeedback():
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
    return render_template('viewanonfeedback.html', feedbacks=feedbacks)


# Registration, Login, and Logout
@app.route('/')
@app.route('/index')
def index():
    pagename='index'
    return render_template('index.html', pagename=pagename)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method=='GET':
        return render_template('register.html')
    else:
        user_name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # generating the hashed password
        hashed_password=bcrypt.generate_password_hash(password).decode('utf-8')
        user_type = int(request.form['user_type'])
        new_user = User(username=user_name, email=email, password=hashed_password, user_type=user_type)
        
        db.session.add_all([new_user])
        db.session.commit()
        db.session.close()

        flash('registration successful! Please login now:')
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
            log_details = (
            username,
            password
            )
           # session['username']=username
            session['username'] = username
            session.permanent=True
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('name', default = None)
    return redirect(url_for('index'))

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

