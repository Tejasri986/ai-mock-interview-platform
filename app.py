import streamlit as st
import time
import random
import spacy
import PyPDF2

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# -------------------------------
# Resume & JD Parsing
# -------------------------------
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_keywords(text):
    doc = nlp(text)
    keywords = [token.text for token in doc if token.is_alpha and not token.is_stop]
    return list(set(keywords))

# -------------------------------
# Interview Question Bank
# -------------------------------
questions = {
    "easy": ["Explain OOP concepts.", "What is Python used for?"],
    "medium": ["How does garbage collection work in Java?", "Explain REST API design."],
    "hard": ["Design a scalable IoT system for smart cities.", "How would you optimize a database query under heavy load?"]
}

# -------------------------------
# Scoring Logic
# -------------------------------
def evaluate_answer(answer, elapsed, difficulty):
    if not answer.strip():
        return 0, "No answer provided."
    
    score = 0
    if len(answer.split()) > 5:
        score += 5
    else:
        score += 2
    
    score += min(len(answer.split()) // 5, 5)
    
    if elapsed <= 30:
        score += 5
    else:
        score -= 2
    
    score += difficulty
    feedback = "Good attempt!" if score > 10 else "Needs improvement."
    return score, feedback

# -------------------------------
# Streamlit App
# -------------------------------
st.title("🤖 AI-Powered Mock Interview Platform")

st.sidebar.header("Upload Details")
resume = st.sidebar.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
jd = st.sidebar.text_area("Paste Job Description")

if resume and jd:
    st.success("Resume and JD uploaded successfully!")
    resume_text = extract_text_from_pdf(resume)
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd)

    st.write("### Extracted Resume Keywords:", resume_keywords[:10])
    st.write("### Extracted JD Keywords:", jd_keywords[:10])

    st.write("### Interview Simulation")
    total_score = 0
    difficulty_level = 1

    for i in range(3):  # 3 questions demo
        if difficulty_level == 1:
            q = random.choice(questions["easy"])
        elif difficulty_level == 2:
            q = random.choice(questions["medium"])
        else:
            q = random.choice(questions["hard"])
        
        st.write(f"**Question {i+1}:** {q}")
        start_time = time.time()
        answer = st.text_area("Your Answer:", key=q)
        elapsed = time.time() - start_time
        
        if st.button(f"Submit Answer {i+1}", key=f"btn{i}"):
            score, feedback = evaluate_answer(answer, elapsed, difficulty_level)
            st.write(f"**Score:** {score}")
            st.write(f"**Feedback:** {feedback}")
            total_score += score
            
            if score > 10 and difficulty_level < 3:
                difficulty_level += 1
            elif score < 5 and difficulty_level > 1:
                difficulty_level -= 1

    st.write("## 📊 Final Interview Report")
    st.write(f"**Total Score:** {total_score}")
    if total_score >= 30:
        readiness = "Strong"
    elif total_score >= 15:
        readiness = "Average"
    else:
        readiness = "Needs Improvement"
    st.write(f"**Readiness Indicator:** {readiness}")
    st.write("### Actionable Feedback")
    st.write("- Improve clarity and depth in answers.")
    st.write("- Manage time better under pressure.")
    st.write("- Strengthen technical concepts aligned with JD.")