import streamlit as st
import PyPDF2
import docx
import language_tool_python

# ---------- Helper Functions ----------
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def grammar_score(text):
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    total_words = len(text.split())
    mistakes = len(matches)
    score = max(0, 100 - (mistakes / total_words * 100)) if total_words > 0 else 0
    return round(score, 2), matches

def keyword_score(text, keywords):
    found = [k for k in keywords if k.lower() in text.lower()]
    return round(len(found) / len(keywords) * 100, 2), found

def structure_score(text):
    required_sections = ['education', 'experience', 'skills', 'projects', 'summary']
    found = [s for s in required_sections if s in text.lower()]
    return round(len(found) / len(required_sections) * 100, 2), found

# ---------- Streamlit Frontend ----------
st.set_page_config(page_title="AI Resume Reviewer", page_icon="🧠", layout="centered")
st.title("🧠 AI Resume Reviewer")
st.write("Upload your resume (PDF or DOCX) to get an AI-based score and feedback!")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

job_keywords = st.text_input("Enter Job Role Keywords (comma-separated)", 
                             "python, automation, api testing, selenium")

if uploaded_file is not None:
    if uploaded_file.name.endswith(".pdf"):
        text = extract_text_from_pdf(uploaded_file)
    else:
        text = extract_text_from_docx(uploaded_file)

    if st.button("Validate Resume"):
        with st.spinner("Analyzing resume..."):
            g_score, g_issues = grammar_score(text)
            k_score, found_keywords = keyword_score(text, [k.strip() for k in job_keywords.split(",")])
            s_score, found_sections = structure_score(text)

            final_score = round((g_score * 0.4) + (k_score * 0.3) + (s_score * 0.3), 2)

        st.success(f"✅ Resume Review Completed!")
        st.metric("Overall Resume Score", f"{final_score} / 100")

        st.subheader("Detailed Breakdown:")
        st.write(f"**Grammar & Language:** {g_score}/100")
        st.write(f"**Keyword Match:** {k_score}/100 → Found: {', '.join(found_keywords)}")
        st.write(f"**Structure Completeness:** {s_score}/100 → Sections: {', '.join(found_sections)}")

        st.subheader("Suggestions for Improvement:")
        if len(g_issues) > 0:
            st.write(f"- Grammar corrections suggested: {len(g_issues)} issues found.")
        else:
            st.write("✅ Great! No major grammatical issues found.")

        if k_score < 80:
            st.write("- Add more job-relevant keywords.")
        if s_score < 80:
            st.write("- Ensure all key sections (Education, Skills, Experience, Projects, Summary) are included.")

else:
    st.info("Please upload your resume to begin.")
