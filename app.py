import sqlalchemy as db
from sqlalchemy import Column, ForeignKey, create_engine
from datetime import timedelta
from sqlalchemy.dialects.sqlite import *
from sqlalchemy.orm import relationship, declarative_base
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
    details = db.Column(db.String)
    # Connecting assessment with the instructor
    instructor_id = db.Column(db.Integer, ForeignKey('users.user_id'), nullable=False)

# Table with the students and their corresponding assessments
class AssessmentsStudent(db.Model):
    __tablename__ = 'student_assessments'
    user_id = db.Column(db.Integer, ForeignKey('users.user_id'), primary_key=True)
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
    feedback_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    instructor_id = db.Column(db.Integer, ForeignKey('users.user_id'), nullable=False)
    feedback_inst_1 = db.Column(db.String, nullable=False)
    feedback_inst_2 = db.Column(db.String, nullable=False)
    feedback_lab_1 = db.Column(db.String, nullable=False)
    feedback_lab_2 = db.Column(db.String, nullable=False)
    reviewed = db.Column(db.Integer, nullable=False, default=0)

    # Connecting the feedback to an instructor
    instr_to_feedback = relationship("User", back_populates="instr_feedback")
    
class RemarkRequests(db.Model):
    __tablename__ = 'remarkrequests'
    remark_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assessment_id = db.Column(db.Integer, ForeignKey('assessments.assessment_id'), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.user_id'), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=0)
    remark_reason = db.Column(db.String(500), nullable=True)

    # Connecting the feedback to an instructor
    remark_to_user = relationship("User", backref='remarkrequests')
    remark_to_assessment = relationship("Assessment", backref='remarkrequests')


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
    return render_template('assignments.html', user=user)


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
    return redirect("https://markus2.utsc.utoronto.ca/")

@app.route('/anonfeedback', methods = ['GET', 'POST'])
def anonfeedback():
    username = session['name']
    user = User.query.filter_by(username=username).first()

    if not user.user_type == 0:
        return render_template('viewanonfeedback.html') 

    if not user:
        return render_template('homepage.html')

    professors = User.query.filter_by(user_type=1).all()
    if request.method == "POST":
        professor_id = request.form.get('professor')

        instruct_feed = request.form.get('instruct_feed')
        instruct_tips = request.form.get('instruct_tips')
        lab_feed = request.form.get('lab_feed')
        lab_tips = request.form.get('lab_tips')

        if not professor_id:
            flash('Please select a Professor.', 'warning')

        elif not instruct_feed or not instruct_tips or not lab_feed or not lab_tips:
            flash('Please provide at least one piece of feedback per section.', 'warning')

        else:   
            new_feedback = Feedback(
                instructor_id = professor_id,
                feedback_inst_1 = instruct_feed,
                feedback_inst_2 = instruct_tips,
                feedback_lab_1 = lab_feed,
                feedback_lab_2 = lab_tips
                )

            db.session.add(new_feedback)
            db.session.commit()
            flash('Your feedback has been submitted successfully!', 'success')

            return render_template('anonfeedback.html', success=True, professors=professors, user=user)
            

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
    assessments = Assessment.query.all()
    students = User.query.filter_by(user_type=0).all()
    
    for assessment in assessments:
        for student in students:
            # Determine if student already assigned to an assessment
            existing_assignment = AssessmentsStudent.query.filter_by(
                user_id=student.user_id,
                assessment_id=assessment.assessment_id
            ).first()
            
            if not existing_assignment:
                # assign assessment to student if not already
                new_assignment = AssessmentsStudent(
                    user_id=student.user_id,
                    assessment_id=assessment.assessment_id,
                    marks=None
                )
                db.session.add(new_assignment)
                db.session.commit() 
                
    try:
        assignments = (
            db.session.query(AssessmentsStudent, Assessment)
            .join(Assessment, AssessmentsStudent.assessment_id == Assessment.assessment_id)
            .join(User, AssessmentsStudent.user_id == User.user_id)
            .add_entity(User)
            .all()
        )
        
        return render_template('viewstudentgrades.html', assignments=assignments, user=user)
    except Exception as e:
        return "An error occurred", 500
    
@app.route('/updatestudentgrades', methods=['GET', 'POST'])
def updatestudentgrades():
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    
    assessments = Assessment.query.all()
    students = User.query.filter_by(user_type=0).all()
    assignments = db.session.query(AssessmentsStudent).join(User, User.user_id == AssessmentsStudent.user_id).join(Assessment, Assessment.assessment_id == AssessmentsStudent.assessment_id).all()
    
    for assessment in assessments:
        for student in students:
            # Determine if student is assigned this assessment
            existing_assignment = AssessmentsStudent.query.filter_by(
                user_id=student.user_id,
                assessment_id=assessment.assessment_id
            ).first()
            
            if not existing_assignment:
                # assign them the assessment, if not already
                new_assignment = AssessmentsStudent(
                    user_id=student.user_id,
                    assessment_id=assessment.assessment_id,
                    marks=None
                )
                db.session.add(new_assignment)
                db.session.commit() 
    
    if request.method == 'POST':
        for assignment in assignments:
            input_name = f"reviewed_{assignment.user_id}_{assignment.assessment_id}"  
            new_mark = request.form.get(input_name)  
            
            if new_mark is None or new_mark.strip() == '':  
                assignment.marks = None 
            else:
                try:
                    new_mark = int(new_mark)  

                    # Check if the mark is within the valid range
                    if 0 <= new_mark <= 100:
                        assignment.marks = new_mark
                    else:
                        flash("Marks must be between 0 and 100.", "error")
                        return redirect(url_for('updatestudentgrades'))

                except ValueError:
                    flash("Invalid mark entered. Please enter a valid number.", "error")
                    return redirect(url_for('updatestudentgrades')) 
        
        db.session.commit() 
        flash("Marks updated successfully!", "success")
        return redirect(url_for('updatestudentgrades'))

    return render_template('updatestudentgrades.html', user=user, assignments=assignments)
    
@app.route('/viewanonfeedback', methods=['GET', 'POST'])
def viewanonfeedback():
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    if request.method == 'POST':
        
        for feedback in Feedback.query.all():
            checkbox_name = f"reviewed_{feedback.feedback_id}"

            if checkbox_name in request.form:
                feedback.reviewed = 1
            else:
                feedback.reviewed = 0
        
        db.session.commit() 
            
    feedbacks = Feedback.query.filter(Feedback.instructor_id==user.user_id).all()
    
    return render_template('viewanonfeedback.html', feedbacks=feedbacks, user=user)

@app.route('/viewremarkrequests', methods=['GET', 'POST'])
def viewremarkrequests():
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    
    if request.method == 'POST':
        # Loop over each remark request in the form
        for remark in RemarkRequests.query.all():
            remark_status = request.form.get(f'reviewed_{remark.remark_id}') 

            if remark_status == '1':
                remark.status = 1 
            elif remark_status == '2':
                remark.status = 2
            else:
                remark.status = 0

        db.session.commit()
            
    feedbacks = Feedback.query.all()
    
    requests = db.session.query(RemarkRequests).join(User, User.user_id == RemarkRequests.user_id).all()
    
    return render_template('viewremarkrequests.html', requests=requests, user=user)


@app.route('/createassessment', methods=['GET', 'POST'])
def createassessment():
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
    if not username:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        assignment_name = request.form.get('assignment_name')
        assignment_type = request.form.get('assignment_type')
        assignment_details = request.form.get('assignment_details')
        instructor_id = user.user_id
        existing_assignment = Assessment.query.filter_by(name=assignment_name).first()
        
        if not assignment_name or not instructor_id:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for('createassessment'))
        elif existing_assignment:
            flash("This assignment name already exists.", "error")
            return redirect(url_for('createassessment'))
        elif assignment_type not in ["Assignment", "Test", "Lab"]:
            flash("The Assignment Type must be either 'Assignment', 'Test', or 'Lab'", "error")
            return redirect(url_for('createassessment'))

        try:
            with db.session.no_autoflush:
                    
                new_assessment = Assessment(
                    name=assignment_name,
                    type=assignment_type,
                    instructor_id=instructor_id,
                    details=assignment_details
                )
                db.session.add(new_assessment)
                db.session.flush()

                students = User.query.filter_by(user_type=0).all()
                for student in students:
                    student_assignment = AssessmentsStudent(
                        user_id=student.user_id,
                        assessment_id=new_assessment.assessment_id,
                        marks=None
                    )
                    db.session.add(student_assignment)

            db.session.commit()
            flash("Assessment created successfully!", "success")

        except Exception as e:
            db.session.rollback()
            flash("Error creating assessment: {str(e)}", "error")
    
    return render_template('createassessment.html', user=user)

