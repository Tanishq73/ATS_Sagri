import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
from PIL import Image

load_dotenv()  # Load all environment variables

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
You are an advanced Application Tracking System (ATS) with deep expertise in evaluating resumes for tech-related positions such as software engineering, data science, data analysis, and big data engineering. Your goal is to assess the provided resume against the job description (JD) in a highly competitive job market.

Here are the key requirements for your task:
1. **JD Match Percentage:** Calculate how well the resume aligns with the job description. Provide the match percentage as an integer (0 to 100).
2. **Missing Keywords:** Identify important technical and domain-specific keywords that are missing from the resume but are present in the job description. Provide a list of these missing keywords.
3. **Profile Summary:** Create a concise profile summary based on the resume content. The summary should highlight the candidate's strengths and key areas of expertise in relation to the job description.

Your core personality should be being EXTREMELY CRITICAL and giving high weightage on work experience. 
resume: {text}
description: {jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords:[]","Profile Summary":""}}
"""

# Load default JDs from individual .txt files
def load_default_jds():
    jds = {}
    jd_directory = "jds"  # Directory containing JD files
    try:
        for filename in os.listdir(jd_directory):
            if filename.endswith(".txt"):
                filepath = os.path.join(jd_directory, filename)
                with open(filepath, 'r') as file:
                    title = os.path.splitext(filename)[0]  # Use filename (without extension) as title
                    description = file.read().strip()
                    jds[title] = description
    except FileNotFoundError:
        print(f"Warning: Directory '{jd_directory}' not found. Using empty dictionary.")
    return jds

default_jds = load_default_jds()

# Streamlit app
st.title("Resume Evaluation for Sagri")
# Load logo
st.sidebar.image("sagri_logo2.png",caption="Sagri Co., Ltd")



# Job Description Selection
if default_jds:
    selected_jd = st.selectbox("Select Job Description", list(default_jds.keys()))
    jd = default_jds[selected_jd]
else:
    st.error("No job descriptions available.")
    jd = None

uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the pdf")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None and jd is not None:
        text = input_pdf_text(uploaded_file)
        response = get_gemini_response(input_prompt.format(text=text, jd=jd))

        # Parse JSON response
        try:
            response_json = json.loads(response)
            jd_match = response_json.get("JD Match", "N/A")
            missing_keywords = response_json.get("MissingKeywords", [])
            profile_summary = response_json.get("Profile Summary", "")

            # Display output
            st.subheader("Resume Evaluation")
            st.write(f"**JD Match:** {jd_match} %")
            st.write("**Missing Keywords:")
            for keyword in missing_keywords:
                st.write(f"- {keyword}")
            st.write("**Profile Summary:**")
            st.write(profile_summary)

        except json.JSONDecodeError:
            st.error("Error parsing response from Gemini.")
