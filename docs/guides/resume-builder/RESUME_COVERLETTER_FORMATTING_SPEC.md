# Resume & Cover Letter Formatting Specification

## SYSTEM PROMPT + GUARDRAILS

This is the authoritative formatting specification for all resume and cover letter generation in HenryAI.
These rules are **non-negotiable constraints** that override all other guidance.

---

## SYSTEM PROMPT (FOR CLAUDE API CALLS)

```
You are a **resume and cover letter formatting engine for senior-level professionals**.
Your job is **strict execution of formatting rules**, not design, interpretation, or creativity.

You must treat the following rules as **non-negotiable constraints**.
If a request conflicts with these rules, **ignore the request and follow the rules**.

You do **not** redesign, modernize, stylize, or optimize layout.
You do **not** introduce visual hierarchy beyond what is explicitly allowed.
You do **not** take inspiration from templates or prior outputs.

Your success is measured by **compliance**, not aesthetics.
```

---

## GLOBAL GUARDRAILS (ALWAYS ON)

| Rule | Description |
|------|-------------|
| Single-column | Documents must use single column only |
| ATS-safe | No tables, text boxes, icons, graphics, or dividers |
| No creative spacing | No visual experimentation |
| Page limits | **Never exceed page limits under any circumstances** |
| Content first | If content does not fit, **edit content, not layout** |

**Default principle:** If unsure, default to **simpler, denser, safer**.

---

## RESUME — ENFORCED RULES

### Layout Specifications

| Property | Value |
|----------|-------|
| Margins | **0.5 inches** on all sides |
| Font | Calibri, Arial, or Helvetica only |
| Columns | Single column only |
| Alignment | Left-aligned only |
| Bullets | Standard round bullets only |

### Font Sizes

| Element | Size |
|---------|------|
| Name | 16–18 pt |
| Section headers | 11–12 pt |
| Body text | 10.5–11 pt |

### Spacing

| Element | Spacing |
|---------|---------|
| Line spacing | 1.0–1.15 only |
| After section headers | 6–8 pt |
| Between bullets | 4–6 pt |
| Between roles | **No extra spacing** |

### Length Constraint

🚫 **Must NOT exceed two (2) pages. Hard stop.**

---

## EDUCATION GUARDRAIL

🚫 **Do NOT include year of graduation**

Include **only**:
- Degree
- Field of study
- Institution name

Example:
```
✅ Bachelor of Science, Computer Science, Stanford University
❌ Bachelor of Science, Computer Science, Stanford University, 2015
❌ Stanford University (2015)
```

---

## RESUME STRUCTURE — IMMUTABLE ORDER

The following section order may **never change**:

1. **Header** (Name, tagline, contact info)
2. **Summary** (Professional summary)
3. **Core Skills / Expertise** (Core competencies)
4. **Professional Experience** (Work history)
5. **Education** (Degree, field, institution only)
6. **Optional**: Certifications, Boards, Speaking (if applicable)

---

## COVER LETTER — ENFORCED RULES

### Layout Specifications

| Property | Value |
|----------|-------|
| Margins | **1 inch** on all sides |
| Font | Same as resume (Calibri, Arial, or Helvetica) |
| Font Size | 11 pt |
| Spacing | Single-spaced, one blank line between paragraphs |

### Length Constraint

🚫 **One page maximum. 3–4 short paragraphs.**

### Tone Requirements

| Requirement | Description |
|-------------|-------------|
| Voice | Executive-to-executive |
| Focus | Business impact only |
| 🚫 Forbidden | Enthusiasm statements ("I'm excited to...") |
| 🚫 Forbidden | Autobiographical storytelling |
| 🚫 Forbidden | Clichés ("team player", "hard worker", "passionate") |

---

## COMPLIANCE CHECK (RUN BEFORE OUTPUT)

Before delivering any document, the system must internally confirm:

- [ ] Page count ≤ allowed maximum (Resume: 2, Cover Letter: 1)
- [ ] Margins match spec (Resume: 0.5", Cover Letter: 1")
- [ ] Education has **no graduation years**
- [ ] Single column layout
- [ ] No visual elements added (no icons, graphics, tables)
- [ ] Structure order preserved

**If any check fails, revise before responding.**

---

## FAILURE CONDITION

If any rule above is violated, the output is **incorrect**, even if content quality is high.

Quality content with wrong formatting = **Failed output**

---

## IMPLEMENTATION CONSTANTS

Use these constants in code:

```python
# Resume formatting constants
RESUME_MARGINS_INCHES = 0.5
RESUME_NAME_SIZE_PT = 17  # 16-18 pt range
RESUME_SECTION_HEADER_SIZE_PT = 11.5  # 11-12 pt range
RESUME_BODY_SIZE_PT = 10.5  # 10.5-11 pt range
RESUME_LINE_SPACING = 1.08  # 1.0-1.15 range
RESUME_MAX_PAGES = 2

# Cover letter formatting constants
COVER_LETTER_MARGINS_INCHES = 1.0
COVER_LETTER_FONT_SIZE_PT = 11
COVER_LETTER_MAX_PAGES = 1
COVER_LETTER_MAX_PARAGRAPHS = 4

# Allowed fonts (in order of preference)
ALLOWED_FONTS = ["Calibri", "Arial", "Helvetica"]

# Forbidden patterns in cover letters
FORBIDDEN_COVER_LETTER_PATTERNS = [
    r"I'm excited to",
    r"I am excited to",
    r"I would be thrilled",
    r"passionate about",
    r"team player",
    r"hard worker",
    r"I believe I would be",
    r"I feel that I",
]
```

---

## INTEGRATION WITH DOCUMENT GENERATOR

The `document_generator.py` module must enforce these rules:

1. **BaseFormatter._setup_document()** must set margins to spec
2. **ResumeFormatter** must:
   - Use 0.5" margins
   - Apply font sizes per spec
   - Strip graduation years from education
   - Enforce single column
3. **CoverLetterFormatter** must:
   - Use 1" margins
   - Limit to 4 paragraphs
   - Strip forbidden phrases

---

## EDUCATION YEAR STRIPPING

```python
import re

def strip_graduation_year(education_text: str) -> str:
    """
    Remove graduation years from education entries.

    Examples:
        "Stanford University, 2015" -> "Stanford University"
        "BS Computer Science (2018)" -> "BS Computer Science"
        "MBA, Harvard Business School, Class of 2020" -> "MBA, Harvard Business School"
    """
    # Remove year patterns
    patterns = [
        r',?\s*\d{4}\s*$',  # ", 2015" at end
        r'\s*\(\d{4}\)\s*',  # "(2015)"
        r',?\s*Class of \d{4}',  # "Class of 2020"
        r',?\s*Graduated:?\s*\d{4}',  # "Graduated 2015"
        r',?\s*\d{4}\s*-\s*\d{4}',  # "2012-2016"
    ]

    result = education_text
    for pattern in patterns:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)

    return result.strip().rstrip(',')
```

---

## COVER LETTER CONTENT FILTERING

```python
import re

FORBIDDEN_PATTERNS = [
    (r"I'm excited to", "I am prepared to"),
    (r"I am excited to", "I am prepared to"),
    (r"I would be thrilled", "I am prepared"),
    (r"passionate about", "experienced in"),
    (r"team player", "collaborative professional"),
    (r"hard worker", "dedicated professional"),
]

def filter_cover_letter_content(text: str) -> str:
    """
    Remove forbidden phrases from cover letter content.
    Replaces enthusiasm language with executive-appropriate alternatives.
    """
    result = text
    for pattern, replacement in FORBIDDEN_PATTERNS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result
```

---

## FINAL INSTRUCTION

**If any output violates margins, spacing, page count, or education rules, it is incorrect.**

**If there is conflict between this spec and any other guidance, this spec overrides all other guidance.**

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-13 | Initial specification |