@app.route('/index')
def index():
    pagename='index'
    username = session.get('name')
    user = User.query.filter_by(username=username).first()
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

        # Checking if the username has already been used
        existing_user = User.query.filter_by(username=user_name).first()

        # Display an error if the username is taken
        if existing_user:
            flash('This username is already taken.', 'error')
            return redirect(url_for('register'))

        # Checking if the email has already been used
        existing_email = User.query.filter_by(email=email).first()

        # Display an error if the email is taken
        if existing_email:
            flash('This email is already being used.', 'error')
            return redirect(url_for('register'))


        new_user = User(first_name=first_name, last_name=last_name, username=user_name, email=email, password=hashed_password, user_type=user_type)
        
        db.session.add_all([new_user])
        db.session.commit()

        return redirect(url_for('login'))
    
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        email  = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(username = username).first()
        email = User.query.filter_by(email = email).first()

        if not user or not email or not bcrypt.check_password_hash(user.password, password):
            flash('Please check your login details and try again.', 'error')
            return render_template('login.html')
        else:
            session['name'] = user.username
            session.permanent=True
            if (user.user_type == 0 ): 
                flash(f"Welcome {user.first_name}! Click the Menu button to navigate to your grades.", 'success')
            elif (user.user_type == 1 ):
                flash(f"Welcome instructor {user.first_name}! Click the Menu button to see all the grades of your class.", 'succes')
            
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()  
        flash('You have been logged out.', 'success')
        return redirect(url_for('homepage')) 



