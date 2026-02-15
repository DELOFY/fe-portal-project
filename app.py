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

# --- 3. SYLLABUS DATA ---
SYLLABUS = {
    "Engineering Physics": {"chapters": ["Fundamentals of Photonics", "Quantum Physics", "Wave Optics", "Semiconductor Physics", "Nanoparticles"]},
    "Engineering Chemistry": {"chapters": ["Water Technology", "Instrumental Methods", "Advanced Materials", "Energy Sources", "Corrosion"]},
    "Basic Electrical Engineering": {"chapters": ["DC Circuits", "Electromagnetism", "AC Fundamentals", "AC Circuits", "Electric Machines"]},
    "Basic Electronics Engineering": {"chapters": ["Diodes", "Transistors", "Logic Gates", "Op-Amp", "Sensors"]},
    "Engineering Mechanics": {"chapters": ["Force Systems", "Equilibrium", "Friction", "Kinematics", "Kinetics"]},
    "Engineering Graphics": {"chapters": ["Projections", "Curves", "Isometric Projection"]},
    "Engineering Mathematics-I": {"chapters": ["Calculus", "Matrices", "Eigen Values"]},
    "Programming": {"chapters": ["C Intro", "Control Flow", "Arrays", "Functions"]}
}

# --- 4. EXTENDED STATIC BACKUP (15 Questions) ---
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
        {"q": "Python is a...", "opts": ["High-level Language", "Hardware", "Operating System", "Database"], "ans": "High-level Language"},
        {"q": "The derivative of sin(x) is...", "opts": ["cos(x)", "-cos(x)", "tan(x)", "sec(x)"], "ans": "cos(x)"},
        {"q": "Power is defined as...", "opts": ["Rate of doing work", "Force x Distance", "Mass x Velocity", "None"], "ans": "Rate of doing work"},
        {"q": "What is the atomic number of Carbon?", "opts": ["6", "12", "8", "14"], "ans": "6"},
        {"q": "In a DC circuit, the inductor acts as...", "opts": ["Short Circuit", "Open Circuit", "Resistor", "Capacitor"], "ans": "Short Circuit"},
        {"q": "Which is a scalar quantity?", "opts": ["Speed", "Velocity", "Force", "Acceleration"], "ans": "Speed"}
    ]
}

# --- 5. SMART AI FUNCTIONS ---
def get_working_model(api_key):
    """
    Tries multiple model names to find one that works for the user's key.
    """
    possible_models = ["gemini-1.5-flash", "gemini-pro", "gemini-1.0-pro", "gemini-1.5-pro-latest"]
    
    genai.configure(api_key=api_key)
    for model_name in possible_models:
        try:
            model = genai.GenerativeModel(model_name)
            # Test with a tiny prompt to check connection
            model.generate_content("Test")
            return model # Found a working one!
        except:
            continue # Try next one
    return None # None worked

def get_ai_questions(subject, chapter, count=5):
    api_key = st.session_state.get('api_key')
    
    if api_key and HAS_AI:
        try:
            # Use the smart model finder
            model = get_working_model(api_key)
            
            if model:
                prompt = f"""
                Generate {count} multiple-choice questions for '{subject}' (Chapter: {chapter}).
                Strictly return a Python list of dictionaries. NO markdown.
                Format: [{{'q': 'Question?', 'opts': ['A', 'B', 'C', 'D'], 'ans': 'Correct Option Text'}}]
                """
                response = model.generate_content(prompt)
                text = response.text.strip().replace("```python", "").replace("```", "")
                import ast
                return ast.literal_eval(text)
            else:
                st.error("❌ Key valid, but no available models found. Check Google AI Studio.")
                
        except Exception as e:
            st.error(f"❌ AI Error: {str(e)}")
            st.toast("Using Backup Questions")
    
    # Fallback
    return random.sample(STATIC_QUESTIONS["Default"], min(count, 10))

def get_ai_notes(topic, context="Engineering"):
    api_key = st.session_state.get('api_key')
    if api_key and HAS_AI:
        try:
            model = get_working_model(api_key)
            if model:
                res = model.generate_content(f"Write study notes for '{topic}' in context of {context}.")
                return res.text
        except Exception as e:
            return f"❌ AI Error: {str(e)}"
    return "⚠️ AI Key missing or invalid."

