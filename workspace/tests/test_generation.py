"""
Test script to generate sample resume and cover letter.
Run this to verify formatting works correctly.
"""

import json
import os
from document_generator.resume_formatter import ResumeFormatter
from document_generator.cover_letter_formatter import CoverLetterFormatter


def generate_sample_resume():
    """Generate a sample resume from JSON data."""
    print("\n=== GENERATING SAMPLE RESUME ===\n")

    # Load data
    with open('examples/sample_resume_data.json', 'r') as f:
        data = json.load(f)

    # Initialize formatter
    formatter = ResumeFormatter()

    # Add header
    formatter.add_header(
        name=data['candidate']['name'],
        tagline=data['candidate']['tagline'],
        contact_info=data['candidate']['contact']
    )

    # Add summary
    formatter.add_section_header("Summary")
    formatter.add_summary(data['summary'])

    # Add core competencies
    formatter.add_section_header("Core Competencies")
    formatter.add_core_competencies(data['competencies'])

    # Add experience
    formatter.add_section_header("Experience")
    for job in data['experience']:
        formatter.add_experience_entry(
            company=job['company'],
            title=job['title'],
            location=job['location'],
            dates=job['dates'],
            overview=job.get('overview'),
            bullets=job['bullets']
        )

    # Add skills
    formatter.add_section_header("Skills")
    formatter.add_skills(data['skills'])

    # Add education
    formatter.add_section_header("Education")
    formatter.add_education(
        school=data['education']['school'],
        degree=data['education']['degree'],
        details=data['education'].get('details')
    )

    # Save
    output_path = 'outputs/test_resume.docx'
    os.makedirs('outputs', exist_ok=True)
    formatter.save(output_path)
    return output_path


def generate_sample_cover_letter():
    """Generate a sample cover letter from JSON data."""
    print("\n=== GENERATING SAMPLE COVER LETTER ===\n")

    # Load data
    with open('examples/sample_cover_letter_data.json', 'r') as f:
        data = json.load(f)

    # Initialize formatter
    formatter = CoverLetterFormatter()

    # Add header
    formatter.add_header(
        name=data['candidate']['name'],
        tagline=data['candidate']['tagline'],
        contact_info=data['candidate']['contact']
    )

    # Add section label
    formatter.add_section_label()

    # Add salutation
    formatter.add_salutation(recipient_name=data.get('recipient_name'))

    # Add body paragraphs
    for paragraph in data['paragraphs']:
        formatter.add_body_paragraph(paragraph)

    # Add signature
    formatter.add_signature(data['candidate']['name'])

    # Save
    output_path = 'outputs/test_cover_letter.docx'
    os.makedirs('outputs', exist_ok=True)
    formatter.save(output_path)
    return output_path


if __name__ == '__main__':
    print("\n" + "="*60)
    print("DOCUMENT GENERATION TEST")
    print("="*60)

    # Generate both documents
    resume_path = generate_sample_resume()
    cover_letter_path = generate_sample_cover_letter()

    print("\n" + "="*60)
    print("✓ GENERATION COMPLETE")
    print("="*60)
    print(f"\nResume: {resume_path}")
    print(f"Cover Letter: {cover_letter_path}")
    print("\nOpen these files to verify formatting matches templates exactly.\n")
