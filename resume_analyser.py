import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
from io import BytesIO

try:
    from PyPDF2 import PdfReader
except ImportError:
    st.error("Please install PyPDF2: pip install PyPDF2")
    st.stop() 
try:
    from docx import Document
except ImportError:
    st.error("Please install python-docx: pip install python-docx")
    st.stop() 
---
load_dotenv()
API_KEY = os.getenv('GOOGLE_API_KEY')


if not API_KEY:
    st.error("Error: GOOGLE_API_KEY environment variable not set.")
    st.info("Please set it in your .env file in the project root (e.g., GOOGLE_API_KEY='your_api_key').")
    st.stop()
genai.configure(api_key=API_KEY)

MODEL_NAME = 'gemini-1.5-flash'  

def read_pdf(file):
    """Extracts text from PDF files"""
    pdf = PdfReader(BytesIO(file.read()))
    text = ""
    for page in pdf.pages:
        text += page.extract_text() or ""  
    return text

def read_docx(file):
    doc = Document(BytesIO(file.read()))
    return "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text])

def read_txt(file):
    return file.read().decode("utf-8")

def get_resume_analysis(job_description: str, resume_text: str):
    analysis_prompt = f"""
    You are an expert resume analysis AI. Analyze this resume against the job description and provide:

    1. Match Score (1-100%)
    2. Key Strengths (3-5 bullet points)
    3. Missing Keywords/Skills (3-5 bullet points)
    4. Areas for Improvement (2-3 actionable suggestions)
    5. Professional Summary
    6. Selection Chance Assessment (Low/Moderate/High/Very High)

    Job Description:
    {job_description}

    Resume:
    {resume_text}

    Be concise, professional, and brutally honest.
    """

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(analysis_prompt)
    return response.text, response.prompt_feedback, response.candidates
    
st.set_page_config(
    page_title="Resume Analyzer Pro",
    layout="wide",
    page_icon="📄"
)

if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

theme = st.session_state.theme
primary_bg = "#FFFFFF" if theme == 'light' else "#1E1E1E"
secondary_bg = "#E0E2E6" if theme == 'light' else "#2D2D2D" # Slightly darker for better contrast in light mode
text_color = "#000000" if theme == 'light' else "#F0F2F6"
button_bg_color = "#000000" if theme == 'light' else "#1E88E5" # Green for light, Blue for dark

st.markdown(f"""
    <style>
    /* General app background and text color */
    .stApp {{
        background-color: {primary_bg};
        color: {text_color};
    }}

    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {text_color};
    }}
    /* More specific selectors for Streamlit text elements */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown ul, .stMarkdown ol {{
        color: {text_color};
    }}

    /* Input Fields: Text Areas and Text Inputs */
    .stTextArea textarea, .stTextInput input {{
        background-color: {secondary_bg};
        color: {text_color};
        border: 1px solid #555555;
    }}
    /* Placeholder text color for text areas and text inputs */
    .stTextArea textarea::placeholder, .stTextInput input::placeholder {{
        color: {'#999999' if theme == 'light' else '#BBBBBB'}; /* Darker gray for light, lighter for dark */
        opacity: 1; /* Ensure placeholder is not transparent */
    }}

    /* Buttons */
    .stButton > button {{
        background-color: {button_bg_color} !important;
        color: white !important;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
    }}
    .stButton > button:hover {{
        opacity: 0.9;
    }}

    /* Radio buttons and their labels */
    .stRadio > label {{
        color: {text_color};
    }}
    .stRadio .st-dk {{ /* Target the actual radio button circles/text */
        color: {text_color};
    }}

    /* File uploader label */
    .stFileUploader label span {{
        color: {text_color};
    }}
    /* File uploader box */
    .stFileUploader > div > div {{
        background-color: {secondary_bg};
        border: 1px solid #555555;
    }}


    /* Expander text */
    .streamlit-expanderHeader {{
        color: {text_color};
    }}
    .streamlit-expanderContent {{
        color: {text_color};
    }}

    /* General labels (if not covered by other selectors) */
    .st-d{{
        color: {text_color};
    }}
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.title("📄 AI Resume Analyzer")
    st.caption("Optimize your resume for any job using AI")
with col2:
    btn_label = "🌙" if theme == 'light' else "💡"
    st.button(btn_label, on_click=toggle_theme, help="Toggle Dark/Light Mode")

st.divider()

st.header("1. Job Description Input 🎯")

job_description = st.text_area(
    "Paste the job description here:",
    height=200,
    placeholder="Senior Software Engineer requirements...",
    key="jd"
)

st.header("2. Resume Input 📝")
resume_text = ""

upload_option = st.radio(
    "Choose input method:",
    ["Upload File", "Paste Text"],
    horizontal=True,
    label_visibility="visible"
)

if upload_option == "Upload File":
    uploaded_file = st.file_uploader(
        "Upload resume (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        label_visibility="visible" 
    )

    if uploaded_file:
        try:
            if uploaded_file.type == "application/pdf":
                resume_text = read_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = read_docx(uploaded_file)
            elif uploaded_file.type == "text/plain":
                resume_text = read_txt(uploaded_file)

            with st.expander("Preview Resume Content (First 2000 characters)"):
                st.text(resume_text[:2000] + ("..." if len(resume_text) > 2000 else ""))

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
else: 
    resume_text = st.text_area(
        "Paste your resume text here:",
        height=300,
        placeholder="John Doe\nSenior Software Engineer...",
        label_visibility="visible"
    )

st.divider()
if st.button("🚀 Analyze Resume", type="primary"):
    if not job_description.strip():
        st.warning("Please provide a job description")
    elif not resume_text.strip():
        st.warning("Please provide your resume")
    else:
        with st.spinner("Analyzing..."):
            try:
                analysis, feedback, candidates = get_resume_analysis(job_description, resume_text)

                st.success("Analysis Complete!")
                st.subheader("📊 Analysis Results")
                st.markdown(analysis)

            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                st.info("Common fixes: Check API key, internet connection, or try shorter text")

st.header("Got Feedback? We'd Love to Hear From You! 💬")
st.markdown("""
Your insights help us improve this AI Resume Analyzer.
Please share your comments, suggestions, or any issues you encountered.
""")

if st.button("Give Feedback"):
    st.markdown(f'<a href="https://docs.google.com/forms/d/e/1FAIpQLScpyQNtZyJlQTeMtRxtNbmnETo8jmDWgKxwcauBbgJ--GwJpw/viewform?usp=sharing&ouid=104160088181469050251" target="_blank" rel="noopener noreferrer">Click here to open the feedback form!</a>', unsafe_allow_html=True)

st.divider()
st.markdown("""
    *Built with ❤️ *
    *Note: AI analysis should be used as guidance only. Always verify with human experts.*
""")
