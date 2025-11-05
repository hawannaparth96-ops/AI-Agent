import streamlit as st
import PyPDF2
import docx
from textblob import TextBlob
import nltk

# --- Auto-download NLTK/TextBlob data (fixes corpus errors) ---
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
            "Your resume contains several grammatical issues that may impact readability. "
            "Consider proofreading or using grammar-checking tools like Grammarly or LanguageTool "
            "to ensure correct tense usage, punctuation, and consistency."
        )
    elif grammar_count > 3:
        comments.append(
            "A few grammar issues were detected. Review sentence structure and ensure consistency in "
            "verb tense and clarity across bullet points and summary sections."
        )
    else:
        comments.append(
            "Your resume demonstrates strong grammar and writing clarity with minimal to no detectable issues."
        )

    # Structure feedback
    if structure_score < 80:
        comments.append(
            "It appears that some important sections are missing. Ensure that your resume includes: "
            "Education, Experience, Skills, Projects, and a short Professional Summary. "
            "Proper headings improve readability and help recruiters quickly locate key information."
        )
    else:
        comments.append(
            "Your resume includes all the essential sections, providing a well-rounded professional overview. "
            "You may further enhance it by maintaining consistent formatting, margins, and font styles."
        )

    # Keyword / ATS feedback
    if keyword_score < 70:
        comments.append(
            "Your resume could be more optimized for ATS (Applicant Tracking Systems). "
            "Include more role-specific keywords — such as tools, frameworks, and certifications relevant "
            "to your desired job — to increase compatibility with automated resume screening."
        )
    else:
        comments.append(
            "Your resume includes a good amount of job-relevant keywords, improving your visibility in ATS scans. "
            "Continue updating these keywords to match each job description you apply for."
        )

    # Overall presentation feedback
    if ats_score < 60:
        comments.append(
            "Overall, your resume needs improvement. Focus on layout clarity, consistency, and quantifying "
            "achievements with measurable outcomes (e.g., improved efficiency by 30%, managed 5-member team, etc.)."
        )
    elif ats_score < 80:
        comments.append(
            "Your resume is fairly strong but can be refined further. Review section alignment, ensure consistent bullet formatting, "
            "and highlight measurable results to strengthen impact."
        )
    else:
        comments.append(
            "Your resume is well-structured, grammatically sound, and ATS-friendly. A few stylistic enhancements "
            "such as better spacing, font consistency, and concise bullet points will make it even more professional."
        )

    return ats_score, structure_score, keyword_score, comments


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
st.write("### Upload your resume below to get a detailed ATS and quality review:")

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
            st.write(f"- {c}")

        st.markdown("<h4 style='text-align:center; color:#1f77b4;'>Thank You! for visiting this Site</h4>", unsafe_allow_html=True)
