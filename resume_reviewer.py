import streamlit as st
import PyPDF2
import docx

# ========== 📄 Helper Functions ==========

def extract_text_from_pdf(file):
    """Extracts text from a PDF file safely."""
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
        return text.strip()
    except Exception as e:
        st.error(f"⚠️ Error reading PDF file: {e}")
        return ""

def extract_text_from_docx(file):
    """Extracts text from a DOCX file safely."""
    try:
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs]).strip()
    except Exception as e:
        st.error(f"⚠️ Error reading DOCX file: {e}")
        return ""

def analyze_resume(text):
    """Analyzes resume text for structure, keywords, and readability."""
    if not text or len(text) < 100:
        return 0, 0, 0, ["🔴 Resume appears to be empty or unreadable. Please upload a proper text-based file."]

    text_lower = text.lower()

    # Section presence
    required_sections = ['education', 'experience', 'skills', 'projects', 'summary']
    found_sections = [s for s in required_sections if s in text_lower]
    structure_score = round(len(found_sections) / len(required_sections) * 100, 2)

    # Keyword match
    keywords = ['python', 'data', 'project', 'api', 'automation', 'testing', 'machine learning']
    found_keywords = [k for k in keywords if k in text_lower]
    keyword_score = round(len(found_keywords) / len(keywords) * 100, 2)

    # Readability (based on word count range)
    word_count = len(text.split())
    if word_count < 200:
        readability_score = 50
    elif 200 <= word_count <= 800:
        readability_score = 100
    else:
        readability_score = 70

    # Weighted final ATS score
    ats_score = round((structure_score * 0.4) + (keyword_score * 0.4) + (readability_score * 0.2), 2)

    # Comments
    comments = []
    if structure_score < 80:
        comments.append("🟠 Add missing sections like **Education**, **Projects**, or **Summary**.")
    else:
        comments.append("🟢 Strong structure with all essential sections present.")

    if keyword_score < 70:
        comments.append("🟠 Include more role-relevant keywords such as technical skills or tools.")
    else:
        comments.append("🟢 Good keyword usage matching common job descriptions.")

    if readability_score < 80:
        comments.append("🟠 Adjust your resume length. Keep it concise (1–2 pages ideally).")
    else:
        comments.append("🟢 Great length and readability balance!")

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

st.title("💼 Quicky Resume Reviewer and Validator")
st.write("### Upload your resume to get a quick ATS-style review:")

uploaded_file = st.file_uploader("📄 Upload Resume (PDF or DOCX) *", type=["pdf", "docx"])

if st.button("Validate Resume"):
    if not uploaded_file:
        st.error("❌ Please upload your resume before validation.")
    else:
        with st.spinner("⏳ Analyzing your resume... please wait."):
            try:
                if uploaded_file.name.endswith(".pdf"):
                    text = extract_text_from_pdf(uploaded_file)
                else:
                    text = extract_text_from_docx(uploaded_file)

                ats_score, structure_score, keyword_score, comments = analyze_resume(text)

                st.success("Resume analyzed successfully!")
                st.subheader("📊 ATS Score Overview")
                st.progress(int(ats_score))
                st.write(f"**ATS Score:** {ats_score}/100")
                st.write(f"**Structure Score:** {structure_score}/100")
                st.write(f"**Keyword Match:** {keyword_score}/100")

                st.subheader("💬 Review Comments")
                for c in comments:
                    st.write(f"- {c}")

                # Thank You Message
                st.markdown("<h4 style='text-align:center; color:#1f77b4;'>Thank You! for visiting this Site</h4>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"⚠️ An unexpected error occurred: {e}")
