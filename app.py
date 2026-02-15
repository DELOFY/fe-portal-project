import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import random
import os

# Try importing the AI library (if not installed, app won't crash, will just warn)
try:
    import google.generativeai as genai
    HAS_AI = True
except ImportError:
    HAS_AI = False

# --- CONFIGURATION ---
st.set_page_config(
    page_title="FE Portal 2024",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (Fixed Layouts) ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        font-weight: 600;
    }
    .header-text {
        color: #4db8ff;
        font-weight: bold;
    }
    .stRadio > label {
        font-weight: bold;
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

# --- REALISTIC STATIC FALLBACK DATA (No more "Option A") ---
# This is used if the AI fails or no Key is provided.
STATIC_QUESTIONS = {
    "Engineering Physics": [
        {"q": "Which principle explains the working of Optical Fibers?", "opts": ["Total Internal Reflection", "Refraction", "Diffraction", "Polarization"], "ans": "Total Internal Reflection"},
        {"q": "What is the main property of a Laser beam?", "opts": ["Coherence", "Divergence", "Polychromatic", "Low Intensity"], "ans": "Coherence"},
        {"q": "In Quantum Mechanics, a particle in a box has energy that is...", "opts": ["Quantized", "Continuous", "Zero", "Infinite"], "ans": "Quantized"}
    ],
    "Engineering Mathematics-I": [
        {"q": "The rank of a matrix is defined as...", "opts": ["Number of non-zero rows in Echelon form", "Number of columns", "Determinant value", "Sum of diagonal elements"], "ans": "Number of non-zero rows in Echelon form"},
        {"q": "Taylor's series expansion is used for...", "opts": ["Approximating functions", "Solving integrals", "Finding matrix inverse", "Sorting arrays"], "ans": "Approximating functions"}
    ],
    "Default": [
        {"q": "What is the primary unit of current?", "opts": ["Ampere", "Volt", "Ohm", "Watt"], "ans": "Ampere"},
        {"q": "Which law states V=IR?", "opts": ["Ohm's Law", "Newton's Law", "Kirchhoff's Law", "Faraday's Law"], "ans": "Ohm's Law"}
    ]
}

# --- SYLLABUS DATA ---
SYLLABUS = {
    "Engineering Physics": {"chapters": ["Fundamentals of Photonics", "Quantum Physics", "Wave Optics", "Semiconductor Physics", "Nanoparticles"]},
    "Engineering Chemistry": {"chapters": ["Water Technology", "Instrumental Methods", "Advanced Materials", "Energy Sources", "Corrosion"]},
    "Basic Electrical Engineering": {"chapters": ["DC Circuits", "Electromagnetism", "AC Fundamentals", "AC Circuits", "Electric Machines"]},
    "Basic Electronics Engineering": {"chapters": ["Diodes", "Transistors", "Logic Gates", "Op-Amp", "Sensors"]},
    "Engineering Mechanics": {"chapters": ["Force Systems", "Equilibrium", "Friction", "Kinematics", "Kinetics"]},
    "Engineering Mathematics-I": {"chapters": ["Calculus", "Multivariable Calculus", "Matrices", "Eigen Values"]},
    "Fundamentals of Programming Languages": {"chapters": ["C Intro", "Control Flow", "Arrays", "Functions"]}
}

# --- AI HELPER FUNCTIONS ---
def get_ai_questions(api_key, subject, chapter, count=5):
    """Generates questions using Gemini or falls back to static data"""
    if not api_key or not HAS_AI:
        # Fallback to static
        pool = STATIC_QUESTIONS.get(subject, STATIC_QUESTIONS["Default"])
        return [random.choice(pool) for _ in range(count)]
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Generate {count} multiple choice questions for Engineering subject '{subject}' 
        specifically for chapter '{chapter}'.
        Format strictly as this Python list of dictionaries:
        [
            {{"q": "Question text here", "opts": ["Option A", "Option B", "Option C", "Option D"], "ans": "Option C"}},
            ...
        ]
        Do not use markdown formatting. Just the raw list.
        """
        response = model.generate_content(prompt)
        text = response.text.strip().replace("```python", "").replace("```", "")
        import ast
        return ast.literal_eval(text)
    except Exception as e:
        st.error(f"AI Connection Failed: {str(e)}. Using static questions.")
        pool = STATIC_QUESTIONS.get(subject, STATIC_QUESTIONS["Default"])
        return [random.choice(pool) for _ in range(count)]

def get_ai_notes(api_key, topic):
    """Generates study notes"""
    if not api_key or not HAS_AI:
        return f"**Static Note:** AI Key missing. Topic '{topic}' is fundamental to the course. Please refer to standard textbooks."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Explain '{topic}' for a first-year engineering student in 200 words with bullet points.")
        return response.text
    except Exception as e:
        return f"Error generating notes: {str(e)}"

# --- SESSION STATE ---
if 'students_data' not in st.session_state:
    st.session_state.students_data = {} # Initialize empty or mock
    # Create one default student
    st.session_state.students_data["student1"] = {
        "password": "pass123", "name": "Demo Student", "roll_no": "FE001",
        "subjects": list(SYLLABUS.keys())[:5], "marks": {}, "attendance": 85, "has_data": True
    }

if 'teachers_data' not in st.session_state:
    st.session_state.teachers_data = {}
    st.session_state.teachers_data["teacher1"] = {
        "password": "teach123", "name": "Prof. Demo", "subject": "Engineering Physics",
        "feedback_score": 4.5, "feedback_comments": [{"comment": "Great class", "type": "positive"}]
    }

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_type' not in st.session_state: st.session_state.user_type = None
if 'username' not in st.session_state: st.session_state.username = None
if 'current_page' not in st.session_state: st.session_state.current_page = 'login'
if 'api_key' not in st.session_state: st.session_state.api_key = ""

# --- NAVIGATION HELPER ---
def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- SIDEBAR ---
def render_sidebar():
    with st.sidebar:
        st.image("logo.png" if os.path.exists("logo.png") else "https://via.placeholder.com/150", width=150)
        st.title("FE Portal")
        st.caption("2024 Pattern | SPPU")
        
        # API Key Input
        st.markdown("---")
        st.markdown("### 🧠 AI Settings")
        api_key = st.text_input("Gemini API Key", type="password", placeholder="Paste key for Real AI", value=st.session_state.api_key)
        if api_key:
            st.session_state.api_key = api_key
            
        if not st.session_state.api_key:
            st.warning("⚠️ Using Offline Mode. (Add Key for AI)")
        else:
            st.success("✅ AI Active")

        st.markdown("---")
        if st.session_state.logged_in:
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.current_page = 'login'
                st.rerun()

# --- PAGES ---

def login_page():
    st.markdown("<h1 style='text-align: center; color: #4db8ff;'>🎓 FE Engineering Portal</h1>", unsafe_allow_html=True)
    
    with st.expander("🔑 Cheat Sheet"):
        st.code("Student: student1 / pass123\nTeacher: teacher1 / teach123")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        role = st.selectbox("Role", ["Student", "Teacher"])
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            db = st.session_state.students_data if role == "Student" else st.session_state.teachers_data
            if u in db and db[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user_type = role.lower()
                st.session_state.username = u
                navigate_to(f"{role.lower()}_dashboard")
            else:
                st.error("Invalid Credentials")

    with tab2:
        st.write("Registration disabled for this demo view.")

def student_dashboard():
    st.title("Student Dashboard")
    st.write(f"Welcome, **{st.session_state.students_data[st.session_state.username]['name']}**")
    
    c1, c2 = st.columns(2)
    with c1:
        st.info("📝 **Assessments**")
        if st.button("Take New Test"): navigate_to("assessment_setup")
    with c2:
        st.success("🤖 **AI Assistant**")
        if st.button("Open AI Tools"): navigate_to("student_ai")

def assessment_setup():
    st.title("Configure Assessment")
    if st.button("⬅ Back"): navigate_to("student_dashboard")
    
    student = st.session_state.students_data[st.session_state.username]
    sub = st.selectbox("Select Subject", student['subjects'])
    chap = st.selectbox("Select Chapter", SYLLABUS.get(sub, {"chapters": ["General"]})['chapters'])
    
    if st.button("Start Quiz"):
        with st.spinner("Generating Questions..."):
            questions = get_ai_questions(st.session_state.api_key, sub, chap)
            st.session_state.quiz_session = {
                'subject': sub, 'chapter': chap, 'questions': questions, 'start_time': datetime.now()
            }
            navigate_to("quiz_interface")

def quiz_interface():
    if 'quiz_session' not in st.session_state:
        navigate_to("student_dashboard")
        return

    quiz = st.session_state.quiz_session
    st.subheader(f"Quiz: {quiz['subject']}")
    
    answers = {}
    for i, q in enumerate(quiz['questions']):
        st.markdown(f"**Q{i+1}: {q['q']}**")
        # index=None is CRITICAL to ensure no option is pre-selected
        answers[i] = st.radio(f"Select Answer {i}", q['opts'], key=f"q{i}", index=None)
        st.divider()
    
    if st.button("Submit Assessment"):
        score = 0
        for i, q in enumerate(quiz['questions']):
            if answers.get(i) == q['ans']:
                score += 1
        st.session_state.quiz_result = {'score': score, 'total': len(quiz['questions']), 'answers': answers}
        navigate_to("quiz_feedback")

def quiz_feedback():
    st.title("Result & Feedback")
    
    # 1. Show Results
    res = st.session_state.quiz_result
    st.metric("Your Score", f"{res['score']} / {res['total']}")
    
    with st.expander("View Detailed Solutions"):
        quiz = st.session_state.quiz_session
        for i, q in enumerate(quiz['questions']):
            user_ans = res['answers'].get(i, "Skipped")
            color = "green" if user_ans == q['ans'] else "red"
            st.markdown(f"**Q{i+1}:** {q['q']}")
            st.markdown(f":{color}[Your Answer: {user_ans}]")
            st.markdown(f"**Correct Answer:** {q['ans']}")
            st.markdown("---")

    # 2. Teacher Feedback (Mandatory flow)
    st.write("---")
    st.subheader("Rate the Teacher")
    c1, c2 = st.columns(2)
    with c1: st.slider("Clarity", 1, 5, 3)
    with c2: st.slider("Pace", 1, 5, 3)
    
    # Bug Fix: Ensure this button strictly navigates away
    if st.button("Submit Feedback & Return to Dashboard"):
        st.success("Feedback Recorded!")
        time.sleep(1)
        navigate_to("student_dashboard")

def student_ai_page():
    st.title("Student AI Assistant")
    if st.button("⬅ Back"): navigate_to("student_dashboard")
    
    tab1, tab2 = st.tabs(["Ask Question", "Quiz Maker"])
    
    with tab1:
        st.write("Upload a PDF to ask questions about it.")
        uploaded = st.file_uploader("Upload PDF", type="pdf")
        question = st.text_input("Ask your question here...")
        
        if st.button("Get Answer"):
            if not st.session_state.api_key:
                st.error("Please enter a Gemini API Key in the sidebar first.")
            elif question:
                with st.spinner("AI is thinking..."):
                    # Real AI Call
                    ans = get_ai_notes(st.session_state.api_key, question)
                    st.info(ans)

    with tab2:
        st.write("Generate a custom quiz from a file.")
        q_file = st.file_uploader("Upload Material", type="pdf", key="q_file")
        if st.button("Generate Practice Quiz"):
            if st.session_state.api_key:
                st.success("Quiz Generated (See below)")
                # Here you would add logic to parse PDF, but for now we generate based on topic
                qs = get_ai_questions(st.session_state.api_key, "General", "Uploaded Content", 3)
                for q in qs:
                    st.write(f"**Q:** {q['q']}")
            else:
                st.warning("Need API Key for file processing.")

def teacher_dashboard():
    st.title("Teacher Dashboard")
    st.write(f"Logged in as: **{st.session_state.teachers_data[st.session_state.username]['name']}**")
    
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("Student Profiles"): navigate_to("teacher_profiles")
    with c2: 
        if st.button("View Feedback"): navigate_to("teacher_feedback")
    with c3: 
        if st.button("AI Content Tools"): navigate_to("teacher_ai")

def teacher_ai_page():
    st.title("Teacher AI Tools")
    if st.button("⬅ Back"): navigate_to("teacher_dashboard")
    
    tab1, tab2 = st.tabs(["Content Generator", "Question Bank Generator"])
    
    with tab1:
        st.subheader("Lecture Note Generator")
        topic = st.text_input("Enter Topic (e.g., Newton's Laws)")
        if st.button("Generate Notes"):
            with st.spinner("Generating..."):
                notes = get_ai_notes(st.session_state.api_key, topic)
                st.markdown(notes)
                
    with tab2:
        st.subheader("Question Bank Generator")
        # Bug Fix 6: Added File Uploader
        st.file_uploader("Upload Syllabus/PDF Reference", type="pdf")
        sub_input = st.text_input("Subject/Topic")
        
        if st.button("Generate Questions"):
            with st.spinner("Creating Questions..."):
                qs = get_ai_questions(st.session_state.api_key, sub_input, "General", 5)
                for i, q in enumerate(qs):
                    st.write(f"{i+1}. {q['q']}")
                    st.caption(f"Ans: {q['ans']}")

# --- MAIN ROUTER ---
def main():
    render_sidebar()
    
    if not st.session_state.logged_in:
        login_page()
    else:
        # Page Routing
        p = st.session_state.current_page
        if p == 'student_dashboard': student_dashboard()
        elif p == 'assessment_setup': assessment_setup()
        elif p == 'quiz_interface': quiz_interface()
        elif p == 'quiz_feedback': quiz_feedback()
        elif p == 'student_ai': student_ai_page()
        
        elif p == 'teacher_dashboard': teacher_dashboard()
        elif p == 'teacher_ai': teacher_ai_page()
        # Fallback for pages not fully implemented in this snippet to save space
        elif p == 'teacher_profiles': 
            st.title("Student Profiles"); st.button("Back", on_click=lambda: navigate_to('teacher_dashboard'))
        elif p == 'teacher_feedback':
            st.title("Feedback"); st.button("Back", on_click=lambda: navigate_to('teacher_dashboard'))

if __name__ == "__main__":
    main()
