
import random
from io import BytesIO

import pandas as pd
import streamlit as st
import spacy
import PyPDF2
from docx import Document


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Mock Interview Platform",
    page_icon="🤖",
    layout="wide"
)


# ==========================================
# 2. LOAD NLP MODEL
# ==========================================

@st.cache_resource
def load_nlp_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        st.error(
            "The spaCy English model is missing. "
            "Run this command in your terminal: "
            "python -m spacy download en_core_web_sm"
        )
        st.stop()


nlp = load_nlp_model()


# ==========================================
# 3. RESUME TEXT EXTRACTION
# ==========================================

def extract_resume_text(resume_file):
    filename = resume_file.name.lower()

    try:
        if filename.endswith(".pdf"):
            reader = PyPDF2.PdfReader(
                BytesIO(resume_file.getvalue())
            )

            return "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )

        elif filename.endswith(".docx"):
            document = Document(
                BytesIO(resume_file.getvalue())
            )

            return "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
            )

        elif filename.endswith(".txt"):
            return resume_file.getvalue().decode(
                "utf-8",
                errors="replace"
            )

        return ""

    except Exception as error:
        st.error(f"Unable to read the resume: {error}")
        return ""


# ==========================================
# 4. KEYWORD EXTRACTION
# ==========================================

def extract_keywords(text):
    if not text.strip():
        return []

    document = nlp(text)

    keywords = []
    seen = set()

    for token in document:
        word = token.lemma_.lower().strip()

        if (
            token.is_alpha
            and not token.is_stop
            and len(word) > 2
            and word not in seen
        ):
            keywords.append(word)
            seen.add(word)

    return keywords


def compare_keywords(resume_keywords, jd_keywords):
    resume_set = set(resume_keywords)
    jd_set = set(jd_keywords)

    matching = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)

    return matching, missing


# ==========================================
# 5. INTERVIEW QUESTION BANK
# ==========================================

QUESTIONS = {
    "Easy": [
        "Explain the four pillars of Object-Oriented Programming.",
        "What is Python used for?",
        "What is the difference between a list and a tuple?",
        "What is a database?",
        "What is the purpose of version control?"
    ],

    "Medium": [
        "How does garbage collection work in Java?",
        "Explain REST API design.",
        "What is the difference between SQL and NoSQL databases?",
        "How would you debug an application that returns a 500 error?",
        "Explain how a machine learning model is trained."
    ],

    "Hard": [
        "Design a scalable IoT system for a smart city.",
        "How would you optimize a database query under heavy load?",
        "How would you design a system to process millions of events?",
        "How would you monitor and troubleshoot a production application?",
        "Explain the trade-offs between a monolithic and microservices architecture."
    ]
}


# ==========================================
# 6. ANSWER EVALUATION
# ==========================================

def evaluate_answer(answer):
    if not answer.strip():
        return (
            0,
            "No answer provided. Try explaining the concept "
            "and giving an example."
        )

    word_count = len(answer.split())

    if word_count < 10:
        score = 3
        feedback = (
            "Your answer is short. Explain the concept in "
            "more detail and include an example."
        )

    elif word_count < 30:
        score = 6
        feedback = (
            "Good start. Add more technical details and "
            "explain why the concept is useful."
        )

    else:
        score = 8
        feedback = (
            "Your answer contains useful detail. Check its "
            "technical accuracy and make sure it answers "
            "the question directly."
        )

    return score, feedback


# ==========================================
# 7. SESSION STATE
# ==========================================