@app.route('/studentgrades', methods=['GET', 'POST'])
def studentgrades():
    username = session['name']
    user = User.query.filter_by(username=username).first()
    
    assessments = Assessment.query.all()
    
    for assessment in assessments:
        existing_assignment = AssessmentsStudent.query.filter_by(
                user_id=user.user_id,
                assessment_id=assessment.assessment_id
            ).first() 
        
        if not existing_assignment:
                new_assignment = AssessmentsStudent(
                    user_id=user.user_id,
                    assessment_id=assessment.assessment_id,
                    marks=None
                )
                db.session.add(new_assignment)
                db.session.commit()

    if not user.user_type == 0:
        return render_template('viewstudentgrades.html') 
    
    if not user:
        return render_template('homepage.html')
    
    user_id = user.user_id

    r1 = (
        db.session.query(Assessment, AssessmentsStudent)
        .join(AssessmentsStudent, Assessment.assessment_id == AssessmentsStudent.assessment_id)
    )
    r2 = r1.outerjoin(RemarkRequests, AssessmentsStudent.remark_id == RemarkRequests.remark_id)
    r3 = r2.filter(AssessmentsStudent.user_id == user_id)
    r4 = r3.add_columns(RemarkRequests) 
    r5 = r4.all()

    grades= []
    labs = []
    exams = []

    for assessment, student_assessment, remark_request in r5:
        grade_info = {
            'assessment_name': assessment.name,
            'assessment_id': assessment.assessment_id,
            'marks': student_assessment.marks if student_assessment.marks is not None else 'Not Graded',
            'remark_status': remark_request.status if remark_request else "No Remark Requested",
            'user_id': user_id
        }
        if assessment.type == "Test":
            exams.append(grade_info)

        elif assessment.type == "Lab":
            labs.append(grade_info)

        else:
            grades.append(grade_info)

    if request.method == 'POST':
        for assessment in assessments:
            assessment_id = str(assessment.assessment_id)  
            remark_reason = request.form.get(assessment_id)  

            if remark_reason: 
                new_remark_request = RemarkRequests(
                    assessment_id=assessment.assessment_id,
                    user_id=user.user_id,
                    status=0, 
                    remark_reason=remark_reason
                )
                db.session.add(new_remark_request)
                db.session.commit()

                new_remark_request_id = new_remark_request.remark_id  

                existing_assignment = AssessmentsStudent.query.filter_by(
                    user_id=user.user_id,
                    assessment_id=assessment.assessment_id
                ).first()

                if existing_assignment:
                    existing_assignment.remark_id = new_remark_request_id
                    db.session.commit()

                flash('Regrade request submitted successfully!', 'success')
                return redirect(url_for('studentgrades'))



    return render_template('studentgrades.html', grades=grades, labs = labs, exams = exams, user=user)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

    