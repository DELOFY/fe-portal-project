import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import random
import os
import io

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="FE Portal 2024",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LIBRARY CHECKS ---
try:
    import google.generativeai as genai
    HAS_AI = True
except ImportError:
    HAS_AI = False

try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

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
if 'selected_model' not in st.session_state: st.session_state.selected_model = "gemini-1.5-flash"

def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- 5. HELPER FUNCTIONS ---
@st.cache_data
def get_available_models(api_key):
    """Cached model fetcher to prevent 429 errors"""
    if not api_key or not HAS_AI: return []
    try:
        genai.configure(api_key=api_key)
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini' in m.name:
                    models.append(m.name)
        return models
    except:
        return []

def extract_pdf_text(uploaded_file):
    """Reads text from uploaded PDF so AI can see it"""
    if not HAS_PDF: return "ERROR: PyPDF2 library not installed. Please install it to read PDFs."
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        # Read first 5 pages max to save token limit
        for i in range(min(len(reader.pages), 5)):
            text += reader.pages[i].extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

# --- 6. SIDEBAR ---
def render_sidebar():
    with st.sidebar:
        logo_path = "logo.png"
        if not os.path.exists(logo_path):
            files = [f for f in os.listdir('.') if f.endswith('.png')]
            if files: logo_path = files[0]
        
        if os.path.exists(logo_path): st.image(logo_path, width=180)
        else: st.header("🎓 FE Portal")
        
        st.caption("Created by FE DIV-A 2025-26")
        st.markdown("---")
        
        with st.expander("⚙️ AI Settings", expanded=True):
            key = st.text_input("Gemini API Key", type="password", value=st.session_state.api_key)
            if key:
                st.session_state.api_key = key
                valid_models = get_available_models(key)
                if valid_models:
                    st.success(f"✅ Key Active!")
                    # Check PDF Status
                    if HAS_PDF: st.success("✅ PDF Reader Active")
                    else: st.error("❌ PDF Reader Missing")
                    
                    default_idx = 0
                    for i, m in enumerate(valid_models):
                        if 'flash' in m: default_idx = i; break
                    st.session_state.selected_model = st.selectbox("Select AI Model", valid_models, index=default_idx)
                else:
                    st.warning("⚠️ Key invalid or quota exceeded.")
            else:
                st.info("Paste Key to enable AI")
        
        st.markdown("---")
        if st.session_state.logged_in:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.current_page = 'login'
                st.rerun()

# --- 7. AI FUNCTIONS ---
def get_ai_questions(context_text, count=5, difficulty="Medium"):
    """Generates questions based on provided text (Syllabus OR PDF Content)"""
    api_key = st.session_state.get('api_key')
    model_name = st.session_state.get('selected_model')
    
    if api_key and HAS_AI and model_name:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            
            # Truncate context to avoid token limits (approx 3000 chars)
            safe_context = context_text[:3000]
            
            # IMPROVED PROMPT
            prompt = f"""
            You are an Engineering Professor. Generate {count} multiple-choice questions (MCQs) 
            specifically about: "{safe_context}".
            Difficulty Level: {difficulty}.
            
            The questions must be technical and relevant to the subject matter provided.
            Do NOT ask generic questions like "What is this text about?".
            
            Strictly return a Python list of dictionaries. NO markdown.
            Format: [{{'q': 'Question Text', 'opts': ['A', 'B', 'C', 'D'], 'ans': 'Correct Option Text'}}]
            """
            
            response = model.generate_content(prompt)
            text = response.text.strip().replace("```python", "").replace("```", "")
            import ast
            return ast.literal_eval(text)
        except Exception as e:
            st.error(f"AI Error ({model_name}): {str(e)}")
            
    return random.sample(STATIC_QUESTIONS["Default"], min(count, 5))

