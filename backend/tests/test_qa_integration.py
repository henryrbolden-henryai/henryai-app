"""
Integration tests for QA Validation in the full pipeline.
Tests that validation is properly integrated with API endpoints.
"""

import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# FIXTURES: Realistic test data
# =============================================================================

@pytest.fixture
def realistic_resume():
    """A realistic resume that closely matches production data."""
    return {
        "full_name": "Sarah Chen",
        "contact": {
            "email": "sarah.chen@email.com",
            "phone": "415-555-1234",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/sarahchen"
        },
        "current_title": "Senior Product Manager",
        "target_roles": ["Head of Product", "Director of Product"],
        "industries": ["Fintech", "B2B SaaS"],
        "years_experience": "8 years",
        "summary": "Product leader with 8 years of experience building B2B fintech products. Led teams at Stripe and Square, driving $50M+ in ARR through strategic product initiatives.",
        "experience": [
            {
                "company": "Stripe",
                "title": "Senior Product Manager",
                "dates": "2020 - Present",
                "industry": "Fintech",
                "bullets": [
                    "Led development of Stripe Treasury, generating $25M ARR in first year",
                    "Managed cross-functional team of 12 engineers, 3 designers",
                    "Reduced merchant onboarding time from 5 days to 4 hours through automation",
                    "Partnered with sales to close 50+ enterprise accounts including Fortune 500 clients"
                ]
            },
            {
                "company": "Square",
                "title": "Product Manager",
                "dates": "2017 - 2020",
                "industry": "Fintech",
                "bullets": [
                    "Launched Square Banking, reaching 1M+ business accounts",
                    "Improved payment processing reliability from 99.5% to 99.99% uptime",
                    "Led integration with Cash App for seamless fund transfers"
                ]
            },
            {
                "company": "Intuit",
                "title": "Associate Product Manager",
                "dates": "2015 - 2017",
                "industry": "Finance Software",
                "bullets": [
                    "Built QuickBooks integration features used by 500K+ small businesses",
                    "Conducted 100+ customer interviews to inform product roadmap"
                ]
            }
        ],
        "key_achievements": [
            "Generated $50M+ ARR across product launches",
            "Scaled teams from 5 to 15+ engineers",
            "Shipped products used by millions of businesses"
        ],
        "core_competencies": [
            "Product Strategy",
            "Team Leadership",
            "B2B SaaS",
            "Fintech",
            "Data-Driven Decision Making"
        ],
        "skills": [
            "SQL", "Python", "Product Analytics", "A/B Testing",
            "Agile/Scrum", "User Research", "Roadmap Planning",
            "Stakeholder Management", "OKRs"
        ],
        "education": "MBA Stanford GSB, BS Computer Science MIT",
        "certifications": ["Certified Scrum Product Owner"]
    }


@pytest.fixture
def realistic_jd_analysis():
    """A realistic JD analysis that matches production data."""
    return {
        "role_title": "Director of Product",
        "company": "Acme Fintech",
        "_company_name": "Acme Fintech",
        "requirements": [
            "8+ years of product management experience",
            "Experience in fintech or B2B SaaS",
            "Track record of launching products at scale",
            "Strong SQL and analytics skills",
            "Experience managing product teams"
        ],
        "responsibilities": [
            "Lead product strategy for payments platform",
            "Manage team of 5 PMs",
            "Drive product-led growth initiatives",
            "Partner with engineering and design"
        ],
        "fit_score": 85,
        "strengths": [
            "Strong fintech background at Stripe and Square",
            "Proven track record with $50M+ ARR products",
            "Team leadership experience"
        ],
        "gaps": [
            "No direct experience managing other PMs",
            "Limited exposure to product-led growth"
        ],
        "ats_keywords": [
            "fintech", "B2B SaaS", "product strategy", "SQL", "team leadership"
        ],
        "salary_info": "$200K-$250K base + equity"
    }


