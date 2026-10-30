
# 🤖 AI-Powered Mock Interview Platform

## 📌 Problem Statement
In today’s competitive hiring ecosystem, interview readiness is not just about subject knowledge — it’s about adaptability, communication, time management, and performance under pressure.  
This project simulates a **real-world interview environment** using an AI Interviewer.

---

## 🚀 Features
- Resume & JD parsing (skills extraction using spaCy).
- Adaptive interview questions (Easy → Medium → Hard).
- Strict time constraints with scoring penalties.
- Dynamic difficulty adjustment based on performance.
- Objective scoring (Accuracy, Clarity, Depth, Relevance, Time).
- Final Interview Readiness Score with actionable feedback.

---

## 🛠 Tech Stack
- **Frontend/UI:** Streamlit (Python)
- **NLP:** spaCy, PyPDF2, pdfplumber
- **Backend Logic:** Pure Python scoring & evaluation
- **Deployment:** Streamlit Cloud / HuggingFace Spaces (optional)

---

## 📂 Workflow
1. Candidate uploads **Resume** and **Job Description (JD)**.
2. System extracts **skills & keywords**.
3. AI Interviewer asks **adaptive questions**.
4. Candidate answers under **time pressure**.
5. System evaluates responses and adjusts difficulty.
6. Final **Readiness Report** is generated.


---

## 📦 Installation & Run
### 1. Clone the repository
```bash
git clone https://github.com/Tejasri986/ai-mock-interview-platform.git
cd ai-mock-interview-platform
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
streamlit run app.py
```

The application will open in your browser.

## Features
- Resume text extraction from PDF, DOCX, and TXT files
- Resume and job description keyword comparison
- Difficulty-based technical interview questions
- Rule-based answer feedback and scoring
- Interview summary with downloadable CSV report

## Technology Stack
- Python
- Streamlit
- spaCy
- Pandas
- PyPDF2
- python-docx

**Note:** Answer scoring uses basic rules and does not independently verify technical correctness. The application currently does not use a generative AI model.
```bash
git clone https://github.com/your-username/ai-mock-interview-platform.git
cd ai-mock-interview-platform
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app.py