# --- 6. SESSION STATE ---
def generate_mock_students():
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
        for sub in data[uid]['subjects']:
            data[uid]['marks'][sub] = {
                "chapter_tests": [random.randint(5, 10) for _ in range(5)],
                "subject_assessment": random.randint(15, 30),
                "overall": random.randint(50, 95)
            }
    return data

if 'students_data' not in st.session_state: st.session_state.students_data = generate_mock_students()
if 'teachers_data' not in st.session_state:
    st.session_state.teachers_data = {"teacher1": {"password": "teach123", "name": "Prof. Teacher", "subject": "Engineering Physics", "feedback_score": 4.7, "feedback_comments": [{"comment": "Good pace", "type": "positive"}, {"comment": "More examples needed", "type": "negative"}]}}
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_type' not in st.session_state: st.session_state.user_type = None
if 'username' not in st.session_state: st.session_state.username = None
if 'current_page' not in st.session_state: st.session_state.current_page = 'login'
if 'api_key' not in st.session_state: st.session_state.api_key = ""

def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- 7. SIDEBAR ---
def render_sidebar():
    with st.sidebar:
        # SMART LOGO LOADER
        logo_path = "logo.png"
        if not os.path.exists(logo_path):
            # Find any png
            files = [f for f in os.listdir('.') if f.endswith('.png')]
            if files: logo_path = files[0]
            
        if os.path.exists(logo_path):
            st.image(logo_path, width=180)
        else:
            st.header("🎓 FE Portal")
            
        st.caption("Created by FE DIV-A 2025-26")
        st.markdown("---")
        
        with st.expander("⚙️ AI Settings"):
            key = st.text_input("Gemini API Key", type="password", value=st.session_state.api_key)
            if key:
                st.session_state.api_key = key
                st.success("Key Saved!")
        
        st.markdown("---")
        if st.session_state.logged_in:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.current_page = 'login'
                st.rerun()

