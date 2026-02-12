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
    </style>
""", unsafe_allow_html=True)

# Initialize session state
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

# Syllabus Data Structure
SYLLABUS = {
    "Engineering Physics": {
        "chapters": [
            "Fundamentals of Photonics",
            "Quantum Physics",
            "Wave Optics",
            "Semiconductor Physics and Ultrasonics",
            "Physics of Nanoparticles and Superconductivity"
        ]
    },
    "Engineering Chemistry": {
        "chapters": [
            "Water Technology",
            "Instrumental Methods of Analysis",
            "Advanced Engineering Materials",
            "Energy Sources",
            "Corrosion and its Prevention"
        ]
    },
    "Basic Electrical Engineering": {
        "chapters": [
            "Elementary Concepts and DC Circuits",
            "Electromagnetism",
            "AC Fundamentals",
            "AC Circuits",
            "Introduction to Electric Machines"
        ]
    },
    "Basic Electronics Engineering": {
        "chapters": [
            "Diodes and Applications",
            "Transistors and Technology",
            "Logic Gates and Digital Circuits",
            "Operational Amplifier and Electronic Instruments",
            "Sensors and Communication Systems"
        ]
    },
    "Engineering Mechanics": {
        "chapters": [
            "Force Systems and Resultants",
            "Equilibrium",
            "Friction and Trusses",
            "Kinematics of Particle",
            "Kinetics of Particle"
        ]
    },
    "Engineering Graphics": {
        "chapters": [
            "Fundamentals of Engineering Drawing",
            "Projection of Plane",
            "Engineering Curves and Development",
            "Orthographic Projection",
            "Isometric Projection"
        ]
    },
    "Engineering Mathematics-I": {
        "chapters": [
            "Single Variable Calculus",
            "Multivariable Calculus",
            "Applications of Partial Differentiation",
            "Linear Algebra - Matrices",
            "Eigen Values and Vectors"
        ]
    },
    "Engineering Mathematics-II": {
        "chapters": [
            "Integral Calculus",
            "Curve Tracing and Solid Geometry",
            "Multiple Integrals",
            "First Order ODE",
            "Applications of Differential Equations"
        ]
    },
    "Fundamentals of Programming Languages": {
        "chapters": [
            "Introduction to C Programming",
            "Operators and Expressions",
            "Control Flow",
            "Arrays",
            "User Defined Functions"
        ]
    },
    "Programming and Problem Solving": {
        "chapters": [
            "Problem Solving and Python",
            "Data Types and Control",
            "Functions and Strings",
            "File Handling",
            "Object Oriented Programming"
        ]
    },
    "Manufacturing Practice Workshop": {
        "chapters": [
            "Workshop Safety",
            "Cutting Techniques",
            "Sheet Metal Operations",
            "CNC Machines",
            "3D Printing"
        ]
    }
}

# Mock Data Generation
def generate_student_data():
    students = {}
    
    # 25 students with data
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
        
        # Generate marks for each subject
        for subject in students[f"student{i}"]["subjects"]:
            students[f"student{i}"]["marks"][subject] = {
                "chapter_tests": [random.randint(6, 10) for _ in range(5)],
                "subject_assessment": random.randint(18, 30),
                "overall": random.randint(60, 95)
            }
    
    # 5 students without data
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
                {"comment": "Should provide more examples", "type": "negative"},
            ]
        }
    
    return teachers

STUDENTS = generate_student_data()
TEACHERS = generate_teacher_data()

# MCQ Questions Bank
MCQ_BANK = {
    subject: [
        {
            "question": f"Sample question {i+1} for {subject}?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct": random.randint(0, 3)
        } for i in range(30)
    ] for subject in SYLLABUS.keys()
}

# Sidebar
def render_sidebar():
    with st.sidebar:
        st.image("logo.png", width=200)
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

# Login Page
def login_page():
    st.markdown("<h1 style='text-align: center; color: #4db8ff;'>🎓 FE Engineering Portal 2024</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #a0a0a0;'>SPPU 2024 Pattern</h3>", unsafe_allow_html=True)
    
    # Cheat Sheet
    st.markdown("""
        <div class='cheat-sheet'>
            <h3 style='color: #4db8ff;'>🔑 Login Credentials (For Testing)</h3>
            <p><strong>Student Login:</strong></p>
            <ul>
                <li>Username: <code>student1</code></li>
                <li>Password: <code>pass123</code></li>
            </ul>
            <p><strong>Teacher Login:</strong></p>
            <ul>
                <li>Username: <code>teacher1</code></li>
                <li>Password: <code>teach123</code></li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👨‍🎓 Student Login", "👨‍🏫 Teacher Login"])
    
    with tab1:
        st.markdown("### Student Login")
        username = st.text_input("Username", key="student_user", placeholder="student1")
        password = st.text_input("Password", type="password", key="student_pass", placeholder="pass123")
        
        if st.button("Login as Student", use_container_width=True):
            if username in STUDENTS and STUDENTS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.user_type = "student"
                st.session_state.username = username
                st.session_state.current_page = 'subject_selection'
                st.success("Login successful!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid credentials!")
    
    with tab2:
        st.markdown("### Teacher Login")
        username = st.text_input("Username", key="teacher_user", placeholder="teacher1")
        password = st.text_input("Password", type="password", key="teacher_pass", placeholder="teach123")
        
        if st.button("Login as Teacher", use_container_width=True):
            if username in TEACHERS and TEACHERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.user_type = "teacher"
                st.session_state.username = username
                st.session_state.current_page = 'teacher_dashboard'
                st.success("Login successful!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid credentials!")

