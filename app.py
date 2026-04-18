import streamlit as st
from google import genai
from google.genai import errors
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import requests
from bs4 import BeautifulSoup
import base64
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Gemini AI ATS",
    page_icon="👨‍💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR AESTHETICS ---
st.markdown("""
    <style>
    /* Sharp corners for the results box */
    .results-box {
        background-color: #f8f9fa;
        border: 2px solid #e9ecef;
        padding: 25px;
        border-radius: 0px !important; /* Sharp corners applied */
        color: #212529;
        box-shadow: 4px 4px 0px 0px rgba(0,0,0,0.1); /* Subtle retro shadow */
        margin-top: 30px;
        margin-bottom: 80px; /* Room for footer */
    }

    /* Dark mode compatibility for results box */
    @media (prefers-color-scheme: dark) {
        .results-box {
            background-color: #1e1e1e;
            border: 2px solid #333;
            color: #e0e0e0;
            box-shadow: 4px 4px 0px 0px rgba(255,255,255,0.05);
        }
    }

    /* Fixed Footer Banner */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0e1117;
        color: #fafafa;
        text-align: center;
        padding: 12px 0;
        font-size: 14px;
        font-weight: 500;
        border-top: 1px solid #333;
        z-index: 999;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONFIGURATION ---
st.sidebar.title("⚙️ Gemini AI ATS Settings")

# Model Selection Dropdown
st.sidebar.subheader("🤖 AI Model")
selected_model = st.sidebar.selectbox(
    "Choose the Gemini Model",
    options=["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"],
    index=0,
    help="2.5-flash is the standard. Use lite if you are hitting rate limits frequently."
)
st.sidebar.markdown("---")

# API Key Configuration
st.sidebar.subheader("🔑 Authentication")
with st.sidebar.form(key='api_form'):
    api_key_input = st.text_input("Enter your Google API Key", type="password")
    submit_key = st.form_submit_button("Enter / Save Key")

if submit_key:
    st.session_state['api_key'] = api_key_input

API_KEY = st.session_state.get('api_key', '')
# print(API_KEY)

st.sidebar.markdown("Don't have a Google API Key? [Get one here](https://aistudio.google.com/app/apikey).")

if not API_KEY:
    st.warning("👈 Please enter your Google API Key in the sidebar to proceed.")
    st.stop()

# Initialize GenAI Client
client = genai.Client(api_key=API_KEY)

# --- HELPER FUNCTIONS ---
def get_gemini_response(prompt_text, model_name):
    response = client.models.generate_content(
        model=model_name,
        contents=prompt_text,
    )
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

def extract_jd_from_url(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        st.error(f"Error fetching URL: {e}")
        return ""

def display_pdf(uploaded_file):
    base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="650" type="application/pdf" style="border: 1px solid #ccc; border-radius: 0px;"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- PROMPT TEMPLATE ---
input_prompt = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of the tech field, software engineering, data science, data analyst
and big data engineering. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide the 
best assistance for improving the resumes. Assign the percentage Matching based 
on JD and the missing keywords with high accuracy. 
Finally, provide actionable pointers on how the candidate can improve their resume for this specific role.

resume:{text}
description:{jd}

I want the response in one single string having the structure:
{{"JD Match":"%", "MissingKeywords":[], "Profile Summary":"", "Improvement Pointers":[]}}
"""

# --- MAIN APP UI ---
st.title("🎯 Resume Matcher ATS")
st.markdown("Optimize your resume against job descriptions using Google Gemini AI.")
st.markdown("<br>", unsafe_allow_html=True)

# Use columns with specific ratios for better spacing
col1, col2 = st.columns([1.1, 0.9], gap="large")

with col1:
    st.subheader("📝 1. Job Description")

    # URL Extraction Feature
    jd_url = st.text_input("Auto-extract from Link (Optional)", placeholder="Paste a Job Link here...")
    if st.button("Extract JD from Link"):
        if jd_url:
            extracted_text = extract_jd_from_url(jd_url)
            if extracted_text:
                st.session_state['jd_text'] = extracted_text
                st.success("Extracted successfully! Please review below.")
        else:
            st.error("Please enter a valid URL.")

    # JD Text Area
    current_jd = st.session_state.get('jd_text', '')
    jd = st.text_area("Job Description Text", value=current_jd, height=200, placeholder="Paste or confirm the job description here...")

    st.subheader("📄 2. Resume")
    uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the PDF")

    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.button("🚀 Evaluate Resume", type="primary", use_container_width=True)

with col2:
    st.subheader("👁️ Resume Preview")
    if uploaded_file is not None:
        display_pdf(uploaded_file)
    else:
        st.info("Upload a PDF to see the preview here.")

# --- EVALUATION LOGIC ---
if submit:
    if uploaded_file is not None and jd.strip() != "":
        with st.spinner(f"Analyzing your resume using {selected_model}..."):
            text = input_pdf_text(uploaded_file)
            formatted_prompt = input_prompt.format(text=text, jd=jd)

            try:
                # API Call using the model selected from the dropdown
                response = get_gemini_response(formatted_prompt, selected_model)
                # parsed_response = json.loads(response)
                # --- NEW CLEANING STEP ---
                # Strip out any markdown code formatting the AI might add
                print(response)
                clean_response = response.replace("```json", "").replace("```", "").strip()

                # Parse the cleaned string
                parsed_response = json.loads(clean_response)

                # HTML formatter for the sharp-cornered results box
                missing_keywords = ", ".join(parsed_response.get('MissingKeywords', []))
                pointers_html = "".join([f"<li>{p}</li>" for p in parsed_response.get('Improvement Pointers', [])])

                results_html = f"""
                <div class="results-box">
                    <h2 style="margin-top: 0;">📊 Analysis Results</h2>
                    <h3 style="color: #0078D7;">JD Match: {parsed_response.get('JD Match', 'N/A')}</h3>
                    <hr>
                    <h4>🔑 Missing Keywords</h4>
                    <p>{missing_keywords}</p>
                    <h4>👤 Profile Summary</h4>
                    <p>{parsed_response.get('Profile Summary', 'N/A')}</p>
                    <h4>💡 Improvement Pointers</h4>
                    <ul>{pointers_html}</ul>
                </div>
                """
                st.markdown(results_html, unsafe_allow_html=True)

            except errors.ClientError as e:
                if e.code == 429:
                    st.warning("⏳ The AI is currently busy (Rate Limit Exceeded). Please wait about 60 seconds and try again!")
                else:
                    st.error(f"Google API Error: {e.message}")
            except json.JSONDecodeError:
                st.error("The AI returned an improperly formatted response. Please try again.")
    else:
        st.error("Please provide both a Job Description and a Resume PDF.")

# --- FOOTER ---
current_year = datetime.now().year
footer_html = f"""
<div class="footer">
    Developed by 😎 Himanshu Upreti | © {current_year}
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)