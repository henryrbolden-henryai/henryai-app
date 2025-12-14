"""
QA Validation Module for HenryAI

Ensures AI-generated content is grounded in resume data and complete.

Priority 1: Output validation (fabrication detection)
Priority 2: Data quality checks (resume parsing, JD completeness)
Priority 3: JSON output validation (no undefined/null values)
"""

import os
import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from difflib import SequenceMatcher


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("qa_validation")


# =============================================================================
# Configuration - Tunable thresholds and settings
# =============================================================================

class ValidationConfig:
    """Centralized configuration for validation thresholds and settings."""

    # Fuzzy matching thresholds (0.0 to 1.0)
    COMPANY_MATCH_THRESHOLD = 0.8   # Strict - "Spotify" matches "Spotify Inc."
    SKILL_MATCH_THRESHOLD = 0.7     # Moderate - allows "Python development" to match "Python"
    CLAIM_MATCH_THRESHOLD = 0.6     # Loose - allows paraphrasing of achievements

    # Blocking behavior
    BLOCK_ON_FABRICATED_COMPANY = True
    BLOCK_ON_FABRICATED_SKILL = True
    BLOCK_ON_FABRICATED_METRIC = True
    BLOCK_ON_INCOMPLETE_JSON = True
    BLOCK_ON_MISSING_RESUME_FIELDS = True
    BLOCK_UNKNOWN_COMPANIES = True  # Block when AI mentions known company not in resume

    # Confidence thresholds
    MIN_CONFIDENCE_TO_PASS = 0.7    # Below this, add warnings
    BLOCK_CONFIDENCE_THRESHOLD = 0.4  # Below this, block the output

    # Logging
    LOG_DIR = os.path.join(os.path.dirname(__file__), "validation_logs")
    LOG_BLOCKED_OUTPUTS = True

    # Known companies list (expanded to 100+ for cross-industry support)
    KNOWN_COMPANIES: Set[str] = {
        # Tech giants
        "google", "alphabet", "meta", "facebook", "amazon", "aws", "apple", "microsoft",
        "netflix", "nvidia", "intel", "amd", "ibm", "oracle", "salesforce", "adobe",
        "cisco", "vmware", "dell", "hp", "hewlett packard",

        # Fintech & Finance
        "stripe", "square", "block", "coinbase", "robinhood", "plaid", "chime",
        "sofi", "affirm", "klarna", "wise", "revolut", "nubank", "brex",
        "goldman sachs", "morgan stanley", "jpmorgan", "jp morgan", "chase",
        "bank of america", "citibank", "citi", "wells fargo", "capital one",
        "american express", "amex", "visa", "mastercard", "blackrock", "fidelity",

        # Rideshare & Travel
        "uber", "lyft", "doordash", "instacart", "grubhub", "postmates",
        "airbnb", "booking", "expedia", "tripadvisor", "kayak",

        # Social & Communication
        "twitter", "x", "linkedin", "slack", "zoom", "discord", "telegram",
        "snapchat", "snap", "pinterest", "reddit", "tiktok", "bytedance",

        # SaaS & Productivity
        "dropbox", "box", "notion", "asana", "monday", "trello", "atlassian",
        "jira", "confluence", "figma", "canva", "miro", "airtable", "coda",
        "hubspot", "zendesk", "intercom", "twilio", "sendgrid", "mailchimp",
        "shopify", "wix", "squarespace", "webflow",

        # AI/ML Companies
        "openai", "anthropic", "deepmind", "cohere", "hugging face", "stability ai",
        "midjourney", "jasper", "copy.ai", "scale ai", "datarobot", "c3 ai",

        # Data & Analytics
        "snowflake", "databricks", "palantir", "tableau", "looker", "domo",
        "splunk", "datadog", "new relic", "elastic", "elasticsearch",

        # Streaming & Entertainment
        "spotify", "hulu", "disney", "warner", "paramount", "sony", "activision",
        "blizzard", "ea", "electronic arts", "epic games", "roblox", "unity",

        # Healthcare Tech
        "epic systems", "cerner", "veeva", "teladoc", "livongo", "oscar health",
        "clover health", "ro", "hims", "nurx", "one medical", "forward",
        "kaiser", "kaiser permanente", "unitedhealth", "anthem", "cigna", "aetna",
        "cvs health", "walgreens", "mayo clinic", "cleveland clinic",

        # Consulting & Professional Services
        "mckinsey", "bain", "bcg", "boston consulting", "deloitte", "pwc",
        "kpmg", "ey", "ernst young", "accenture", "capgemini", "cognizant",
        "infosys", "tcs", "wipro", "hcl",

        # Automotive & Transportation
        "tesla", "rivian", "lucid", "nio", "ford", "gm", "general motors",
        "toyota", "honda", "bmw", "mercedes", "volkswagen", "waymo", "cruise",
        "aurora", "nuro", "zoox", "argo ai",

        # Aerospace & Defense
        "spacex", "blue origin", "boeing", "lockheed martin", "raytheon",
        "northrop grumman", "general dynamics", "bae systems",

        # E-commerce & Retail
        "walmart", "target", "costco", "kroger", "home depot", "lowes",
        "best buy", "wayfair", "etsy", "ebay", "alibaba", "jd.com",
        "wish", "poshmark", "mercari", "chewy", "petco"
    }


def get_validation_config() -> Dict[str, Any]:
    """Get current validation configuration for inspection/debugging."""
    return {
        "thresholds": {
            "company_match": ValidationConfig.COMPANY_MATCH_THRESHOLD,
            "skill_match": ValidationConfig.SKILL_MATCH_THRESHOLD,
            "claim_match": ValidationConfig.CLAIM_MATCH_THRESHOLD,
            "min_confidence": ValidationConfig.MIN_CONFIDENCE_TO_PASS,
            "block_confidence": ValidationConfig.BLOCK_CONFIDENCE_THRESHOLD,
        },
        "blocking": {
            "fabricated_company": ValidationConfig.BLOCK_ON_FABRICATED_COMPANY,
            "fabricated_skill": ValidationConfig.BLOCK_ON_FABRICATED_SKILL,
            "fabricated_metric": ValidationConfig.BLOCK_ON_FABRICATED_METRIC,
            "incomplete_json": ValidationConfig.BLOCK_ON_INCOMPLETE_JSON,
            "missing_resume_fields": ValidationConfig.BLOCK_ON_MISSING_RESUME_FIELDS,
            "unknown_companies": ValidationConfig.BLOCK_UNKNOWN_COMPANIES,
        },
        "known_companies_count": len(ValidationConfig.KNOWN_COMPANIES),
        "log_dir": ValidationConfig.LOG_DIR,
    }