# Subject Selection Page (Student)
def subject_selection_page():
    st.markdown("<h2 class='header-text'>📚 Select Your 5 Subjects</h2>", unsafe_allow_html=True)
    
    student = STUDENTS[st.session_state.username]
    
    if student['has_data']:
        st.info(f"Your registered subjects: {', '.join(student['subjects'])}")
        st.session_state.selected_subjects = student['subjects']
        st.session_state.current_page = 'student_dashboard'
        st.rerun()
    else:
        st.warning("⚠️ No data available for this student profile (Demo Account)")
        
        all_subjects = list(SYLLABUS.keys())
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Group 1:**")
            group1 = st.selectbox("Select one", ["Engineering Physics", "Basic Electrical Engineering", "Engineering Mechanics"])
        
        with col2:
            st.markdown("**Group 2:**")
            group2 = st.selectbox("Select one", ["Engineering Chemistry", "Basic Electronics Engineering", "Engineering Graphics"])
        
        math = st.selectbox("**Mathematics:**", ["Engineering Mathematics-I", "Engineering Mathematics-II"])
        programming = st.selectbox("**Programming:**", ["Fundamentals of Programming Languages", "Programming and Problem Solving"])
        workshop = "Manufacturing Practice Workshop"
        
        selected = [group1, group2, math, programming, workshop]
        
        if st.button("Confirm Subjects", use_container_width=True):
            st.session_state.selected_subjects = selected
            student['subjects'] = selected
            st.session_state.current_page = 'student_dashboard'
            st.rerun()

# Student Dashboard
def student_dashboard():
    st.markdown("<h2 class='header-text'>🎯 Student Dashboard</h2>", unsafe_allow_html=True)
    
    student = STUDENTS[st.session_state.username]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Name", student['name'])
    with col2:
        st.metric("Roll No", student['roll_no'])
    with col3:
        st.metric("Attendance", f"{student['attendance']}%")
    
    st.markdown("---")
    st.markdown("### Your Subjects:")
    st.write(", ".join(st.session_state.selected_subjects))
    
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

