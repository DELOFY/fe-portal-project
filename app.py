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
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: 600; }
    .header-text { color: #4db8ff; font-weight: bold; font-size: 1.5rem; margin-bottom: 1rem; }
    .stRadio > label { background-color: #262730; padding: 10px; border-radius: 5px; width: 100%; margin-bottom: 5px; border: 1px solid #4a4a4a; }
    .stRadio > label:hover { border-color: #4db8ff; }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & SYLLABUS ---
SYLLABUS = {
    "Engineering Physics": {"chapters": ["Fundamentals of Photonics", "Quantum Physics", "Wave Optics", "Semiconductor Physics"]},
    "Engineering Chemistry": {"chapters": ["Water Technology", "Instrumental Methods", "Advanced Materials", "Corrosion"]},
    "Basic Electrical Engineering": {"chapters": ["DC Circuits", "AC Fundamentals", "Electric Machines"]},
    "Engineering Mechanics": {"chapters": ["Force Systems", "Equilibrium", "Friction", "Kinematics"]},
    "Engineering Graphics": {"chapters": ["Projections", "Curves", "Isometric Projection"]},
    "Mathematics-I": {"chapters": ["Calculus", "Matrices", "Eigen Values"]},
    "Programming": {"chapters": ["C Intro", "Control Flow", "Arrays", "Functions"]}
}

STATIC_QUESTIONS = {
    "Default": [
        {"q": "Which law states V=IR?", "opts": ["Ohm's Law", "Newton's Law", "Kirchhoff's Law", "Faraday's Law"], "ans": "Ohm's Law"},
        {"q": "What is the unit of Force?", "opts": ["Newton", "Joule", "Watt", "Pascal"], "ans": "Newton"},
        {"q": "Binary 1010 equals decimal...", "opts": ["10", "5", "12", "8"], "ans": "10"},
        {"q": "Integral of x dx is...", "opts": ["x^2 / 2", "x^2", "2x", "1/x"], "ans": "x^2 / 2"},
        {"q": "Power is defined as...", "opts": ["Rate of doing work", "Force x Distance", "Mass x Velocity", "None"], "ans": "Rate of doing work"}
    ]
}

# --- 4. SESSION STATE ---
if 'students_data' not in st.session_state:
    st.session_state.students_data = {"student1": {"password": "pass123", "name": "Student 1", "roll_no": "FE001", "subjects": list(SYLLABUS.keys())[:5], "marks": {}, "attendance": 85, "has_data": True}}
if 'teachers_data' not in st.session_state:
    st.session_state.teachers_data = {"teacher1": {"password": "teach123", "name": "Prof. Teacher", "subject": "Engineering Physics", "feedback_score": 4.7, "feedback_comments": [{"comment": "Good", "type": "positive"}]}}
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_type' not in st.session_state: st.session_state.user_type = None
if 'username' not in st.session_state: st.session_state.username = None
if 'current_page' not in st.session_state: st.session_state.current_page = 'login'
if 'api_key' not in st.session_state: st.session_state.api_key = ""
if 'selected_model' not in st.session_state: st.session_state.selected_model = "gemini-pro"

def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- 5. HELPER: FETCH AVAILABLE MODELS ---
def get_available_models(api_key):
    """Asks Google which models are actually available for this key"""
    if not api_key or not HAS_AI: return []
    try:
        genai.configure(api_key=api_key)
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
        return models
    except:
        return []

# --- 6. SIDEBAR (WITH MODEL SELECTOR) ---
def render_sidebar():
    with st.sidebar:
        # LOGO
        logo_path = "logo.png"
        if not os.path.exists(logo_path):
            files = [f for f in os.listdir('.') if f.endswith('.png')]
            if files: logo_path = files[0]
        
        if os.path.exists(logo_path): st.image(logo_path, width=180)
        else: st.header("🎓 FE Portal")
        
        st.caption("Created by FE DIV-A 2025-26")
        st.markdown("---")
        
        # API KEY & MODEL SELECTOR
        with st.expander("⚙️ AI Settings", expanded=True):
            key = st.text_input("Gemini API Key", type="password", value=st.session_state.api_key)
            
            if key:
                st.session_state.api_key = key
                # Auto-fetch models
                valid_models = get_available_models(key)
                if valid_models:
                    st.success(f"✅ Key Active! ({len(valid_models)} models found)")
                    # Dropdown to pick model
                    st.session_state.selected_model = st.selectbox("Select AI Model", valid_models, index=0)
                else:
                    st.warning("⚠️ Key invalid or no models found.")
            else:
                st.info("Paste Key to enable AI")
        
        st.markdown("---")
        if st.session_state.logged_in:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.current_page = 'login'
                st.rerun()

# --- 7. AI FUNCTIONS (USING SELECTED MODEL) ---
def get_ai_questions(subject, chapter, count=5):
    api_key = st.session_state.get('api_key')
    model_name = st.session_state.get('selected_model')
    
    if api_key and HAS_AI and model_name:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            
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
            st.error(f"AI Error ({model_name}): {str(e)}")
            
    return random.sample(STATIC_QUESTIONS["Default"], min(count, 5))

def get_ai_answer(question, context="General"):
    api_key = st.session_state.get('api_key')
    model_name = st.session_state.get('selected_model')
    
    if api_key and HAS_AI and model_name:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            res = model.generate_content(f"Context: {context}. Question: {question}")
            return res.text
        except Exception as e:
            return f"Error: {str(e)}"
    return "⚠️ AI Features Disabled (Check Key)"

# --- 8. PAGES ---
def login_register_page():
    st.markdown("<h1 style='text-align: center; color: #4db8ff;'>FE Engineering Portal 2024</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        with st.expander("ℹ️ Demo Credentials"): st.code("Student: student1 / pass123\nTeacher: teacher1 / teach123")
        role = st.radio("Role:", ["Student", "Teacher"], horizontal=True)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            db = st.session_state.students_data if role == "Student" else st.session_state.teachers_data
            if u in db and db[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user_type = role.lower()
                st.session_state.username = u
                navigate_to(f"{role.lower()}_dashboard")
            else: st.error("Invalid Credentials")

    with tab2:
        st.write("Registration (Demo Mode)"); st.button("Register")

def student_dashboard():
    st.title("🎯 Student Dashboard")
    st.info(f"Subjects: {', '.join(st.session_state.students_data[st.session_state.username]['subjects'])}")
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("📝 Take Assessment", use_container_width=True): navigate_to("assessment_setup")
    with c2: 
        if st.button("🤖 AI Assistant", use_container_width=True): navigate_to("student_ai")

def assessment_setup():
    st.title("📝 Setup Quiz")
    if st.button("Back"): navigate_to("student_dashboard")
    
    sub = st.selectbox("Subject", st.session_state.students_data[st.session_state.username]['subjects'])
    chap = st.selectbox("Chapter", SYLLABUS.get(sub, {'chapters':['General']})['chapters'])
    
    if st.button("Start Quiz", use_container_width=True):
        with st.spinner("Generating..."):
            qs = get_ai_questions(sub, chap, 5)
            st.session_state.quiz_session = {'subject': sub, 'chapter': chap, 'questions': qs}
            navigate_to("quiz_interface")

def quiz_interface():
    if 'quiz_session' not in st.session_state: navigate_to("student_dashboard")
    quiz = st.session_state.quiz_session
    st.header(f"{quiz['subject']}")
    
    answers = {}
    for i, q in enumerate(quiz['questions']):
        st.markdown(f"**Q{i+1}: {q['q']}**")
        answers[i] = st.radio(f"Select:", q['opts'], key=f"q{i}", index=None)
        st.markdown("---")
        
    if st.button("Submit"):
        score = sum([1 for i, q in enumerate(quiz['questions']) if answers.get(i) == q['ans']])
        st.success(f"Score: {score}/{len(quiz['questions'])}")
        st.button("Return", on_click=lambda: navigate_to("student_dashboard"))

def student_ai():
    st.title("🤖 AI Assistant")
    if st.button("Back"): navigate_to("student_dashboard")
    
    tab1, tab2 = st.tabs(["Ask PDF", "Quiz Maker"])
    with tab1:
        uploaded = st.file_uploader("Upload PDF", type="pdf")
        q = st.text_input("Question")
        if st.button("Ask"): 
            with st.spinner("Thinking..."): st.info(get_ai_answer(q, "PDF Content" if uploaded else "General"))
            
    with tab2:
        st.write("Generate Quiz from File")
        if st.button("Generate"):
            qs = get_ai_questions("Uploaded File", "General", 3)
            for i, q in enumerate(qs): st.write(f"**Q{i+1}: {q['q']}** (Ans: {q['ans']})")

def teacher_dashboard():
    st.title("👨‍🏫 Teacher Dashboard")
    c1, c2, c3 = st.columns(3)
    if c1.button("Profiles"): st.info("Profiles View")
    if c2.button("Feedback"): st.info("Feedback View")
    if c3.button("AI Tools"): st.info("AI Tools View")

def main():
    render_sidebar()
    if not st.session_state.logged_in: login_register_page()
    elif st.session_state.user_type == "student":
        p = st.session_state.current_page
        if p == 'student_dashboard': student_dashboard()
        elif p == 'assessment_setup': assessment_setup()
        elif p == 'quiz_interface': quiz_interface()
        elif p == 'student_ai': student_ai()
    elif st.session_state.user_type == "teacher": teacher_dashboard()

if __name__ == "__main__":
    main()
