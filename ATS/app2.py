import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
from PIL import Image
import yaml

load_dotenv()  # load all our environment variables

genai.configure(api_key=os.getenv("API_KEY"))

# Disable XsrfProtection by default
enableXsrfProtection = False

def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Prompt Template
input_prompt = """
Hey Act Like a skilled or very experience ATS(Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving thr resumes. Assign the percentage Matching based 
on Jd and
the missing keywords with high accuracy
resume:{text}
description:{jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords:[]","Profile Summary":""}}
"""

# Load default JDs from a YAML file
def load_default_jds():
    try:
        with open('default_jds.yaml', 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print("Warning: 'default_jds.yaml' not found. Using empty dictionary.")
        return {}

default_jds = load_default_jds()

# Streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume ATS")

# Load logo
logo_image = Image.open("path/to/your/logo.png")  # Replace with the actual path
st.image(logo_image, width=100)  # Adjust width as needed

# Job Description Selection
selected_jd = st.selectbox("Select Job Description", list(default_jds.keys()))
jd = default_jds[selected_jd]

uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the pdf")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        response = get_gemini_response(input_prompt.format(text=text, jd=jd))

        # Parse JSON response
        try:
            response_json = json.loads(response)
            jd_match = response_json.get("JD Match", "N/A")
            missing_keywords = response_json.get("MissingKeywords", [])
            profile_summary = response_json.get("Profile Summary", "")

            # Display output in a user-friendly manner
            st.subheader("Resume Evaluation")
            st.write(f"**JD Match:** {jd_match}%")
            st.write("**Missing Keywords:**")
            for keyword in missing_keywords:
                st.write(f"- {keyword}")
            st.write("**Profile Summary:**")
            st.write(profile_summary)

        except json.JSONDecodeError:
            st.error("Error parsing response from Gemini.")