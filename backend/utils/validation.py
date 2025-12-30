"""Validation utilities for document quality and ATS keyword coverage"""

from typing import Dict, Any, List


def verify_ats_keyword_coverage(generated_text: str, ats_keywords: List[str]) -> Dict[str, Any]:
    """
    Verify that all ATS keywords from JD analysis appear in the generated resume.
    Returns coverage report with missing keywords and coverage percentage.
    """
    if not ats_keywords:
        return {
            "coverage_percentage": 100,
            "total_keywords": 0,
            "found_keywords": [],
            "missing_keywords": [],
            "status": "no_keywords"
        }

    generated_lower = generated_text.lower()
    found_keywords = []
    missing_keywords = []

    for keyword in ats_keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in generated_lower:
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    coverage_percentage = (len(found_keywords) / len(ats_keywords)) * 100 if ats_keywords else 100

    return {
        "coverage_percentage": round(coverage_percentage, 1),
        "total_keywords": len(ats_keywords),
        "found_keywords": found_keywords,
        "missing_keywords": missing_keywords,
        "status": "complete" if coverage_percentage == 100 else "incomplete"
    }


def validate_document_quality(generated_data: Dict[str, Any], source_resume: Dict[str, Any], jd_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate generated documents for quality issues:
    - Grounding (no fabrication)
    - ATS keyword coverage
    - Positioning alignment
    - Generic language detection
    """
    issues = []
    warnings = []

    # Extract resume output
    resume_output = generated_data.get("resume_output", {})
    full_text = resume_output.get("full_text", "")

    # 1. ATS Keyword Coverage Check
    ats_keywords = jd_analysis.get("ats_keywords", [])
    keyword_coverage = verify_ats_keyword_coverage(full_text, ats_keywords)

    if keyword_coverage["status"] == "incomplete":
        missing = keyword_coverage["missing_keywords"]
        issues.append(f"Missing ATS keywords: {', '.join(missing[:5])}" + (" and more" if len(missing) > 5 else ""))

    # 2. Generic Language Detection
    generic_phrases = [
        "team player", "hard worker", "detail-oriented", "results-driven",
        "proven track record", "dynamic professional", "highly motivated",
        "excellent communication skills", "go-getter", "self-starter"
    ]

    found_generic = []
    for phrase in generic_phrases:
        if phrase.lower() in full_text.lower():
            found_generic.append(phrase)

    if found_generic:
        warnings.append(f"Generic phrases detected: {', '.join(found_generic[:3])}")

    # 3. Company Name Validation (comprehensive check)
    source_companies = []
    source_company_titles = []  # Track company + title pairs
    for exp in source_resume.get("experience", []):
        company = exp.get("company", "")
        title = exp.get("title", "")
        if company:
            source_companies.append(company.lower())
            source_company_titles.append((company.lower(), title.lower()))

    generated_companies = []
    generated_company_titles = []
    for exp_section in resume_output.get("experience_sections", []):
        company = exp_section.get("company", "")
        title = exp_section.get("title", "")
        if company:
            generated_companies.append(company.lower())
            generated_company_titles.append((company.lower(), title.lower()))

    # Check if any generated company doesn't appear in source (FABRICATION)
    for gen_company in generated_companies:
        if gen_company and not any(gen_company in src or src in gen_company for src in source_companies):
            issues.append(f"Fabricated company: {gen_company}")

    # Check if any source company is missing from generated (OMISSION)
    for src_company in source_companies:
        if src_company and not any(src_company in gen or gen in src_company for gen in generated_companies):
            # Find which company was omitted
            matching_exp = next((exp for exp in source_resume.get("experience", []) if exp.get("company", "").lower() == src_company), None)
            company_name = matching_exp.get("company", src_company) if matching_exp else src_company
            issues.append(f"Omitted company from source resume: {company_name}")

    # 4. Experience Count Validation
    source_job_count = len(source_resume.get("experience", []))
    generated_job_count = len(resume_output.get("experience_sections", []))

    if generated_job_count < source_job_count:
        missing_count = source_job_count - generated_job_count
        issues.append(f"Missing {missing_count} job(s) from source resume (has {source_job_count}, generated {generated_job_count})")

    # 5. Minimum Length Check
    if len(full_text) < 200:
        issues.append("Resume text too short (< 200 characters)")

    # Calculate overall quality score
    quality_score = 100
    quality_score -= len(issues) * 15  # -15 per issue
    quality_score -= len(warnings) * 5  # -5 per warning
    quality_score = max(0, quality_score)

    return {
        "quality_score": quality_score,
        "issues": issues,
        "warnings": warnings,
        "keyword_coverage": keyword_coverage,
        "approval_status": "PASS" if quality_score >= 70 and len(issues) == 0 else "NEEDS_REVIEW"
    }