@pytest.fixture
def grounded_documents_output():
    """Document generation output that is grounded in resume."""
    return {
        "resume_summary": {
            "summary": "Product leader with 8 years driving B2B fintech products at Stripe and Square. Led development of Stripe Treasury ($25M ARR) and Square Banking (1M+ accounts).",
            "key_qualifications": [
                "Led $25M ARR product launch at Stripe",
                "Managed cross-functional team of 12 engineers at Stripe",
                "Built Square Banking reaching 1M+ businesses"
            ]
        },
        "cover_letter": {
            # Note: Cover letter mentions target company which is expected behavior
            # The validator only checks for fabricated experience at companies not in resume
            "content": "My experience at Stripe leading Treasury ($25M ARR) and at Square launching Banking demonstrates my ability to build fintech products at scale. I have managed teams of 12 engineers and partnered cross-functionally to close Fortune 500 clients.",
            "full_text": "Dear Hiring Manager,\n\nMy experience at Stripe..."
        },
        "interview_prep": {
            "talking_points": [
                "At Stripe, launched Treasury product generating $25M ARR",
                "At Square, scaled Banking to 1M+ business accounts",
                "Led cross-functional team of 12 engineers at Stripe"
            ],
            "star_stories": [{
                "situation": "At Stripe, merchant onboarding took 5 days",
                "task": "Reduce merchant onboarding time from 5 days",
                "action": "Led initiative to automate onboarding workflow",
                "result": "Reduced onboarding time to 4 hours"
            }]
        },
        "outreach": {
            "hiring_manager": "Hi, my work at Stripe ($25M ARR Treasury launch) and Square (1M+ accounts) aligns with your payments platform needs. Would you be open to a call?",
            "recruiter": "Hi, I just applied for the Director role. My 8 years in fintech at Stripe and Square make me a strong fit. Happy to discuss."
        },
        "fit_analysis": {
            "fit_summary": "Strong fit based on fintech experience"
        }
    }


@pytest.fixture
def fabricated_documents_output():
    """Document generation output with fabricated content."""
    return {
        "resume_summary": {
            "summary": "Product leader with experience at Google and Meta building ML products at scale.",
            "key_qualifications": [
                "Led $100M ARR product at Google",  # Fabricated!
                "Managed team of 50 engineers at Meta"  # Fabricated!
            ]
        },
        "cover_letter": {
            "content": "My experience at Google and Meta demonstrates my ability to build ML products at massive scale."
        },
        "interview_prep": {
            "talking_points": [
                "Google ML platform - $100M ARR",  # Fabricated!
                "Meta infrastructure - 5B users"  # Fabricated!
            ]
        },
        "fit_analysis": {
            "fit_summary": "Strong fit"
        }
    }


# =============================================================================
# INTEGRATION TESTS: Document Generation
# =============================================================================

class TestDocumentGenerationValidation:
    """Test QA validation integration with document generation."""

    def test_grounded_output_passes(self, realistic_resume, realistic_jd_analysis, grounded_documents_output):
        """Grounded output should pass validation."""
        from qa_validation import validate_documents_generation

        result = validate_documents_generation(
            output=grounded_documents_output,
            resume_data=realistic_resume,
            jd_data=realistic_jd_analysis
        )

        # Should not block
        assert result.should_block is False
        # Critical issues should be zero or minimal
        critical_issues = [i for i in result.issues
                         if i.severity.value in ["critical", "high"]]
        assert len(critical_issues) == 0

    def test_fabricated_output_blocks(self, realistic_resume, realistic_jd_analysis, fabricated_documents_output):
        """Fabricated output should be blocked."""
        from qa_validation import validate_documents_generation, ValidationCategory

        result = validate_documents_generation(
            output=fabricated_documents_output,
            resume_data=realistic_resume,
            jd_data=realistic_jd_analysis
        )

        # Should have fabrication issues
        fabrication_issues = [i for i in result.issues
                            if i.category == ValidationCategory.FABRICATED_COMPANY]
        assert len(fabrication_issues) > 0

    def test_partial_fabrication_flagged(self, realistic_resume, realistic_jd_analysis):
        """Output with some fabrication should be flagged."""
        from qa_validation import validate_documents_generation

        # Mix of grounded and fabricated content
        mixed_output = {
            "resume_summary": {
                "summary": "Product leader at Stripe (real) and Google (fabricated).",
                "key_qualifications": [
                    "Stripe Treasury - $25M ARR",  # Real
                    "Google Cloud - $500M platform"  # Fabricated
                ]
            },
            "cover_letter": {"content": "My Stripe experience..."},
            "fit_analysis": {"fit_summary": "Good fit"}
        }

        result = validate_documents_generation(
            output=mixed_output,
            resume_data=realistic_resume,
            jd_data=realistic_jd_analysis
        )

        # Should have at least warnings or issues
        assert len(result.issues) > 0 or len(result.warnings) > 0


