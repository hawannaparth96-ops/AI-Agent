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
    body = (
        f"Hi,\n\n"
        f"Your resume review is completed.\n\n"
        f"ATS Score: {score}/100\n\n"
        f"Comments:\n- " + "\n- ".join(comments) +
        "\n\nThank you for using AI Resume Reviewer!\n\nBest Regards,\nATS Resume Validator"
    )

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False


# ========== 🎨 Streamlit Frontend ==========

st.set_page_config(page_title="ATS Resume Reviewer", layout="centered")

st.markdown("""
    <style>
    .main {background-color: #f8f9fa; padding: 20px;}
    h1 {text-align: center; color: #2E86C1;}
    .stButton>button {
        background-color: #2E86C1;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💼 ATS Resume Reviewer")
st.markdown("#### Validate your resume for ATS compatibility and get instant feedback!")

email = st.text_input("📧 Enter Email ID *", placeholder="you@example.com")
uploaded_file = st.file_uploader("📄 Upload Resume *", type=["pdf", "docx"])
job_keywords_input = st.text_input("🧠 Enter Job Role Keywords (comma-separated)", "python, automation, testing, api, selenium")

if st.button("🚀 Validate Resume"):
    if not email or not uploaded_file:
        st.error("❌ Both Email ID and Resume are mandatory!")
    else:
        st.info("⏳ Analyzing your resume... please wait.")
        try:
            if uploaded_file.name.endswith(".pdf"):
                text = extract_text_from_pdf(uploaded_file)
            else:
                text = extract_text_from_docx(uploaded_file)

            job_keywords = [k.strip() for k in job_keywords_input.split(",")]
            ats_score, structure_score, keyword_score, comments, grammar_issues, found_keywords = analyze_resume(text, job_keywords)

            st.success("✅ Resume Analyzed Successfully!")
            st.metric("ATS Score", f"{ats_score}/100")

            st.write("---")
            st.subheader("📊 Detailed Breakdown:")
            st.write(f"**Structure Completeness:** {structure_score}/100")
            st.write(f"**Keyword Match (ATS Relevance):** {keyword_score}/100 → Found: {', '.join(found_keywords) if found_keywords else 'None'}")

            st.write("---")
            st.subheader("💬 Review Comments:")
            for c in comments:
                st.write(f"- {c}")

            st.write("---")
            st.subheader("🔍 Grammar Suggestions (Top 10):")
            if grammar_issues:
                for g in grammar_issues[:10]:
                    st.markdown(f"**Original:** {g['original']}  \n**Suggestion:** {g['suggestion']}")
            else:
                st.write("✅ No major grammar issues found.")

            if send_email(email, ats_score, comments):
                st.success(f"📩 A detailed report has been sent to {email}")
            else:
                st.info("⚠️ Email sending skipped or not configured (check secrets).")

        except Exception as e:
            st.error(f"Error: {e}")
