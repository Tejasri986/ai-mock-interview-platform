```python
import random
import re
import time
from io import BytesIO

import pandas as pd
import streamlit as st
import spacy
import PyPDF2
from docx import Document

# --------------------------------
# Page Configuration
# --------------------------------
st.set_page_config(
    page_title="AI Mock Interview Platform",
    page_icon="🤖",
    layout="wide"
)

# --------------------------------
# Load NLP Model
# --------------------------------
@st.cache_resource
def load_nlp_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        st.error(
            "The spaCy English model is missing. "
            "Install it using: python -m spacy download en_core_web_sm"
        )
        st.stop()


nlp = load_nlp_model()

# --------------------------------
# Resume Text Extraction
# --------------------------------
def extract_resume_text(resume_file):
    file_name = resume_file.name.lower()

    try:
        if file_name.endswith(".pdf"):
            reader = PyPDF2.PdfReader(resume_file)
            return "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )

        elif file_name.endswith(".docx"):
            document = Document(BytesIO(resume_file.getvalue()))
            return "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
            )

        elif file_name.endswith(".txt"):
            return resume_file.getvalue().decode(
                "utf-8", errors="replace"
            )

        return ""

    except Exception as error:
        st.error(f"Could not read the uploaded resume: {error}")
        return ""


# --------------------------------
# Keyword Extraction
# --------------------------------
def extract_keywords(text):
    if not text.strip():
        return []

    doc = nlp(text)

    keywords = []
    seen = set()

    for token in doc:
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


def find_matching_keywords(resume_keywords, jd_keywords):
    resume_set = set(resume_keywords)
    jd_set = set(jd_keywords)

    matching = sorted(resume_set.intersection(jd_set))
    missing = sorted(jd_set - resume_set)

    return matching, missing


# --------------------------------
# Interview Question Bank
# --------------------------------
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


# --------------------------------
# Answer Evaluation
# --------------------------------
def evaluate_answer(answer):
    if not answer.strip():
        return 0, "No answer provided. Try answering with a clear explanation and an example."

    word_count = len(answer.split())

    if word_count < 10:
        score = 3
        feedback = (
            "Your answer is quite short. Explain the concept in more detail "
            "and include an example."
        )
    elif word_count < 30:
        score = 6
        feedback = (
            "Good start. Add more technical details and explain why the "
            "concept is useful."
        )
    else:
        score = 8
        feedback = (
            "Your answer has useful detail. Review its technical accuracy "
            "and make sure it directly answers the question."
        )

    return score, feedback


# --------------------------------
# Session State
# --------------------------------
if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = []

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "answers" not in st.session_state:
    st.session_state.answers = []

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "interview_finished" not in st.session_state:
    st.session_state.interview_finished = False

if "question_start_time" not in st.session_state:
    st.session_state.question_start_time = None


# --------------------------------
# Application Interface
# --------------------------------
st.title("🤖 AI Mock Interview Platform")

st.write(
    "Prepare for technical interviews by reviewing job requirements, "
    "answering practice questions, and receiving basic feedback."
)

st.info(
    "This version uses NLP-based keyword extraction and rule-based "
    "answer feedback. It does not yet use a generative AI model to "
    "judge technical correctness."
)

# --------------------------------
# Sidebar: Resume and Job Description
# --------------------------------
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

# --------------------------------
# Resume Analysis
# --------------------------------
if resume is not None:
    if st.button("Analyze Resume"):
        resume_text = extract_resume_text(resume)

        if not resume_text.strip():
            st.warning(
                "No readable text was found. If this is a scanned PDF, "
                "OCR support may be needed."
            )
        else:
            resume_keywords = extract_keywords(resume_text)
            st.session_state.resume_keywords = resume_keywords
            st.session_state.resume_text = resume_text
            st.success("Resume text extracted successfully!")

if job_description.strip():
    jd_keywords = extract_keywords(job_description)
    st.session_state.jd_keywords = jd_keywords

if (
    "resume_keywords" in st.session_state
    and "jd_keywords" in st.session_state
):
    st.header("📊 Resume and Job Description Analysis")

    resume_keywords = st.session_state.resume_keywords
    jd_keywords = st.session_state.jd_keywords

    matching_keywords, missing_keywords = find_matching_keywords(
        resume_keywords,
        jd_keywords
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Resume Keywords")
        st.write(resume_keywords[:20])

    with col2:
        st.subheader("Job Description Keywords")
        st.write(jd_keywords[:20])

    st.subheader("Keyword Comparison")

    st.metric("Matching Keywords", len(matching_keywords))
    st.write("**Keywords found in both:**")
    st.write(matching_keywords if matching_keywords else "No matching keywords found.")

    st.write("**Job-description keywords not found in the resume:**")
    st.write(missing_keywords[:30] if missing_keywords else "No missing keywords found.")

    st.caption(
        "Keyword overlap is a basic comparison, not a complete measure "
        "of resume quality or job suitability."
    )

# --------------------------------
# Interview Setup
# --------------------------------
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
    st.session_state.question_start_time = time.time()
    st.session_state.selected_difficulty = difficulty

# --------------------------------
# Interview Questions
# --------------------------------
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
            "Your answer",
            key=f"answer_{question_index}",
            height=180,
            placeholder="Type your answer here..."
        )

        if st.button("Submit Answer", key=f"submit_{question_index}"):
            score, feedback = evaluate_answer(answer)

            st.session_state.answers.append({
                "Question": question,
                "Answer": answer,
                "Score": score,
                "Feedback": feedback
            })

            st.session_state.current_question += 1

            if st.session_state.current_question >= len(questions):
                st.session_state.interview_finished = True
            else:
                st.session_state.question_start_time = time.time()

            st.rerun()

# --------------------------------
# Interview Report
# --------------------------------
if st.session_state.interview_finished:
    st.header("📈 Interview Report")

    answers = st.session_state.answers
    total_score = sum(item["Score"] for item in answers)
    maximum_score = len(answers) * 10

    col1, col2, col3 = st.columns(3)

    col1.metric("Questions Answered", len(answers))
    col2.metric("Total Score", f"{total_score}/{maximum_score}")

    percentage = (
        round((total_score / maximum_score) * 100)
        if maximum_score else 0
    )

    col3.metric("Score Percentage", f"{percentage}%")

    if percentage >= 80:
        st.success("Your answers were detailed. Continue practising technical accuracy.")
    elif percentage >= 50:
        st.info("You have a foundation to build on. Add more specific technical details.")
    else:
        st.warning("Practise explaining concepts clearly and supporting them with examples.")

    st.subheader("Answer-by-Answer Feedback")

    for index, item in enumerate(answers, start=1):
        with st.expander(f"Question {index}: {item['Question']}"):
            st.write("**Your answer:**")
            st.write(item["Answer"] or "No answer provided.")

            st.write(f"**Score:** {item['Score']}/10")
            st.write(f"**Feedback:** {item['Feedback']}")

    report_df = pd.DataFrame(answers)
    csv_data = report_df.to_csv(index=False).encode("utf-8")

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
        st.rerun()
```
