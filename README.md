# **HenryAI — The Intelligent Job Search Engine**

*AI-powered job search strategist built for high performers.*

HenryAI transforms messy, confusing job searches into a structured, strategic, and efficient process.  
 It analyzes job descriptions, tailors resumes and cover letters with zero fabrication, tracks applications, powers interview intelligence, and provides strategic guidance throughout the hiring lifecycle.

This is the **MVP foundation** for a full Job Search Operating System designed for the top 0.01% of candidates.

---

## **🔍 Core Features**

### **1\. Job Description Analysis**

* **Fit Score Calculation**: Initial scoring based on skills (50%), experience (30%), and alignment (20%)

* **Eligibility Gating**: Hard requirements checked before scoring proceeds

* **Calibration Layer**: CEC (Capability Evidence Check), credibility signals, and risk factors applied

* **Final Recommendation Lock**: Immutable decision set by the Final Recommendation Controller

* Highlights red flags, missing qualifications, and positioning opportunities

* Converts long, inconsistent job descriptions into clean summaries

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

> **"If it doesn't make the candidate better, no one wins."**

HenryAI is built from actual recruiting expertise, not generic AI templates. It's designed to treat job seekers the way top recruiters treat their best candidates—with strategic honesty, not comfortable fiction.

### Core Values

* **Strategic** — Every output serves a purpose
* **Accurate** — No fabrication, no inflation
* **Empathetic** — Honest guidance delivered with care
* **Factual** — Grounded in resume evidence, not wishful thinking
* **High-leverage** — Focus energy where it matters
* **Zero fluff** — Direct communication, no padding

### What HenryAI Refuses to Do

HenryAI is opinionated and constraint-driven. The system enforces hard limits to protect candidate outcomes:

* **Refuses mass-apply behavior** — Quality over quantity. Apply to 10 roles strategically, not 100 blindly.
* **Refuses to fabricate experience** — Every statement grounded in actual resume content. Zero hallucination tolerance.
* **Refuses to override market reality** — If alignment is partial, say so. No optimism at the expense of truth.
* **Enforces hard constraints** — Eligibility gates, experience caps, and recommendation locks exist to prevent bad outcomes.

These refusals are features, not limitations.

### User Transformation

HenryAI doesn't just organize job searches—it teaches candidates how recruiters think. The goal isn't convenience. The goal is better decision-making that compounds over time.

* Learn which roles actually fit your background
* Understand why certain applications fail before they start
* Build positioning instincts that transfer to every future search

This is not a resume vending machine.
This is a career acceleration engine.