defaults = {
    "resume_keywords": [],
    "jd_keywords": [],
    "resume_analyzed": False,
    "interview_questions": [],
    "current_question": 0,
    "answers": [],
    "interview_started": False,
    "interview_finished": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================
# 8. APPLICATION HEADER
# ==========================================

st.title("🤖 AI Mock Interview Platform")

st.write(
    "Prepare for technical interviews by analysing "
    "resume keywords, practising interview questions, "
    "and reviewing your answers."
)

st.info(
    "This version uses NLP for keyword extraction and "
    "rule-based scoring for answer feedback. It does not "
    "automatically verify whether technical answers are correct."
)


# ==========================================
# 9. RESUME AND JOB DESCRIPTION
# ==========================================

st.sidebar.header("📄 Candidate Details")

resume = st.sidebar.file_uploader(
    "Upload your resume",
    type=["pdf", "docx", "txt"]
)

job_description = st.sidebar.text_area(
    "Paste the job description",
    height=200,
    placeholder="Paste the job description here..."
)


# ==========================================
# 10. RESUME ANALYSIS
# ==========================================

st.header("📊 Resume Analysis")

if resume is not None:
    if st.button("Analyze Resume"):
        resume_text = extract_resume_text(resume)

        if not resume_text.strip():
            st.warning(
                "No readable text was found. Scanned PDFs "
                "may require OCR."
            )

            st.session_state.resume_analyzed = False

        else:
            st.session_state.resume_keywords = extract_keywords(
                resume_text
            )

            st.session_state.resume_analyzed = True

            st.success("Resume analysed successfully!")


# Extract job-description keywords when provided.

if job_description.strip():
    st.session_state.jd_keywords = extract_keywords(
        job_description
    )
else:
    st.session_state.jd_keywords = []


# Display keyword comparison.

if st.session_state.resume_analyzed:
    resume_keywords = st.session_state.resume_keywords
    jd_keywords = st.session_state.jd_keywords

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Resume Keywords")
        st.write(resume_keywords[:20])

    with col2:
        st.subheader("Job Description Keywords")

        if job_description.strip():
            st.write(jd_keywords[:20])
        else:
            st.write("Enter a job description in the sidebar.")

    if job_description.strip():
        matching, missing = compare_keywords(
            resume_keywords,
            jd_keywords
        )

        st.subheader("Keyword Comparison")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Matching Keywords",
                len(matching)
            )

        with col2:
            st.metric(
                "Missing Keywords",
                len(missing)
            )

        st.write("**Keywords found in both:**")

        if matching:
            st.write(", ".join(matching))
        else:
            st.write("No matching keywords found.")

        st.write("**Job-description keywords not found in resume:**")

        if missing:
            st.write(", ".join(missing[:30]))
        else:
            st.write("No missing keywords found.")

        st.caption(
            "Keyword overlap is a basic comparison. It does not "
            "measure complete resume quality or job suitability."
        )


# ==========================================
# 11. INTERVIEW SETUP
# ==========================================

st.divider()

st.header("🎯 Mock Interview")

difficulty = st.selectbox(
    "Choose interview difficulty",
    ["Easy", "Medium", "Hard"]
)

if st.button("Start New Interview"):
    st.session_state.interview_questions = random.sample(
        QUESTIONS[difficulty],
        k=3
    )

    st.session_state.current_question = 0
    st.session_state.answers = []
    st.session_state.interview_started = True
    st.session_state.interview_finished = False

    st.rerun()


# ==========================================
# 12. INTERVIEW QUESTIONS
# ==========================================

if (
    st.session_state.interview_started
    and not st.session_state.interview_finished
):

    question_index = st.session_state.current_question
    questions = st.session_state.interview_questions

    if question_index < len(questions):

        question = questions[question_index]

        st.subheader(
            f"Question {question_index + 1} of {len(questions)}"
        )

        st.write(f"**{question}**")

        answer = st.text_area(
            "Your Answer",
            key=f"answer_{question_index}",
            height=180,
            placeholder="Type your answer here..."
        )

        if st.button(
            "Submit Answer",
            key=f"submit_{question_index}"
        ):

            score, feedback = evaluate_answer(answer)

            st.session_state.answers.append({
                "Question": question,
                "Answer": answer,
                "Score": score,
                "Feedback": feedback
            })

            st.session_state.current_question += 1

            if (
                st.session_state.current_question
                >= len(questions)
            ):
                st.session_state.interview_finished = True

            st.rerun()


# ==========================================
# 13. FINAL INTERVIEW REPORT
# ==========================================

if st.session_state.interview_finished:

    st.divider()

    st.header("📈 Final Interview Report")

    answers = st.session_state.answers

    total_score = sum(
        item["Score"] for item in answers
    )

    maximum_score = len(answers) * 10

    percentage = (
        round((total_score / maximum_score) * 100)
        if maximum_score > 0
        else 0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Questions Answered",
        len(answers)
    )

    col2.metric(
        "Total Score",
        f"{total_score}/{maximum_score}"
    )

    col3.metric(
        "Score Percentage",
        f"{percentage}%"
    )

    if percentage >= 80:
        st.success(
            "Your answers were detailed. Continue practising "
            "and checking technical accuracy."
        )

    elif percentage >= 50:
        st.info(
            "You have a foundation to build on. Add specific "
            "technical details and examples."
        )

    else:
        st.warning(
            "Practise explaining concepts clearly and supporting "
            "your answers with examples."
        )

    st.subheader("Answer-by-Answer Feedback")

    for index, item in enumerate(answers, start=1):

        with st.expander(
            f"Question {index}: {item['Question']}"
        ):

            st.write("**Your Answer:**")

            st.write(
                item["Answer"] or "No answer provided."
            )

            st.write(
                f"**Score:** {item['Score']}/10"
            )

            st.write(
                f"**Feedback:** {item['Feedback']}"
            )

    report_df = pd.DataFrame(answers)

    csv_data = report_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Interview Report (CSV)",
        data=csv_data,
        file_name="interview_report.csv",
        mime="text/csv"
    )

    if st.button("Start Another Interview"):

        st.session_state.interview_started = False
        st.session_state.interview_finished = False
        st.session_state.current_question = 0
        st.session_state.answers = []
        st.session_state.interview_questions = []

        st.rerun()
