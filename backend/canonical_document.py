"""
Canonical Document System

The resume and cover letter are generated ONCE, stored once, rendered once,
and exported once. No reassembly. No regeneration.

This module defines the canonical document schema and validation.
"""

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


# ============================================================================
# CANONICAL DOCUMENT SCHEMA
# ============================================================================

@dataclass
class ContactInfo:
    """Contact information - all fields required for download integrity."""
    name: str
    email: str
    phone: str = ""
    location: str = ""
    linkedin: str = ""

    def is_valid(self) -> bool:
        """Contact is valid if name and email are present."""
        return bool(self.name and self.name.strip()) and bool(self.email and self.email.strip())

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "linkedin": self.linkedin,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContactInfo":
        return cls(
            name=str(data.get("name", "") or ""),
            email=str(data.get("email", "") or ""),
            phone=str(data.get("phone", "") or ""),
            location=str(data.get("location", "") or ""),
            linkedin=str(data.get("linkedin", "") or ""),
        )


@dataclass
class ExperienceEntry:
    """A single job experience entry."""
    company: str
    title: str
    dates: str
    location: str = ""
    overview: str = ""
    bullets: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company": self.company,
            "title": self.title,
            "dates": self.dates,
            "location": self.location,
            "overview": self.overview,
            "bullets": self.bullets,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperienceEntry":
        return cls(
            company=str(data.get("company", "") or ""),
            title=str(data.get("title", "") or ""),
            dates=str(data.get("dates", "") or ""),
            location=str(data.get("location", "") or ""),
            overview=str(data.get("overview", "") or ""),
            bullets=list(data.get("bullets", []) or []),
        )


