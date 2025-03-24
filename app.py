from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Creating an engine that will connect to the SQLite database
engine = create_engine('sqlite:///assignment3.db')

# Session setup
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# Table for the users
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    first_name = Column(String(100))
    # 0 = student, 1 = instructor
    user_type = Column(Integer, nullable=False)

    # Connecting feedback to the instructor
    instr_feedback = relationship("Feedback", back_populates="instr_to_feedback")


# Table for different types of assessments
class Assessment(Base):
    __tablename__ = 'assessments'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    mark = Column(Integer)

    # Connecting assessment with the instructor
    instructor_id = Column(Integer, ForeignKey('users.id'), nullable=False)

# Table with the students and their corresponding assessments
class AssessmentsStudent(Base):
    __tablename__ = 'student_assessments'
    student_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    assessment_id = Column(Integer, ForeignKey('assessments.id'), primary_key=True)
    marks = Column(Integer, nullable=True)
    # default is NULL, 0 = pending, 1 = approved, 2 = rejected
    remark_status = Column(Integer, nullable=True)
    remark_reason = Column(String(500), nullable=True)

    # Connecting students to their assessments
    student_to_assess = relationship("User", backref="student_assessments")
    assess_to_student = relationship("Assessment", backref="student_assessments")


# Table for feedback (anonymous feedback from students to instructors)
class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True, autoincrement=True)
    instructor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    feedback = Column(String, nullable=False)

    # Connecting the feedback to an instructor
    instr_to_feedback = relationship("User", back_populates="instr_feedback")


# Create the tables in the database
Base.metadata.create_all(engine)

# NOTEE: DELETE EVERYTHING AFTER THIS BEFORE SUBMISSION
# Inserting new users into the database
'''
instructor = User(username='jane_doe', email='jane@example.com', password='securepassword', user_type=1)  # INSTRUCTOR = 1
student = User(username='john_doe', email='john@example.com', password='securepassword2', user_type=0)  # STUDENT = 0
session.add_all([instructor, student])
session.commit()

# Example: Add a new assessment
assessment = Assessment(name="Math Exam", mark=100, instructor_id=instructor.id)
session.add(assessment)
session.commit()

# Example: Add feedback from a student about the instructor
feedback = Feedback(instructor_id=instructor.id, feedback="Great teacher, very clear explanations!")
session.add(feedback)
session.commit()

# Close the session once done
session.close()
'''