def set_validation_threshold(threshold_name: str, value: float) -> None:
    """Dynamically adjust a validation threshold."""
    if hasattr(ValidationConfig, threshold_name):
        setattr(ValidationConfig, threshold_name, value)
        logger.info(f"Set {threshold_name} to {value}")
    else:
        raise ValueError(f"Unknown threshold: {threshold_name}")


def add_known_companies(companies: List[str]) -> None:
    """Add companies to the known companies list (for industry expansion)."""
    for company in companies:
        ValidationConfig.KNOWN_COMPANIES.add(company.lower().strip())
    logger.info(f"Added {len(companies)} companies to known companies list")


# =============================================================================
# Data Structures
# =============================================================================

class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    CRITICAL = "critical"    # Must block - definite fabrication
    HIGH = "high"            # Should block - likely fabrication
    MEDIUM = "medium"        # Warning - possible issue
    LOW = "low"              # Info - minor concern


class ValidationCategory(Enum):
    """Categories of validation issues."""
    FABRICATED_COMPANY = "fabricated_company"
    FABRICATED_SKILL = "fabricated_skill"
    FABRICATED_METRIC = "fabricated_metric"
    FABRICATED_EXPERIENCE = "fabricated_experience"
    UNGROUNDED_CLAIM = "ungrounded_claim"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    INCOMPLETE_DATA = "incomplete_data"
    NULL_VALUE = "null_value"
    EMPTY_STRING = "empty_string"


@dataclass
class ValidationIssue:
    """Represents a single validation issue found."""
    category: ValidationCategory
    severity: ValidationSeverity
    field_path: str
    message: str
    claim: Optional[str] = None
    evidence: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    confidence_score: float  # 0.0 to 1.0
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)

    @property
    def should_block(self) -> bool:
        """Determine if the output should be blocked based on issues."""
        critical_issues = [i for i in self.issues
                         if i.severity in (ValidationSeverity.CRITICAL, ValidationSeverity.HIGH)]
        # Only block if there are actual CRITICAL or HIGH severity issues
        # Low confidence with warnings should NOT block - this is too aggressive
        # and blocks legitimate cover letters/outreach that naturally contain
        # content not directly in the resume
        if len(critical_issues) > 0:
            return True
        # Removed: blocking on low confidence + warnings was too strict
        # Warnings alone should never block - only log for review
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "is_valid": self.is_valid,
            "confidence_score": self.confidence_score,
            "should_block": self.should_block,
            "issues": [
                {
                    "category": i.category.value,
                    "severity": i.severity.value,
                    "field": i.field_path,
                    "message": i.message,
                    "claim": i.claim,
                }
                for i in self.issues
            ],
            "warnings": [
                {
                    "category": w.category.value,
                    "severity": w.severity.value,
                    "field": w.field_path,
                    "message": w.message,
                }
                for w in self.warnings
            ],
        }


# =============================================================================
# Resume Grounding Validator
# =============================================================================

