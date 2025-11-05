import streamlit as st
import PyPDF2
import docx
from textblob import TextBlob
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# ========== 📄 Helper Functions ==========

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def analyze_resume(text, job_keywords):
    """
    Analyze grammar, structure, and keyword relevance.
    No Java required (TextBlob-based correction).
    """
    blob = TextBlob(text)

    # Grammar corrections
    grammar_issues = []
    for sentence in blob.sentences:
        corrected = sentence.correct()
        if corrected != sentence:
            grammar_issues.append({
                "original": str(sentence),
                "suggestion": str(corrected)
            })

    grammar_count = len(grammar_issues)

    # Structure & ATS section check
    required_sections = ['education', 'experience', 'skills', 'projects', 'summary']
    found_sections = [s for s in required_sections if s in text.lower()]
    structure_score = round(len(found_sections) / len(required_sections) * 100, 2)

    # Keyword match (ATS relevance)
    found_keywords = [k for k in job_keywords if k.lower() in text.lower()]
    keyword_score = round(len(found_keywords) / len(job_keywords) * 100, 2)

    # Overall ATS Score
    ats_score = round((structure_score * 0.4) + (keyword_score * 0.4) + ((100 - grammar_count * 2) * 0.2), 2)

    # Comments
    comments = []
    if grammar_count > 10:
        comments.append("Too many grammatical errors found. Please proofread carefully.")
    elif grammar_count > 3:
        comments.append("Some minor grammar issues found.")
    else:
        comments.append("Excellent grammar — very few errors!")

    if structure_score < 80:
        comments.append("Your resume is missing important sections. Include all key areas (Education, Experience, Skills, Projects, Summary).")
    else:
        comments.append("All key sections are well structured.")

    if keyword_score < 70:
        comments.append("Your resume does not include enough job-relevant keywords. Try adding more role-specific skills.")
    else:
        comments.append("Good keyword usage relevant to the job role.")

    return ats_score, structure_score, keyword_score, comments, grammar_issues, found_keywords


def send_email(recipient_email, score, comments):
    """
    Optional: Send results via email.
    Configure using Streamlit Secrets.
    """
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        return False  # skip sending if not configured

    subject = "Your Resume Review & ATS Report"
    body = f"""
Hi,

Your resume review is completed.

ATS Score: {score}/100

Comments:
- {chr(10).join(comments)}

Thank you for using AI Resume Reviewer!

Best Regards,
ATS Resume Vali