@dataclass
class Education:
    """Education entry."""
    school: str
    degree: str
    details: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {
            "school": self.school,
            "degree": self.degree,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Education":
        details = data.get("details", "") or ""
        if isinstance(details, list):
            details = ", ".join(details)
        return cls(
            school=str(data.get("school", "") or ""),
            degree=str(data.get("degree", "") or ""),
            details=str(details),
        )


@dataclass
class CanonicalResume:
    """The canonical resume document - single source of truth."""
    contact: ContactInfo
    tagline: str
    summary: str
    experience: List[ExperienceEntry]
    skills: Dict[str, List[str]]
    education: Education
    competencies: List[str] = field(default_factory=list)
    ats_keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contact": self.contact.to_dict(),
            "tagline": self.tagline,
            "summary": self.summary,
            "experience": [e.to_dict() for e in self.experience],
            "skills": self.skills,
            "education": self.education.to_dict(),
            "competencies": self.competencies,
            "ats_keywords": self.ats_keywords,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CanonicalResume":
        return cls(
            contact=ContactInfo.from_dict(data.get("contact", {})),
            tagline=str(data.get("tagline", "") or ""),
            summary=str(data.get("summary", "") or ""),
            experience=[ExperienceEntry.from_dict(e) for e in data.get("experience", [])],
            skills=data.get("skills", {}),
            education=Education.from_dict(data.get("education", {})),
            competencies=list(data.get("competencies", []) or []),
            ats_keywords=list(data.get("ats_keywords", []) or []),
        )

    def _build_formatter(self):
        """
        Build a ResumeFormatter populated with canonical data.
        Shared by to_full_text(), to_html(), and DOCX generation.
        """
        from document_generator import ResumeFormatter

        formatter = ResumeFormatter()

        # Add header
        formatter.add_header(
            name=self.contact.name,
            tagline=self.tagline,
            contact_info={
                "phone": self.contact.phone,
                "email": self.contact.email,
                "linkedin": self.contact.linkedin,
                "location": self.contact.location,
            }
        )

        # Add summary
        if self.summary:
            formatter.add_section_header("Summary")
            formatter.add_summary(self.summary)

        # Add core competencies
        if self.competencies:
            formatter.add_section_header("Core Competencies")
            formatter.add_core_competencies(self.competencies)

        # Add experience
        if self.experience:
            formatter.add_section_header("Experience")
            for exp in self.experience:
                formatter.add_experience_entry(
                    company=exp.company,
                    title=exp.title,
                    location=exp.location,
                    dates=exp.dates,
                    overview=exp.overview,
                    bullets=exp.bullets,
                )

        # Add skills
        if self.skills:
            formatter.add_section_header("Skills")
            formatter.add_skills(self.skills)

        # Add education
        if self.education.school or self.education.degree:
            formatter.add_section_header("Education")
            formatter.add_education(
                school=self.education.school,
                degree=self.education.degree,
                details=self.education.details,
            )

        return formatter

    def to_full_text(self) -> str:
        """
        Generate the full text representation for preview and hash computation.
        Uses ResumeFormatter to ensure preview === download.
        """
        return self._build_formatter().to_plain_text()

    def to_html(self) -> str:
        """
        Generate styled HTML preview that visually mirrors the DOCX output.
        Uses the same ResumeFormatter and canonical data as to_full_text().
        """
        return self._build_formatter().to_html()


@dataclass
class CanonicalCoverLetter:
    """The canonical cover letter - single source of truth."""
    contact: ContactInfo
    tagline: str
    recipient_name: str = ""
    recipient_title: str = ""
    company_name: str = ""
    paragraphs: List[str] = field(default_factory=list)
    full_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contact": self.contact.to_dict(),
            "tagline": self.tagline,
            "recipient_name": self.recipient_name,
            "recipient_title": self.recipient_title,
            "company_name": self.company_name,
            "paragraphs": self.paragraphs,
            "full_text": self.full_text,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CanonicalCoverLetter":
        return cls(
            contact=ContactInfo.from_dict(data.get("contact", {})),
            tagline=str(data.get("tagline", "") or ""),
            recipient_name=str(data.get("recipient_name", "") or ""),
            recipient_title=str(data.get("recipient_title", "") or ""),
            company_name=str(data.get("company_name", "") or ""),
            paragraphs=list(data.get("paragraphs", []) or []),
            full_text=str(data.get("full_text", "") or ""),
        )


@dataclass
class FitScoreDelta:
    """
    Tracks the fit score improvement from original resume to canonical document.

    This is NOT a re-analysis - it's showing the delta caused by approved changes.
    """
    original_score: int  # Score from initial analysis
    final_score: int  # Score after strengthening/tailoring
    original_verdict: str  # "Do Not Apply", "Conditional Apply", "Apply"
    final_verdict: str
    improvement_summary: str  # One sentence explaining what improved
    score_locked: bool = False  # True after user clicks Approve & Download
    locked_at: Optional[str] = None

    @property
    def delta(self) -> int:
        return self.final_score - self.original_score

    @property
    def improved(self) -> bool:
        return self.delta > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_score": self.original_score,
            "final_score": self.final_score,
            "delta": self.delta,
            "improved": self.improved,
            "original_verdict": self.original_verdict,
            "final_verdict": self.final_verdict,
            "improvement_summary": self.improvement_summary,
            "score_locked": self.score_locked,
            "locked_at": self.locked_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FitScoreDelta":
        return cls(
            original_score=data.get("original_score", 0),
            final_score=data.get("final_score", 0),
            original_verdict=data.get("original_verdict", ""),
            final_verdict=data.get("final_verdict", ""),
            improvement_summary=data.get("improvement_summary", ""),
            score_locked=data.get("score_locked", False),
            locked_at=data.get("locked_at"),
        )


@dataclass
class DocumentMetadata:
    """Metadata for document integrity verification."""
    generated_at: str
    source_resume_hash: str
    jd_hash: str
    version: str = "1.0"
    content_hash: str = ""
    fit_score_delta: Optional[FitScoreDelta] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "generated_at": self.generated_at,
            "source_resume_hash": self.source_resume_hash,
            "jd_hash": self.jd_hash,
            "version": self.version,
            "content_hash": self.content_hash,
        }
        if self.fit_score_delta:
            result["fit_score_delta"] = self.fit_score_delta.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentMetadata":
        fit_score_delta = None
        if data.get("fit_score_delta"):
            fit_score_delta = FitScoreDelta.from_dict(data["fit_score_delta"])
        return cls(
            generated_at=data.get("generated_at", ""),
            source_resume_hash=data.get("source_resume_hash", ""),
            jd_hash=data.get("jd_hash", ""),
            version=data.get("version", "1.0"),
            content_hash=data.get("content_hash", ""),
            fit_score_delta=fit_score_delta,
        )


@dataclass
class CanonicalDocument:
    """
    The complete canonical document object.

    This is the ONLY source for preview and download.
    No reassembly. No regeneration.
    """
    resume: CanonicalResume
    cover_letter: CanonicalCoverLetter
    metadata: DocumentMetadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resume": self.resume.to_dict(),
            "cover_letter": self.cover_letter.to_dict(),
            "metadata": self.metadata.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CanonicalDocument":
        metadata_dict = data.get("metadata", {
            "generated_at": datetime.now().isoformat(),
            "source_resume_hash": "",
            "jd_hash": "",
        })
        return cls(
            resume=CanonicalResume.from_dict(data.get("resume", {})),
            cover_letter=CanonicalCoverLetter.from_dict(data.get("cover_letter", {})),
            metadata=DocumentMetadata.from_dict(metadata_dict),
        )

    def compute_content_hash(self) -> str:
        """Compute a hash of the document content for integrity verification."""
        content = (
            self.resume.to_full_text() +
            self.cover_letter.full_text
        )
        return hashlib.sha256(content.encode()).hexdigest()[:16]


