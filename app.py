import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import random
import os

# --- 1. SETUP & CONFIGURATION ---
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
    .success-box {
        padding: 15px;
        border-radius: 10px;
        background-color: rgba(0, 255, 0, 0.1);
        border: 1px solid #00ff00;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & SYLLABUS ---
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

# Static Fallback Questions (Used if AI fails)
STATIC_QUESTIONS = {
    "Default": [
        {"q": "Which law states V=IR?", "opts": ["Ohm's Law", "Newton's Law", "Kirchhoff's Law", "Faraday's Law"], "ans": "Ohm's Law"},
        {"q": "What is the unit of Force?", "opts": ["Newton", "Joule", "Watt", "Pascal"], "ans": "Newton"},
        {"q": "Binary 1010 equals decimal...", "opts": ["10", "5", "12", "8"], "ans": "10"}
    ]
}

# --- 4. HELPER FUNCTIONS ---
def generate_mock_students():
    """Generates 25 mock students for the demo"""
    data = {}
    for i in range(1, 26):
        uid = f"student{i}"
        data[uid] = {
            "password": "pass123",
            "name": f"Student {i}",
            "roll_no": f"FE2024{str(i).zfill(3)}",
            "subjects": random.sample(list(SYLLABUS.keys()), 5),
            "marks": {},
            "attendance": random.randint(60, 98),
            "has_data": True
        }
        # Fill mock marks
        for sub in data[uid]['subjects']:
            data[uid]['marks'][sub] = {
                "chapter_tests": [random.randint(5, 10) for _ in range(5)],
                "subject_assessment": random.randint(15, 30),
                "overall": random.randint(50, 95)
            }
    return data

def get_ai_questions(subject, chapter, count=5):
    """
    Tries to get Real AI questions. 
    If Key is missing or AI fails, falls back to Static questions.
    """
    api_key = st.session_state.get('api_key')
    
    if api_key and HAS_AI:
        try:
            genai.configure(api_key=api_key)
            # FIX: Changed model to 'gemini-pro' to fix the 404 error
            model = genai.GenerativeModel('gemini-pro')
            
            # Strict Prompt for JSON-like Python list
            prompt = f"""
            Generate {count} multiple-choice questions for '{subject}' (Chapter: {chapter}).
            Strictly return a Python list of dictionaries. NO markdown. NO code blocks.
            Format: [{{'q': 'Question?', 'opts': ['A', 'B', 'C', 'D'], 'ans': 'Correct Option Text'}}]
            """
            
            response = model.generate_content(prompt)
            # Clean string to ensure it's valid python code
            text = response.text.strip().replace("```python", "").replace("```", "")
            import ast
            return ast.literal_eval(text)
        except Exception as e:
            st.toast(f"⚠️ AI Error: {str(e)}. Using Static Data.")
            
    # Fallback
    return random.sample(STATIC_QUESTIONS["Default"], min(count, len(STATIC_QUESTIONS["Default"])))

def get_ai_notes(topic, context="Engineering"):
    """Generates notes using AI"""
    api_key = st.session_state.get('api_key')
    if api_key and HAS_AI:
        try:
            genai.configure(api_key=api_key)
            # FIX: Changed model to 'gemini-pro'
            model = genai.GenerativeModel('gemini-pro')
            res = model.generate_content(f"Write study notes for '{topic}' in the context of {context}. Use bullet points.")
            return res.text
        except Exception as e:
            return f"❌ AI Error: {str(e)}"
    return "⚠️ AI Key missing. Please provide a key in the sidebar."

# --- 5. SESSION STATE INITIALIZATION ---
if 'students_data' not in st.session_state:
    st.session_state.students_data = generate_mock_students()
if 'teachers_data' not in st.session_state:
    st.session_state.teachers_data = {
        "teacher1": {
            "password": "teach123", "name": "Prof. Teacher 1", 
            "subject": "Engineering Physics", 
            "feedback_score": 4.7,
            "feedback_comments": [
                {"comment": "Excellent explanations", "type": "positive"},
                {"comment": "Needs to write larger on board", "type": "negative"},
                {"comment": "Very interactive class", "type": "positive"}
            ]
        }
    }
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_type' not in st.session_state: st.session_state.user_type = None
if 'username' not in st.session_state: st.session_state.username = None
if 'current_page' not in st.session_state: st.session_state.current_page = 'login'
if 'api_key' not in st.session_state: st.session_state.api_key = ""

# Navigation Helper
def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- 6. SIDEBAR ---
def render_sidebar():
    with st.sidebar:
        # Logo Logic
        if os.path.exists("logo.png"):
            st.image("logo.png", width=200)
        else:
            st.write("### 🎓 FE Portal")
            
        st.markdown("---")
        st.caption("Created by FE DIV-A 2025-26")
        
        # API Key Input
        with st.expander("⚙️ AI Settings"):
            key_input = st.text_input("Gemini API Key", type="password", value=st.session_state.api_key)
            if key_input:
                st.session_state.api_key = key_input
                st.success("✅ Key Saved")
                
        st.markdown("---")
        if st.session_state.logged_in:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.current_page = 'login'
                st.rerun()

# --- 7. AUTHENTICATION PAGES ---
def login_register_page():
    st.markdown("<h1 style='text-align: center; color: #4db8ff;'>🎓 FE Engineering Portal 2024</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    # Login Tab
    with tab1:
        st.markdown("#### Login")
        with st.expander("Cheat Sheet (For Demo)"):
            st.code("Student: student1 / pass123\nTeacher: teacher1 / teach123")
            
        role = st.radio("I am a...", ["Student", "Teacher"], horizontal=True)
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        
        if st.button("Login", use_container_width=True):
            db = st.session_state.students_data if role == "Student" else st.session_state.teachers_data
            if u in db and db[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user_type = role.lower()
                st.session_state.username = u
                
                if role == "Student":
                    # Check if they have subjects
                    if db[u]['has_data']:
                        st.session_state.selected_subjects = db[u]['subjects']
                        navigate_to("student_dashboard")
                    else:
                        navigate_to("subject_selection")
                else:
                    navigate_to("teacher_dashboard")
            else:
                st.error("Invalid Username or Password")

    # Register Tab
    with tab2:
        st.markdown("#### Create New Account")
        r_role = st.selectbox("Register as", ["Student", "Teacher"])
        r_name = st.text_input("Full Name")
        r_user = st.text_input("Choose Username")
        r_pass = st.text_input("Choose Password", type="password")
        
        extra = {}
        if r_role == "Teacher":
            extra['sub'] = st.selectbox("Subject Taught", list(SYLLABUS.keys()))
        else:
            extra['roll'] = st.text_input("Roll Number")
            
        if st.button("Register Now", use_container_width=True):
            target_db = st.session_state.teachers_data if r_role == "Teacher" else st.session_state.students_data
            
            if r_user in target_db:
                st.error("Username already taken!")
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
                st.success("Account Created! Please switch to Login tab.")

# --- 8. STUDENT PAGES ---
def subject_selection():
    st.markdown("<h2 class='header-text'>📚 Select Your 5 Subjects</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1: g1 = st.selectbox("Group 1", ["Engineering Physics", "Basic Electrical Engineering", "Engineering Mechanics"])
    with c2: g2 = st.selectbox("Group 2", ["Engineering Chemistry", "Basic Electronics Engineering", "Engineering Graphics"])
    
    math = st.selectbox("Mathematics", ["Engineering Mathematics-I", "Engineering Mathematics-II"])
    prog = st.selectbox("Programming", ["Fundamentals of Programming Languages", "Programming and Problem Solving"])
    work = "Manufacturing Practice Workshop"
    
    if st.button("Confirm Subjects"):
        user = st.session_state.username
        st.session_state.students_data[user]['subjects'] = [g1, g2, math, prog, work]
        st.session_state.students_data[user]['has_data'] = True
        st.session_state.selected_subjects = [g1, g2, math, prog, work]
        navigate_to("student_dashboard")

def student_dashboard():
    st.markdown("<h2 class='header-text'>🎯 Student Dashboard</h2>", unsafe_allow_html=True)
    data = st.session_state.students_data[st.session_state.username]
    
    # Profile Card
    c1, c2, c3 = st.columns(3)
    c1.metric("Name", data['name'])
    c2.metric("Roll No", data['roll_no'])
    c3.metric("Attendance", f"{data['attendance']}%")
    
    st.info(f"**Subjects:** {', '.join(st.session_state.selected_subjects)}")
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📝 Take Assessment", use_container_width=True): navigate_to("assessment_setup")
    with c2:
        if st.button("🤖 AI Assistant", use_container_width=True): navigate_to("student_ai")

def assessment_setup():
    st.markdown("<h2 class='header-text'>📝 Configure Quiz</h2>", unsafe_allow_html=True)
    if st.button("⬅ Back"): navigate_to("student_dashboard")
    
    sub = st.selectbox("Select Subject", st.session_state.selected_subjects)
    chap = st.selectbox("Select Chapter", SYLLABUS[sub]['chapters'])
    
    if st.button("Start Quiz (AI Generated)", use_container_width=True):
        with st.spinner("AI is generating questions..."):
            questions = get_ai_questions(sub, chap, 5)
            st.session_state.quiz_session = {
                'subject': sub, 'chapter': chap, 'questions': questions,
                'start_time': datetime.now()
            }
            navigate_to("quiz_interface")

def quiz_interface():
    if 'quiz_session' not in st.session_state: navigate_to("student_dashboard")
    
    quiz = st.session_state.quiz_session
    st.markdown(f"### {quiz['subject']} - {quiz['chapter']}")
    
    answers = {}
    for i, q in enumerate(quiz['questions']):
        st.markdown(f"**Q{i+1}. {q['q']}**")
        answers[i] = st.radio(f"Select option {i}", q['opts'], key=f"q{i}", index=None)
        st.markdown("---")
        
    if st.button("Submit Quiz", use_container_width=True):
        score = sum([1 for i, q in enumerate(quiz['questions']) if answers.get(i) == q['ans']])
        st.session_state.quiz_result = {'score': score, 'total': len(quiz['questions']), 'answers': answers}
        navigate_to("quiz_feedback")

def quiz_feedback():
    st.markdown("<h2 class='header-text'>📊 Results</h2>", unsafe_allow_html=True)
    res = st.session_state.quiz_result
    
    st.metric("Your Score", f"{res['score']} / {res['total']}")
    
    with st.expander("Show Detailed Solutions"):
        quiz = st.session_state.quiz_session
        for i, q in enumerate(quiz['questions']):
            user_ans = res['answers'].get(i, "Not Answered")
            color = "green" if user_ans == q['ans'] else "red"
            st.markdown(f"**Q{i+1}:** {q['q']}")
            st.markdown(f":{color}[Your Answer: {user_ans}]")
            st.markdown(f"**Correct Answer:** {q['ans']}")
            st.divider()
            
    st.markdown("### Rate the Teacher")
    c1, c2 = st.columns(2)
    with c1: st.slider("Clarity", 1, 5, 3)
    with c2: st.slider("Pace", 1, 5, 3)
    
    if st.button("Submit & Return Home", use_container_width=True):
        navigate_to("student_dashboard")

def student_ai():
    st.markdown("<h2 class='header-text'>🤖 AI Assistant</h2>", unsafe_allow_html=True)
    if st.button("⬅ Back"): navigate_to("student_dashboard")
    
    tab1, tab2 = st.tabs(["Ask PDF", "Quiz Maker"])
    
    with tab1:
        st.write("Upload a PDF to ask questions about it.")
        uploaded = st.file_uploader("Upload PDF", type="pdf")
        q = st.text_input("Ask a question...")
        if st.button("Get Answer"):
            if not st.session_state.api_key:
                st.error("No API Key found. Please add it in the sidebar.")
            else:
                with st.spinner("AI Thinking..."):
                    ans = get_ai_notes(q, context="Uploaded PDF content")
                    st.info(ans)
                    
    with tab2:
        st.write("Generate a quiz from a topic or file.")
        topic = st.text_input("Enter Topic (e.g., Thermodynamics)")
        if st.button("Generate Quiz"):
            if not st.session_state.api_key:
                st.error("No API Key.")
            else:
                with st.spinner("Generating..."):
                    qs = get_ai_questions("General", topic, 3)
                    for i, q in enumerate(qs):
                        st.markdown(f"**Q{i+1}: {q['q']}**")
                        st.caption(f"Ans: {q['ans']}")

# --- 9. TEACHER PAGES ---
def teacher_dashboard():
    st.markdown("<h2 class='header-text'>👨‍🏫 Teacher Dashboard</h2>", unsafe_allow_html=True)
    data = st.session_state.teachers_data[st.session_state.username]
    
    c1, c2 = st.columns(2)
    c1.metric("Welcome", data['name'])
    c2.metric("Subject", data['subject'])
    
    st.markdown("---")
    
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("📊 Student Profiles", use_container_width=True): navigate_to("t_profiles")
    with b2:
        if st.button("💬 Feedback", use_container_width=True): navigate_to("t_feedback")
    with b3:
        if st.button("🤖 AI Tools", use_container_width=True): navigate_to("t_ai")

def teacher_profiles():
    st.markdown("<h2 class='header-text'>📊 Student Analytics</h2>", unsafe_allow_html=True)
    if st.button("⬅ Back"): navigate_to("teacher_dashboard")
    
    # Filter students
    t_sub = st.session_state.teachers_data[st.session_state.username]['subject']
    students = [s for s in st.session_state.students_data.values() if t_sub in s.get('subjects', [])]
    
    if not students:
        st.warning(f"No students enrolled in {t_sub}")
        return
        
    sel_name = st.selectbox("Select Student", [s['name'] for s in students])
    student = next(s for s in students if s['name'] == sel_name)
    
    st.markdown(f"### Performance: {sel_name}")
    
    c1, c2 = st.columns(2)
    
    # Bar Chart
    with c1:
        if t_sub in student['marks']:
            scores = student['marks'][t_sub]['chapter_tests']
            fig = px.bar(x=[f"Ch {i+1}" for i in range(5)], y=scores, title="Chapter Performance")
            st.plotly_chart(fig, use_container_width=True)
            
    # Radar Chart
    with c2:
        subs = student['subjects']
        # Mock aggregate scores for radar
        vals = [random.randint(60, 90) for _ in subs]
        fig2 = go.Figure(data=go.Scatterpolar(r=vals, theta=subs, fill='toself'))
        fig2.update_layout(title="Overall Growth", polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
        st.plotly_chart(fig2, use_container_width=True)

def teacher_feedback():
    st.markdown("<h2 class='header-text'>💬 Student Feedback</h2>", unsafe_allow_html=True)
    if st.button("⬅ Back"): navigate_to("teacher_dashboard")
    
    data = st.session_state.teachers_data[st.session_state.username]
    st.metric("Net Rating", f"{data['feedback_score']}/5.0")
    
    for comm in data['feedback_comments']:
        if comm['type'] == 'negative':
            st.error(f"Improvement: {comm['comment']}")
        else:
            st.success(f"Praise: {comm['comment']}")

def teacher_ai():
    st.markdown("<h2 class='header-text'>🤖 AI Teaching Tools</h2>", unsafe_allow_html=True)
    if st.button("⬅ Back"): navigate_to("teacher_dashboard")
    
    tab1, tab2 = st.tabs(["Lecture Notes", "Question Bank"])
    
    with tab1:
        topic = st.text_input("Enter Topic")
        if st.button("Generate Notes"):
            with st.spinner("Writing notes..."):
                st.markdown(get_ai_notes(topic, "Teaching Material"))
                
    with tab2:
        q_topic = st.text_input("Enter Topic for Questions")
        if st.button("Generate Question Bank"):
            with st.spinner("Creating questions..."):
                qs = get_ai_questions("General", q_topic, 5)
                for i, q in enumerate(qs):
                    st.write(f"{i+1}. {q['q']} (Ans: {q['ans']})")

# --- 10. MAIN ROUTER ---
def main():
    render_sidebar()
    
    if not st.session_state.logged_in:
        login_register_page()
    else:
        p = st.session_state.current_page
        if p == 'subject_selection': subject_selection()
        elif p == 'student_dashboard': student_dashboard()
        elif p == 'assessment_setup': assessment_setup()
        elif p == 'quiz_interface': quiz_interface()
        elif p == 'quiz_feedback': quiz_feedback()
        elif p == 'student_ai': student_ai()
        
        elif p == 'teacher_dashboard': teacher_dashboard()
        elif p == 't_profiles': teacher_profiles()
        elif p == 't_feedback': teacher_feedback()
        elif p == 't_ai': teacher_ai()

if __name__ == "__main__":
    main()