class ResumeGroundingValidator:
    """
    Validates that AI-generated content is grounded in actual resume data.
    Extracts verifiable facts from resume and checks claims against them.
    """

    def __init__(self, resume_data: Dict[str, Any]):
        """Initialize with parsed resume data."""
        self.resume_data = resume_data
        self.companies = self._extract_companies()
        self.skills = self._extract_skills()
        self.metrics = self._extract_metrics()
        self.achievements = self._extract_achievements()
        self.titles = self._extract_titles()
        self.education = self._extract_education()
        self.resume_text = self._build_resume_text()

    def _extract_companies(self) -> Set[str]:
        """Extract all company names from resume."""
        companies = set()

        # From experience entries
        for exp in self.resume_data.get("experience", []):
            if company := exp.get("company"):
                companies.add(company.lower().strip())
                # Also add variations
                for part in company.split():
                    if len(part) > 3:
                        companies.add(part.lower().strip())

        # From education entries (handle both list of dicts and string format)
        education = self.resume_data.get("education", [])
        if isinstance(education, list):
            for edu in education:
                if isinstance(edu, dict):
                    if school := edu.get("school"):
                        companies.add(school.lower().strip())
                    if school := edu.get("institution"):
                        companies.add(school.lower().strip())
                elif isinstance(edu, str):
                    # Education is a string, add school names if we can extract them
                    companies.add(edu.lower().strip())
        elif isinstance(education, str):
            # Single education string
            companies.add(education.lower().strip())

        return companies

    def _extract_skills(self) -> Set[str]:
        """Extract all skills from resume."""
        skills = set()

        # Direct skills array
        for skill in self.resume_data.get("skills", []):
            if isinstance(skill, str):
                skills.add(skill.lower().strip())
            elif isinstance(skill, dict):
                if name := skill.get("name"):
                    skills.add(name.lower().strip())

        # Technical skills
        tech_skills = self.resume_data.get("technical_skills", {})
        if isinstance(tech_skills, dict):
            for category, skill_list in tech_skills.items():
                if isinstance(skill_list, list):
                    for skill in skill_list:
                        skills.add(skill.lower().strip())
        elif isinstance(tech_skills, list):
            for skill in tech_skills:
                skills.add(skill.lower().strip())

        # Skills from experience bullets (extract common tech terms)
        for exp in self.resume_data.get("experience", []):
            for bullet in exp.get("bullets", []):
                # Extract known tech terms
                skills.update(self._extract_tech_terms(bullet))

        return skills

    def _extract_tech_terms(self, text: str) -> Set[str]:
        """Extract technology terms from text."""
        tech_terms = set()
        common_tech = [
            "python", "java", "javascript", "typescript", "react", "node",
            "aws", "gcp", "azure", "docker", "kubernetes", "sql", "nosql",
            "mongodb", "postgresql", "mysql", "redis", "elasticsearch",
            "machine learning", "ml", "ai", "data science", "analytics",
            "api", "rest", "graphql", "microservices", "agile", "scrum"
        ]
        text_lower = text.lower()
        for term in common_tech:
            if term in text_lower:
                tech_terms.add(term)
        return tech_terms

    def _extract_metrics(self) -> Set[str]:
        """Extract quantifiable metrics from resume."""
        metrics = set()

        # Pattern for numbers with context
        patterns = [
            r'\$[\d,.]+[KMB]?',           # Dollar amounts
            r'[\d,.]+%',                   # Percentages
            r'[\d,.]+x',                   # Multipliers
            r'\d+\+?\s*(users|customers|clients|employees|team members)',
            r'[\d,.]+\s*(ARR|MRR|revenue)',
        ]

        for exp in self.resume_data.get("experience", []):
            for bullet in exp.get("bullets", []):
                for pattern in patterns:
                    matches = re.findall(pattern, bullet, re.IGNORECASE)
                    metrics.update(m.lower() for m in matches)

        return metrics

    def _extract_achievements(self) -> List[str]:
        """Extract achievement statements from resume."""
        achievements = []

        for exp in self.resume_data.get("experience", []):
            achievements.extend(exp.get("bullets", []))

        # Also include summary points
        if summary := self.resume_data.get("summary"):
            if isinstance(summary, str):
                achievements.append(summary)
            elif isinstance(summary, list):
                achievements.extend(summary)

        return achievements

    def _extract_titles(self) -> Set[str]:
        """Extract job titles from resume."""
        titles = set()

        for exp in self.resume_data.get("experience", []):
            if title := exp.get("title"):
                titles.add(title.lower().strip())
                # Also extract key words from titles
                for word in title.lower().split():
                    if word in ["senior", "lead", "principal", "staff", "manager",
                               "director", "vp", "head", "chief", "engineer",
                               "developer", "designer", "analyst", "pm", "product"]:
                        titles.add(word)

        return titles

    def _extract_education(self) -> Set[str]:
        """Extract education details from resume."""
        education_set = set()

        edu_data = self.resume_data.get("education", [])

        # Handle string education (e.g., "MBA Stanford University")
        if isinstance(edu_data, str):
            education_set.add(edu_data.lower().strip())
            return education_set

        # Handle list of education entries
        if isinstance(edu_data, list):
            for edu in edu_data:
                if isinstance(edu, dict):
                    if degree := edu.get("degree"):
                        education_set.add(degree.lower().strip())
                    if field := edu.get("field"):
                        education_set.add(field.lower().strip())
                    if school := edu.get("school"):
                        education_set.add(school.lower().strip())
                elif isinstance(edu, str):
                    education_set.add(edu.lower().strip())

        return education_set

    def _build_resume_text(self) -> str:
        """Build full-text representation for fuzzy matching."""
        parts = []

        # Name
        if name := self.resume_data.get("full_name"):
            parts.append(name)

        # Summary
        if summary := self.resume_data.get("summary"):
            parts.append(summary if isinstance(summary, str) else " ".join(summary))

        # Experience
        for exp in self.resume_data.get("experience", []):
            parts.append(exp.get("company", ""))
            parts.append(exp.get("title", ""))
            parts.extend(exp.get("bullets", []))

        # Education
        for edu in self.resume_data.get("education", []):
            if isinstance(edu, dict):
                parts.append(edu.get("school", ""))
                parts.append(edu.get("degree", ""))
            elif isinstance(edu, str):
                parts.append(edu)

        # Skills
        skills = self.resume_data.get("skills", [])
        if isinstance(skills, list):
            parts.extend(str(s) for s in skills)

        return " ".join(str(p) for p in parts).lower()

    def _fuzzy_match(self, text1: str, text2: str, threshold: float) -> bool:
        """Check if two strings are similar enough."""
        # Quick exact match
        if text1 == text2:
            return True

        # Substring check
        if text1 in text2 or text2 in text1:
            return True

        # Sequence matching
        ratio = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        return ratio >= threshold

    def validate_company_mention(self, company_name: str) -> Tuple[bool, str]:
        """
        Validate that a mentioned company exists in the resume.

        Returns:
            (is_valid, evidence_or_error)
        """
        company_lower = company_name.lower().strip()

        # Direct match
        if company_lower in self.companies:
            return True, f"Found company '{company_name}' in resume"

        # Fuzzy match with configurable threshold
        for resume_company in self.companies:
            if self._fuzzy_match(company_lower, resume_company,
                                ValidationConfig.COMPANY_MATCH_THRESHOLD):
                return True, f"Found similar company '{resume_company}' in resume"

        return False, f"Company '{company_name}' not found in resume"

    def validate_skill_mention(self, skill: str) -> Tuple[bool, str]:
        """
        Validate that a mentioned skill exists in the resume.

        Returns:
            (is_valid, evidence_or_error)
        """
        skill_lower = skill.lower().strip()

        # Direct match in skills
        if skill_lower in self.skills:
            return True, f"Found skill '{skill}' in resume"

        # Check in resume text with fuzzy match
        for resume_skill in self.skills:
            if self._fuzzy_match(skill_lower, resume_skill,
                                ValidationConfig.SKILL_MATCH_THRESHOLD):
                return True, f"Found similar skill '{resume_skill}' in resume"

        # Check if skill appears in resume text at all
        if skill_lower in self.resume_text:
            return True, f"Found '{skill}' in resume content"

        return False, f"Skill '{skill}' not found in resume"

    def validate_metric_mention(self, metric: str) -> Tuple[bool, str]:
        """
        Validate that a mentioned metric exists in the resume.

        Returns:
            (is_valid, evidence_or_error)
        """
        metric_lower = metric.lower().strip()

        # Direct match
        if metric_lower in self.resume_text:
            return True, f"Found metric '{metric}' in resume"

        # Check individual numbers
        numbers = re.findall(r'[\d,.]+', metric)
        for num in numbers:
            if num in self.resume_text:
                return True, f"Found number '{num}' in resume"

        return False, f"Metric '{metric}' not found in resume"

    def validate_claim(self, claim: str) -> Tuple[bool, float, str]:
        """
        Validate that a claim can be traced to resume content.

        Returns:
            (is_valid, confidence, evidence_or_error)
        """
        claim_lower = claim.lower()

        # Check direct containment in resume text
        if claim_lower in self.resume_text:
            return True, 1.0, "Direct match in resume"

        # Check fuzzy match against achievements with configurable threshold
        for achievement in self.achievements:
            if self._fuzzy_match(claim_lower, achievement.lower(),
                                ValidationConfig.CLAIM_MATCH_THRESHOLD):
                return True, 0.9, f"Matches achievement: {achievement[:100]}..."

        # Check if claim contains resume elements (more lenient)
        elements_found = 0
        total_elements = 0

        # Check companies
        for company in self.companies:
            if len(company) > 3:  # Skip short names
                total_elements += 1
                if company in claim_lower:
                    elements_found += 1

        # Check skills
        for skill in self.skills:
            if len(skill) > 3:
                total_elements += 1
                if skill in claim_lower:
                    elements_found += 1

        # Check titles
        for title in self.titles:
            if len(title) > 3:
                total_elements += 1
                if title in claim_lower:
                    elements_found += 1

        if total_elements > 0:
            confidence = elements_found / min(total_elements, 5)  # Cap denominator
            if confidence > 0.3:
                return True, confidence, f"Found {elements_found} resume elements in claim"

        # Allow positioning/inference phrases (not fabrication)
        positioning_phrases = [
            "position yourself", "highlight your", "emphasize", "leverage your",
            "showcase", "demonstrate", "draw from", "building on", "based on your",
            "your background in", "your experience with", "your work at"
        ]
        for phrase in positioning_phrases:
            if phrase in claim_lower:
                return True, 0.7, "Positioning/inference phrase - not a factual claim"

        return False, 0.0, "Claim not grounded in resume content"