# ============================================================================
# DOCUMENT INTEGRITY CHECKS
# ============================================================================

class IntegrityIssue(Enum):
    MISSING_NAME = "missing_name"
    MISSING_EMAIL = "missing_email"
    MISSING_EXPERIENCE = "missing_experience"
    MISSING_SUMMARY = "missing_summary"
    KEYWORD_STUFFING = "keyword_stuffing"
    EMPTY_BULLETS = "empty_bullets"
    HASH_MISMATCH = "hash_mismatch"


@dataclass
class IntegrityCheckResult:
    """Result of document integrity check."""
    passed: bool
    issues: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "issues": self.issues,
            "warnings": self.warnings,
        }


def check_document_integrity(
    doc: CanonicalDocument,
    max_keyword_occurrences: int = 4
) -> IntegrityCheckResult:
    """
    Run integrity checks on a canonical document.

    Checks:
    - Contact info present (name, email required)
    - Experience section not empty
    - Summary present
    - Keyword frequency within limits
    - No empty bullets

    Returns IntegrityCheckResult with passed flag and any issues.
    """
    issues = []
    warnings = []

    # Check contact info
    if not doc.resume.contact.name or not doc.resume.contact.name.strip():
        issues.append({
            "type": IntegrityIssue.MISSING_NAME.value,
            "message": "Candidate name is missing from contact information",
            "fix": "Add your full name to complete the document",
        })

    if not doc.resume.contact.email or not doc.resume.contact.email.strip():
        issues.append({
            "type": IntegrityIssue.MISSING_EMAIL.value,
            "message": "Email address is missing from contact information",
            "fix": "Add your email address to complete the document",
        })

    # Check experience
    if not doc.resume.experience:
        issues.append({
            "type": IntegrityIssue.MISSING_EXPERIENCE.value,
            "message": "No work experience found in resume",
            "fix": "Add at least one work experience entry",
        })

    # Check summary
    if not doc.resume.summary or not doc.resume.summary.strip():
        warnings.append("Professional summary is empty - consider adding one")

    # Check for empty bullets
    empty_bullet_count = 0
    for exp in doc.resume.experience:
        for bullet in exp.bullets:
            if not bullet or not bullet.strip():
                empty_bullet_count += 1

    if empty_bullet_count > 0:
        issues.append({
            "type": IntegrityIssue.EMPTY_BULLETS.value,
            "message": f"Found {empty_bullet_count} empty bullet point(s)",
            "fix": "Remove or fill in empty bullet points",
        })

    # Check keyword frequency
    keyword_issues = check_keyword_frequency(doc.resume, max_keyword_occurrences)
    if keyword_issues:
        issues.append({
            "type": IntegrityIssue.KEYWORD_STUFFING.value,
            "message": f"Keywords overused: {', '.join(keyword_issues)}",
            "fix": "Keyword frequency has been normalized",
        })

    return IntegrityCheckResult(
        passed=len(issues) == 0,
        issues=issues,
        warnings=warnings,
    )


def check_keyword_frequency(
    resume: CanonicalResume,
    max_occurrences: int = 4
) -> List[str]:
    """
    Check for keyword stuffing.

    Returns list of keywords that appear more than max_occurrences times.
    """
    # Combine all text content
    all_text = resume.summary + " "
    for exp in resume.experience:
        all_text += " ".join(exp.bullets) + " "

    all_text = all_text.lower()

    # Check each ATS keyword
    overused = []
    for keyword in resume.ats_keywords:
        keyword_lower = keyword.lower()
        # Count occurrences (word boundary matching)
        pattern = r'\b' + re.escape(keyword_lower) + r'\b'
        count = len(re.findall(pattern, all_text))
        if count > max_occurrences:
            overused.append(f"{keyword} ({count}x)")

    return overused


# ============================================================================
# KEYWORD DEDUPLICATION
# ============================================================================

