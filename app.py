import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import random
import os
import google.generativeai as genai

# --- CONFIGURATION ---
st.set_page_config(page_title="FE Portal 2024", page_icon="🎓", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: 600; }
    .stRadio > label { background-color: #262730; padding: 10px; border-radius: 5px; width: 100%; border: 1px solid #4a4a4a; }
    </style>
""", unsafe_allow_html=True)

# --- SYLLABUS DATA ---
SYLLABUS = {
    "Engineering Physics": {"chapters": ["Fundamentals of Photonics", "Quantum Physics", "Wave Optics", "Semiconductor Physics"]},
    "Engineering Chemistry": {"chapters": ["Water Technology", "Instrumental Methods", "Advanced Materials", "Corrosion"]},
    "Basic Electrical Engineering": {"chapters": ["DC Circuits", "AC Fundamentals", "Electric Machines"]},
    "Engineering Mathematics-I": {"chapters": ["Calculus", "Matrices", "Eigen Values"]},
    "Fundamentals of Programming": {"chapters": ["C Intro", "Control Flow", "Arrays"]}
}

# --- SESSION STATE ---
if 'students_data' not in st.session_state:
    st.session_state.students_data = {"student1": {"password": "pass123", "name": "Demo Student", "roll_no": "FE001", "subjects": list(SYLLABUS.keys()), "marks": {}, "attendance": 85, "has_data": True}}
if 'teachers_data' not in st.session_state:
    st.session_state.teachers_data = {"teacher1": {"password": "teach123", "name": "Prof. Demo", "subject": "Engineering Physics", "feedback_score": 4.5, "feedback_comments": [{"comment": "Great class", "type": "positive"}]}}
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_type' not in st.session_state: st.session_state.user_type = None
if 'username' not in st.session_state: st.session_state.username = None
if 'current_page' not in st.session_state: st.session_state.current_page = 'login'
if 'api_key' not in st.session_state: st.session_state.api_key = ""

def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- AI FUNCTIONS (NO MOCK FALLBACK) ---
def get_ai_questions(subject, chapter, count=5):
    """
    Connects to Google Gemini to get REAL questions.
    If it fails, it will display the ERROR on screen.
    """
    if not st.session_state.api_key:
        st.error("❌ API Key is missing! Please enter it in the sidebar.")
        return []

    try:
        genai.configure(api_key=st.session_state.api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Strict prompt to force Python list format
        prompt = f"""
        Create {count} multiple-choice questions for {subject}, Chapter: {chapter}.
        Return ONLY a raw Python list of dictionaries. No markdown, no code blocks.
        Format: [{{'q': 'Question?', 'opts': ['A', 'B', 'C', 'D'], 'ans': 'Correct Option Text'}}]
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean up potential markdown formatting from AI
        if text.startswith("```"): text = text.replace("```python", "").replace("```", "")
        
        import ast
        return ast.literal_eval(text)
        
    except Exception as e:
        st.error(f"⚠️ AI Connection Error: {str(e)}")
        return []

def get_ai_answer(question, context="General Engineering"):
    if not st.session_state.api_key: return "Please enter API Key."
    try:
        genai.configure(api_key=st.session_state.api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        res = model.generate_content(f"Context: {context}. Question: {question}. Keep answer under 50 words.")
        return res.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- SIDEBAR ---
def render_sidebar():
    with st.sidebar:
        st.title("FE Portal 2024")
        st.markdown("### 🔑 AI Setup")
        key = st.text_input("Gemini API Key", type="password", value=st.session_state.api_key)
        if key:
            st.session_state.api_key = key
            st.success("Key Saved!")
        
        if st.session_state.logged_in:
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.current_page = 'login'
                st.rerun()

# --- PAGES ---
def login_page():
    st.title("🎓 FE Portal Login")
    with st.expander("Cheat Sheet"): st.write("student1 / pass123 | teacher1 / teach123")
    
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

def student_dashboard():
    st.title("Student Dashboard")
    st.write("Welcome to the Student Portal.")
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("📝 Take AI Quiz"): navigate_to("quiz_setup")
    with c2: 
        if st.button("🤖 Ask AI"): navigate_to("ask_ai")

def quiz_setup():
    st.title("Setup Quiz")
    if st.button("Back"): navigate_to("student_dashboard")
    
    sub = st.selectbox("Subject", list(SYLLABUS.keys()))
    chap = st.selectbox("Chapter", SYLLABUS[sub]['chapters'])
    
    if st.button("Generate Questions (Real AI)"):
        with st.spinner("Contacting Google Gemini..."):
            qs = get_ai_questions(sub, chap)
            if qs:
                st.session_state.quiz_session = {'questions': qs, 'score': 0}
                navigate_to("quiz_run")

def quiz_run():
    st.title("Quiz Time")
    qs = st.session_state.quiz_session['questions']
    
    answers = {}
    for i, q in enumerate(qs):
        st.markdown(f"**{i+1}. {q['q']}**")
        answers[i] = st.radio(f"Options {i}", q['opts'], key=f"q{i}", index=None)
        st.markdown("---")
        
    if st.button("Submit"):
        score = sum([1 for i, q in enumerate(qs) if answers.get(i) == q['ans']])
        st.session_state.quiz_session['score'] = score
        st.success(f"You scored {score} / {len(qs)}")
        if st.button("Back to Dashboard"): navigate_to("student_dashboard")

def ask_ai():
    st.title("Ask AI")
    if st.button("Back"): navigate_to("student_dashboard")
    
    uploaded = st.file_uploader("Upload PDF (Context)", type="pdf")
    q = st.text_input("Ask a question...")
    
    if st.button("Get Answer"):
        context = "PDF Content (Simulated for Demo)" if uploaded else "General Engineering"
        ans = get_ai_answer(q, context)
        st.info(ans)

def teacher_dashboard():
    st.title("Teacher Dashboard")
    if st.button("Generate Lecture Notes"): navigate_to("gen_notes")

def gen_notes():
    st.title("AI Lecture Notes")
    if st.button("Back"): navigate_to("teacher_dashboard")
    topic = st.text_input("Topic")
    if st.button("Generate"):
        st.write(get_ai_answer(f"Create lecture notes for {topic}", "Teaching"))

# --- MAIN ---
def main():
    render_sidebar()
    if not st.session_state.logged_in: login_page()
    elif st.session_state.user_type == "student":
        if st.session_state.current_page == 'student_dashboard': student_dashboard()
        elif st.session_state.current_page == 'quiz_setup': quiz_setup()
        elif st.session_state.current_page == 'quiz_run': quiz_run()
        elif st.session_state.current_page == 'ask_ai': ask_ai()
    elif st.session_state.user_type == "teacher":
        if st.session_state.current_page == 'teacher_dashboard': teacher_dashboard()
        elif st.session_state.current_page == 'gen_notes': gen_notes()

if __name__ == "__main__":
    main()