# =============================================================================
# Output Validator - Validates AI-generated documents
# =============================================================================

class OutputValidator:
    """
    Validates AI-generated outputs (resume summaries, cover letters, etc.)
    for fabrication and completeness.
    """

    def __init__(self, grounding_validator: ResumeGroundingValidator):
        self.grounding_validator = grounding_validator

    def validate_resume_output(self, output: Dict[str, Any]) -> ValidationResult:
        """Validate AI-generated resume summary and core competencies."""
        issues = []
        warnings = []
        confidence_scores = []

        # Validate summary
        if summary := output.get("summary"):
            self._validate_text_section(summary, "summary", issues, warnings, confidence_scores)

        # Validate core competencies (previously key_qualifications)
        if core_comps := output.get("core_competencies"):
            if isinstance(core_comps, list):
                for i, comp in enumerate(core_comps):
                    self._validate_text_section(
                        comp, f"core_competencies[{i}]", issues, warnings, confidence_scores
                    )

        # Also check for legacy key_qualifications field
        if key_quals := output.get("key_qualifications"):
            if isinstance(key_quals, list):
                for i, qual in enumerate(key_quals):
                    self._validate_text_section(
                        qual, f"key_qualifications[{i}]", issues, warnings, confidence_scores
                    )

        # Validate professional narrative
        if narrative := output.get("professional_narrative"):
            self._validate_text_section(narrative, "professional_narrative", issues, warnings, confidence_scores)

        # Calculate overall confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 1.0

        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence_score=avg_confidence,
            issues=issues,
            warnings=warnings
        )

    def validate_cover_letter(self, output: Dict[str, Any]) -> ValidationResult:
        """Validate AI-generated cover letter content."""
        issues = []
        warnings = []
        confidence_scores = []

        # Validate paragraphs - including full_text which is the actual field used
        for para_key in ["opening_paragraph", "body_paragraph_1", "body_paragraph_2",
                         "body_paragraph_3", "closing_paragraph", "content",
                         "full_text", "opening", "body", "closing", "greeting"]:
            if para := output.get(para_key):
                self._validate_text_section(para, para_key, issues, warnings, confidence_scores)

        # Calculate overall confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 1.0

        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence_score=avg_confidence,
            issues=issues,
            warnings=warnings
        )

    def validate_interview_prep(self, output: Dict[str, Any]) -> ValidationResult:
        """Validate AI-generated interview prep content."""
        issues = []
        warnings = []
        confidence_scores = []

        # Validate narrative (Tell me about yourself)
        if narrative := output.get("narrative"):
            self._validate_text_section(narrative, "narrative", issues, warnings, confidence_scores)

        # Validate talking points
        if talking_points := output.get("talking_points"):
            if isinstance(talking_points, list):
                for i, point in enumerate(talking_points):
                    if isinstance(point, dict):
                        text = point.get("content") or point.get("point") or str(point)
                    else:
                        text = str(point)
                    self._validate_text_section(text, f"talking_points[{i}]", issues, warnings, confidence_scores)

        # Validate gap mitigation strategies
        if gap_mitigation := output.get("gap_mitigation"):
            if isinstance(gap_mitigation, list):
                for i, gap in enumerate(gap_mitigation):
                    text = gap if isinstance(gap, str) else str(gap)
                    self._validate_text_section(text, f"gap_mitigation[{i}]", issues, warnings, confidence_scores)

        # Validate STAR stories (may not be present in documents endpoint output)
        if star_stories := output.get("star_stories"):
            if isinstance(star_stories, list):
                for i, story in enumerate(star_stories):
                    if isinstance(story, dict):
                        for key in ["situation", "task", "action", "result", "story"]:
                            if text := story.get(key):
                                self._validate_text_section(
                                    text, f"star_stories[{i}].{key}", issues, warnings, confidence_scores
                                )

        # Validate questions to ask
        # (These are generated, not resume-based, so skip validation)

        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 1.0

        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence_score=avg_confidence,
            issues=issues,
            warnings=warnings
        )

    def validate_outreach(self, output: Dict[str, Any]) -> ValidationResult:
        """Validate AI-generated outreach templates."""
        issues = []
        warnings = []
        confidence_scores = []

        # Validate outreach templates - including actual field names from documents endpoint
        for key in ["recruiter_outreach_template", "hiring_manager_outreach_template",
                    "linkedin_message", "email_template",
                    "hiring_manager", "recruiter", "linkedin_help_text"]:
            if template := output.get(key):
                self._validate_text_section(template, key, issues, warnings, confidence_scores)

        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 1.0

        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence_score=avg_confidence,
            issues=issues,
            warnings=warnings
        )

    def _validate_text_section(self, text: str, field_path: str,
                               issues: List[ValidationIssue],
                               warnings: List[ValidationIssue],
                               confidence_scores: List[float]) -> None:
        """Validate a text section for fabrication."""
        if not text or not isinstance(text, str):
            return

        # Extract potential claims (sentences with verifiable content)
        claims = self._extract_claims(text)

        for claim in claims:
            is_valid, confidence, evidence = self.grounding_validator.validate_claim(claim)
            confidence_scores.append(confidence)

            if not is_valid:
                # Check if it contains a fabricated company
                company_match = self._extract_company_mention(claim)
                if company_match:
                    valid, _ = self.grounding_validator.validate_company_mention(company_match)
                    if not valid and ValidationConfig.BLOCK_ON_FABRICATED_COMPANY:
                        issues.append(ValidationIssue(
                            category=ValidationCategory.FABRICATED_COMPANY,
                            severity=ValidationSeverity.CRITICAL,
                            field_path=field_path,
                            message=f"Reference to company '{company_match}' not found in resume",
                            claim=claim
                        ))
                        continue

                # Check for fabricated metrics
                metric_match = self._extract_metric(claim)
                if metric_match:
                    valid, _ = self.grounding_validator.validate_metric_mention(metric_match)
                    if not valid and ValidationConfig.BLOCK_ON_FABRICATED_METRIC:
                        issues.append(ValidationIssue(
                            category=ValidationCategory.FABRICATED_METRIC,
                            severity=ValidationSeverity.HIGH,
                            field_path=field_path,
                            message=f"Metric '{metric_match}' not found in resume",
                            claim=claim
                        ))
                        continue

                # General ungrounded claim (warning only)
                if confidence < ValidationConfig.MIN_CONFIDENCE_TO_PASS:
                    warnings.append(ValidationIssue(
                        category=ValidationCategory.UNGROUNDED_CLAIM,
                        severity=ValidationSeverity.MEDIUM,
                        field_path=field_path,
                        message=f"Claim may not be grounded in resume (confidence: {confidence:.2f})",
                        claim=claim
                    ))

    def _extract_claims(self, text: str) -> List[str]:
        """Extract verifiable claims from text."""
        claims = []

        # Split into sentences
        sentences = re.split(r'[.!?]+', text)

        # Indicators of verifiable claims
        claim_indicators = [
            r'\d+',                    # Numbers
            r'\$',                     # Dollar signs
            r'%',                      # Percentages
            r'led|managed|built|created|developed|launched|grew|increased|decreased',
            r'at \w+',                 # "at [Company]"
            r'with \w+',               # "with [Company]"
            r'for \w+',                # "for [Company]"
        ]

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Skip very short fragments
                for pattern in claim_indicators:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        claims.append(sentence)
                        break

        return claims

    def _extract_company_mention(self, text: str) -> Optional[str]:
        """Extract company name from text."""
        # Check against known companies with word boundary matching
        text_lower = text.lower()
        for company in ValidationConfig.KNOWN_COMPANIES:
            # Skip companies that are too short to avoid false positives
            if len(company) < 4:
                continue
            # Use word boundary matching
            pattern = r'\b' + re.escape(company) + r'\b'
            if re.search(pattern, text_lower):
                return company

        # Pattern: "at [Company]" or "with [Company]"
        patterns = [
            r'at (\w+(?:\s+\w+)?)',
            r'with (\w+(?:\s+\w+)?)',
            r'for (\w+(?:\s+\w+)?)',
            r'from (\w+(?:\s+\w+)?)',
        ]

        # Common words that are NOT company names
        non_company_words = {
            'the', 'a', 'an', 'their', 'our', 'your', 'my', 'his', 'her', 'its',
            'experience', 'expertise', 'skills', 'work', 'job', 'role', 'team',
            'least', 'most', 'first', 'last', 'start', 'end', 'time', 'times',
            'days', 'weeks', 'months', 'years', 'hours', 'minutes', 'seconds',
            'engineering', 'design', 'sales', 'marketing', 'product', 'data',
            'all', 'some', 'any', 'each', 'every', 'both', 'few', 'many',
            'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom',
            'scale', 'speed', 'quality', 'level', 'rate', 'pace', 'cost',
        }

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                potential_company = match.group(1).strip()
                # Filter out common non-company words and numbers
                words = potential_company.lower().split()
                if (words[0] not in non_company_words and
                    not words[0].isdigit() and
                    len(potential_company) > 2):
                    return potential_company

        return None

    def _extract_metric(self, text: str) -> Optional[str]:
        """Extract metric/number from text."""
        patterns = [
            r'\$[\d,.]+[KMB]?',
            r'[\d,.]+%',
            r'[\d,.]+x',
            r'\d+\+?\s*(users|customers|clients|team members|employees)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)

        return None


# =============================================================================
# Chat Response Validator - For Ask Henry
# =============================================================================

class ChatResponseValidator:
    """
    Validates chat responses from Ask Henry for fabrication.
    More lenient than document validation since chat is conversational.
    """

    def __init__(self, grounding_validator: ResumeGroundingValidator):
        self.grounding_validator = grounding_validator

    def validate_response(self, response: str, user_question: str) -> ValidationResult:
        """Validate a chat response for fabrication."""
        issues = []
        warnings = []
        confidence_scores = []

        # Positioning phrases that are OK even without direct resume match
        positioning_phrases = [
            "you could mention", "consider highlighting", "emphasize your",
            "position yourself as", "frame your", "leverage your", "draw from",
            "highlight your", "showcase your", "demonstrate your", "build on your",
            "based on your", "given your background", "with your experience",
            "try to emphasize", "you might want to", "I'd suggest", "I recommend"
        ]

        response_lower = response.lower()

        # First pass: Check for company names in response that aren't in resume
        # Skip very short company names to avoid false positives on substrings
        for company in ValidationConfig.KNOWN_COMPANIES:
            # Skip companies that are too short (likely to cause false positives)
            if len(company) < 4:
                continue

            # Use word boundary matching to avoid substring false positives
            # This ensures "Google" matches but "key" doesn't match "keyboard"
            pattern = r'\b' + re.escape(company) + r'\b'
            if re.search(pattern, response_lower):
                # Check if this company is in the candidate's resume
                if company not in self.grounding_validator.companies:
                    # Verify it's not a partial match with a resume company
                    is_partial_match = False
                    for resume_company in self.grounding_validator.companies:
                        if company in resume_company or resume_company in company:
                            is_partial_match = True
                            break

                    if not is_partial_match and ValidationConfig.BLOCK_UNKNOWN_COMPANIES:
                        issues.append(ValidationIssue(
                            category=ValidationCategory.FABRICATED_COMPANY,
                            severity=ValidationSeverity.CRITICAL,
                            field_path="chat_response",
                            message=f"Chat response mentions '{company}' which is not in the candidate's resume",
                            claim=f"Reference to {company}..."
                        ))

        # Second pass: Extract and validate claims
        sentences = re.split(r'[.!?]+', response)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue

            # Skip sentences that are just positioning advice
            is_positioning = any(phrase in sentence.lower() for phrase in positioning_phrases)

            # Check if sentence contains verifiable claims
            has_company = self._mentions_company(sentence)
            has_metric = bool(re.search(r'\d+', sentence))
            has_experience_claim = bool(re.search(
                r'(you|your)\s+(worked|led|managed|built|created|increased|grew)',
                sentence, re.IGNORECASE
            ))

            if (has_company or has_metric or has_experience_claim) and not is_positioning:
                is_valid, confidence, evidence = self.grounding_validator.validate_claim(sentence)
                confidence_scores.append(confidence)

                if not is_valid and confidence < 0.3:
                    # Check if it's specifically about a fabricated company
                    company_in_sentence = self._extract_company_from_sentence(sentence)
                    if company_in_sentence:
                        valid, _ = self.grounding_validator.validate_company_mention(company_in_sentence)
                        if not valid:
                            issues.append(ValidationIssue(
                                category=ValidationCategory.FABRICATED_EXPERIENCE,
                                severity=ValidationSeverity.HIGH,
                                field_path="chat_response",
                                message=f"Response makes claims about experience not in resume",
                                claim=sentence[:150]
                            ))

        # Calculate confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.8

        # Log if blocking
        if issues:
            logger.warning(f"Chat response BLOCKED: {len(issues)} fabrication issues. Question: {user_question[:50]}...")
            for issue in issues:
                logger.warning(f"  - {issue.message}: {issue.claim}")

        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence_score=avg_confidence,
            issues=issues,
            warnings=warnings
        )

    def _mentions_company(self, text: str) -> bool:
        """Check if text mentions any known company."""
        text_lower = text.lower()
        for company in ValidationConfig.KNOWN_COMPANIES:
            if len(company) < 4:
                continue
            pattern = r'\b' + re.escape(company) + r'\b'
            if re.search(pattern, text_lower):
                return True
        return False

    def _extract_company_from_sentence(self, sentence: str) -> Optional[str]:
        """Extract company name from a sentence."""
        sentence_lower = sentence.lower()
        for company in ValidationConfig.KNOWN_COMPANIES:
            if len(company) < 4:
                continue
            pattern = r'\b' + re.escape(company) + r'\b'
            if re.search(pattern, sentence_lower):
                return company
        return None


