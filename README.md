# **HenryAI — The Intelligent Job Search Engine**

*AI-powered job search strategist built for high performers.*

HenryAI transforms messy, confusing job searches into a structured, strategic, and efficient process.  
 It analyzes job descriptions, tailors resumes and cover letters with zero fabrication, tracks applications, powers interview intelligence, and provides strategic guidance throughout the hiring lifecycle.

This is the **MVP foundation** for a full Job Search Operating System designed for the top 0.01% of candidates.

---

## **🔍 Core Features**

### **1\. Job Description Analysis**

* Uses a structured 50/30/20 Fit Score (skills, experience, alignment).

* Highlights red flags, missing qualifications, and positioning opportunities.

* Converts long, inconsistent job descriptions into clean summaries.

### **2\. Resume Parsing & Tailored Resume Generation**

* Zero-fabrication rule enforced.

* Extracts all factual content from the user’s resume.

* Applies strict formatting (DOCX templates).

* ATS-optimized and recruiter-centered.

### **3\. Tailored Cover Letters**

* Same header as the resume.

* Structured, concise, and targeted to the role.

* Fully editable before download.

### **4\. Document Downloads**

* All outputs available as `.docx`

* Clean separation of resume and cover letter templates.

### **5\. Application Tracking**

* Tracks roles, companies, dates, statuses, follow-ups, and notes.

* Future integration with reminders and a daily command center.

### **6\. Interview Intelligence (Phase 1.5 / Phase 2\)**

* Parse transcripts (when provided).

* Summarize strengths, weaknesses, behavioral signals, communication patterns.

* Provide actionable coaching and readiness scoring.

---

## **🧠 The Intelligence Layer**

HenryAI includes a growing set of advanced capabilities:

* Multi-step navigation

* Network intelligence

* Compensation insights

* Success pattern recognition

* Strategic recommendations

* Job quality scoring

* Post-interview debrief analytics

These are powered through structured prompts in the `/prompts` directory.

---

## **📁 Project Structure**

`HenryAI/`  
`│`  
`├── backend/`  
`│   ├── backend.py`  
`│   ├── models/`  
`│   ├── services/`  
`│   ├── utils/`  
`│   └── requirements.txt`  
`│`  
`├── frontend/`  
`│   ├── index.html`  
`│   ├── analyze.html`  
`│   ├── results.html`  
`│   ├── tracker.html`  
`│   ├── package.html`  
`│   ├── index.css`  
`│   └── assets/`  
`│       ├── css/`  
`│       ├── fonts/`  
`│       ├── img/`  
`│       └── js/`  
`│`  
`├── downloads/`  
`│   ├── resumes/`  
`│   └── cover_letters/`  
`│`  
`├── prompts/`  
`│   ├── core/`  
`│   ├── resume/`  
`│   ├── cover_letter/`  
`│   ├── interview/`  
`│   ├── navigation/`  
`│   ├── enhancements/`  
`│   ├── phase_outputs/`  
`│   └── schemas/`  
`│`  
`├── docs/`  
`│   ├── checklists/`  
`│   ├── diagrams/`  
`│   ├── flows/`  
`│   ├── guides/`  
`│   └── summaries/`  
`│`  
`├── workspace/`  
`│   ├── archived_versions/`  
`│   ├── claude_notes/`  
`│   ├── diagnostics/`  
`│   ├── scratch/`  
`│   └── tests/`  
`│`  
`└── README.md`

---

## **🚀 Installation & Running Locally**

### **1\. Create a virtual environment**

`python3 -m venv venv`  
`source venv/bin/activate`

### **2\. Install dependencies**

`pip install -r backend/requirements.txt`

### **3\. Add your API key**

Create a `.env` file in `/backend`:

`ANTHROPIC_API_KEY=your_key_here`

### **4\. Start the backend**

`cd backend`  
`uvicorn backend:app --reload --port 8000`

### **5\. Open the frontend**

Just open:

`frontend/index.html`

in the browser.

---

## **🌱 Roadmap**

### **Near-Term (Dec–Jan)**

* Resume \+ cover letter accuracy pipeline

* Real-time resume preview UI

* Improved conversation flow

* Fix multi-output download accuracy

* Add user preference memory

* Strengthen strategic recommendation engine

### **Mid-Term**

* Daily command center

* Network analysis engine

* Compensation intelligence

* Timeline prediction for applications

* Chrome extension (auto-capture job postings)

### **Long-Term**

* Conversation-driven job search

* Real recruiter coaching layer

* Full job search operating system

* Multi-user accounts \+ subscription model

---

## **🎯 Philosophy**

HenryAI is built from actual recruiting expertise, not generic AI templates.  
 It’s designed to treat job seekers the way top recruiters treat their candidates:

* strategic

* accurate

* empathetic

* factual

* high-leverage

* zero fluff

This is not a resume vending machine.  
 This is a career acceleration engine.

