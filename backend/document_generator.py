"""
Document Generator Module for HenryAI

Professional DOCX formatters for resumes and cover letters.
Designed to be ATS-safe with clean, consistent formatting.
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from typing import Dict, Any, List, Optional


class BaseFormatter:
    """Base class for document formatters with common utilities."""

    def __init__(self):
        self.doc = Document()
        self._setup_document()

    def _setup_document(self):
        """Set up ATS-safe document defaults."""
        # Set ATS-safe margins (0.75 inches all around)
        for section in self.doc.sections:
            section.top_margin = Inches(0.75)
            section.bottom_margin = Inches(0.75)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)

    def _set_font(self, run, font_name='Calibri', font_size=11, bold=False, italic=False):
        """Apply consistent font settings to a run."""
        run.font.name = font_name
        run.font.size = Pt(font_size)
        run.bold = bold
        run.italic = italic

        # Ensure font is set for complex scripts
        r = run._element
        rPr = r.get_or_add_rPr()
        rFonts = OxmlElement('w:rFonts')
        rFonts.set(qn('w:ascii'), font_name)
        rFonts.set(qn('w:hAnsi'), font_name)
        rFonts.set(qn('w:cs'), font_name)
        rFonts.set(qn('w:eastAsia'), font_name)
        rPr.insert(0, rFonts)

    def _add_paragraph(self, text: str, font_size: int = 11, bold: bool = False,
                       alignment=None, space_before: int = 0, space_after: int = 0):
        """Add a paragraph with standard formatting."""
        p = self.doc.add_paragraph()
        p.style = self.doc.styles['Normal']
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15

        if alignment:
            p.alignment = alignment

        run = p.add_run(text)
        self._set_font(run, font_size=font_size, bold=bold)

        return p

    def get_document(self):
        """Return the Document object."""
        return self.doc


class ResumeFormatter(BaseFormatter):
    """
    Professional resume formatter with ATS-safe formatting.

    Tracks all content added so it can generate both DOCX and plain text
    from the same source (single source of truth for preview === download).
    """

    def __init__(self):
        super().__init__()
        # Track content for plain text generation
        self._content = {
            "name": "",
            "tagline": "",
            "contact_parts": [],
            "summary": "",
            "competencies": [],
            "experience": [],
            "skills": None,
            "education": [],
        }

    def add_header(self, name: str, tagline: str = "", contact_info: Dict[str, Any] = None):
        """Add resume header with name, tagline, and contact info."""
        # Track for plain text
        self._content["name"] = name
        self._content["tagline"] = tagline

        # Name - large and bold, centered
        p = self._add_paragraph(name, font_size=18, bold=True,
                               alignment=WD_ALIGN_PARAGRAPH.CENTER)

        # Tagline - slightly smaller
        if tagline:
            self._add_paragraph(tagline, font_size=12,
                              alignment=WD_ALIGN_PARAGRAPH.CENTER,
                              space_after=4)

        # Contact info - single line, centered
        if contact_info:
            contact_parts = []
            if contact_info.get('phone'):
                contact_parts.append(contact_info['phone'])
            if contact_info.get('email'):
                contact_parts.append(contact_info['email'])
            if contact_info.get('linkedin'):
                contact_parts.append(contact_info['linkedin'])
            if contact_info.get('location'):
                contact_parts.append(contact_info['location'])

            # Track for plain text
            self._content["contact_parts"] = contact_parts

            if contact_parts:
                contact_text = " | ".join(contact_parts)
                self._add_paragraph(contact_text, font_size=10,
                                  alignment=WD_ALIGN_PARAGRAPH.CENTER,
                                  space_after=12)

    def add_section_header(self, title: str):
        """Add a section header (e.g., 'Experience', 'Education')."""
        # Add a little space before section
        self._add_paragraph("", space_before=8)

        # Section header - bold, with underline effect via border
        p = self.doc.add_paragraph()
        p.style = self.doc.styles['Normal']
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(4)

        run = p.add_run(title.upper())
        self._set_font(run, font_size=11, bold=True)

        # Add bottom border for visual separation
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), '000000')
        pBdr.append(bottom)
        p._p.get_or_add_pPr().append(pBdr)

    def add_summary(self, summary: str):
        """Add professional summary section."""
        # Track for plain text
        self._content["summary"] = summary
        self._add_paragraph(summary, font_size=11, space_after=6)

    def add_core_competencies(self, competencies: List[str]):
        """Add core competencies as a formatted list or grid."""
        if not competencies:
            return

        # Track for plain text
        self._content["competencies"] = competencies

        # Format as a comma-separated list or multi-column
        competency_text = " • ".join(competencies)
        self._add_paragraph(competency_text, font_size=10, space_after=6)

    def add_experience_entry(self, company: str, title: str, location: str = "",
                            dates: str = "", overview: str = None, bullets: List[str] = None):
        """Add a single experience entry."""
        # Track for plain text
        self._content["experience"].append({
            "company": company,
            "title": title,
            "location": location,
            "dates": dates,
            "overview": overview,
            "bullets": bullets or [],
        })

        # Company and dates on same line
        p = self.doc.add_paragraph()
        p.style = self.doc.styles['Normal']
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)

        # Company name - bold
        company_run = p.add_run(company)
        self._set_font(company_run, font_size=11, bold=True)

        # Location if provided
        if location:
            loc_run = p.add_run(f", {location}")
            self._set_font(loc_run, font_size=11)

        # Dates - right aligned would be ideal but keeping simple for ATS
        if dates:
            dates_run = p.add_run(f"  |  {dates}")
            self._set_font(dates_run, font_size=11)

        # Title - italic
        if title:
            title_p = self.doc.add_paragraph()
            title_p.style = self.doc.styles['Normal']
            title_p.paragraph_format.space_before = Pt(0)
            title_p.paragraph_format.space_after = Pt(4)

            title_run = title_p.add_run(title)
            self._set_font(title_run, font_size=11, italic=True)

        # Overview paragraph if provided
        if overview:
            self._add_paragraph(f"Company Overview: {overview}", font_size=10, space_after=4)

        # Bullet points
        if bullets:
            for bullet in bullets:
                bullet_text = f"• {bullet}" if not bullet.startswith("•") else bullet
                self._add_paragraph(bullet_text, font_size=11, space_after=2)

    def add_skills(self, skills: Dict[str, Any]):
        """Add skills section - handles various formats."""
        # Track for plain text
        self._content["skills"] = skills

        if isinstance(skills, dict):
            for category, skill_list in skills.items():
                # Title case the category name
                category_title = category.title() if category else ""
                if isinstance(skill_list, list):
                    skill_text = f"{category_title}: {', '.join(skill_list)}"
                else:
                    skill_text = f"{category_title}: {skill_list}"
                self._add_paragraph(skill_text, font_size=10, space_after=2)
        elif isinstance(skills, list):
            skills_text = " • ".join(skills)
            self._add_paragraph(skills_text, font_size=10, space_after=4)
        elif isinstance(skills, str):
            self._add_paragraph(skills, font_size=10, space_after=4)

    def add_education(self, school: str, degree: str = "", details = None):
        """Add education entry."""
        # Track for plain text
        self._content["education"].append({
            "school": school,
            "degree": degree,
            "details": details,
        })

        p = self.doc.add_paragraph()
        p.style = self.doc.styles['Normal']
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)

        # School name - bold
        school_run = p.add_run(school)
        self._set_font(school_run, font_size=11, bold=True)

        # Degree
        if degree:
            degree_p = self.doc.add_paragraph()
            degree_p.style = self.doc.styles['Normal']
            degree_p.paragraph_format.space_before = Pt(0)
            degree_p.paragraph_format.space_after = Pt(2)

            degree_run = degree_p.add_run(degree)
            self._set_font(degree_run, font_size=11)

        # Additional details - ensure it's a string, not a list
        if details:
            if isinstance(details, list):
                details = ', '.join(str(d) for d in details if d)
            if details:
                self._add_paragraph(str(details), font_size=10, space_after=4)

    def to_plain_text(self) -> str:
        """
        Generate plain text representation of resume.
        This is the CANONICAL text that preview displays.
        Matches exactly what goes into the DOCX.
        """
        lines = []

        # Header
        lines.append(self._content["name"].upper())
        if self._content["tagline"]:
            lines.append(self._content["tagline"])
        if self._content["contact_parts"]:
            lines.append(" | ".join(self._content["contact_parts"]))
        lines.append("")
        lines.append("─" * 60)
        lines.append("")

        # Summary
        if self._content["summary"]:
            lines.append("SUMMARY")
            lines.append(self._content["summary"])
            lines.append("")

        # Core Competencies
        if self._content["competencies"]:
            lines.append("CORE COMPETENCIES")
            lines.append(" • ".join(self._content["competencies"]))
            lines.append("")

        # Experience
        if self._content["experience"]:
            lines.append("EXPERIENCE")
            lines.append("")
            for exp in self._content["experience"]:
                # Company line with location and dates
                company_line = exp["company"]
                if exp["location"]:
                    company_line += f", {exp['location']}"
                if exp["dates"]:
                    company_line += f"  |  {exp['dates']}"
                lines.append(company_line)

                # Title
                if exp["title"]:
                    lines.append(exp["title"])

                # Overview
                if exp["overview"]:
                    lines.append(f"Company Overview: {exp['overview']}")

                # Bullets
                for bullet in exp["bullets"]:
                    if bullet:
                        bullet_text = f"• {bullet}" if not bullet.startswith("•") else bullet
                        lines.append(bullet_text)
                lines.append("")

        # Skills
        if self._content["skills"]:
            lines.append("SKILLS")
            skills = self._content["skills"]
            if isinstance(skills, dict):
                for category, skill_list in skills.items():
                    category_title = category.title() if category else ""
                    if isinstance(skill_list, list):
                        lines.append(f"{category_title}: {', '.join(skill_list)}")
                    else:
                        lines.append(f"{category_title}: {skill_list}")
            elif isinstance(skills, list):
                lines.append(" • ".join(skills))
            else:
                lines.append(str(skills))
            lines.append("")

        # Education
        if self._content["education"]:
            lines.append("EDUCATION")
            for edu in self._content["education"]:
                if edu["school"]:
                    lines.append(edu["school"])
                if edu["degree"]:
                    lines.append(edu["degree"])
                if edu["details"]:
                    details = edu["details"]
                    if isinstance(details, list):
                        details = ", ".join(str(d) for d in details if d)
                    if details:
                        lines.append(str(details))
            lines.append("")

        return "\n".join(lines).strip()


class CoverLetterFormatter(BaseFormatter):
    """Professional cover letter formatter with ATS-safe formatting."""

    def add_header(self, name: str, tagline: str = "", contact_info: Dict[str, Any] = None):
        """Add cover letter header matching resume style."""
        # Name - large and bold, centered
        self._add_paragraph(name, font_size=18, bold=True,
                          alignment=WD_ALIGN_PARAGRAPH.CENTER)

        # Tagline
        if tagline:
            self._add_paragraph(tagline, font_size=12,
                              alignment=WD_ALIGN_PARAGRAPH.CENTER,
                              space_after=4)

        # Contact info
        if contact_info:
            contact_parts = []
            if contact_info.get('email'):
                contact_parts.append(contact_info['email'])
            if contact_info.get('phone'):
                contact_parts.append(contact_info['phone'])
            if contact_info.get('location'):
                contact_parts.append(contact_info['location'])

            if contact_parts:
                contact_text = " | ".join(contact_parts)
                self._add_paragraph(contact_text, font_size=10,
                                  alignment=WD_ALIGN_PARAGRAPH.CENTER,
                                  space_after=12)

    def add_section_label(self, label: str = "COVER LETTER"):
        """Add section label similar to resume sections."""
        # Add space before
        self._add_paragraph("", space_before=12)

        # Section label with border
        p = self.doc.add_paragraph()
        p.style = self.doc.styles['Normal']
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(12)

        run = p.add_run(label)
        self._set_font(run, font_size=11, bold=True)

        # Add bottom border
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), '000000')
        pBdr.append(bottom)
        p._p.get_or_add_pPr().append(pBdr)

    def add_salutation(self, recipient_name: Optional[str] = None):
        """Add greeting/salutation."""
        if recipient_name:
            salutation = f"Dear {recipient_name},"
        else:
            salutation = "Dear Hiring Manager,"

        self._add_paragraph(salutation, font_size=11, space_after=12)

    def add_body_paragraph(self, text: str):
        """Add a body paragraph."""
        self._add_paragraph(text, font_size=11, space_after=12)

    def add_signature(self, name: str):
        """Add closing and signature."""
        # Closing
        self._add_paragraph("Sincerely,", font_size=11, space_before=12)

        # Space for signature
        self._add_paragraph("", space_before=24)

        # Name
        self._add_paragraph(name, font_size=11)
