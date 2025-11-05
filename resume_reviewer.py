import streamlit as st
import PyPDF2
import docx
from textblob import TextBlob
import nltk
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os

# --- Auto-download NLTK/TextBlob data ---
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
nltk.download('brown', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# ========== 📄 Helper Functions ==========

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def analyze_resume(text):
    blob = TextBlob(text)

    # Grammar correction detection
    grammar_issues = []
    for sentence in blob.sentences:
        corrected = sentence.correct()
        if corrected != sentence:
            grammar_issues.append((str(sentence), str(corrected)))

    grammar_count = len(grammar_issues)

    # Section presence
    required_sections = ['education', 'experience', 'skills', 'projects', 'summary']
    found_sections = [s for s in required_sections if s in text.lower()]
    structure_score = round(len(found_sections) / len(required_sections) * 100, 2)

    # Keyword check (basic ATS simulation)
    keywords = ['python', 'data', 'project', 'api', 'automation', 'testing', 'machine learning']
    found_keywords = [k for k in keywords if k.lower() in text.lower()]
    keyword_score = round(len(found_keywords) / len(keywords) * 100, 2)

    # Overall ATS score
    ats_score = round((structure_score * 0.4) + (keyword_score * 0.4) + ((100 - grammar_count * 2) * 0.2), 2)
    ats_score = max(0, min(100, ats_score))

    # Detailed Review Comments
    comments = []

    # Grammar feedback
    if grammar_count > 10:
        comments.append(
            "Your resume contains multiple grammatical issues that may affect readability. "
            "Consider using professional proofreading tools like Grammarly or LanguageTool to ensure correct tense usage, punctuation, and sentence flow."
        )
    elif grammar_count > 3:
        comments.append(
            "A few minor grammar issues were found. Review your sentences for clarity, avoid long phrases, and maintain consistent verb tenses throughout the document."
        )
    else:
        comments.append(
            "Excellent grammar usage. Sentences are clear and concise with proper structure and punctuation."
        )

    # Structure feedback
    if structure_score < 80:
        comments.append(
            "Your resume seems to be missing one or more key sections. "
            "Ensure your resume includes: Education, Experience, Skills, Projects, and a Career Summary section. "
            "This improves ATS readability and gives recruiters a complete picture of your qualifications."
        )
    else:
        comments.append(
            "Your resume is well structured, covering all major sections required for a professional profile. "
            "Consider keeping consistent formatting (font size, alignment, and bullet points) for better presentation."
        )

    # Keyword / ATS feedback
    if keyword_score < 70:
        comments.append(
            "The resume could include more job-specific keywords. Add role-relevant technologies, tools, or domain-specific terms "
            "(e.g., frameworks, programming languages, or certifications) to increase visibility in Applicant Tracking Systems (ATS)."
        )
    else:
        comments.append(
            "Your resume has a good amount of role-relevant keywords. Ensure these are evenly distributed in Experience and Skills sections for maximum ATS optimization."
        )

    # Overall presentation feedback
    if ats_score < 60:
        comments.append(
            "Overall, your resume needs improvement. Focus on layout, clear section headings, quantifying achievements, and aligning content with job descriptions."
        )
    elif ats_score < 80:
        comments.append(
            "Your resume is fairly strong but can be improved. Fine-tune section alignment, make bullet points more action-oriented, and verify consistency in date formatting."
        )
    else:
        comments.append(
            "Your resume is well-written, structured, and ATS-friendly. A few refinements in design and measurable results will make it stand out."
        )

    return ats_score, structure_score, keyword_score, comments


def send_email(recipient_email, score, comments):
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        return False

    subject = "Your Resume Review & ATS Report"
    body = (
        f"Hello,\n\n"
        f"Your resume review is completed.\n\n"
        f"ATS Score: {score}/100\n\n"
        f"Comments:\n- " + "\n- ".join(comments) +
        "\n\nThank you for using Quicky Resume Reviewer and Validator!"
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

st.set_page_config(page_title="Quicky Resume Reviewer and Validator", layout="centered")

st.markdown("""
    <style>
    .main {background-color: #f9fafb; padding: 20px;}
    h1 {text-align: center; color: #1f77b4;}
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Quicky Resume Reviewer and Validator")
st.write("### Please enter your details below to review your resume:")

email = st.text_input("Email ID")
uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])

if st.button("Validate Resume"):
    if not email or not uploaded_file:
        st.error("Both Email ID and Resume file are required.")
    else:
        with st.spinner("Analyzing your resume..."):
            if uploaded_file.name.endswith(".pdf"):
                text = extract_text_from_pdf(uploaded_file)
            else:
                text = extract_text_from_docx(uploaded_file)

            ats_score, structure_score, keyword_score, comments = analyze_resume(text)

        st.success("Resume analysis completed successfully!")

        st.subheader("ATS Score Summary")
        st.progress(int(ats_score))
        st.write(f"**ATS Score:** {ats_score}/100")
        st.write(f"**Structure Score:** {structure_score}/100")
        st.write(f"**Keyword Match:** {keyword_score}/100")

        st.subheader("Detailed Review Comments")
        for c in comments:
            st.write(f"- {c}")

        # Thank You Message
        st.markdown("<h4 style='text-align:center; color:#1f77b4;'>Thank You! for visiting this Site</h4>", unsafe_allow_html=True)

        success = send_email(email, ats_score, comments)
        if success:
            st.info(f"A detailed review report has been sent to {email}")
        else:
            st.warning("Could not send email. Please check SMTP configuration.")