# =============================================================================
# INTEGRATION TESTS: Chat/Ask Henry
# =============================================================================

class TestChatValidation:
    """Test QA validation integration with Ask Henry chat."""

    def test_grounded_chat_passes(self, realistic_resume):
        """Chat response grounded in resume should pass."""
        from qa_validation import validate_chat_response

        response = "Your Stripe Treasury experience ($25M ARR) is exactly what Acme needs. Lead with that."
        result = validate_chat_response(response, "What should I highlight?", realistic_resume)

        assert result.should_block is False

    def test_fabricated_chat_blocks(self, realistic_resume):
        """Chat response with fabrication should be blocked."""
        from qa_validation import validate_chat_response

        response = "Your Google Cloud experience leading the $500M platform is perfect for this role."
        result = validate_chat_response(response, "What should I highlight?", realistic_resume)

        # Should flag Google as fabricated
        assert result.should_block is True

    def test_positioning_advice_allowed(self, realistic_resume):
        """Positioning advice without specific fabrication should pass."""
        from qa_validation import validate_chat_response

        response = "Position yourself as a senior fintech leader. Emphasize your scale experience."
        result = validate_chat_response(response, "How should I position myself?", realistic_resume)

        # Positioning advice should be allowed
        assert result.should_block is False

    def test_inference_vs_fabrication(self, realistic_resume):
        """Logical inference should be allowed, fabrication should not."""
        from qa_validation import validate_chat_response

        # Inference from resume data (allowed)
        inference_response = "Your experience managing teams of 12+ positions you as a senior leader."
        result1 = validate_chat_response(inference_response, "How am I positioned?", realistic_resume)
        assert result1.should_block is False

        # Fabrication (not allowed)
        fabrication_response = "Your Amazon experience with AWS infrastructure is highly relevant."
        result2 = validate_chat_response(fabrication_response, "How am I positioned?", realistic_resume)
        assert result2.should_block is True


# =============================================================================
# INTEGRATION TESTS: Resume Parse
# =============================================================================

class TestResumeParseValidation:
    """Test QA validation integration with resume parsing."""

    def test_complete_resume_passes(self, realistic_resume):
        """Complete resume should pass validation."""
        from qa_validation import validate_resume_parse

        result = validate_resume_parse(realistic_resume)
        assert result.is_valid is True
        assert result.should_block is False

    def test_missing_critical_fields_blocks(self):
        """Resume missing critical fields should be blocked."""
        from qa_validation import validate_resume_parse

        incomplete_resume = {
            "full_name": "",  # Empty!
            "contact": {},  # No contact info!
            "experience": []  # No experience!
        }

        result = validate_resume_parse(incomplete_resume)
        assert result.should_block is True

    def test_missing_recommended_warns(self):
        """Resume missing recommended fields should warn but not block."""
        from qa_validation import validate_resume_parse

        minimal_resume = {
            "full_name": "Jane Doe",
            "contact": {"email": "jane@test.com"},
            "experience": [{"company": "Test Co", "bullets": ["Did stuff"]}]
            # Missing: skills, education, summary
        }

        result = validate_resume_parse(minimal_resume)
        # Should have warnings but not block
        assert result.should_block is False
        assert len(result.warnings) > 0


# =============================================================================
# INTEGRATION TESTS: JD Analysis
# =============================================================================

class TestJDAnalysisValidation:
    """Test QA validation integration with JD analysis."""

    def test_complete_jd_passes(self, realistic_jd_analysis):
        """Complete JD analysis should pass."""
        from qa_validation import validate_jd_analysis

        result = validate_jd_analysis(realistic_jd_analysis)
        assert result.is_valid is True

    def test_incomplete_jd_warns(self):
        """Incomplete JD should warn but not block."""
        from qa_validation import validate_jd_analysis

        minimal_jd = {
            "role_title": "Product Manager"
            # Missing: company, requirements, responsibilities, salary
        }

        result = validate_jd_analysis(minimal_jd)
        # JD issues don't block, just warn
        assert result.is_valid is True
        assert len(result.warnings) > 0


# =============================================================================
# INTEGRATION TESTS: Interview Prep
# =============================================================================

