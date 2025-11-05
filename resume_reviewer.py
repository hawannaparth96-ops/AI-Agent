import streamlit as st
import PyPDF2
import docx
import language_tool_python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ========== Helper Functions ==========
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def analyze_resume(text):
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    grammar_issues = len(matches)

    required_sections = ['education', 'experience', 'skills', 'projects', 'summary']
    found_sections = [s for s in required_sections if s in text.lower()]
    structure_score = round(len(found_sections) / len(required_sections) * 100, 2)

    score = max(0, 100 - grammar_issues)
    final_score = round((score * 0.6) + (structure_score * 0.4), 2)

    comments = []
    if grammar_issues > 10:
        comments.append("Too many grammatical errors found. Please proofread carefully.")
    elif grammar_issues > 3:
        comments.append("Minor grammar issues found. Can be improved.")
    else:
        comments.append("Great grammar! Very few mistakes.")

    if structure_score < 80:
        comments.append("Missing some key sections. Include Education, Experience, Skills, and Projects.")
    else:
        comments.append("Good structure — all key sections found.")

    return final_score, comments

def send_email(recipient_email, score, comments):
    # Configure your email here (you can use Gmail SMTP)
    sender_email = "your_email@gmail.com"
    sender_password = "your_app_password"  # Use App Password, not real password

    subject = "Your Resume Review Report"
    body = f"Hi,\n\nYour resume review is completed.\n\nScore: {score}/100\nComments:\n- " + "\n- ".join(comments) + "\n\nBest Regards,\nAI Resume Reviewer"

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

# ========== Streamlit Frontend ==========
st.set_page_config(page_title="AI Resume Reviewer", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .main {background-color: #f8f9fa; padding: 20px;}
    h1 {text-align: center; color: #2E86C1;}
    .stButton>button {
        background-color: #2E86C1;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- UI ----------
st.title("💼 Wel-Come to Resume Reviewer")
st.write("Please provide your email and upload your resume for analysis.")

email = st.text_input("📧 Email ID *", placeholder="Enter your email address")
uploaded_file = st.file_uploader("📄 Upload Resume *", type=["pdf", "docx"])

if st.button("Proceed 🚀"):
    if not email or not uploaded_file:
        st.error("❌ Both Email ID and Resume are mandatory!")
    else:
        st.info("⏳ Validating your resume, please wait...")
        try:
            if uploaded_file.name.endswith(".pdf"):
                text = extract_text_from_pdf(uploaded_file)
            else:
                text = extract_text_from_docx(uploaded_file)

            score, comments = analyze_resume(text)

            st.success(f"✅ Resume Reviewed Successfully!")
            st.metric("Final Resume Score", f"{score}/100")
            st.subheader("Review Comments:")
            for c in comments:
                st.write(f"- {c}")

            if send_email(email, score, comments):
                st.success(f"📩 Review sent to {email}")
            else:
                st.warning("⚠️ Could not send email. Check SMTP configuration.")
        except Exception as e:
            st.error(f"Error: {e}")
