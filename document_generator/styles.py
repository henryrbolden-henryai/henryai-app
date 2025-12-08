"""
Centralized style definitions for resume and cover letter generation.
ALL formatting values live here. No hardcoded values anywhere else in codebase.

Based on templates:
- HenryRBoldenIiiResume.pdf
- HenryRBoldenIiiCoverLetter.pdf
"""

from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ==============================================================================
# DOCUMENT SETTINGS
# ==============================================================================

PAGE_WIDTH = Inches(8.5)
PAGE_HEIGHT = Inches(11)

# ==============================================================================
# MARGINS
# ==============================================================================

# Resume margins
RESUME_MARGIN_TOP = Inches(0.5)
RESUME_MARGIN_BOTTOM = Inches(0.5)
RESUME_MARGIN_LEFT = Inches(0.75)
RESUME_MARGIN_RIGHT = Inches(0.75)

# Cover letter margins (1" all sides)
CL_MARGIN_ALL = Inches(1.0)

# ==============================================================================
# FONTS
# ==============================================================================

FONT_FAMILY = "Arial"  # Primary font for all documents

# Resume font sizes
FONT_SIZE_RESUME_NAME = Pt(18)           # Candidate name in header
FONT_SIZE_RESUME_TAGLINE = Pt(11)        # Role/specialization line
FONT_SIZE_RESUME_CONTACT = Pt(9)         # Contact info line
FONT_SIZE_SECTION_HEADER = Pt(12)        # SUMMARY, EXPERIENCE, etc.
FONT_SIZE_COMPANY = Pt(11)               # Company names
FONT_SIZE_JOB_TITLE = Pt(10)             # Job titles
FONT_SIZE_COMPANY_OVERVIEW = Pt(9)       # Italic company description
FONT_SIZE_DEFAULT = Pt(10)               # Body text, bullets

# Cover letter font sizes
FONT_SIZE_CL_NAME = Pt(14)               # Candidate name
FONT_SIZE_CL_TAGLINE = Pt(11)            # Tagline
FONT_SIZE_CL_CONTACT = Pt(10)            # Contact info
FONT_SIZE_CL_BODY = Pt(11)               # All body text

# ==============================================================================
# COLORS
# ==============================================================================

COLOR_BLACK = RGBColor(0, 0, 0)
COLOR_DARK_GRAY = RGBColor(102, 102, 102)  # #666666

# ==============================================================================
# SPACING (all values in points)
# ==============================================================================

# Resume spacing
SPACING_AFTER_NAME = Pt(3)
SPACING_AFTER_TAGLINE = Pt(6)
SPACING_AFTER_CONTACT = Pt(0)
SPACING_BEFORE_SECTION_HEADER = Pt(12)
SPACING_AFTER_SECTION_HEADER = Pt(6)
SPACING_AFTER_SUMMARY = Pt(12)
SPACING_BETWEEN_BULLETS = Pt(3)
SPACING_BETWEEN_JOBS = Pt(12)
SPACING_AFTER_JOB_TITLE = Pt(3)
SPACING_AFTER_COMPANY_OVERVIEW = Pt(6)

# Cover letter spacing
CL_SPACING_AFTER_NAME = Pt(3)
CL_SPACING_AFTER_TAGLINE = Pt(6)
CL_SPACING_AFTER_CONTACT = Pt(18)
CL_SPACING_BEFORE_LABEL = Pt(18)
CL_SPACING_AFTER_LABEL = Pt(12)
CL_SPACING_BEFORE_SALUTATION = Pt(12)
CL_SPACING_AFTER_SALUTATION = Pt(12)
CL_SPACING_AFTER_BODY_PARA = Pt(12)
CL_SPACING_BEFORE_CLOSING = Pt(18)
CL_SPACING_AFTER_CLOSING = Pt(24)

# ==============================================================================
# INDENTATION
# ==============================================================================

BULLET_INDENT = Inches(0.25)             # Hanging indent for bullets
COMPETENCY_INDENT = Inches(0.25)         # Core competencies indent

# ==============================================================================
# LINE SPACING
# ==============================================================================

LINE_SPACING_SINGLE = 1.0
LINE_SPACING_CL_BODY = 1.15              # Cover letter body (more open)

# ==============================================================================
# ALIGNMENT
# ==============================================================================

ALIGN_LEFT = WD_ALIGN_PARAGRAPH.LEFT
ALIGN_CENTER = WD_ALIGN_PARAGRAPH.CENTER
ALIGN_RIGHT = WD_ALIGN_PARAGRAPH.RIGHT
ALIGN_JUSTIFY = WD_ALIGN_PARAGRAPH.JUSTIFY

# ==============================================================================
# BORDERS
# ==============================================================================

BORDER_THIN = 8      # 1pt (in eighths of a point)
BORDER_THICK = 16    # 2pt
