import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import random

# Page configuration
st.set_page_config(
    page_title="FE Portal 2024",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #145a8a;
    }
    .css-1d391kg {
        background-color: #1a1d24;
    }
    .stSelectbox {
        color: white;
    }
    .header-text {
        color: #4db8ff;
        font-size: 24px;
        font-weight: bold;
    }
    .info-box {
        background-color: #1a1d24;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .cheat-sheet {
        background-color: #2d3748;
        padding: 15px;
        border-radius: 8px;
        border: 2px solid #4db8ff;
        margin: 20px 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #052c65;
        border: 1px solid #1f77b4;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Syllabus Data Structure (Same as before)
SYLLABUS = {
    "Engineering Physics": {"chapters": ["Fundamentals of Photonics", "Quantum Physics", "Wave Optics", "Semiconductor Physics", "Nanoparticles"]},
    "Engineering Chemistry": {"chapters": ["Water Technology", "Instrumental Methods", "Advanced Materials", "Energy Sources", "Corrosion"]},
    "Basic Electrical Engineering": {"chapters": ["DC Circuits", "Electromagnetism", "AC Fundamentals", "AC Circuits", "Electric Machines"]},
    "Basic Electronics Engineering": {"chapters": ["Diodes", "Transistors", "Logic Gates", "Op-Amp", "Sensors"]},
    "Engineering Mechanics": {"chapters": ["Force Systems", "Equilibrium", "Friction", "Kinematics", "Kinetics"]},
    "Engineering Graphics": {"chapters": ["Drawing Fundamentals", "Projection of Plane", "Engineering Curves", "Orthographic Projection", "Isometric Projection"]},
    "Engineering Mathematics-I": {"chapters": ["Calculus", "Multivariable Calculus", "Partial Differentiation", "Matrices", "Eigen Values"]},
    "Engineering Mathematics-II": {"chapters": ["Integral Calculus", "Solid Geometry", "Multiple Integrals", "ODE", "Diff Eq Applications"]},
    "Fundamentals of Programming Languages": {"chapters": ["C Intro", "Operators", "Control Flow", "Arrays", "Functions"]},
    "Programming and Problem Solving": {"chapters": ["Python Intro", "Data Types", "Functions & Strings", "File Handling", "OOP"]},
    "Manufacturing Practice Workshop": {"chapters": ["Safety", "Cutting", "Sheet Metal", "CNC", "3D Printing"]}
}

# --- DATA GENERATION FUNCTIONS ---
def generate_student_data():
    students = {}
    for i in range(1, 26):
        students[f"student{i}"] = {
            "password": "pass123",
            "name": f"Student {i}",
            "roll_no": f"FE2024{str(i).zfill(3)}",
            "subjects": random.sample(list(SYLLABUS.keys()), 5),
            "marks": {},
            "attendance": random.randint(75, 95),
            "has_data": True
        }
        for subject in students[f"student{i}"]["subjects"]:
            students[f"student{i}"]["marks"][subject] = {
                "chapter_tests": [random.randint(6, 10) for _ in range(5)],
                "subject_assessment": random.randint(18, 30),
                "overall": random.randint(60, 95)
            }
    # Empty profiles
    for i in range(26, 31):
        students[f"student{i}"] = {
            "password": "pass123",
            "name": f"Student {i}",
            "roll_no": f"FE2024{str(i).zfill(3)}",
            "subjects": [],
            "marks": {},
            "attendance": 0,
            "has_data": False
        }
    return students

def generate_teacher_data():
    teachers = {}
    subjects = list(SYLLABUS.keys())
    for i in range(1, 12):
        teachers[f"teacher{i}"] = {
            "password": "teach123",
            "name": f"Prof. Teacher {i}",
            "subject": subjects[i-1] if i <= len(subjects) else subjects[0],
            "feedback_score": round(random.uniform(3.5, 4.8), 1),
            "feedback_comments": [
                {"comment": "Needs to explain concepts more clearly", "type": "negative"},
                {"comment": "Too fast in teaching", "type": "negative"},
                {"comment": "Great teaching methodology", "type": "positive"},
            ]
        }
    return teachers

# --- SESSION STATE INITIALIZATION ---
# This ensures data persists when you click buttons or register users
if 'students_data' not in st.session_state:
    st.session_state.students_data = generate_student_data()

if 'teachers_data' not in st.session_state:
    st.session_state.teachers_data = generate_teacher_data()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'selected_subjects' not in st.session_state:
    st.session_state.selected_subjects = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'

# MCQ Questions Bank (Static)
MCQ_BANK = {
    subject: [{"question": f"Sample question {i+1} for {subject}?", "options": ["Option A", "Option B", "Option C", "Option D"], "correct": random.randint(0, 3)} for i in range(30)] 
    for subject in SYLLABUS.keys()
}

# --- SIDEBAR ---
def render_sidebar():
    with st.sidebar:
        # Use your logo here (ensure logo.png is in the folder)
        try:
            st.image("logo.png", width=200)
        except:
            st.image("https://via.placeholder.com/200x100.png?text=FE+Portal+Logo", width=200)
            
        st.markdown("---")
        st.markdown("### 🎓 FE Portal 2024")
        st.markdown("**Created by**")
        st.markdown("**FE DIV-A 2025-26**")
        st.markdown("---")
        
        if st.session_state.logged_in:
            st.success(f"👤 {st.session_state.username}")
            st.info(f"🔖 {st.session_state.user_type.title()}")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_type = None
                st.session_state.username = None
                st.session_state.current_page = 'login'
                st.rerun()

# --- AUTHENTICATION PAGES ---

def login_register_page():
    st.markdown("<h1 style='text-align: center; color: #4db8ff;'>🎓 FE Engineering Portal 2024</h1>", unsafe_allow_html=True)
    
    # Cheat Sheet
    with st.expander("🔑 View Demo Credentials (Cheat Sheet)"):
        st.markdown("""
            **Student:** `student1` / `pass123`  
            **Teacher:** `teacher1` / `teach123`
        """)

    # Tabs for Login vs Register
    tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register New Account"])
    
    # --- LOGIN TAB ---
    with tab_login:
        role = st.radio("Select Role", ["Student", "Teacher"], horizontal=True)
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", use_container_width=True):
            if role == "Student":
                db = st.session_state.students_data
                if username in db and db[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user_type = "student"
                    st.session_state.username = username
                    st.session_state.current_page = 'subject_selection' if not db[username]['has_data'] else 'student_dashboard'
                    if db[username]['has_data']:
                        st.session_state.selected_subjects = db[username]['subjects']
                    st.rerun()
                else:
                    st.error("Invalid Student credentials")
            else:
                db = st.session_state.teachers_data
                if username in db and db[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user_type = "teacher"
                    st.session_state.username = username
                    st.session_state.current_page = 'teacher_dashboard'
                    st.rerun()
                else:
                    st.error("Invalid Teacher credentials")

    # --- REGISTRATION TAB ---
    with tab_register:
        st.markdown("### Create New Account")
        reg_role = st.selectbox("I am a...", ["Student", "Teacher"])
        reg_name = st.text_input("Full Name")
        reg_user = st.text_input("Choose Username")
        reg_pass = st.text_input("Choose Password", type="password")
        
        # Specific fields based on role
        extra_data = {}
        if reg_role == "Teacher":
            reg_subject = st.selectbox("Subject you teach", list(SYLLABUS.keys()))
            extra_data['subject'] = reg_subject
        else:
            reg_roll = st.text_input("Roll Number (e.g., FE2024099)")
            extra_data['roll_no'] = reg_roll

        if st.button("Create Account", use_container_width=True):
            if reg_user and reg_pass and reg_name:
                if reg_role == "Student":
                    if reg_user in st.session_state.students_data:
                        st.error("Username already exists!")
                    else:
                        # Add new student to session state
                        st.session_state.students_data[reg_user] = {
                            "password": reg_pass,
                            "name": reg_name,
                            "roll_no": extra_data['roll_no'],
                            "subjects": [],
                            "marks": {},
                            "attendance": 0,
                            "has_data": False # Flags them as new user
                        }
                        st.success("✅ Student Account Created! Go to Login tab.")
                
                elif reg_role == "Teacher":
                    if reg_user in st.session_state.teachers_data:
                        st.error("Username already exists!")
                    else:
                        # Add new teacher to session state
                        st.session_state.teachers_data[reg_user] = {
                            "password": reg_pass,
                            "name": reg_name,
                            "subject": extra_data['subject'],
                            "feedback_score": 0.0,
                            "feedback_comments": []
                        }
                        st.success("✅ Teacher Account Created! Go to Login tab.")
            else:
                st.warning("Please fill all fields.")

# --- STUDENT PAGES ---

def subject_selection_page():
    st.markdown("<h2 class='header-text'>📚 Select Your 5 Subjects</h2>", unsafe_allow_html=True)
    
    student = st.session_state.students_data[st.session_state.username]
    
    # If student already has subjects, skip this page (double check)
    if student['has_data'] and len(student['subjects']) > 0:
        st.session_state.selected_subjects = student['subjects']
        st.session_state.current_page = 'student_dashboard'
        st.rerun()
        
    all_subjects = list(SYLLABUS.keys())
    col1, col2 = st.columns(2)
    with col1:
        group1 = st.selectbox("Group 1", ["Engineering Physics", "Basic Electrical Engineering", "Engineering Mechanics"])
    with col2:
        group2 = st.selectbox("Group 2", ["Engineering Chemistry", "Basic Electronics Engineering", "Engineering Graphics"])
    
    math = st.selectbox("Mathematics", ["Engineering Mathematics-I", "Engineering Mathematics-II"])
    prog = st.selectbox("Programming", ["Fundamentals of Programming Languages", "Programming and Problem Solving"])
    work = "Manufacturing Practice Workshop"
    
    selected = [group1, group2, math, prog, work]
    
    if st.button("Confirm Subjects", use_container_width=True):
        # Update student data in session state
        st.session_state.students_data[st.session_state.username]['subjects'] = selected
        st.session_state.students_data[st.session_state.username]['has_data'] = True
        st.session_state.selected_subjects = selected
        st.session_state.current_page = 'student_dashboard'
        st.rerun()

def student_dashboard():
    st.markdown("<h2 class='header-text'>🎯 Student Dashboard</h2>", unsafe_allow_html=True)
    student = st.session_state.students_data[st.session_state.username]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Name", student['name'])
    col2.metric("Roll No", student['roll_no'])
    col3.metric("Attendance", f"{student['attendance']}%")
    
    st.write(f"**Registered Subjects:** {', '.join(st.session_state.selected_subjects)}")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Assessment", use_container_width=True):
            st.session_state.current_page = 'assessment'
            st.rerun()
    with col2:
        if st.button("🤖 AI Assistant", use_container_width=True):
            st.session_state.current_page = 'ai_assistant'
            st.rerun()

def assessment_page():
    st.markdown("<h2 class='header-text'>📝 Assessment</h2>", unsafe_allow_html=True)
    if st.button("⬅️ Back"):
        st.session_state.current_page = 'student_dashboard'
        st.rerun()
        
    subject = st.selectbox("Select Subject", st.session_state.selected_subjects)
    a_type = st.radio("Type", ["Chapter Assessment", "Subject Assessment"])
    
    if a_type == "Chapter Assessment":
        chapter = st.selectbox("Chapter", SYLLABUS[subject]["chapters"])
        marks, mins, q_count = 10, 10, 10
    else:
        chapter = "All Chapters"
        marks, mins, q_count = 30, 30, 30
        
    if st.button("Start Assessment", use_container_width=True):
        st.session_state.quiz_data = {
            'subject': subject, 'chapter': chapter, 'marks': marks, 'duration': mins,
            'num_questions': q_count, 'start_time': datetime.now(),
            'questions': random.sample(MCQ_BANK[subject], min(q_count, len(MCQ_BANK[subject])))
        }
        st.session_state.current_page = 'quiz'
        st.rerun()

def quiz_page():
    quiz = st.session_state.quiz_data
    st.markdown(f"### {quiz['subject']} - {quiz['chapter']}")
    
    # Simple Timer logic (Visual only for demo)
    elapsed = (datetime.now() - quiz['start_time']).seconds
    st.progress(min(elapsed / (quiz['duration'] * 60), 1.0))
    
    answers = {}
    for i, q in enumerate(quiz['questions']):
        st.write(f"**Q{i+1}. {q['question']}**")
        answers[i] = st.radio(f"Select answer {i}", q['options'], key=f"q_{i}", label_visibility="collapsed")
        st.markdown("---")
        
    if st.button("Submit Assessment", use_container_width=True):
        # Calculate dummy score
        score = sum([1 for i in range(len(quiz['questions'])) if random.choice([True, False])]) # Randomized for demo
        st.session_state.quiz_score = score
        st.session_state.current_page = 'feedback_form'
        st.rerun()

def feedback_form_page():
    st.markdown("### 📋 Mandatory Teacher Feedback")
    st.info("Rate the teacher before seeing results.")
    
    c1, c2 = st.columns(2)
    with c1: st.slider("Teaching Quality", 1, 5, 3)
    with c2: st.slider("Clarity", 1, 5, 3)
    
    if st.button("Submit & View Results"):
        st.balloons()
        st.success(f"You scored: {st.session_state.quiz_score} / {st.session_state.quiz_data['num_questions']}")
        
        # Save score to student data in session state
        subject = st.session_state.quiz_data['subject']
        student = st.session_state.students_data[st.session_state.username]
        
        # Initialize marks dict if new
        if subject not in student['marks']:
            student['marks'][subject] = {'chapter_tests': [], 'subject_assessment': 0, 'overall': 0}
            
        if st.session_state.quiz_data['chapter'] != "All Chapters":
            student['marks'][subject]['chapter_tests'].append(st.session_state.quiz_score)
        else:
            student['marks'][subject]['subject_assessment'] = st.session_state.quiz_score
            
        time.sleep(2)
        st.session_state.current_page = 'student_dashboard'
        st.rerun()

def ai_assistant_page():
    st.markdown("### 🤖 AI Assistant")
    if st.button("⬅️ Back"): st.session_state.current_page = 'student_dashboard'; st.rerun()
    
    tab1, tab2 = st.tabs(["Ask Question", "Quiz Maker"])
    with tab1:
        st.file_uploader("Upload PDF")
        if st.text_input("Ask a question"):
            st.info("AI: Based on the syllabus, this concept refers to...")
    with tab2:
        if st.button("Generate Practice Quiz"):
            st.success("Quiz generated below (Mock)...")

# --- TEACHER PAGES ---

def teacher_dashboard():
    st.markdown("## 👨‍🏫 Teacher Dashboard")
    teacher = st.session_state.teachers_data[st.session_state.username]
    
    c1, c2 = st.columns(2)
    c1.metric("Name", teacher['name'])
    c2.metric("Subject", teacher['subject'])
    
    if st.button("Student Profiles"): st.session_state.current_page = 'student_profiles'; st.rerun()
    if st.button("Feedback"): st.session_state.current_page = 'teacher_feedback'; st.rerun()
    if st.button("AI Tools"): st.session_state.current_page = 'teacher_ai'; st.rerun()

def student_profiles_page():
    st.markdown("### 📊 Student Profiles")
    if st.button("⬅️ Back"): st.session_state.current_page = 'teacher_dashboard'; st.rerun()
    
    teacher = st.session_state.teachers_data[st.session_state.username]
    subject = teacher['subject']
    
    # Filter students taking this subject
    students_in_sub = {uid: data for uid, data in st.session_state.students_data.items() if subject in data['subjects']}
    
    if not students_in_sub:
        st.warning(f"No students enrolled in {subject} yet.")
    else:
        sel_id = st.selectbox("Select Student", list(students_in_sub.keys()), format_func=lambda x: students_in_sub[x]['name'])
        s_data = students_in_sub[sel_id]
        
        st.write(f"**Analysis for {s_data['name']}**")
        
        # Mock Charts
        if subject in s_data['marks']:
            marks = s_data['marks'][subject].get('chapter_tests', [0])
            st.bar_chart(marks)
        else:
            st.info("No test data for this subject yet.")

def teacher_feedback_page():
    st.markdown("### 💬 Feedback")
    if st.button("⬅️ Back"): st.session_state.current_page = 'teacher_dashboard'; st.rerun()
    teacher = st.session_state.teachers_data[st.session_state.username]
    st.write(f"Net Score: {teacher['feedback_score']}/5.0")
    for comm in teacher['feedback_comments']:
        st.error(f"{comm['comment']}") if comm['type'] == 'negative' else st.success(f"{comm['comment']}")

def teacher_ai_page():
    st.markdown("### 🤖 Teacher AI Tools")
    if st.button("⬅️ Back"): st.session_state.current_page = 'teacher_dashboard'; st.rerun()
    st.info("AI Tools for generating content and questions (Mock Interface).")

# --- MAIN CONTROLLER ---

def main():
    render_sidebar()
    
    if not st.session_state.logged_in:
        login_register_page()
    else:
        # Route pages based on user type
        if st.session_state.user_type == "student":
            if st.session_state.current_page == 'subject_selection': subject_selection_page()
            elif st.session_state.current_page == 'student_dashboard': student_dashboard()
            elif st.session_state.current_page == 'assessment': assessment_page()
            elif st.session_state.current_page == 'quiz': quiz_page()
            elif st.session_state.current_page == 'feedback_form': feedback_form_page()
            elif st.session_state.current_page == 'ai_assistant': ai_assistant_page()
            
        elif st.session_state.user_type == "teacher":
            if st.session_state.current_page == 'teacher_dashboard': teacher_dashboard()
            elif st.session_state.current_page == 'student_profiles': student_profiles_page()
            elif st.session_state.current_page == 'teacher_feedback': teacher_feedback_page()
            elif st.session_state.current_page == 'teacher_ai': teacher_ai_page()

if __name__ == "__main__":
    main()