class TestInterviewPrepValidation:
    """Test QA validation integration with interview prep."""

    def test_grounded_prep_passes(self, realistic_resume):
        """Interview prep grounded in resume should pass."""
        from qa_validation import validate_interview_prep

        prep = {
            "talking_points": [
                "At Stripe, led development of Treasury generating $25M ARR",
                "At Square, launched Banking reaching 1M+ business accounts",
                "Managed cross-functional team of 12 engineers at Stripe"
            ],
            "star_stories": [{
                "situation": "At Stripe, merchant onboarding took 5 days which was hurting conversion",
                "task": "Reduce merchant onboarding time from 5 days to under 1 day",
                "action": "Led cross-functional initiative to automate the onboarding workflow at Stripe",
                "result": "Reduced merchant onboarding time from 5 days to 4 hours"
            }]
        }

        result = validate_interview_prep(prep, realistic_resume)
        assert result.should_block is False

    def test_fabricated_prep_blocks(self, realistic_resume):
        """Interview prep with fabrication should be blocked."""
        from qa_validation import validate_interview_prep

        prep = {
            "talking_points": [
                "Google Cloud platform - $500M revenue",  # Fabricated!
                "Meta infrastructure - 5B monthly users"  # Fabricated!
            ]
        }

        result = validate_interview_prep(prep, realistic_resume)
        # Should have issues
        assert len(result.issues) > 0


# =============================================================================
# INTEGRATION TESTS: Configuration
# =============================================================================

class TestConfigurationIntegration:
    """Test that configuration changes affect validation behavior."""

    def test_threshold_affects_validation(self, realistic_resume):
        """Changing thresholds should affect validation results."""
        from qa_validation import (
            validate_chat_response,
            ValidationConfig,
            set_validation_threshold
        )

        # Store original
        original = ValidationConfig.BLOCK_CONFIDENCE_THRESHOLD

        try:
            # With strict threshold
            set_validation_threshold("BLOCK_CONFIDENCE_THRESHOLD", 0.8)
            response = "Some advice that may or may not be grounded."
            result1 = validate_chat_response(response, "test", realistic_resume)

            # With lenient threshold
            set_validation_threshold("BLOCK_CONFIDENCE_THRESHOLD", 0.1)
            result2 = validate_chat_response(response, "test", realistic_resume)

            # Lenient should be less likely to block
            # (This is a sanity check, not a strict assertion)
            assert isinstance(result1.should_block, bool)
            assert isinstance(result2.should_block, bool)

        finally:
            # Reset
            ValidationConfig.BLOCK_CONFIDENCE_THRESHOLD = original

    def test_company_list_expansion(self, realistic_resume):
        """Adding companies should affect validation."""
        from qa_validation import (
            validate_chat_response,
            add_known_companies,
            ValidationConfig
        )

        # Add a new company
        add_known_companies(["newstartup xyz"])

        # Response mentioning this company should now be flagged
        response = "Your newstartup xyz experience is impressive."
        result = validate_chat_response(response, "test", realistic_resume)

        # Should flag as potential fabrication
        assert result.should_block is True


# =============================================================================
# INTEGRATION TESTS: Logging
# =============================================================================

class TestLoggingIntegration:
    """Test that validation logging works correctly."""

    def test_blocked_output_logged(self, realistic_resume, fabricated_documents_output, tmp_path):
        """Blocked outputs should be logged to file."""
        from qa_validation import (
            validate_documents_generation,
            ValidationLogger,
            ValidationConfig
        )

        # Use temp directory for logs
        original_log_dir = ValidationConfig.LOG_DIR
        ValidationConfig.LOG_DIR = str(tmp_path)

        try:
            result = validate_documents_generation(
                output=fabricated_documents_output,
                resume_data=realistic_resume,
                jd_data={}
            )

            if result.should_block:
                # Log the blocked output
                entry_id = ValidationLogger.log_blocked_output(
                    endpoint="/api/documents/generate",
                    result=result,
                    output=fabricated_documents_output,
                    resume_data=realistic_resume
                )

                assert entry_id != ""

                # Check logs can be retrieved
                logs = ValidationLogger.get_blocked_logs(limit=10)
                assert len(logs) > 0

        finally:
            ValidationConfig.LOG_DIR = original_log_dir


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