def get_ai_answer(question, context_text):
    api_key = st.session_state.get('api_key')
    model_name = st.session_state.get('selected_model')
    
    if api_key and HAS_AI and model_name:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            safe_context = context_text[:3000]
            res = model.generate_content(f"Context: {safe_context}\n\nQuestion: {question}")
            return res.text
        except Exception as e:
            return f"Error: {str(e)}"
    return "⚠️ AI Features Disabled"

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
        st.subheader("Create New Account")
        reg_role = st.selectbox("I am a...", ["Student", "Teacher"])
        reg_user = st.text_input("Choose Username")
        reg_pass = st.text_input("Choose Password", type="password")
        
        if st.button("Create Account"):
            target_db = st.session_state.teachers_data if reg_role == "Teacher" else st.session_state.students_data
            if reg_user in target_db:
                st.error("Username already exists!")
            else:
                # Create basic profile
                if reg_role == "Student":
                    target_db[reg_user] = {"password": reg_pass, "name": reg_user, "subjects": [], "marks": {}, "attendance": 0, "has_data": False}
                else:
                    target_db[reg_user] = {"password": reg_pass, "name": reg_user, "subject": "General", "feedback_score": 0, "feedback_comments": []}
                st.success("Account Created! Please switch to Login tab.")

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
            # Pass Subject + Chapter as context
            context = f"Subject: {sub}, Chapter: {chap}. Specific technical engineering concepts."
            qs = get_ai_questions(context, 5, "Medium")
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
        # FIX: Removed on_click callback that caused the error
        if st.button("Return to Dashboard"):
            navigate_to("student_dashboard")

def student_ai():
    st.title("🤖 AI Assistant")
    if st.button("Back"): navigate_to("student_dashboard")
    
    tab1, tab2 = st.tabs(["Ask PDF", "Quiz Maker"])
    
    with tab1:
        uploaded = st.file_uploader("Upload PDF", type="pdf", key="chat_pdf")
        q = st.text_input("Question")
        if st.button("Ask"):
            if not uploaded: st.error("Upload PDF first")
            else:
                with st.spinner("Reading & Thinking..."):
                    pdf_text = extract_pdf_text(uploaded)
                    st.info(get_ai_answer(q, pdf_text))
                    
    with tab2:
        st.subheader("Generate Quiz from File")
        q_file = st.file_uploader("Upload PDF for Quiz", type="pdf", key="q_maker_upload")
        difficulty = st.select_slider("Select Difficulty", options=["Easy", "Medium", "Hard"])
        
        if st.button("Generate"):
            if not q_file:
                st.error("Please upload a file first.")
            else:
                with st.spinner("Reading PDF & Generating..."):
                    pdf_text = extract_pdf_text(q_file)
                    qs = get_ai_questions(pdf_text, 3, difficulty)
                    for i, q in enumerate(qs): st.write(f"**Q{i+1}: {q['q']}** (Ans: {q['ans']})")

def teacher_dashboard():
    st.title("👨‍🏫 Teacher Dashboard")
    st.write("Welcome Professor.")
    
    c1, c2, c3 = st.columns(3)
    # FIX: Added actual navigation for teacher buttons
    if c1.button("📊 Profiles"): 
        st.session_state.teacher_page = "profiles"
        st.rerun()
    if c2.button("💬 Feedback"): 
        st.session_state.teacher_page = "feedback"
        st.rerun()
    if c3.button("🤖 AI Tools"): 
        st.session_state.teacher_page = "ai_tools"
        st.rerun()

    # Teacher Sub-page Router
    t_page = st.session_state.get("teacher_page", "dashboard")
    
    if t_page == "profiles":
        st.divider()
        st.subheader("Student Profiles")
        # Mock Graph
        df = pd.DataFrame({"Student": ["A", "B", "C", "D"], "Score": [85, 92, 78, 88]})
        fig = px.bar(df, x="Student", y="Score", title="Class Performance")
        st.plotly_chart(fig)
        if st.button("Close View"): st.session_state.teacher_page = "dashboard"; st.rerun()
        
    elif t_page == "feedback":
        st.divider()
        st.subheader("Student Feedback")
        st.info("Course Pace: 4.5/5")
        st.warning("Needs more practical examples.")
        if st.button("Close View"): st.session_state.teacher_page = "dashboard"; st.rerun()
        
    elif t_page == "ai_tools":
        st.divider()
        st.subheader("Lesson Planner")
        topic = st.text_input("Enter Topic")
        if st.button("Generate Plan"):
            st.write(get_ai_answer(f"Create a lesson plan for {topic}", "Teaching"))
        if st.button("Close View"): st.session_state.teacher_page = "dashboard"; st.rerun()

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
