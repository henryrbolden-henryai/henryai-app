"""
Resume formatter that generates DOCX files matching the exact template specification.
Every formatting value comes from styles.py.
"""

from docx import Document
from docx.shared import Pt, Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from . import styles
from .utils import add_paragraph_border, format_date_range, validate_contact_info


class ResumeFormatter:
    """Generates formatted resume documents."""

    def __init__(self):
        """Initialize document with default settings."""
        self.doc = Document()
        self._setup_document()

    def _setup_document(self):
        """Configure page settings and margins."""
        sections = self.doc.sections
        for section in sections:
            section.page_height = styles.PAGE_HEIGHT
            section.page_width = styles.PAGE_WIDTH
            section.top_margin = styles.RESUME_MARGIN_TOP
            section.bottom_margin = styles.RESUME_MARGIN_BOTTOM
            section.left_margin = styles.RESUME_MARGIN_LEFT
            section.right_margin = styles.RESUME_MARGIN_RIGHT

    def add_header(self, name, tagline, contact_info):
        """
        Add resume header with name, tagline, and contact info.

        Args:
            name (str): Full name (will be uppercased)
            tagline (str): Role/specialization
            contact_info (dict): {phone, email, linkedin, location}
        """
        contact_info = validate_contact_info(contact_info)

        # Name - centered, bold, 18pt
        name_para = self.doc.add_paragraph()
        name_para.alignment = styles.ALIGN_CENTER
        name_run = name_para.add_run(name.upper())
        name_run.font.size = styles.FONT_SIZE_RESUME_NAME
        name_run.font.bold = True
        name_run.font.name = styles.FONT_FAMILY
        name_run.font.color.rgb = styles.COLOR_BLACK
        name_para.paragraph_format.space_after = styles.SPACING_AFTER_NAME

        # Tagline - centered, 11pt, dark gray
        tagline_para = self.doc.add_paragraph()
        tagline_para.alignment = styles.ALIGN_CENTER
        tagline_run = tagline_para.add_run(tagline)
        tagline_run.font.size = styles.FONT_SIZE_RESUME_TAGLINE
        tagline_run.font.name = styles.FONT_FAMILY
        tagline_run.font.color.rgb = styles.COLOR_DARK_GRAY
        tagline_para.paragraph_format.space_after = styles.SPACING_AFTER_TAGLINE

        # Contact info - centered, 9pt, bullet-separated
        contact_para = self.doc.add_paragraph()
        contact_para.alignment = styles.ALIGN_CENTER
        contact_parts = [v for v in [
            contact_info['phone'],
            contact_info['email'],
            contact_info['linkedin'],
            contact_info['location']
        ] if v]
        contact_text = " • ".join(contact_parts)
        contact_run = contact_para.add_run(contact_text)
        contact_run.font.size = styles.FONT_SIZE_RESUME_CONTACT
        contact_run.font.name = styles.FONT_FAMILY
        contact_run.font.color.rgb = styles.COLOR_BLACK
        contact_para.paragraph_format.space_after = styles.SPACING_AFTER_CONTACT

        # Add bottom border (1pt solid line)
        add_paragraph_border(contact_para, bottom=True, bottom_width=styles.BORDER_THIN)

    def add_section_header(self, title):
        """
        Add section header (SUMMARY, EXPERIENCE, etc.) with borders.

        Args:
            title (str): Section name (will be uppercased)
        """
        header_para = self.doc.add_paragraph()
        header_para.alignment = styles.ALIGN_LEFT
        header_run = header_para.add_run(title.upper())
        header_run.font.size = styles.FONT_SIZE_SECTION_HEADER
        header_run.font.bold = True
        header_run.font.name = styles.FONT_FAMILY
        header_run.font.color.rgb = styles.COLOR_BLACK

        # Add top (2pt) and bottom (1pt) borders
        add_paragraph_border(
            header_para,
            top=True,
            bottom=True,
            top_width=styles.BORDER_THICK,
            bottom_width=styles.BORDER_THIN
        )

        header_para.paragraph_format.space_before = styles.SPACING_BEFORE_SECTION_HEADER
        header_para.paragraph_format.space_after = styles.SPACING_AFTER_SECTION_HEADER

    def add_summary(self, text):
        """
        Add summary paragraph (justified alignment).

        Args:
            text (str): Summary text
        """
        summary_para = self.doc.add_paragraph()
        summary_para.alignment = styles.ALIGN_JUSTIFY
        summary_run = summary_para.add_run(text)
        summary_run.font.size = styles.FONT_SIZE_DEFAULT
        summary_run.font.name = styles.FONT_FAMILY
        summary_run.font.color.rgb = styles.COLOR_BLACK
        summary_para.paragraph_format.space_after = styles.SPACING_AFTER_SUMMARY

    def add_core_competencies(self, competencies):
        """
        Add core competencies as 3-column layout with checkmarks.

        Args:
            competencies (list): List of competency strings
        """
        # Calculate rows needed for 3-column layout
        rows_needed = (len(competencies) + 2) // 3

        # Create table
        table = self.doc.add_table(rows=rows_needed, cols=3)

        # Remove all borders and set cell properties
        for row in table.rows:
            for cell in row.cells:
                # Remove borders
                tc = cell._element
                tcPr = tc.get_or_add_tcPr()
                tcBorders = OxmlElement('w:tcBorders')
                for border_name in ['top', 'left', 'bottom', 'right']:
                    border = OxmlElement(f'w:{border_name}')
                    border.set(qn('w:val'), 'nil')
                    tcBorders.append(border)
                tcPr.append(tcBorders)

        # Fill cells with competencies
        for i, comp in enumerate(competencies):
            row_idx = i // 3
            col_idx = i % 3
            cell = table.rows[row_idx].cells[col_idx]

            cell_para = cell.paragraphs[0]
            # Add hanging indent so text wraps under text, not under checkmark
            cell_para.paragraph_format.left_indent = Pt(12)  # Indent for the checkmark
            cell_para.paragraph_format.first_line_indent = Pt(-12)  # Negative indent for first line (checkmark)

            # Add checkmark
            check_run = cell_para.add_run("✓ ")
            check_run.font.size = styles.FONT_SIZE_DEFAULT
            check_run.font.name = styles.FONT_FAMILY

            # Add competency text
            comp_run = cell_para.add_run(comp)
            comp_run.font.size = styles.FONT_SIZE_DEFAULT
            comp_run.font.name = styles.FONT_FAMILY
            comp_run.font.color.rgb = styles.COLOR_BLACK

    def add_experience_entry(self, company, title, location, dates, overview=None, bullets=None):
        """
        Add a job entry in Experience section.

        Args:
            company (str): Company name
            title (str): Job title
            location (str): City, STATE
            dates (str): YYYY - YYYY
            overview (str): Company overview text (optional)
            bullets (list): List of bullet point strings
        """
        if bullets is None:
            bullets = []

        # Create 2-row table for proper layout:
        # Row 1: Company (left) | Location (right)
        # Row 2: Job Title (left) | Dates (right)
        company_table = self.doc.add_table(rows=2, cols=2)
        company_table.autofit = False
        company_table.allow_autofit = False

        # Remove borders from all cells
        for row in company_table.rows:
            for cell in row.cells:
                tc = cell._element
                tcPr = tc.get_or_add_tcPr()
                tcBorders = OxmlElement('w:tcBorders')
                for border_name in ['top', 'left', 'bottom', 'right']:
                    border = OxmlElement(f'w:{border_name}')
                    border.set(qn('w:val'), 'nil')
                    tcBorders.append(border)
                tcPr.append(tcBorders)

        # Row 1, Left cell: Company name (bold, 11pt)
        company_cell = company_table.rows[0].cells[0]
        company_para = company_cell.paragraphs[0]
        company_para.paragraph_format.space_after = Pt(0)  # Remove spacing after company
        company_run = company_para.add_run(company)
        company_run.font.size = styles.FONT_SIZE_COMPANY
        company_run.font.bold = True
        company_run.font.name = styles.FONT_FAMILY
        company_run.font.color.rgb = styles.COLOR_BLACK

        # Row 1, Right cell: Location (right-aligned, gray)
        location_cell = company_table.rows[0].cells[1]
        location_para = location_cell.paragraphs[0]
        location_para.alignment = styles.ALIGN_RIGHT
        if location:
            location_run = location_para.add_run(location)
            location_run.font.size = styles.FONT_SIZE_DEFAULT
            location_run.font.name = styles.FONT_FAMILY
            location_run.font.color.rgb = styles.COLOR_DARK_GRAY

        # Row 2, Left cell: Job title (bold, 10pt)
        title_cell = company_table.rows[1].cells[0]
        title_para = title_cell.paragraphs[0]
        title_para.paragraph_format.space_before = Pt(0)  # Remove spacing between rows
        title_run = title_para.add_run(title)
        title_run.font.size = styles.FONT_SIZE_JOB_TITLE
        title_run.font.bold = True
        title_run.font.name = styles.FONT_FAMILY
        title_run.font.color.rgb = styles.COLOR_BLACK

        # Row 2, Right cell: Dates (right-aligned, gray)
        dates_cell = company_table.rows[1].cells[1]
        dates_para = dates_cell.paragraphs[0]
        dates_para.alignment = styles.ALIGN_RIGHT
        dates_para.paragraph_format.space_before = Pt(0)  # Single-spaced
        dates_run = dates_para.add_run(dates)
        dates_run.font.size = styles.FONT_SIZE_DEFAULT
        dates_run.font.name = styles.FONT_FAMILY
        dates_run.font.color.rgb = styles.COLOR_DARK_GRAY

        # Company overview (italic, gray, same size as other details)
        if overview:
            overview_para = self.doc.add_paragraph()
            overview_para.alignment = styles.ALIGN_LEFT
            overview_run = overview_para.add_run(f"Company Overview: {overview}")
            overview_run.font.size = styles.FONT_SIZE_DEFAULT  # Same as location/dates
            overview_run.font.italic = True
            overview_run.font.name = styles.FONT_FAMILY
            overview_run.font.color.rgb = styles.COLOR_DARK_GRAY
            overview_para.paragraph_format.space_before = Pt(0)  # Single-spaced
            overview_para.paragraph_format.space_after = Pt(6)  # Add space before bullets

        # Bullets (left-aligned with hanging indent)
        for i, bullet in enumerate(bullets):
            bullet_para = self.doc.add_paragraph()
            bullet_para.alignment = styles.ALIGN_LEFT
            # Bullet at 0.0", text starts at 0.25", wrapped text aligns at 0.25"
            bullet_para.paragraph_format.left_indent = Inches(0.25)  # Where all text (including wrapped) starts
            bullet_para.paragraph_format.first_line_indent = Inches(-0.25)  # Pulls first line (bullet) back to 0.0"
            # Use tab after bullet to ensure text starts exactly at 0.25"
            bullet_run = bullet_para.add_run("•\t" + bullet)
            bullet_run.font.size = styles.FONT_SIZE_DEFAULT
            bullet_run.font.name = styles.FONT_FAMILY
            bullet_run.font.color.rgb = styles.COLOR_BLACK
            bullet_para.paragraph_format.space_after = styles.SPACING_BETWEEN_BULLETS
            # Add extra spacing after the last bullet to separate jobs
            if i == len(bullets) - 1:
                bullet_para.paragraph_format.space_after = styles.SPACING_BETWEEN_JOBS

    def add_skills(self, skills_dict):
        """
        Add skills section with category headers.

        Args:
            skills_dict (dict): {"Category": ["skill1", "skill2", ...]}
        """
        for category, skills_list in skills_dict.items():
            skills_para = self.doc.add_paragraph()

            # Category header (bold)
            category_run = skills_para.add_run(f"{category}: ")
            category_run.font.size = styles.FONT_SIZE_DEFAULT
            category_run.font.bold = True
            category_run.font.name = styles.FONT_FAMILY
            category_run.font.color.rgb = styles.COLOR_BLACK

            # Skills (bullet-separated)
            skills_text = " • ".join(skills_list)
            skills_run = skills_para.add_run(skills_text)
            skills_run.font.size = styles.FONT_SIZE_DEFAULT
            skills_run.font.name = styles.FONT_FAMILY
            skills_run.font.color.rgb = styles.COLOR_BLACK
            skills_para.paragraph_format.space_after = Pt(6)

    def add_education(self, school, degree, details=None):
        """
        Add education entry.

        Args:
            school (str): School name (institution)
            degree (str): Degree type and major
            details (list): Optional list of detail strings (e.g., concentration, honors)
        """
        # Line 1: Degree type and major (regular, 10pt)
        if degree and degree.strip():
            degree_para = self.doc.add_paragraph()
            degree_para.alignment = styles.ALIGN_LEFT
            degree_run = degree_para.add_run(degree)
            degree_run.font.size = styles.FONT_SIZE_DEFAULT
            degree_run.font.name = styles.FONT_FAMILY
            degree_run.font.color.rgb = styles.COLOR_BLACK
            degree_para.paragraph_format.space_after = Pt(0)  # Single-spaced

        # Line 2: Institution/School name (bold, 10pt)
        if school and school.strip():
            school_para = self.doc.add_paragraph()
            school_para.alignment = styles.ALIGN_LEFT
            school_run = school_para.add_run(school)
            school_run.font.size = styles.FONT_SIZE_DEFAULT
            school_run.font.bold = True
            school_run.font.name = styles.FONT_FAMILY
            school_run.font.color.rgb = styles.COLOR_BLACK
            school_para.paragraph_format.space_after = Pt(0)  # Single-spaced

        # Line 3+: Details like concentration (regular, 10pt)
        if details:
            for detail in details:
                if detail and str(detail).strip():
                    detail_para = self.doc.add_paragraph()
                    detail_para.alignment = styles.ALIGN_LEFT
                    detail_run = detail_para.add_run(detail)
                    detail_run.font.size = styles.FONT_SIZE_DEFAULT
                    detail_run.font.name = styles.FONT_FAMILY
                    detail_run.font.color.rgb = styles.COLOR_BLACK
                    detail_para.paragraph_format.space_after = Pt(0)

    def save(self, filepath):
        """
        Save document to file.

        Args:
            filepath (str): Output path
        """
        self.doc.save(filepath)
        print(f"✓ Resume saved to: {filepath}")

    def get_document(self):
        """Return the document object for further processing."""
        return self.doc
