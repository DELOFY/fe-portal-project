import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import random
import os

# Try importing the AI library (graceful fallback if not installed)
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

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
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

# --- REALISTIC STATIC DATA (Fallback if no AI Key) ---
STATIC_QUESTIONS = {
    "Engineering Physics": [
        {"q": "Which principle explains the working of Optical Fibers?", "opts": ["Total Internal Reflection", "Refraction", "Diffraction", "Polarization"], "ans": "Total Internal Reflection"},
        {"q": "What is the main property of a Laser beam?", "opts": ["Coherence", "Divergence", "Polychromatic", "Low Intensity"], "ans": "Coherence"},
        {"q": "In Quantum Mechanics, a particle in a box has energy that is...", "opts": ["Quantized", "Continuous", "Zero", "Infinite"], "ans": "Quantized"},
        {"q": "What is the full form of LASER?", "opts": ["Light Amplification by Stimulated Emission of Radiation", "Light Absorption by Stimulated Emission of Radiation", "Light Amplification by Spontaneous Emission of Radiation", "None"], "ans": "Light Amplification by Stimulated Emission of Radiation"},
        {"q": "Ultrasonic waves have frequency...", "opts": ["> 20 kHz", "< 20 Hz", "20 Hz to 20 kHz", "None of these"], "ans": "> 20 kHz"}
    ],
    "Engineering Chemistry": [
        {"q": "Hardness of water is caused by...", "opts": ["Calcium and Magnesium salts", "Sodium salts", "Potassium salts", "None"], "ans": "Calcium and Magnesium salts"},
        {"q": "Which method is used for water softening?", "opts": ["Zeolite Process", "Filtration", "Sedimentation", "Boiling"], "ans": "Zeolite Process"},
        {"q": "Corrosion is an example of...", "opts": ["Oxidation", "Reduction", "Polymerization", "None"], "ans": "Oxidation"}
    ],
    "Default": [
        {"q": "What is the primary unit of current?", "opts": ["Ampere", "Volt", "Ohm", "Watt"], "ans": "Ampere"},
        {"q": "Which law states V=IR?", "opts": ["Ohm's Law", "Newton's Law", "Kirchhoff's Law", "Faraday's Law"], "ans": "Ohm's Law"},
        {"q": "What is the derivative of x^2?", "opts": ["2x", "x", "2", "x^2"], "ans": "2x"},
        {"q": "Force is equal to...", "opts": ["Mass x Acceleration", "Mass x Velocity", "Mass / Volume", "None"], "ans": "Mass x Acceleration"},
        {"q": "Which gate returns true only if both inputs are true?", "opts": ["AND", "OR", "NOT", "XOR"], "ans": "AND"}
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

# --- HELPER FUNCTIONS ---
def get_questions(subject, count=5):
    """Gets questions from Static list (Reliable) or AI (if Key exists)"""
    # Check if we can use AI
    api_key = st.session_state.get('api_key', '')
    
    if api_key and HAS_AI:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            Generate {count} multiple choice questions for Engineering subject '{subject}'.
            Format strictly as a Python list of dictionaries:
            [{{"q": "Question?", "opts": ["A", "B", "C", "D"], "ans": "Correct Option Text"}}]
            Do not use markdown.
            """
            response = model.generate_content(prompt)
            import ast
            return ast.literal_eval(response.text.strip().replace("```python", "").replace("```", ""))
        except:
            st.toast("AI failed, using static backup questions.")
            
    # Fallback to Static Data
    pool = STATIC_QUESTIONS.get(subject, STATIC_QUESTIONS["Default"])
    # Ensure we have enough questions
    while len(pool) < count:
        pool.append(random.choice(STATIC_QUESTIONS["Default"]))
    return random.sample(pool, count)

def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- SESSION STATE SETUP ---
if 'students_data' not in st.session_state:
    st.session_state.students_data = {}
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
if 'selected_subjects' not in st.session_state: st.session_state.selected_subjects = []

# --- SIDEBAR ---
def render_sidebar():
    with st.sidebar:
        try:
            st.image("logo.png", width=150)
        except:
            st.write("FE Portal")
            
        st.title("FE Portal 2024")
        st.caption("2024 Pattern | SPPU")
        
        st.markdown("---")
        st.markdown("### 🧠 AI Settings")
        api_input = st.text_input("Gemini API Key", type="password", key="api_key_input")
        if api_input:
            st.session_state.api_key = api_input
            st.success("✅ AI Key Saved")
        
        st.markdown("---")
        if st.session_state.logged_in:
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.current_page = 'login'
                st.rerun()

# --- PAGES ---

def login_page():
    st.markdown("<h1 style='text-align: center; color: #4db8ff;'>🎓 FE Engineering Portal</h1>", unsafe_allow_html=True)
    
    with st.expander("🔑 Cheat Sheet (Demo Users)"):
        st.code("Student: student1 / pass123\nTeacher: teacher1 / teach123")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        role = st.selectbox("Login Role", ["Student", "Teacher"])
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            db = st.session_state.students_data if role == "Student" else st.session_state.teachers_data
            if u in db and db[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user_type = role.lower()
                st.session_state.username = u
                
                if role == "Student":
                    if db[u]['has_data']:
                        st.session_state.selected_subjects = db[u]['subjects']
                        navigate_to('student_dashboard')
                    else:
                        navigate_to('subject_selection')
                else:
                    navigate_to('teacher_dashboard')
            else:
                st.error("Invalid Credentials")

    with tab2:
        r_role = st.selectbox("Register Role", ["Student", "Teacher"])
        r_name = st.text_input("Full Name")
        r_user = st.text_input("New Username")
        r_pass = st.text_input("New Password", type="password")
        
        extra = {}
        if r_role == "Teacher":
            extra['sub'] = st.selectbox("Subject You Teach", list(SYLLABUS.keys()))
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
                st.success("Account Created! You can now Login.")

def student_dashboard():
    st.title("Student Dashboard")
    data = st.session_state.students_data[st.session_state.username]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Name", data['name'])
    c2.metric("Roll No", data['roll_no'])
    c3.metric("Attendance", f"{data['attendance']}%")
    
    st.subheader("Your Subjects")
    if not st.session_state.selected_subjects:
        st.warning("No subjects selected.")
    else:
        st.info(", ".join(st.session_state.selected_subjects))
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📝 Take Assessment"): navigate_to("assessment_setup")
    with c2:
        if st.button("🤖 AI Assistant"): navigate_to("student_ai")

def assessment_setup():
    st.title("Configure Assessment")
    if st.button("⬅ Back"): navigate_to("student_dashboard")
    
    student = st.session_state.students_data[st.session_state.username]
    if not student['subjects']:
        st.error("Please select subjects first.")
        return

    sub = st.selectbox("Select Subject", student['subjects'])
    chap = st.selectbox("Select Chapter", SYLLABUS.get(sub, {"chapters": ["General"]})['chapters'])
    
    if st.button("Start Quiz"):
        # Use fallback if AI fails or no key
        questions = get_questions(sub, 5)
        st.session_state.quiz_session = {
            'subject': sub, 'chapter': chap, 
            'questions': questions,
            'start_time': datetime.now()
        }
        navigate_to("quiz_interface")

def quiz_interface():
    if 'quiz_session' not in st.session_state:
        navigate_to("student_dashboard")
        return

    quiz = st.session_state.quiz_session
    st.subheader(f"Quiz: {quiz['subject']} - {quiz['chapter']}")
    
    answers = {}
    for i, q in enumerate(quiz['questions']):
        st.markdown(f"**Q{i+1}: {q['q']}**")
        answers[i] = st.radio(f"Select Answer {i}", q['opts'], key=f"q{i}", index=None)
        st.markdown("---")
        
    if st.button("Submit Assessment"):
        score = 0
        for i, q in enumerate(quiz['questions']):
            if answers.get(i) == q['ans']:
                score += 1
        
        st.session_state.quiz_result = {'score': score, 'total': len(quiz['questions']), 'answers': answers}
        navigate_to("quiz_feedback")

def quiz_feedback():
    st.title("Result & Feedback")
    
    res = st.session_state.quiz_result
    st.metric("Your Score", f"{res['score']} / {res['total']}")
    
    with st.expander("View Solutions"):
        quiz = st.session_state.quiz_session
        for i, q in enumerate(quiz['questions']):
            user_ans = res['answers'].get(i, "Skipped")
            color = "green" if user_ans == q['ans'] else "red"
            st.markdown(f"**Q{i+1}:** {q['q']}")
            st.markdown(f":{color}[Your Answer: {user_ans}]")
            st.markdown(f"**Correct Answer:** {q['ans']}")
            st.divider()

    st.subheader("Rate the Teacher (Mandatory)")
    c1, c2 = st.columns(2)
    with c1: st.slider("Clarity", 1, 5, 3)
    with c2: st.slider("Pace", 1, 5, 3)
    
    if st.button("Submit Feedback & Return"):
        st.success("Feedback Recorded!")
        time.sleep(1)
        navigate_to("student_dashboard")

def student_ai_page():
    st.title("Student AI Assistant")
    if st.button("⬅ Back"): navigate_to("student_dashboard")
    
    tab1, tab2 = st.tabs(["Ask Question", "Quiz Maker"])
    
    with tab1:
        st.write("Upload a PDF to ask questions.")
        uploaded = st.file_uploader("Upload PDF", type="pdf")
        user_q = st.text_input("Ask a question about the PDF...")
        
        if st.button("Get Answer"):
            if user_q:
                # Mock response if no Key, Real response if Key exists
                api_key = st.session_state.get('api_key', '')
                if api_key and HAS_AI:
                     try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        res = model.generate_content(f"Answer this question based on general engineering knowledge: {user_q}")
                        st.info(res.text)
                     except:
                        st.error("AI Error. Check Key.")
                else:
                    st.info(f"**AI (Simulated):** Based on the document context, the answer to '{user_q}' involves the core principles of the subject...")

    with tab2:
        st.write("Generate practice quiz from file.")
        st.file_uploader("Upload Material", type="pdf", key="q_up")
        if st.button("Generate Quiz"):
             st.success("Quiz Generated Below:")
             qs = get_questions("Default", 3)
             for i, q in enumerate(qs):
                 st.write(f"**Q{i+1}: {q['q']}**")
                 st.write(f"Ans: {q['ans']}")
                 st.divider()

def teacher_dashboard():
    st.title("Teacher Dashboard")
    data = st.session_state.teachers_data[st.session_state.username]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Name", data['name'])
    c2.metric("Subject", data['subject'])
    c3.metric("Rating", f"{data['feedback_score']}/5.0")
    
    st.markdown("---")
    
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("📊 Student Profiles"): navigate_to("teacher_profiles")
    with c2: 
        if st.button("💬 View Feedback"): navigate_to("teacher_feedback")
    with c3: 
        if st.button("🤖 AI Tools"): navigate_to("teacher_ai")

def teacher_profiles():
    st.title("Student Analytics")
    if st.button("⬅ Back"): navigate_to("teacher_dashboard")
    
    teacher_sub = st.session_state.teachers_data[st.session_state.username]['subject']
    students = [s for s in st.session_state.students_data.values() if teacher_sub in s.get('subjects', [])]
    
    if not students:
        st.warning(f"No students enrolled in {teacher_sub}")
        return

    sel_name = st.selectbox("Select Student", [s['name'] for s in students])
    sel_student = next(s for s in students if s['name'] == sel_name)
    
    st.subheader(f"Performance: {sel_name}")
    
    # Mock Marks for graph
    marks = [random.randint(5, 10) for _ in range(5)]
    fig = px.bar(x=[f"Ch {i+1}" for i in range(5)], y=marks, title=f"{teacher_sub} - Chapter Tests")
    st.plotly_chart(fig, use_container_width=True)
    
    # Radar Chart
    subjects = sel_student['subjects']
    r_vals = [random.randint(60, 90) for _ in subjects]
    fig2 = go.Figure(data=go.Scatterpolar(r=r_vals, theta=subjects, fill='toself', name='Progress'))
    fig2.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
    st.plotly_chart(fig2, use_container_width=True)

def teacher_feedback():
    st.title("Feedback Analysis")
    if st.button("⬅ Back"): navigate_to("teacher_dashboard")
    
    comments = st.session_state.teachers_data[st.session_state.username]['feedback_comments']
    
    for c in comments:
        if c['type'] == 'negative':
            st.error(f"Improvement Area: {c['comment']}")
        else:
            st.success(f"Praise: {c['comment']}")

def teacher_ai_page():
    st.title("Teacher AI Tools")
    if st.button("⬅ Back"): navigate_to("teacher_dashboard")
    
    tab1, tab2 = st.tabs(["Content Generator", "Question Bank"])
    
    with tab1:
        topic = st.text_input("Lecture Topic")
        if st.button("Generate Notes"):
            api_key = st.session_state.get('api_key', '')
            if api_key and HAS_AI:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    res = model.generate_content(f"Create lecture notes for: {topic}")
                    st.markdown(res.text)
                except:
                    st.error("AI Error")
            else:
                st.markdown(f"### Notes for {topic}\n1. Introduction...\n2. Key Concepts...\n*(Simulated Content)*")

    with tab2:
        st.file_uploader("Upload Reference PDF", type="pdf")
        if st.button("Generate Question Bank"):
            st.success("Questions Generated:")
            qs = get_questions("Engineering Physics", 3)
            for q in qs:
                st.write(f"- {q['q']} (Ans: {q['ans']})")

# --- MAIN ROUTER ---
def main():
    render_sidebar()
    if not st.session_state.logged_in:
        login_page()
    else:
        # Simple Page Routing
        p = st.session_state.current_page
        if p == 'subject_selection': 
            # Inline Subject Selection
            st.title("Select Subjects")
            s = st.session_state.students_data[st.session_state.username]
            if st.button("Auto-Select Default Subjects"):
                 s['subjects'] = list(SYLLABUS.keys())[:5]
                 s['has_data'] = True
                 st.session_state.selected_subjects = s['subjects']
                 navigate_to('student_dashboard')
                 
        elif p == 'student_dashboard': student_dashboard()
        elif p == 'assessment_setup': assessment_setup()
        elif p == 'quiz_interface': quiz_interface()
        elif p == 'quiz_feedback': quiz_feedback()
        elif p == 'student_ai': student_ai_page()
        
        elif p == 'teacher_dashboard': teacher_dashboard()
        elif p == 'teacher_profiles': teacher_profiles()
        elif p == 'teacher_feedback': teacher_feedback()
        elif p == 'teacher_ai': teacher_ai_page()

if __name__ == "__main__":
    main()
