---

# **HenryAI — Prompts Directory**

This folder contains **all AI system instructions** that power HenryAI’s intelligence layer.  
 Prompts are organized into modular subfolders so each component of the system can be loaded, versioned, and improved independently.

The goal:  
 **Make HenryAI deterministic, structured, and zero-fabrication across every feature.**

---

# **🔍 Folder Structure Overview**

`prompts/`  
   `core/`  
   `cover_letter/`  
   `enhancements/`  
   `interview/`  
   `navigation/`  
   `phase_outputs/`  
   `resume/`  
   `schemas/`

Each folder has a clear purpose:

---

## **1\. `/core` — Global Thinking & System Behavior**

These prompts define the *fundamental intelligence* of HenryAI:

* reasoning rules

* intelligence-layer corrections

* multi-step logic

* global constraints

* behavioral guardrails

These should load **before** any feature-specific prompts.

---

## **2\. `/cover_letter` — Cover Letter Logic**

Contains prompts that govern:

* cover letter tone

* structure

* formatting

* non-fabrication rules

* personalization

* header/footer consistency

(Empty now — will be populated when CL templates and rules are finalized.)

---

## **3\. `/enhancements` — Add-ons & Optional Logic**

Includes:

* extra features

* API documentation

* experimental improvements

* optional instructions that modify or extend capabilities

These prompts are not required for core functionality but enhance it.

---

## **4\. `/interview` — Interview Intelligence Engine**

Contains all prompts related to:

* interview question extraction

* response scoring

* behavioral analysis

* STAR mapping

* coaching logic

* post-interview feedback

This is the foundation of HenryAI’s Interview Intelligence module.

---

## **5\. `/navigation` — Conversational & UI Flow Logic**

Controls:

* user onboarding sequences

* question flow

* screen transitions

* decision paths

* Phase 1.5 conversational intake

These prompts determine how HenryAI interacts with users during setup.

---

## **6\. `/phase_outputs` — Versioned Implementation Snapshots**

Stores:

* phase completion summaries

* implementation notes

* fix logs

* structured updates

These are references for developers and should not be loaded as active prompts.

---

## **7\. `/resume` — Resume Generation & Transformation Rules**

Contains instructions governing:

* resume rewriting

* non-fabrication

* bullet transformation

* naming logic

* formatting standards

* Phase 1 required fixes

* BEFORE/AFTER style transformations

This is the foundation of the Resume Intelligence Engine.

---

## **8\. `/schemas` — JSON Structures & Output Specifications**

Contains structured templates for:

* expected JSON responses

* document generation schemas

* resume/CL field definitions

* validation-layer formats

These files ensure consistent output formatting and enable template-based DOCX generation.

These should always be loaded **as raw schemas** — not prose.

---

# **📦 Loading Order (Recommended)**

When calling Claude, load prompts in this order:

1. **core**

2. **schemas**

3. **navigation** (if conversational flow is needed)

4. **resume or cover\_letter** (depending on feature)

5. **interview** (if running interview modules)

6. **enhancements** (optional)

This ensures:

* constraints load first

* structure loads next

* task-specific instructions override only where needed

---

# **🧩 How to Use These Prompts (Backend Integration)**

The backend should load prompts dynamically by reading file contents from their subfolders:

`import os`

`def load_prompt(folder):`  
    `base = "prompts/" + folder`  
    `text = ""`  
    `for file in os.listdir(base):`  
        `path = os.path.join(base, file)`  
        `if os.path.isfile(path) and file.endswith((".md", ".txt", ".json")):`  
            `text += open(path).read() + "\n\n"`  
    `return text`

This allows:

* modular updates

* versioning

* selective loading per feature

and ensures that Claude always receives the correct full instruction set.

---

# **🔒 Non-Negotiable Rules for Prompt Quality**

Every prompt in this directory must:

* enforce **zero fabrication**

* maintain **resume factual integrity**

* support **ATS safety**

* maintain **consistent formatting**

* avoid syntax that encourages hallucination

* use structured output (Markdown, JSON, tables)

This keeps HenryAI clean, safe, and trustworthy.

---

# **📌 Future Enhancements**

* Add prompt versioning (`v1`, `v2`, `v3`) to critical files

* Add “templates” folder for DOCX header/footer rules

* Add unit tests to validate schema conformity

* Add combined system prompt assembler script

* Add detailed CL rewrite rules to `/cover_letter`