# =============================================================================
# Data Quality Validator
# =============================================================================

class DataQualityValidator:
    """Validates data quality for resume parsing and JD analysis."""

    REQUIRED_RESUME_FIELDS = ["full_name", "contact", "experience"]
    RECOMMENDED_RESUME_FIELDS = ["skills", "education", "summary"]

    RECOMMENDED_JD_FIELDS = ["role_title", "company", "requirements", "responsibilities"]
    NICE_TO_HAVE_JD_FIELDS = ["salary_info", "benefits", "location"]

    @classmethod
    def validate_parsed_resume(cls, resume_data: Dict[str, Any]) -> ValidationResult:
        """Validate that a parsed resume has all critical fields."""
        issues = []
        warnings = []

        # Check required fields
        for field in cls.REQUIRED_RESUME_FIELDS:
            value = resume_data.get(field)
            if value is None or value == "" or value == []:
                if ValidationConfig.BLOCK_ON_MISSING_RESUME_FIELDS:
                    issues.append(ValidationIssue(
                        category=ValidationCategory.MISSING_REQUIRED_FIELD,
                        severity=ValidationSeverity.CRITICAL,
                        field_path=field,
                        message=f"Required field '{field}' is missing or empty"
                    ))

        # Check contact info specifically
        contact = resume_data.get("contact", {})
        if isinstance(contact, dict):
            if not contact.get("email") and not contact.get("phone"):
                issues.append(ValidationIssue(
                    category=ValidationCategory.MISSING_REQUIRED_FIELD,
                    severity=ValidationSeverity.HIGH,
                    field_path="contact",
                    message="No email or phone number found in resume"
                ))

        # Check recommended fields (warnings only)
        for field in cls.RECOMMENDED_RESUME_FIELDS:
            value = resume_data.get(field)
            if value is None or value == "" or value == []:
                warnings.append(ValidationIssue(
                    category=ValidationCategory.INCOMPLETE_DATA,
                    severity=ValidationSeverity.LOW,
                    field_path=field,
                    message=f"Recommended field '{field}' is missing"
                ))

        # Check experience entries have required sub-fields
        for i, exp in enumerate(resume_data.get("experience", [])):
            if not exp.get("company"):
                warnings.append(ValidationIssue(
                    category=ValidationCategory.INCOMPLETE_DATA,
                    severity=ValidationSeverity.MEDIUM,
                    field_path=f"experience[{i}].company",
                    message=f"Experience entry {i+1} missing company name"
                ))
            if not exp.get("bullets") or len(exp.get("bullets", [])) == 0:
                warnings.append(ValidationIssue(
                    category=ValidationCategory.INCOMPLETE_DATA,
                    severity=ValidationSeverity.MEDIUM,
                    field_path=f"experience[{i}].bullets",
                    message=f"Experience entry {i+1} has no bullet points"
                ))

        # Calculate confidence based on completeness
        total_fields = len(cls.REQUIRED_RESUME_FIELDS) + len(cls.RECOMMENDED_RESUME_FIELDS)
        missing_fields = len(issues) + len(warnings)
        confidence = max(0.0, 1.0 - (missing_fields / total_fields))

        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence_score=confidence,
            issues=issues,
            warnings=warnings
        )

    @classmethod
    def validate_jd_analysis(cls, jd_data: Dict[str, Any]) -> ValidationResult:
        """Validate that a JD analysis is complete enough to use."""
        issues = []
        warnings = []

        # Check recommended fields (warnings for JD - don't block)
        for field in cls.RECOMMENDED_JD_FIELDS:
            value = jd_data.get(field)
            if value is None or value == "" or value == []:
                warnings.append(ValidationIssue(
                    category=ValidationCategory.INCOMPLETE_DATA,
                    severity=ValidationSeverity.MEDIUM,
                    field_path=field,
                    message=f"JD field '{field}' is missing - may affect output quality"
                ))

        # Check nice-to-have fields (info only)
        for field in cls.NICE_TO_HAVE_JD_FIELDS:
            value = jd_data.get(field)
            if value is None or value == "" or value == []:
                warnings.append(ValidationIssue(
                    category=ValidationCategory.INCOMPLETE_DATA,
                    severity=ValidationSeverity.LOW,
                    field_path=field,
                    message=f"JD field '{field}' not found in job description"
                ))

        # Calculate confidence
        total_fields = len(cls.RECOMMENDED_JD_FIELDS) + len(cls.NICE_TO_HAVE_JD_FIELDS)
        missing_fields = len(warnings)
        confidence = max(0.3, 1.0 - (missing_fields / total_fields))

        return ValidationResult(
            is_valid=True,  # JD issues don't block
            confidence_score=confidence,
            issues=issues,
            warnings=warnings
        )