# --- 8. PAGES ---
def login_register_page():
    st.markdown("<h1 style='text-align: center; color: #4db8ff;'>FE Engineering Portal 2024</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        with st.expander("ℹ️ Demo Credentials (Cheat Sheet)"):
            st.code("Student: student1 / pass123\nTeacher: teacher1 / teach123")
            
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
        st.subheader("New User Registration")
        reg_role = st.selectbox("Register Role", ["Student", "Teacher"])
        reg_user = st.text_input("New Username")
        reg_pass = st.text_input("New Password", type="password")
        
        extra = {}
        if reg_role == "Teacher":
            extra['sub'] = st.selectbox("Subject Taught", list(SYLLABUS.keys()))
        else:
            extra['roll'] = st.text_input("Roll Number")

        if st.button("Create Account"):
            target_db = st.session_state.teachers_data if reg_role == "Teacher" else st.session_state.students_data
            
            if reg_role == "Student":
                target_db[reg_user] = {
                    "password": reg_pass, "name": "New User", "roll_no": extra['roll'],
                    "subjects": [], "marks": {}, "attendance": 0, "has_data": False
                }
            else:
                target_db[reg_user] = {
                    "password": reg_pass, "name": "New User", "subject": extra['sub'],
                    "feedback_score": 0.0, "feedback_comments": []
                }
            st.success("Account Created! Go to Login.")

def subject_selection():
    st.title("📚 Select Subjects")
    if st.button("Auto-Select Default (Demo)"):
        user = st.session_state.username
        st.session_state.students_data[user]['subjects'] = list(SYLLABUS.keys())[:5]
        st.session_state.students_data[user]['has_data'] = True
        st.session_state.selected_subjects = list(SYLLABUS.keys())[:5]
        navigate_to("student_dashboard")

def student_dashboard():
    st.title("🎯 Student Dashboard")
    st.write(f"Welcome, **{st.session_state.students_data[st.session_state.username]['name']}**")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Attendance", "85%")
    c2.metric("Avg Score", "78%")
    c3.metric("Pending Tasks", "2")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Take Assessment", use_container_width=True): navigate_to("assessment_setup")
    with col2:
        if st.button("🤖 AI Assistant", use_container_width=True): navigate_to("student_ai")

def assessment_setup():
    st.title("📝 Configure Quiz")
    if st.button("⬅ Back"): navigate_to("student_dashboard")
    
    sub = st.selectbox("Subject", st.session_state.selected_subjects)
    chap = st.selectbox("Chapter", SYLLABUS.get(sub, {'chapters':['General']})['chapters'])
    
    if st.button("Start Quiz", use_container_width=True):
        with st.spinner("Generating..."):
            questions = get_ai_questions(sub, chap, 5)
            st.session_state.quiz_session = {'subject': sub, 'chapter': chap, 'questions': questions}
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
        st.session_state.quiz_result = {'score': score, 'total': len(quiz['questions']), 'answers': answers}
        navigate_to("quiz_feedback")

def quiz_feedback():
    st.title("Result")
    res = st.session_state.quiz_result
    st.success(f"Score: {res['score']} / {res['total']}")
    
    st.subheader("Teacher Feedback (Mandatory)")
    c1, c2 = st.columns(2)
    with c1: st.slider("Clarity", 1, 5, 3)
    with c2: st.slider("Pace", 1, 5, 3)
    
    if st.button("Submit & Return"): navigate_to("student_dashboard")

# --- 9. AI ASSISTANT PAGE ---
def student_ai():
    st.title("🤖 AI Assistant")
    if st.button("⬅ Back"): navigate_to("student_dashboard")
    
    tab1, tab2 = st.tabs(["📄 Ask PDF", "📝 Quiz Maker"])
    
    with tab1:
        st.subheader("Chat with your Syllabus/Notes")
        uploaded = st.file_uploader("Upload PDF", type="pdf", key="chat_pdf")
        q = st.text_input("Ask a question about the file...")
        
        if st.button("Get Answer"):
            if not st.session_state.api_key:
                st.error("Please enter API Key in sidebar")
            else:
                with st.spinner("AI Thinking..."):
                    context = "Uploaded PDF" if uploaded else "General Engineering"
                    st.info(get_ai_notes(q, context))
                    
    with tab2:
        st.subheader("Generate a Practice Quiz")
        st.write("Upload a PDF to generate a quiz from it.")
        q_pdf = st.file_uploader("Upload Material", type="pdf", key="quiz_pdf")
        
        if st.button("Generate Quiz"):
            if not st.session_state.api_key:
                st.error("Please enter API Key in sidebar")
            else:
                with st.spinner("Creating Quiz..."):
                    qs = get_ai_questions("Uploaded Material", "General", 3)
                    st.success("Quiz Generated Below:")
                    for i, q in enumerate(qs):
                        st.markdown(f"**Q{i+1}: {q['q']}**")
                        st.caption(f"Answer: {q['ans']}")
                        st.divider()

# --- 10. TEACHER PAGES ---
def teacher_dashboard():
    st.title("👨‍🏫 Teacher Dashboard")
    data = st.session_state.teachers_data[st.session_state.username]
    
    c1, c2 = st.columns(2)
    c1.metric("Welcome", data['name'])
    c2.metric("Subject", data['subject'])
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Student Profiles"): navigate_to("t_profiles")
    with col2:
        if st.button("💬 Feedback"): navigate_to("t_feedback")
    with col3: 
        if st.button("🤖 AI Tools"): navigate_to("t_ai")

def teacher_profiles():
    st.title("Student Analytics")
    if st.button("Back"): navigate_to("teacher_dashboard")
    
    t_sub = st.session_state.teachers_data[st.session_state.username]['subject']
    students = [s for s in st.session_state.students_data.values() if t_sub in s.get('subjects', [])]
    
    if not students:
        st.warning(f"No students enrolled in {t_sub}")
        return
        
    sel_name = st.selectbox("Select Student", [s['name'] for s in students])
    student = next(s for s in students if s['name'] == sel_name)
    
    c1, c2 = st.columns(2)
    with c1:
        if t_sub in student['marks']:
            scores = student['marks'][t_sub]['chapter_tests']
            fig = px.bar(x=[f"Ch {i+1}" for i in range(5)], y=scores, title="Chapter Performance")
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        subs = student['subjects']
        vals = [random.randint(60, 90) for _ in subs]
        fig2 = go.Figure(data=go.Scatterpolar(r=vals, theta=subs, fill='toself'))
        fig2.update_layout(title="Overall Growth", polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
        st.plotly_chart(fig2, use_container_width=True)

def teacher_feedback():
    st.title("Feedback")
    if st.button("Back"): navigate_to("teacher_dashboard")
    st.info("Great teaching pace! (4.7/5)")

def teacher_ai():
    st.title("Teacher AI Tools")
    if st.button("Back"): navigate_to("teacher_dashboard")
    
    topic = st.text_input("Enter Topic for Notes")
    if st.button("Generate"):
        with st.spinner("Writing..."):
            st.markdown(get_ai_notes(topic))

# --- 11. MAIN ROUTER ---
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