# Assessment Page
def assessment_page():
    st.markdown("<h2 class='header-text'>📝 Assessment</h2>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.current_page = 'student_dashboard'
        st.rerun()
    
    subject = st.selectbox("Select Subject", st.session_state.selected_subjects)
    assessment_type = st.radio("Assessment Type", ["Chapter Assessment", "Subject Assessment"])
    
    if assessment_type == "Chapter Assessment":
        chapter = st.selectbox("Select Chapter", SYLLABUS[subject]["chapters"])
        marks = 10
        duration = 10
        num_questions = 10
    else:
        chapter = "All Chapters"
        marks = 30
        duration = 30
        num_questions = 30
    
    st.info(f"📊 Total Marks: {marks} | ⏱️ Duration: {duration} minutes")
    
    if st.button("Start Assessment", use_container_width=True):
        st.session_state.quiz_data = {
            'subject': subject,
            'chapter': chapter,
            'marks': marks,
            'duration': duration,
            'num_questions': num_questions,
            'start_time': datetime.now(),
            'questions': random.sample(MCQ_BANK[subject], num_questions)
        }
        st.session_state.current_page = 'quiz'
        st.rerun()

# Quiz Page
def quiz_page():
    quiz = st.session_state.quiz_data
    
    st.markdown(f"<h2 class='header-text'>📝 {quiz['subject']} - {quiz['chapter']}</h2>", unsafe_allow_html=True)
    
    # Timer
    elapsed = (datetime.now() - quiz['start_time']).seconds
    remaining = quiz['duration'] * 60 - elapsed
    
    if remaining <= 0:
        st.error("⏰ Time's up!")
        st.session_state.current_page = 'feedback_form'
        st.rerun()
    
    mins, secs = divmod(remaining, 60)
    st.warning(f"⏱️ Time Remaining: {mins:02d}:{secs:02d}")
    
    # Questions
    answers = {}
    for i, q in enumerate(quiz['questions']):
        st.markdown(f"**Q{i+1}. {q['question']}**")
        answers[i] = st.radio(f"Select answer for Q{i+1}", q['options'], key=f"q{i}")
        st.markdown("---")
    
    if st.button("Submit Assessment", use_container_width=True):
        # Calculate score
        score = sum(1 for i, q in enumerate(quiz['questions']) if q['options'].index(answers.get(i, "")) == q['correct'])
        st.session_state.quiz_score = score
        st.session_state.current_page = 'feedback_form'
        st.rerun()

# Feedback Form (Mandatory after quiz)
def feedback_form_page():
    st.markdown("<h2 class='header-text'>📋 Teacher Feedback</h2>", unsafe_allow_html=True)
    st.info("Please rate your teacher's performance for this subject before viewing your results.")
    
    subject = st.session_state.quiz_data['subject']
    
    rating = st.slider("Overall Rating (1-5)", 1, 5, 3)
    teaching_quality = st.slider("Teaching Quality (1-5)", 1, 5, 3)
    clarity = st.slider("Clarity of Explanation (1-5)", 1, 5, 3)
    engagement = st.slider("Student Engagement (1-5)", 1, 5, 3)
    
    comments = st.text_area("Additional Comments (Optional)")
    
    if st.button("Submit Feedback & View Results", use_container_width=True):
        # Show results
        score = st.session_state.quiz_score
        total = st.session_state.quiz_data['num_questions']
        percentage = (score / total) * 100
        
        st.success(f"### 🎉 Your Score: {score}/{total} ({percentage:.1f}%)")
        
        if percentage >= 75:
            st.balloons()
            st.success("Excellent performance! 🌟")
        elif percentage >= 50:
            st.info("Good effort! Keep practicing. 💪")
        else:
            st.warning("Need improvement. Please review the chapters. 📚")
        
        time.sleep(3)
        st.session_state.current_page = 'student_dashboard'
        st.rerun()

# AI Assistant Page
def ai_assistant_page():
    st.markdown("<h2 class='header-text'>🤖 AI Assistant</h2>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.current_page = 'student_dashboard'
        st.rerun()
    
    tab1, tab2 = st.tabs(["❓ Ask Question", "📝 Quiz Maker"])
    
    with tab1:
        st.markdown("### Upload PDF and Ask Questions")
        uploaded_file = st.file_uploader("Upload PDF Document", type=['pdf'])
        
        if uploaded_file:
            st.success("✅ PDF uploaded successfully!")
            
            question = st.text_area("Ask your question about the document:")
            
            if st.button("Get Answer"):
                with st.spinner("AI is processing your question..."):
                    time.sleep(2)
                    st.markdown("""
                        <div class='info-box'>
                        <h4>📖 AI Response (Simulated)</h4>
                        <p>This is a simulated AI response based on your PDF document. 
                        In a real implementation, this would use advanced NLP models to 
                        extract relevant information from your uploaded document and 
                        provide accurate answers to your questions.</p>
                        <p>Your question: <strong>{}</strong></p>
                        <p>Based on the document context, here's a comprehensive answer 
                        that addresses your query with relevant examples and explanations.</p>
                        </div>
                    """.format(question), unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### AI-Powered Quiz Generator")
        
        subject = st.selectbox("Select Subject", st.session_state.selected_subjects)
        difficulty = st.select_slider("Difficulty Level", ["Easy", "Intermediate", "Advanced"])
        num_questions = st.slider("Number of Questions", 5, 15, 10)
        
        if st.button("Generate Quiz"):
            with st.spinner("Generating quiz..."):
                time.sleep(2)
                st.success("✅ Quiz generated!")
                
                questions = random.sample(MCQ_BANK[subject], num_questions)
                
                for i, q in enumerate(questions):
                    st.markdown(f"**Q{i+1}. {q['question']}**")
                    for opt in q['options']:
                        st.write(f"  - {opt}")
                    
                    with st.expander("Show Answer"):
                        st.success(f"Correct Answer: {q['options'][q['correct']]}")
                    
                    st.markdown("---")

# Teacher Dashboard
def teacher_dashboard():
    st.markdown("<h2 class='header-text'>👨‍🏫 Teacher Dashboard</h2>", unsafe_allow_html=True)
    
    teacher = TEACHERS[st.session_state.username]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Name", teacher['name'])
    with col2:
        st.metric("Subject", teacher['subject'])
    with col3:
        st.metric("Feedback Score", f"{teacher['feedback_score']}/5.0")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👥 Student Profiles", use_container_width=True):
            st.session_state.current_page = 'student_profiles'
            st.rerun()
    
    with col2:
        if st.button("💬 Feedback", use_container_width=True):
            st.session_state.current_page = 'teacher_feedback'
            st.rerun()
    
    with col3:
        if st.button("🤖 AI Assistant", use_container_width=True):
            st.session_state.current_page = 'teacher_ai'
            st.rerun()

# Student Profiles (Teacher View)
def student_profiles_page():
    st.markdown("<h2 class='header-text'>👥 Student Profiles</h2>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.current_page = 'teacher_dashboard'
        st.rerun()
    
    teacher = TEACHERS[st.session_state.username]
    subject = teacher['subject']
    
    # Filter students who have this subject
    relevant_students = {k: v for k, v in STUDENTS.items() if subject in v.get('subjects', [])}
    
    if not relevant_students:
        st.warning("No students enrolled in your subject yet.")
        return
    
    student_names = {k: v['name'] for k, v in relevant_students.items()}
    selected_student_key = st.selectbox("Select Student", list(student_names.keys()), 
                                        format_func=lambda x: student_names[x])
    
    student = relevant_students[selected_student_key]
    
    st.markdown(f"### 📊 Performance Analysis: {student['name']}")
    
    # Chapter test performance (Bar Graph)
    st.markdown("#### Chapter Test Performance")
    if subject in student['marks']:
        chapter_scores = student['marks'][subject]['chapter_tests']
        chapters = [f"Ch {i+1}" for i in range(len(chapter_scores))]
        
        fig_bar = go.Figure(data=[
            go.Bar(x=chapters, y=chapter_scores, marker_color='#1f77b4')
        ])
        fig_bar.update_layout(
            title="Chapter-wise Test Scores (out of 10)",
            xaxis_title="Chapters",
            yaxis_title="Marks",
            plot_bgcolor='#1a1d24',
            paper_bgcolor='#1a1d24',
            font=dict(color='white')
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Marks distribution (Pie Chart)
        st.markdown("#### Marks Distribution")
        categories = ['Chapter Tests', 'Subject Assessment']
        values = [sum(chapter_scores), student['marks'][subject]['subject_assessment']]
        
        fig_pie = go.Figure(data=[go.Pie(labels=categories, values=values)])
        fig_pie.update_layout(
            plot_bgcolor='#1a1d24',
            paper_bgcolor='#1a1d24',
            font=dict(color='white')
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Multi-subject radar chart
    st.markdown("#### Overall Performance Across Subjects")
    
    subjects_list = student['subjects'][:5]  # Get up to 5 subjects
    subject_scores = [student['marks'][subj]['overall'] for subj in subjects_list if subj in student['marks']]
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=subject_scores,
        theta=subjects_list,
        fill='toself',
        name=student['name']
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        plot_bgcolor='#1a1d24',
        paper_bgcolor='#1a1d24',
        font=dict(color='white')
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # Weak concepts
    st.markdown("#### 🔍 Weak Concepts Identified")
    weak_concepts = [
        f"Chapter {i+1}: {SYLLABUS[subject]['chapters'][i]}" 
        for i, score in enumerate(chapter_scores) if score < 7
    ]
    
    if weak_concepts:
        for concept in weak_concepts:
            st.warning(f"⚠️ {concept}")
    else:
        st.success("✅ No significant weaknesses identified!")

# Teacher Feedback View
def teacher_feedback_page():
    st.markdown("<h2 class='header-text'>💬 Student Feedback</h2>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.current_page = 'teacher_dashboard'
        st.rerun()
    
    teacher = TEACHERS[st.session_state.username]
    
    # Net feedback score
    st.markdown(f"### Overall Feedback Score: {teacher['feedback_score']}/5.0")
    
    # Progress bar
    st.progress(teacher['feedback_score'] / 5.0)
    
    st.markdown("---")
    st.markdown("### 📉 Areas for Improvement (Negative Feedback)")
    
    negative_feedback = [f for f in teacher['feedback_comments'] if f['type'] == 'negative']
    
    for i, feedback in enumerate(negative_feedback):
        with st.expander(f"❌ {feedback['comment']}"):
            st.markdown("**AI-Generated Suggestion:**")
            suggestions = {
                "Needs to explain concepts more clearly": "Consider using more visual aids and real-world examples. Break down complex topics into smaller, digestible parts. Encourage student questions during lectures.",
                "Too fast in teaching": "Implement periodic pauses for student comprehension checks. Use the 'chunking' method - teach in smaller segments with review periods. Record lectures for students to review at their own pace.",
                "Should provide more examples": "Develop a repository of practical examples for each topic. Include industry case studies. Create problem-solving sessions with step-by-step walkthroughs.",
            }
            st.info(suggestions.get(feedback['comment'], "Seek student feedback regularly and adapt teaching methods accordingly. Consider peer observation and professional development workshops."))

# Teacher AI Assistant
def teacher_ai_page():
    st.markdown("<h2 class='header-text'>🤖 AI Teaching Assistant</h2>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.current_page = 'teacher_dashboard'
        st.rerun()
    
    tab1, tab2, tab3 = st.tabs(["📚 Content Generator", "❓ Question Bank", "📊 Analytics"])
    
    with tab1:
        st.markdown("### Lecture Content Generator")
        teacher = TEACHERS[st.session_state.username]
        
        chapter = st.selectbox("Select Chapter", SYLLABUS[teacher['subject']]['chapters'])
        content_type = st.selectbox("Content Type", ["Lecture Notes", "Presentation Slides", "Assignment Questions"])
        
        if st.button("Generate Content"):
            with st.spinner("AI is generating content..."):
                time.sleep(2)
                st.success("✅ Content generated successfully!")
                st.markdown(f"""
                    <div class='info-box'>
                    <h4>📝 Generated {content_type} for: {chapter}</h4>
                    <p>This is a simulated AI-generated content. In a real implementation, 
                    this would use advanced AI models to create comprehensive educational 
                    materials tailored to the selected chapter.</p>
                    <ul>
                        <li>Introduction to key concepts</li>
                        <li>Detailed explanations with diagrams</li>
                        <li>Practical examples and applications</li>
                        <li>Summary and review questions</li>
                    </ul>
                    </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Intelligent Question Bank")
        difficulty = st.select_slider("Question Difficulty", ["Easy", "Medium", "Hard"])
        num_questions = st.slider("Number of Questions", 5, 20, 10)
        
        if st.button("Generate Questions"):
            with st.spinner("Generating questions..."):
                time.sleep(2)
                st.success(f"✅ Generated {num_questions} {difficulty} questions!")
    
    with tab3:
        st.markdown("### Class Performance Analytics")
        st.info("📊 Simulated analytics showing class average, topic-wise performance, and improvement trends.")

# Main App Logic
def main():
    render_sidebar()
    
    if not st.session_state.logged_in:
        login_page()
    else:
        # Student Flow
        if st.session_state.user_type == "student":
            if st.session_state.current_page == 'subject_selection':
                subject_selection_page()
            elif st.session_state.current_page == 'student_dashboard':
                student_dashboard()
            elif st.session_state.current_page == 'assessment':
                assessment_page()
            elif st.session_state.current_page == 'quiz':
                quiz_page()
            elif st.session_state.current_page == 'feedback_form':
                feedback_form_page()
            elif st.session_state.current_page == 'ai_assistant':
                ai_assistant_page()
        
        # Teacher Flow
        elif st.session_state.user_type == "teacher":
            if st.session_state.current_page == 'teacher_dashboard':
                teacher_dashboard()
            elif st.session_state.current_page == 'student_profiles':
                student_profiles_page()
            elif st.session_state.current_page == 'teacher_feedback':
                teacher_feedback_page()
            elif st.session_state.current_page == 'teacher_ai':
                teacher_ai_page()

if __name__ == "__main__":
    main()