"""
Utility functions for document generation.
"""

from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def add_paragraph_border(paragraph, top=False, bottom=False, top_width=16, bottom_width=8):
    """
    Add border to a paragraph.

    Args:
        paragraph: docx paragraph object
        top (bool): Add top border
        bottom (bool): Add bottom border
        top_width (int): Border width in eighths of a point (16 = 2pt)
        bottom_width (int): Border width in eighths of a point (8 = 1pt)
    """
    pPr = paragraph._element.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')

    if top:
        top_border = OxmlElement('w:top')
        top_border.set(qn('w:val'), 'single')
        top_border.set(qn('w:sz'), str(top_width))
        top_border.set(qn('w:space'), '1')
        top_border.set(qn('w:color'), '000000')
        pBdr.append(top_border)

    if bottom:
        bottom_border = OxmlElement('w:bottom')
        bottom_border.set(qn('w:val'), 'single')
        bottom_border.set(qn('w:sz'), str(bottom_width))
        bottom_border.set(qn('w:space'), '1')
        bottom_border.set(qn('w:color'), '000000')
        pBdr.append(bottom_border)

    pPr.append(pBdr)


def format_date_range(start_date, end_date):
    """
    Format date range as 'YYYY - YYYY' or 'YYYY - Present'.

    Args:
        start_date (str): Start year (e.g., "2023")
        end_date (str): End year or "Present"

    Returns:
        str: Formatted date range
    """
    if not end_date or end_date.lower() in ['present', 'current']:
        return f"{start_date} - Present"
    return f"{start_date} - {end_date}"


def validate_contact_info(contact_info):
    """
    Validate required contact info fields.

    Args:
        contact_info (dict): Contact information

    Returns:
        dict: Validated contact info (fills missing with empty strings)
    """
    required_fields = ['phone', 'email', 'linkedin', 'location']
    validated = {}

    for field in required_fields:
        validated[field] = contact_info.get(field, '')

    return validated


def create_table_cell_border_none():
    """Create XML element to remove table cell borders."""
    tcPr = OxmlElement('w:tcPr')
    tcBorders = OxmlElement('w:tcBorders')

    for border_name in ['top', 'left', 'bottom', 'right']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'nil')
        tcBorders.append(border)

    tcPr.append(tcBorders)
    return tcBorders