# =============================================================================
# JSON Output Validator
# =============================================================================

class JSONOutputValidator:
    """Validates JSON outputs for completeness (no null/undefined/empty values)."""

    # Fields that must have values
    REQUIRED_FIELDS_BY_TYPE = {
        "documents_generation": [
            # Updated to match actual output structure from /api/documents/generate
            "resume_output.summary",
            "resume_output.core_competencies",
            "cover_letter.full_text",
            "interview_prep.narrative",
        ],
        "interview_prep": [
            "talking_points",
            "star_stories",
            "questions_to_ask",
        ],
        "jd_analysis": [
            "role_title",
            "company",
        ],
    }

    @classmethod
    def validate_output(cls, output: Dict[str, Any], output_type: str) -> ValidationResult:
        """Validate that a JSON output has no null/empty required fields."""
        issues = []
        warnings = []

        required_fields = cls.REQUIRED_FIELDS_BY_TYPE.get(output_type, [])

        for field_path in required_fields:
            value = cls._get_nested_value(output, field_path)

            if value is None:
                if ValidationConfig.BLOCK_ON_INCOMPLETE_JSON:
                    issues.append(ValidationIssue(
                        category=ValidationCategory.NULL_VALUE,
                        severity=ValidationSeverity.HIGH,
                        field_path=field_path,
                        message=f"Required field '{field_path}' is null/undefined"
                    ))
            elif value == "" or value == []:
                issues.append(ValidationIssue(
                    category=ValidationCategory.EMPTY_STRING,
                    severity=ValidationSeverity.HIGH,
                    field_path=field_path,
                    message=f"Required field '{field_path}' is empty"
                ))

        # Recursively check for null values in the entire structure
        null_fields = cls._find_null_fields(output)
        for field in null_fields:
            if field not in [i.field_path for i in issues]:
                warnings.append(ValidationIssue(
                    category=ValidationCategory.NULL_VALUE,
                    severity=ValidationSeverity.LOW,
                    field_path=field,
                    message=f"Field '{field}' has null value"
                ))

        confidence = 1.0 if not issues else max(0.0, 1.0 - (len(issues) * 0.2))

        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence_score=confidence,
            issues=issues,
            warnings=warnings
        )

    @classmethod
    def _get_nested_value(cls, obj: Dict[str, Any], path: str) -> Any:
        """Get a nested value from a dictionary using dot notation."""
        keys = path.split(".")
        value = obj
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value

    @classmethod
    def _find_null_fields(cls, obj: Any, prefix: str = "") -> List[str]:
        """Recursively find all null fields in an object."""
        null_fields = []

        if isinstance(obj, dict):
            for key, value in obj.items():
                path = f"{prefix}.{key}" if prefix else key
                if value is None:
                    null_fields.append(path)
                elif isinstance(value, (dict, list)):
                    null_fields.extend(cls._find_null_fields(value, path))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                path = f"{prefix}[{i}]"
                null_fields.extend(cls._find_null_fields(item, path))

        return null_fields