def deduplicate_keywords(
    resume: CanonicalResume,
    max_occurrences: int = 3
) -> CanonicalResume:
    """
    Deduplicate keywords in resume to prevent ATS penalties.

    For each keyword that appears more than max_occurrences times,
    we replace excess occurrences with contextual alternatives or remove them.
    """
    import copy
    result = copy.deepcopy(resume)

    # Track keyword occurrences
    keyword_counts: Dict[str, int] = {kw.lower(): 0 for kw in resume.ats_keywords}

    # Process summary
    result.summary = _dedupe_text(result.summary, keyword_counts, max_occurrences)

    # Process experience bullets
    for exp in result.experience:
        new_bullets = []
        for bullet in exp.bullets:
            deduped = _dedupe_text(bullet, keyword_counts, max_occurrences)
            new_bullets.append(deduped)
        exp.bullets = new_bullets

    return result


def _dedupe_text(text: str, keyword_counts: Dict[str, int], max_occ: int) -> str:
    """Deduplicate keywords in a single text block."""
    result = text

    for keyword in keyword_counts.keys():
        pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)

        def replace_if_over(match):
            keyword_counts[keyword] += 1
            if keyword_counts[keyword] > max_occ:
                # Replace with empty or contextual alternative
                # For now, just remove the excess (keep sentence structure)
                return ""
            return match.group(0)

        result = pattern.sub(replace_if_over, result)

    # Clean up double spaces and trailing punctuation issues
    result = re.sub(r'\s+', ' ', result).strip()
    result = re.sub(r'\s+([,.])', r'\1', result)

    return result


# ============================================================================
# DOCUMENT ASSEMBLY FROM GENERATION OUTPUT
# ============================================================================

def calculate_fit_score_delta(
    original_score: int,
    original_verdict: str,
    canonical_resume: CanonicalResume,
    jd_keywords: List[str],
) -> FitScoreDelta:
    """
    Calculate the fit score delta based on canonical resume improvements.

    This uses the SAME scoring logic as initial analysis, just with
    the improved resume content. No new weights, no new logic.

    Args:
        original_score: The initial fit score from JD analysis
        original_verdict: The initial verdict (Do Not Apply, Conditional Apply, Apply)
        canonical_resume: The improved/tailored resume
        jd_keywords: Keywords from the job description

    Returns:
        FitScoreDelta with before/after comparison
    """
    # Calculate keyword coverage in canonical resume
    resume_text = canonical_resume.summary.lower() + " "
    for exp in canonical_resume.experience:
        resume_text += " ".join(exp.bullets).lower() + " "

    # Count keyword matches
    keywords_found = 0
    for keyword in jd_keywords:
        if keyword.lower() in resume_text:
            keywords_found += 1

    keyword_coverage = (keywords_found / len(jd_keywords) * 100) if jd_keywords else 100

    # Score boost based on improvements:
    # - Keyword coverage improvement
    # - Quantified bullets (metrics present)
    # - Clear scope indicators

    # Count quantified bullets
    quantified_count = 0
    total_bullets = 0
    for exp in canonical_resume.experience:
        for bullet in exp.bullets:
            total_bullets += 1
            if any(char.isdigit() for char in bullet):
                quantified_count += 1

    quantification_rate = (quantified_count / total_bullets * 100) if total_bullets > 0 else 0

    # Calculate final score (same formula as initial, but with improved content)
    # Base: keyword coverage * 0.6 + quantification * 0.2 + competency match * 0.2
    final_score = int(
        keyword_coverage * 0.6 +
        quantification_rate * 0.25 +
        min(len(canonical_resume.competencies), 6) / 6 * 15  # Up to 15 points for competencies
    )

    # Cap at 95 and floor at original
    final_score = max(original_score, min(95, final_score))

    # Determine verdict
    if final_score >= 80:
        final_verdict = "Apply"
    elif final_score >= 60:
        final_verdict = "Conditional Apply"
    else:
        final_verdict = "Do Not Apply"

    # Generate improvement summary
    delta = final_score - original_score
    if delta > 0:
        improvements = []
        if keyword_coverage > 70:
            improvements.append("better keyword alignment")
        if quantification_rate > 50:
            improvements.append("stronger metrics")
        if len(canonical_resume.competencies) >= 4:
            improvements.append("clearer competencies")

        if improvements:
            improvement_summary = f"Improved by {', '.join(improvements)}."
        else:
            improvement_summary = "Improved through tailoring and clarity."
    elif delta == 0:
        improvement_summary = "Your fit score didn't change, but your resume is clearer and safer for screening."
    else:
        improvement_summary = "Score adjusted based on content changes."

    return FitScoreDelta(
        original_score=original_score,
        final_score=final_score,
        original_verdict=original_verdict,
        final_verdict=final_verdict,
        improvement_summary=improvement_summary,
    )


