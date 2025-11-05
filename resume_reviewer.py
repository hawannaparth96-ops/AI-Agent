import streamlit as st
import PyPDF2
import docx
from textblob import TextBlob
import nltk

# --- Auto-download NLTK/TextBlob data ---
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
nltk.download('brown', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# ========== Helper Functions ==========

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

    # Grammar detection
    grammar_issues = []
    for sentence in blob.sentences:
        corrected = sentence.correct()
        if corrected != sentence:
            grammar_issues.append((str(sentence), str(corrected)))
    grammar_count = len(grammar_issues)

    # Section check
    required_sections = ['education', 'experience', 'skills', 'projects', 'summary']
    found_sections = [s for s in required_sections if s in text.lower()]
    structure_score = round(len(found_sections) / len(required_sections) * 100, 2)

    # Keyword check
    keywords = ['python', 'data', 'project', 'api', 'automation', 'testing', 'machine learning']
    found_keywords = [k for k in keywords if k.lower() in text.lower()]
    keyword_score = round(len(found_keywords) / len(keywords) * 100, 2)

    # Overall ATS score
    ats_score = round((structure_score * 0.4) + (keyword_score * 0.4) + ((100 - grammar_count * 2) * 0.2), 2)
    ats_score = max(0, min(100, ats_score))

    # Detailed actionable comments
    comments = []

    # 1️⃣ Grammar
    if grammar_count > 10:
        comments.append(
            "✏️ *Grammar Issues Detected:* Your resume contains several grammatical or spelling mistakes. "
            "Focus on your **Summary** and **Experience** sections — ensure verbs are in past tense (e.g., “Developed”, “Led”) "
            "and avoid run-on sentences. Example:\n\n❌ 'I am responsible for testing and creating test cases'\n"
            "✅ 'Created and executed automated test cases improving efficiency by 20%'."
        )
    elif grammar_count > 3:
        comments.append(
            "📝 *Minor Grammar Issues:* A few inconsistencies were found. Review the **Skills** and **Projects** sections for clarity "
            "and uniform tense. Keep sentences short and impactful."
        )
    else:
        comments.append(
            "✅ *Excellent Grammar:* Your resume writing is clear, professional, and grammatically correct."
        )

    # 2️⃣ Structure
    missing_sections = [s.title() for s in required_sections if s not in found_sections]
    if missing_sections:
        comments.append(
            f"📂 *Missing Sections:* {', '.join(missing_sections)} section(s) seem to be missing. "
            "Add these with clear headings and bullet points for better readability."
        )
    else:
        comments.append(
            "📘 *Strong Structure:* All key sections are present and logically organized. Maintain uniform header formatting."
        )

    # 3️⃣ Keyword Optimization (ATS)
    missing_keywords = [k for k in keywords if k.lower() not in text.lower()]
    if keyword_score < 70:
        comments.append(
            f"⚙️ *ATS Optimization:* Add missing job-relevant keywords like {', '.join(missing_keywords[:5])}. "
            "Example: If applying for data-related roles, mention tools like Pandas, SQL, or Selenium. "
            "This boosts ATS compatibility."
        )
    else:
        comments.append(
            "🔍 *ATS Ready:* Your resume includes strong role-relevant keywords. Continue tailoring them for each job description."
        )

    # 4️⃣ Layout / Presentation
    if ats_score < 60:
        comments.append(
            "🧾 *Presentation Tip:* Improve alignment and spacing. Ensure bullet points are consistent, and avoid dense text blocks. "
            "Use simple fonts (Calibri, Arial) and keep resume length to one page if under 5 years of experience."
        )
    elif ats_score < 80:
        comments.append(
            "📄 *Formatting Suggestion:* You have a good base. Refine visual consistency — use equal spacing, proper margins, "
            "and align bullets neatly for a polished look."
        )
    else:
        comments.append(
            "🌟 *Excellent Presentation:* Your resume layout looks clean and recruiter-friendly. Keep it updated with recent achievements."
        )

    return ats_score, structure_score, keyword_score, comments


# ========== Streamlit Frontend ==========

st.set_page_config(page_title="Quicky Resume Reviewer and Validator through ATS", layout="centered")

st.markdown("""
    <style>
    .main {background-color: #f9fafb; padding: 20px;}
    h1 {
        text-align: center;
        color: #1f77b4;
        font-size: 42px;
        white-space: nowrap;
        width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 10px;
    }
    .footer {
        text-align: right;
        font-size: 13px;
        color: gray;
        margin-top: 50px;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Header (Single Line, Full Width)
st.markdown("""
    <h1>Quicky Resume Reviewer and Validator through ATS</h1>
""", unsafe_allow_html=True)

st.write("### Upload your resume to receive a detailed ATS-based and section-wise review:")

uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])

if st.button("Validate Resume"):
    if not uploaded_file:
        st.error("Please upload your resume before proceeding.")
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
            st.markdown(f"<p style='margin-bottom:10px;'>{c}</p>", unsafe_allow_html=True)

        st.markdown("<h4 style='text-align:center; color:#1f77b4;'>Thank You! for visiting this Site</h4>", unsafe_allow_html=True)
        st.markdown("<p class='footer'>Done by - its.parthav</p>", unsafe_allow_html=True)
