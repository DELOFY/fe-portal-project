import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import random
import os

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="FE Portal 2024",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Try importing AI library
try:
    import google.generativeai as genai
    HAS_AI = True
except ImportError:
    HAS_AI = False

# --- 2. CUSTOM CSS ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
    }
    .header-text {
        color: #4db8ff;
        font-weight: bold;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    .stRadio > label {
        background-color: #262730;
        padding: 10px;
        border-radius: 5px;
        width: 100%;
        margin-bottom: 5px;
        border: 1px solid #4a4a4a;
    }
    .stRadio > label:hover {
        border-color: #4db8ff;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & SYLLABUS ---
SYLLABUS = {
    "Engineering Physics": {"chapters": ["Fundamentals of Photonics", "Quantum Physics", "Wave Optics", "Semiconductor Physics"]},
    "Engineering Chemistry": {"chapters": ["Water Technology", "Instrumental Methods", "Advanced Materials", "Corrosion"]},
    "Basic Electrical Engineering": {"chapters": ["DC Circuits", "Electromagnetism", "AC Fundamentals", "Electric Machines"]},
    "Engineering Mechanics": {"chapters": ["Force Systems", "Equilibrium", "Friction", "Kinematics"]},
    "Programming": {"chapters": ["C Intro", "Control Flow", "Arrays", "Functions"]}
}

# --- IMPROVED STATIC BACKUP (10 Questions so it doesn't repeat) ---
STATIC_QUESTIONS = {
    "Default": [
        {"q": "Which law states V=IR?", "opts": ["Ohm's Law", "Newton's Law", "Kirchhoff's Law", "Faraday's Law"], "ans": "Ohm's Law"},
        {"q": "What is the unit of Force?", "opts": ["Newton", "Joule", "Watt", "Pascal"], "ans": "Newton"},
        {"q": "Binary 1010 equals decimal...", "opts": ["10", "5", "12", "8"], "ans": "10"},
        {"q": "Which material is a semiconductor?", "opts": ["Silicon", "Copper", "Rubber", "Iron"], "ans": "Silicon"},
        {"q": "What does LED stand for?", "opts": ["Light Emitting Diode", "Low Energy Device", "Light Energy Diode", "None"], "ans": "Light Emitting Diode"},
        {"q": "Integral of x dx is...", "opts": ["x^2 / 2", "x^2", "2x", "1/x"], "ans": "x^2 / 2"},
        {"q": "Which gate returns TRUE only if both inputs are TRUE?", "opts": ["AND", "OR", "XOR", "NOT"], "ans": "AND"},
        {"q": "The pH of pure water is...", "opts": ["7", "0", "14", "1"], "ans": "7"},
        {"q": "Kinetic Energy formula is...", "opts": ["1/2 mv^2", "mgh", "ma", "mc^2"], "ans": "1/2 mv^2"},
        {"q": "Python is a...", "opts": ["High-level Language", "Hardware", "Operating System", "Database"], "ans": "High-level Language"}
    ]
}

# --- 4. HELPER FUNCTIONS ---
def generate_mock_students():
    data = {}
    for i in range(1, 26):
        uid = f"student{i}"
        data[uid] = {
            "password": "pass123",
            "name": f"Student {i}",
            "roll_no": f"FE2024{str(i).zfill(3)}",
            "subjects": random.sample(list(SYLLABUS.keys()), 3),
            "marks": {},
            "attendance": random.randint(60, 98),
            "has_data": True
        }
        for sub in data[uid]['subjects']:
            data[uid]['marks'][sub] = {
                "chapter_tests": [random.randint(5, 10) for _ in range(5)],
                "subject_assessment": random.randint(15, 30),
                "overall": random.randint(50, 95)
            }
    return data

def get_ai_questions(subject, chapter, count=5):
    """
    DIAGNOSTIC VERSION: Prints Errors to Screen
    """
    api_key = st.session_state.get('api_key')
    
    if api_key and HAS_AI:
        try:
            genai.configure(api_key=api_key)
            # Using the standard model that is most reliable
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Generate {count} multiple-choice questions for '{subject}' (Chapter: {chapter}).
            Strictly return a Python list of dictionaries. NO markdown.
            Format: [{{'q': 'Question?', 'opts': ['A', 'B', 'C', 'D'], 'ans': 'Correct Option Text'}}]
            """
            
            response = model.generate_content(prompt)
            text = response.text.strip().replace("```python", "").replace("```", "")
            import ast
            return ast.literal_eval(text)
            
        except Exception as e:
            # --- THIS IS THE DIAGNOSTIC PRINT ---
            st.error(f"❌ AI Connection Failed: {str(e)}")
            st.warning("⚠️ Using Static Backup Questions instead.")
            # ------------------------------------
            
    elif not api_key:
        st.warning("⚠️ No API Key entered. Using Backup Data.")
            
    # Fallback to Static Data (Random Sample from the new list of 10)
    pool = STATIC_QUESTIONS["Default"]
    return random.sample(pool, min(count, len(pool)))

# --- 5. SESSION STATE ---
if 'students_data' not in st.session_state: st.session_state.students_data = generate_mock_students()
if 'teachers_data' not in st.session_state:
    st.session_state.teachers_data = {"teacher1": {"password": "teach123", "name": "Prof. Teacher", "subject": "Engineering Physics", "feedback_score": 4.7, "feedback_comments": []}}
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_type' not in st.session_state: st.session_state.user_type = None
if 'username' not in st.session_state: st.session_state.username = None
if 'current_page' not in st.session_state: st.session_state.current_page = 'login'
if 'api_key' not in st.session_state: st.session_state.api_key = ""

def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- 6. SIDEBAR ---
def render_sidebar():
    with st.sidebar:
        st.header("🎓 FE Portal")
        st.caption("Created by FE DIV-A 2025-26")
        st.markdown("---")
        
        # API Key Input
        key_input = st.text_input("🔑 Gemini API Key", type="password", value=st.session_state.api_key)
        if key_input:
            st.session_state.api_key = key_input
            st.success("Key Saved")
        else:
            st.info("Paste API Key for Real AI")
                
        st.markdown("---")
        if st.session_state.logged_in:
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.current_page = 'login'
                st.rerun()

# --- 7. PAGES ---
def login_page():
    st.title("🎓 FE Engineering Portal 2024")
    
    with st.expander("ℹ️ Login Details (Demo)"):
        st.write("Student: `student1` / `pass123`")
        st.write("Teacher: `teacher1` / `teach123`")
            
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        role = st.radio("Login As:", ["Student", "Teacher"], horizontal=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            db = st.session_state.students_data if role == "Student" else st.session_state.teachers_data
            if u in db and db[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user_type = role.lower()
                st.session_state.username = u
                if role == "Student":
                    if db[u]['has_data']:
                        st.session_state.selected_subjects = db[u]['subjects']
                        navigate_to("student_dashboard")
                    else:
                        navigate_to("subject_selection")
                else:
                    navigate_to("teacher_dashboard")
            else:
                st.error("Invalid Credentials")
    
    with tab2:
        st.write("Registration System (Demo Mode)")
        st.text_input("New Username")
        st.button("Register")

def subject_selection():
    st.title("📚 Subject Selection")
    st.write("Select your 5 subjects.")
    if st.button("Auto-Select Default"):
        user = st.session_state.username
        st.session_state.students_data[user]['subjects'] = list(SYLLABUS.keys())[:5]
        st.session_state.students_data[user]['has_data'] = True
        st.session_state.selected_subjects = list(SYLLABUS.keys())[:5]
        navigate_to("student_dashboard")

def student_dashboard():
    st.title("🎯 Student Dashboard")
    st.write(f"Welcome, **{st.session_state.students_data[st.session_state.username]['name']}**")
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📝 Take Assessment", use_container_width=True): navigate_to("assessment_setup")
    with c2:
        if st.button("🤖 AI Assistant", use_container_width=True): navigate_to("student_ai")

def assessment_setup():
    st.title("📝 Configure Quiz")
    if st.button("⬅ Back"): navigate_to("student_dashboard")
    
    sub = st.selectbox("Subject", st.session_state.selected_subjects)
    chap = st.selectbox("Chapter", SYLLABUS.get(sub, {'chapters':['General']})['chapters'])
    
    if st.button("Start Quiz", use_container_width=True):
        # Calls the function that now prints ERRORS to screen
        with st.spinner("Generating..."):
            questions = get_ai_questions(sub, chap, 5)
            st.session_state.quiz_session = {
                'subject': sub, 'chapter': chap, 'questions': questions
            }
            navigate_to("quiz_interface")

def quiz_interface():
    if 'quiz_session' not in st.session_state: navigate_to("student_dashboard")
    quiz = st.session_state.quiz_session
    st.header(f"{quiz['subject']}")
    
    answers = {}
    for i, q in enumerate(quiz['questions']):
        st.markdown(f"**Q{i+1}: {q['q']}**")
        answers[i] = st.radio(f"Select option {i}", q['opts'], key=f"q{i}", index=None)
        st.markdown("---")
        
    if st.button("Submit"):
        score = sum([1 for i, q in enumerate(quiz['questions']) if answers.get(i) == q['ans']])
        st.success(f"Score: {score}/{len(quiz['questions'])}")
        if st.button("Return to Dashboard"): navigate_to("student_dashboard")

def student_ai():
    st.title("🤖 AI Assistant")
    if st.button("⬅ Back"): navigate_to("student_dashboard")
    st.write("AI Chat Interface (Demo)")

def teacher_dashboard():
    st.title("👨‍🏫 Teacher Dashboard")
    st.write("Welcome Professor.")
    if st.button("Student Profiles"): st.info("Profile View")

# --- 8. MAIN ROUTER ---
def main():
    render_sidebar()
    if not st.session_state.logged_in:
        login_page()
    else:
        p = st.session_state.current_page
        if p == 'subject_selection': subject_selection()
        elif p == 'student_dashboard': student_dashboard()
        elif p == 'assessment_setup': assessment_setup()
        elif p == 'quiz_interface': quiz_interface()
        elif p == 'student_ai': student_ai()
        elif p == 'teacher_dashboard': teacher_dashboard()

if __name__ == "__main__":
    main()