def assemble_canonical_document(
    generation_output: Dict[str, Any],
    source_resume: Dict[str, Any],
    job_description: str,
    contact_info: Dict[str, Any],
    original_fit_score: Optional[int] = None,
    original_verdict: Optional[str] = None,
    jd_keywords: Optional[List[str]] = None,
) -> CanonicalDocument:
    """
    Assemble a canonical document from generation output.

    This is the ONLY place where document assembly happens.
    After this point, no reconstruction is allowed.

    Args:
        generation_output: The output from document generation (Claude response)
        source_resume: The original parsed resume
        job_description: The job description text
        contact_info: Contact information (name, email, phone, etc.)
        original_fit_score: The initial fit score from JD analysis (optional)
        original_verdict: The initial verdict (optional)
        jd_keywords: Keywords from JD for delta calculation (optional)

    Returns:
        CanonicalDocument: The single source of truth
    """
    resume_output = generation_output.get("resume_output", {})
    cover_letter_output = generation_output.get("cover_letter", {})

    # Build contact
    contact = ContactInfo(
        name=str(contact_info.get("name", "") or ""),
        email=str(contact_info.get("email", "") or ""),
        phone=str(contact_info.get("phone", "") or ""),
        location=str(contact_info.get("location", "") or ""),
        linkedin=str(contact_info.get("linkedin", "") or ""),
    )

    # Build experience from generation output (STRATEGIC order already applied)
    experience_sections = resume_output.get("experience_sections", [])
    experience = [ExperienceEntry.from_dict(e) for e in experience_sections]

    # Build skills
    skills_data = resume_output.get("skills", {})
    if isinstance(skills_data, list):
        skills = {"Skills": skills_data}
    elif isinstance(skills_data, dict):
        skills = {k: (v if isinstance(v, list) else [v]) for k, v in skills_data.items()}
    else:
        skills = {}

    # Build education — try generated output first, fall back to source resume
    # Claude's generation includes education as a list of dicts
    edu_data = None
    gen_education = resume_output.get("education", [])
    if isinstance(gen_education, list) and gen_education:
        first = gen_education[0]
        if isinstance(first, dict) and (first.get("institution") or first.get("school") or first.get("degree")):
            # Map "institution" -> "school" for Education.from_dict compatibility
            if "institution" in first and "school" not in first:
                first["school"] = first["institution"]
            edu_data = first

    # Fall back to source resume education if generation didn't include it
    if not edu_data:
        edu_data = source_resume.get("education", {})

    # Parse education from whatever format we got
    if isinstance(edu_data, str) and edu_data.strip():
        education = Education(school=edu_data.strip(), degree="", details="")
    elif isinstance(edu_data, list) and edu_data:
        edu_data = edu_data[0]
        education = Education.from_dict(edu_data) if isinstance(edu_data, dict) else Education(str(edu_data), "", "")
    elif isinstance(edu_data, dict):
        education = Education.from_dict(edu_data)
    else:
        education = Education("", "", "")

    # Build resume
    resume = CanonicalResume(
        contact=contact,
        tagline=str(resume_output.get("headline", "") or ""),
        summary=str(resume_output.get("summary", "") or ""),
        experience=experience,
        skills=skills,
        education=education,
        competencies=list(resume_output.get("core_competencies", []) or []),
        ats_keywords=list(resume_output.get("ats_keywords", []) or []),
    )

    # Deduplicate keywords
    resume = deduplicate_keywords(resume, max_occurrences=3)

    # Build cover letter
    cover_letter = CanonicalCoverLetter(
        contact=contact,
        tagline=resume.tagline,
        company_name=str(generation_output.get("company_name", "") or ""),
        full_text=str(cover_letter_output.get("full_text", "") or ""),
        paragraphs=list(cover_letter_output.get("paragraphs", []) or []),
    )

    # Calculate fit score delta if original score provided
    fit_score_delta = None
    if original_fit_score is not None and jd_keywords:
        fit_score_delta = calculate_fit_score_delta(
            original_score=original_fit_score,
            original_verdict=original_verdict or "Conditional Apply",
            canonical_resume=resume,
            jd_keywords=jd_keywords,
        )

    # Build metadata
    metadata = DocumentMetadata(
        generated_at=datetime.now().isoformat(),
        source_resume_hash=hashlib.sha256(str(source_resume).encode()).hexdigest()[:16],
        jd_hash=hashlib.sha256(job_description.encode()).hexdigest()[:16],
        version="1.0",
        fit_score_delta=fit_score_delta,
    )

    doc = CanonicalDocument(
        resume=resume,
        cover_letter=cover_letter,
        metadata=metadata,
    )

    # Compute and store content hash
    doc.metadata.content_hash = doc.compute_content_hash()

    return doc