# =============================================================================
# Validation Logger - For review and tuning
# =============================================================================

class ValidationLogger:
    """Logs blocked outputs for manual review and tuning."""

    @staticmethod
    def _ensure_log_dir():
        """Create log directory if it doesn't exist."""
        if not os.path.exists(ValidationConfig.LOG_DIR):
            os.makedirs(ValidationConfig.LOG_DIR, exist_ok=True)

    @classmethod
    def log_blocked_output(cls, endpoint: str, result: ValidationResult,
                          output: Any, resume_data: Dict[str, Any],
                          request_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Log a blocked output for manual review.
        Returns the log entry ID.
        """
        if not ValidationConfig.LOG_BLOCKED_OUTPUTS:
            return ""

        cls._ensure_log_dir()

        timestamp = datetime.now()
        entry_id = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{id(output) % 1000000:06d}"

        log_entry = {
            "id": entry_id,
            "timestamp": timestamp.isoformat(),
            "endpoint": endpoint,
            "validation_result": result.to_dict(),
            "output_preview": cls._truncate_output(output),
            "resume_companies": list(ResumeGroundingValidator(resume_data).companies)[:10],
            "request_context": request_context or {},
        }

        # Write to daily log file
        log_file = os.path.join(
            ValidationConfig.LOG_DIR,
            f"blocked_{timestamp.strftime('%Y-%m-%d')}.jsonl"
        )

        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        logger.info(f"Logged blocked output: {entry_id}")
        return entry_id

    @classmethod
    def log_override(cls, entry_id: str, reason: str) -> None:
        """Log when a blocked output is manually approved (for learning)."""
        cls._ensure_log_dir()

        override_entry = {
            "entry_id": entry_id,
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
        }

        override_file = os.path.join(ValidationConfig.LOG_DIR, "overrides.jsonl")

        with open(override_file, "a") as f:
            f.write(json.dumps(override_entry) + "\n")

        logger.info(f"Logged override for {entry_id}: {reason}")

    @classmethod
    def get_blocked_logs(cls, date: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve blocked output logs for review."""
        cls._ensure_log_dir()

        if date:
            log_file = os.path.join(ValidationConfig.LOG_DIR, f"blocked_{date}.jsonl")
            files = [log_file] if os.path.exists(log_file) else []
        else:
            # Get all log files
            files = sorted([
                os.path.join(ValidationConfig.LOG_DIR, f)
                for f in os.listdir(ValidationConfig.LOG_DIR)
                if f.startswith("blocked_") and f.endswith(".jsonl")
            ], reverse=True)

        logs = []
        for log_file in files:
            if len(logs) >= limit:
                break
            try:
                with open(log_file, "r") as f:
                    for line in f:
                        if line.strip():
                            logs.append(json.loads(line))
                            if len(logs) >= limit:
                                break
            except (IOError, json.JSONDecodeError):
                continue

        return logs[:limit]

    @classmethod
    def get_override_stats(cls) -> Dict[str, Any]:
        """Get statistics about overrides (false positives)."""
        cls._ensure_log_dir()

        override_file = os.path.join(ValidationConfig.LOG_DIR, "overrides.jsonl")
        if not os.path.exists(override_file):
            return {"total_overrides": 0, "reasons": {}}

        overrides = []
        try:
            with open(override_file, "r") as f:
                for line in f:
                    if line.strip():
                        overrides.append(json.loads(line))
        except (IOError, json.JSONDecodeError):
            pass

        reason_counts: Dict[str, int] = {}
        for override in overrides:
            reason = override.get("reason", "unknown")[:50]
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

        return {
            "total_overrides": len(overrides),
            "reasons": reason_counts,
        }

    @staticmethod
    def _truncate_output(output: Any, max_length: int = 1000) -> Any:
        """Truncate output for logging."""
        if isinstance(output, str):
            return output[:max_length] + "..." if len(output) > max_length else output
        elif isinstance(output, dict):
            return {k: ValidationLogger._truncate_output(v, max_length // 2)
                   for k, v in list(output.items())[:10]}
        elif isinstance(output, list):
            return [ValidationLogger._truncate_output(item, max_length // 2)
                   for item in output[:5]]
        return output


# =============================================================================
# High-Level Validation Functions
# =============================================================================

def validate_documents_generation(output: Dict[str, Any],
                                  resume_data: Dict[str, Any],
                                  jd_data: Optional[Dict[str, Any]] = None) -> ValidationResult:
    """
    Validate the full documents generation output.
    Combines fabrication detection, JSON completeness, and data quality checks.
    """
    all_issues = []
    all_warnings = []
    confidence_scores = []

    # Initialize grounding validator
    grounding_validator = ResumeGroundingValidator(resume_data)
    output_validator = OutputValidator(grounding_validator)

    # 1. Validate resume output (was previously "resume_summary", now "resume_output")
    if resume_output := output.get("resume_output"):
        result = output_validator.validate_resume_output(resume_output)
        all_issues.extend(result.issues)
        all_warnings.extend(result.warnings)
        confidence_scores.append(result.confidence_score)

    # 2. Validate cover letter
    if cover_letter := output.get("cover_letter"):
        result = output_validator.validate_cover_letter(cover_letter)
        all_issues.extend(result.issues)
        all_warnings.extend(result.warnings)
        confidence_scores.append(result.confidence_score)

    # 3. Validate interview prep
    if interview_prep := output.get("interview_prep"):
        result = output_validator.validate_interview_prep(interview_prep)
        all_issues.extend(result.issues)
        all_warnings.extend(result.warnings)
        confidence_scores.append(result.confidence_score)

    # 4. Validate outreach
    if outreach := output.get("outreach"):
        result = output_validator.validate_outreach(outreach)
        all_issues.extend(result.issues)
        all_warnings.extend(result.warnings)
        confidence_scores.append(result.confidence_score)

    # 5. JSON completeness check
    json_result = JSONOutputValidator.validate_output(output, "documents_generation")
    all_issues.extend(json_result.issues)
    all_warnings.extend(json_result.warnings)
    confidence_scores.append(json_result.confidence_score)

    # Calculate overall confidence
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5

    return ValidationResult(
        is_valid=len(all_issues) == 0,
        confidence_score=avg_confidence,
        issues=all_issues,
        warnings=all_warnings
    )


def validate_chat_response(response: str,
                          user_question: str,
                          resume_data: Dict[str, Any]) -> ValidationResult:
    """Validate an Ask Henry chat response for fabrication."""
    grounding_validator = ResumeGroundingValidator(resume_data)
    chat_validator = ChatResponseValidator(grounding_validator)

    return chat_validator.validate_response(response, user_question)


def validate_resume_parse(resume_data: Dict[str, Any]) -> ValidationResult:
    """Validate that a parsed resume is complete enough to use."""
    return DataQualityValidator.validate_parsed_resume(resume_data)


def validate_jd_analysis(jd_data: Dict[str, Any]) -> ValidationResult:
    """Validate that a JD analysis is complete enough to use."""
    return DataQualityValidator.validate_jd_analysis(jd_data)


def validate_interview_prep(prep_data: Dict[str, Any],
                           resume_data: Dict[str, Any]) -> ValidationResult:
    """Validate interview prep content for fabrication."""
    grounding_validator = ResumeGroundingValidator(resume_data)
    output_validator = OutputValidator(grounding_validator)

    return output_validator.validate_interview_prep(prep_data)


# =============================================================================
# Response Helpers
# =============================================================================

def create_validation_error_response(result: ValidationResult) -> Dict[str, Any]:
    """Create an error response for blocked outputs."""
    return {
        "error": "validation_failed",
        "message": "Output blocked due to potential fabrication or incomplete data",
        "validation": result.to_dict(),
        "user_message": (
            "I noticed some issues with the generated content that need to be addressed. "
            "Some claims may not be fully supported by your resume. "
            "Please review your resume data or try again."
        ),
    }


def create_chat_fallback_response(result: ValidationResult, user_question: str) -> str:
    """Create a safe fallback response when chat validation fails."""
    return (
        "I want to make sure I give you accurate advice based on your actual experience. "
        "Could you help me understand more about your background related to this question? "
        f"Specifically regarding: {user_question[:100]}..."
    )


def add_validation_warnings_to_response(response: Dict[str, Any],
                                        result: ValidationResult) -> Dict[str, Any]:
    """Add validation warnings to a successful response."""
    if result.warnings:
        response["_validation"] = {
            "warnings": [
                {
                    "field": w.field_path,
                    "message": w.message,
                    "severity": w.severity.value,
                }
                for w in result.warnings
            ],
            "confidence_score": result.confidence_score
        }
    return response
