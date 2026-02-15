import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import random

# --- CONFIGURATION ---
st.set_page_config(
    page_title="FE Portal 2024",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .header-text {
        color: #4db8ff;
        font-weight: bold;
    }
    .success-box {
        padding: 10px;
        background-color: rgba(0, 255, 0, 0.1);
        border: 1px solid green;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SYLLABUS DATA ---
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

# --- DATA GENERATION ---
def generate_student_data():
    students = {}
    for i in range(1, 26):
        username = f"student{i}"
        students[username] = {
            "password": "pass123",
            "name": f"Student {i}",
            "roll_no": f"FE2024{str(i).zfill(3)}",
            "subjects": random.sample(list(SYLLABUS.keys()), 5),
            "marks": {},
            "attendance": random.randint(75, 95),
            "has_data": True
        }
        # Pre-fill some marks
        for sub in students[username]["subjects"]:
            students[username]["marks"][sub] = {
                "chapter_tests": [random.randint(5, 10) for _ in range(5)],
                "subject_assessment": random.randint(15, 30),
                "overall": random.randint(60, 95)
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
                {"comment": "Great teaching methodology", "type": "positive"},
                {"comment": "Class pace is perfect", "type": "positive"},
                {"comment": "Handwriting on board is unclear", "type": "negative"}
            ]
        }
    return teachers

# --- MOCK QUESTION GENERATOR ---
def get_mock_questions(subject, count):
    questions = []
    for i in range(count):
        # Randomized correct option to prevent "Option A" always being correct
        options = ["Option A (Incorrect)", "Option B (Incorrect)", "Option C (Correct)", "Option D (Incorrect)"]
        random.shuffle(options)
        correct_opt = next(opt for opt in options if "(Correct)" in opt)
        correct_idx = options.index(correct_opt)
        
        # Clean up options for display
        clean_options = [o.replace(" (Correct)", "").replace(" (Incorrect)", "") for o in options]
        
        questions.append({
            "question": f"Mock Question {i+1} for {subject}: What is the primary concept of...?",
            "options": clean_options,
            "correct_index": correct_idx,
            "correct_answer": clean_options[correct_idx]
        })
    return questions

# --- SESSION STATE SETUP ---
if 'students_data' not in st.session_state: st.session_state.students_data = generate_student_data()
if 'teachers_data' not in st.session_state: st.session_state.teachers_data = generate_teacher_data()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_type' not in st.session_state: st.session_state.user_type = None
if 'username' not in st.session_state: st.session_state.username = None
if 'current_page' not in st.session_state: st.session_state.current_page = 'login'
if 'selected_subjects' not in st.session_state: st.session_state.selected_subjects = []

# --- SIDEBAR ---
def render_sidebar():
    with st.sidebar:
        try:
            st.image("logo.png", width=200)
        except:
            st.write("FE Portal Logo") # Fallback if image missing
            
        st.markdown("---")
        st.markdown("### 🎓 FE Portal 2024")
        st.caption("Created by FE DIV-A 2025-26")
        
        if st.session_state.logged_in:
            st.success(f"👤 {st.session_state.username}")
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.current_page = 'login'
                st.rerun()

# --- LOGIN / REGISTER ---
def login_register_page():
    st.markdown("<h1 style='text-align: center; color: #4db8ff;'>🎓 FE Engineering Portal 2024</h1>", unsafe_allow_html=True)
    
    with st.expander("🔑 Cheat Sheet (Demo Users)"):
        st.code("Student: student1 / pass123\nTeacher: teacher1 / teach123")

    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        role = st.radio("Login As", ["Student", "Teacher"], horizontal=True)
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        
        if st.button("Login"):
            db = st.session_state.students_data if role == "Student" else st.session_state.teachers_data
            if u in db and db[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user_type = role.lower()
                st.session_state.username = u
                
                if role == "Student":
                    # Check if subjects selected
                    if db[u]['has_data'] and db[u]['subjects']:
                        st.session_state.selected_subjects = db[u]['subjects']
                        st.session_state.current_page = 'student_dashboard'
                    else:
                        st.session_state.current_page = 'subject_selection'
                else:
                    st.session_state.current_page = 'teacher_dashboard'
                st.rerun()
            else:
                st.error("Invalid Credentials")

    with tab2:
        r_role = st.selectbox("Role", ["Student", "Teacher"])
        r_name = st.text_input("Full Name")
        r_user = st.text_input("New Username")
        r_pass = st.text_input("New Password", type="password")
        
        extra = {}
        if r_role == "Teacher":
            extra['sub'] = st.selectbox("Subject", list(SYLLABUS.keys()))
        else:
            extra['roll'] = st.text_input("Roll No")
            
        if st.button("Create Account"):
            target_db = st.session_state.teachers_data if r_role == "Teacher" else st.session_state.students_data
            if r_user in target_db:
                st.error("Username taken")
            else:
                if r_role == "Student":
                    target_db[r_user] = {
                        "password": r_pass, "name": r_name, "roll_no": extra['roll'],
                        "subjects": [], "marks": {}, "attendance": 0, "has_data": False
                    }
                else:
                    target_db[r_user] = {
                        "password": r_pass, "name": r_name, "subject": extra['sub'],
                        "feedback_score": 0.0, "feedback_comments": []
                    }
                st.success("Account Created! Please Login.")

# --- STUDENT WORKFLOW ---
def subject_selection_page():
    st.title("📚 Select 5 Subjects")
    
    c1, c2 = st.columns(2)
    with c1: g1 = st.selectbox("Group 1", ["Engineering Physics", "Basic Electrical Engineering", "Engineering Mechanics"])
    with c2: g2 = st.selectbox("Group 2", ["Engineering Chemistry", "Basic Electronics Engineering", "Engineering Graphics"])
    
    math = st.selectbox("Mathematics", ["Engineering Mathematics-I", "Engineering Mathematics-II"])
    prog = st.selectbox("Programming", ["Fundamentals of Programming Languages", "Programming and Problem Solving"])
    work = "Manufacturing Practice Workshop"
    
    if st.button("Confirm Selection"):
        st.session_state.students_data[st.session_state.username]['subjects'] = [g1, g2, math, prog, work]
        st.session_state.students_data[st.session_state.username]['has_data'] = True
        st.session_state.selected_subjects = [g1, g2, math, prog, work]
        st.session_state.current_page = 'student_dashboard'
        st.rerun()

def student_dashboard():
    st.title("🎯 Student Dashboard")
    data = st.session_state.students_data[st.session_state.username]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Name", data['name'])
    c2.metric("Roll No", data['roll_no'])
    c3.metric("Attendance", f"{data['attendance']}%")
    
    st.subheader("Your Subjects")
    st.write(", ".join(st.session_state.selected_subjects))
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📝 Take Assessment"): st.session_state.current_page = 'assessment'; st.rerun()
    with c2:
        if st.button("🤖 AI Assistant"): st.session_state.current_page = 'student_ai'; st.rerun()

def assessment_page():
    st.title("📝 Assessment")
    if st.button("⬅️ Back"): st.session_state.current_page = 'student_dashboard'; st.rerun()
    
    sub = st.selectbox("Subject", st.session_state.selected_subjects)
    a_type = st.radio("Mode", ["Chapter Wise", "Full Subject"])
    
    if a_type == "Chapter Wise":
        chap = st.selectbox("Chapter", SYLLABUS[sub]['chapters'])
        q_count = 5
    else:
        chap = "All Chapters"
        q_count = 15
        
    if st.button("Start Test"):
        st.session_state.quiz_session = {
            'subject': sub, 'chapter': chap, 
            'questions': get_mock_questions(sub, q_count),
            'start_time': datetime.now()
        }
        st.session_state.current_page = 'quiz_interface'
        st.rerun()

def quiz_interface():
    quiz = st.session_state.quiz_session
    st.subheader(f"{quiz['subject']} - {quiz['chapter']}")
    
    answers = {}
    for i, q in enumerate(quiz['questions']):
        st.markdown(f"**Q{i+1}: {q['question']}**")
        # index=None prevents pre-selection
        answers[i] = st.radio(f"Select Answer {i}", q['options'], key=f"q{i}", index=None)
        st.markdown("---")
        
    if st.button("Submit Assessment"):
        score = 0
        for i, q in enumerate(quiz['questions']):
            if answers.get(i) == q['options'][q['correct_index']]:
                score += 1
        
        st.session_state.quiz_result = {'score': score, 'total': len(quiz['questions']), 'answers': answers}
        st.session_state.current_page = 'quiz_feedback'
        st.rerun()

def quiz_feedback():
    st.title("📋 Teacher Feedback")
    st.warning("Please rate the teacher before viewing results.")
    
    c1, c2 = st.columns(2)
    with c1: st.slider("Clarity", 1, 5, 3)
    with c2: st.slider("Pace", 1, 5, 3)
    st.text_input("Comments (Optional)")
    
    if st.button("Submit & View Score"):
        res = st.session_state.quiz_result
        st.balloons()
        st.success(f"You Scored: {res['score']} / {res['total']}")
        
        with st.expander("View Correct Answers"):
            quiz = st.session_state.quiz_session
            for i, q in enumerate(quiz['questions']):
                user_ans = res['answers'].get(i, "No Answer")
                corr_ans = q['correct_answer']
                color = "green" if user_ans == corr_ans else "red"
                st.markdown(f"**Q{i+1}:** :{color}[Your Answer: {user_ans}] | **Correct:** {corr_ans}")
        
        if st.button("Return to Dashboard"):
            # Save Score Logic Here
            st.session_state.current_page = 'student_dashboard'
            st.rerun()

def student_ai_page():
    st.title("🤖 Student AI Assistant")
    if st.button("⬅️ Back"): st.session_state.current_page = 'student_dashboard'; st.rerun()
    
    tab1, tab2 = st.tabs(["Ask Question", "Quiz Maker"])
    
    with tab1:
        st.subheader("Document Q&A")
        uploaded = st.file_uploader("Upload PDF Reference", type="pdf")
        
        # Chat interface
        user_q = st.chat_input("Ask a question about your PDF...")
        if user_q:
            if not uploaded:
                st.error("Please upload a PDF first.")
            else:
                with st.chat_message("user"):
                    st.write(user_q)
                with st.chat_message("assistant"):
                    with st.spinner("AI Thinking..."):
                        time.sleep(1.5)
                        st.write(f"**Mock Answer:** Based on the uploaded document '{uploaded.name}', the answer to '{user_q}' is related to the core concepts found in Chapter 2. (This is a simulation).")

    with tab2:
        st.subheader("Generate Practice Quiz")
        q_uploaded = st.file_uploader("Upload Material for Quiz", type="pdf", key="q_up")
        diff = st.select_slider("Difficulty", ["Easy", "Intermediate", "Hard"])
        
        if st.button("Generate Quiz"):
            if not q_uploaded:
                st.error("Upload a file first!")
            else:
                st.success(f"Generated {diff} Quiz from {q_uploaded.name}")
                st.markdown("""
                **Q1. (Mock) What is the main principle discussed?**
                * [ ] Option A
                * [ ] Option B
                * [x] Option C (Correct)
                
                **Q2. (Mock) Calculate the value of X...**
                * [x] 42 (Correct)
                * [ ] 10
                """)

# --- TEACHER WORKFLOW ---
def teacher_dashboard():
    st.title("👨‍🏫 Teacher Dashboard")
    data = st.session_state.teachers_data[st.session_state.username]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Name", data['name'])
    c2.metric("Subject", data['subject'])
    c3.metric("Rating", f"{data['feedback_score']}/5.0")
    
    st.markdown("---")
    
    # Correct Layout: Columns for buttons
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("📊 Student Profiles"): st.session_state.current_page = 't_profiles'; st.rerun()
    with b2:
        if st.button("💬 View Feedback"): st.session_state.current_page = 't_feedback'; st.rerun()
    with b3:
        if st.button("🤖 AI Tools"): st.session_state.current_page = 't_ai'; st.rerun()

def teacher_profiles():
    st.title("📊 Student Analytics")
    if st.button("⬅️ Back"): st.session_state.current_page = 'teacher_dashboard'; st.rerun()
    
    teacher_sub = st.session_state.teachers_data[st.session_state.username]['subject']
    
    # Filter students
    students = [s for s in st.session_state.students_data.values() if teacher_sub in s.get('subjects', [])]
    
    if not students:
        st.warning(f"No students enrolled in {teacher_sub}")
        return

    sel_name = st.selectbox("Select Student", [s['name'] for s in students])
    sel_student = next(s for s in students if s['name'] == sel_name)
    
    st.subheader(f"Analysis for {sel_name}")
    
    # --- GRAPHS ---
    c1, c2 = st.columns(2)
    
    # Graph 1: Bar Chart (Chapter Tests)
    with c1:
        if teacher_sub in sel_student['marks']:
            scores = sel_student['marks'][teacher_sub]['chapter_tests']
            fig_bar = px.bar(x=[f"Ch {i+1}" for i in range(len(scores))], y=scores, title="Chapter Performance")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No Data")

    # Graph 2: Pie Chart (Assessment Distribution)
    with c2:
        if teacher_sub in sel_student['marks']:
            marks_data = sel_student['marks'][teacher_sub]
            labels = ['Chapter Avg', 'Final Assessment', 'Internal']
            values = [sum(marks_data['chapter_tests'])/5, marks_data['subject_assessment'], 20]
            fig_pie = px.pie(names=labels, values=values, title="Marks Distribution")
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Graph 3: Radar Chart (Overall Progress)
    st.subheader("Holistic Progress")
    categories = sel_student['subjects']
    # Mocking data for other subjects for the graph
    r_values = [random.randint(60, 90) for _ in categories]
    
    fig_radar = go.Figure(data=go.Scatterpolar(
      r=r_values,
      theta=categories,
      fill='toself'
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
    st.plotly_chart(fig_radar, use_container_width=True)
    
    st.info("**Weak Areas:** Thermodynamics, Vector Calculus (AI Detected)")

def teacher_feedback():
    st.title("💬 Feedback Analysis")
    if st.button("⬅️ Back"): st.session_state.current_page = 'teacher_dashboard'; st.rerun()
    
    data = st.session_state.teachers_data[st.session_state.username]
    st.metric("Net Score", f"{data['feedback_score']}/5.0")
    
    st.subheader("Student Comments")
    for comm in data['feedback_comments']:
        # FIX FOR BUG 7: Use standard if/else, not ternary for st functions
        if comm['type'] == 'negative':
            with st.expander(f"🔴 {comm['comment']}"):
                st.write("**AI Suggestion:** Try to use more diagrams to explain this concept.")
        else:
            st.success(f"🟢 {comm['comment']}")

def teacher_ai():
    st.title("🤖 AI Teaching Assistant")
    if st.button("⬅️ Back"): st.session_state.current_page = 'teacher_dashboard'; st.rerun()
    
    tab1, tab2 = st.tabs(["Content Generator", "Question Bank"])
    
    with tab1:
        st.subheader("Generate Lecture Notes")
        topic = st.text_input("Enter Topic (e.g., Newton's Laws)")
        if st.button("Generate Notes"):
            with st.spinner("Generating..."):
                time.sleep(2)
                st.markdown(f"### Lecture Plan: {topic}")
                st.write("1. **Introduction**: Define the core concept...")
                st.write("2. **Examples**: Real-world application...")
                st.success("Notes generated!")
                
    with tab2:
        st.subheader("Create Exam Questions")
        diff = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"])
        if st.button("Generate Questions"):
            st.write(f"**1. ({diff}) Explain the concept of...**")
            st.write(f"**2. ({diff}) Calculate the value of...**")

# --- ROUTER ---
def main():
    render_sidebar()
    if not st.session_state.logged_in:
        login_register_page()
    else:
        if st.session_state.user_type == "student":
            if st.session_state.current_page == 'subject_selection': subject_selection_page()
            elif st.session_state.current_page == 'student_dashboard': student_dashboard()
            elif st.session_state.current_page == 'assessment': assessment_page()
            elif st.session_state.current_page == 'quiz_interface': quiz_interface()
            elif st.session_state.current_page == 'quiz_feedback': quiz_feedback()
            elif st.session_state.current_page == 'student_ai': student_ai_page()
        elif st.session_state.user_type == "teacher":
            if st.session_state.current_page == 'teacher_dashboard': teacher_dashboard()
            elif st.session_state.current_page == 't_profiles': teacher_profiles()
            elif st.session_state.current_page == 't_feedback': teacher_feedback()
            elif st.session_state.current_page == 't_ai': teacher_ai()

if __name__ == "__main__":
    main()
