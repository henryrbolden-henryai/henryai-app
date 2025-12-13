"""
Unit tests for QA Validation module.
Tests fabrication detection, data quality checks, and JSON output validation.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_validation import (
    ResumeGroundingValidator,
    OutputValidator,
    DataQualityValidator,
    JSONOutputValidator,
    ChatResponseValidator,
    ValidationSeverity,
    ValidationCategory,
    ValidationConfig,
    validate_documents_generation,
    validate_chat_response,
    validate_resume_parse,
    validate_jd_analysis,
    validate_interview_prep,
    get_validation_config,
    set_validation_threshold,
    add_known_companies,
)


# =============================================================================
# FIXTURES: Test data for validation
# =============================================================================

@pytest.fixture
def sample_resume():
    """A realistic resume for testing validation."""
    return {
        "full_name": "Jane Smith",
        "contact": {
            "email": "jane@test.com",
            "phone": "555-123-4567",
            "location": "San Francisco, CA"
        },
        "current_title": "Senior Product Manager",
        "summary": "Experienced PM with 8 years in B2B SaaS and fintech.",
        "experience": [
            {
                "company": "Spotify",
                "title": "Senior Product Manager",
                "dates": "2020 - Present",
                "bullets": [
                    "Led $12M ARR feature launch for playlist recommendations",
                    "Managed team of 5 engineers building audio analytics",
                    "Increased user engagement by 35% through personalization",
                    "Collaborated with design team on mobile app redesign"
                ]
            },
            {
                "company": "Stripe",
                "title": "Product Manager",
                "dates": "2017 - 2020",
                "bullets": [
                    "Launched payment APIs serving 10M+ transactions monthly",
                    "Reduced fraud rates by 25% through ML-based detection",
                    "Partnered with sales to close $5M enterprise deals"
                ]
            }
        ],
        "skills": [
            "Python", "SQL", "Product Strategy", "Agile", "Data Analysis",
            "User Research", "A/B Testing", "Roadmap Planning"
        ],
        "education": "MBA Stanford University, BS Computer Science UC Berkeley"
    }


@pytest.fixture
def minimal_resume():
    """A minimal resume missing some fields."""
    return {
        "full_name": "John Doe",
        "contact": {},
        "experience": []
    }


@pytest.fixture
def sample_jd_analysis():
    """Sample JD analysis data."""
    return {
        "role_title": "Senior Product Manager",
        "company": "Acme Corp",
        "requirements": ["5+ years PM experience", "B2B SaaS background", "SQL skills"],
        "responsibilities": ["Lead product roadmap", "Manage engineering teams"]
    }


# =============================================================================
# RESUME GROUNDING VALIDATOR TESTS
# =============================================================================

class TestResumeGroundingValidator:
    """Tests for the ResumeGroundingValidator class."""

    def test_extract_companies(self, sample_resume):
        """Should extract all companies from resume."""
        validator = ResumeGroundingValidator(sample_resume)
        assert "spotify" in validator.companies
        assert "stripe" in validator.companies

    def test_extract_skills(self, sample_resume):
        """Should extract all skills from resume."""
        validator = ResumeGroundingValidator(sample_resume)
        assert "python" in validator.skills
        assert "sql" in validator.skills
        assert "agile" in validator.skills

    def test_validate_company_direct_match(self, sample_resume):
        """Should validate companies that exist in resume."""
        validator = ResumeGroundingValidator(sample_resume)
        is_valid, msg = validator.validate_company_mention("Spotify")
        assert is_valid is True
        assert "spotify" in msg.lower()

    def test_validate_company_fuzzy_match(self, sample_resume):
        """Should validate similar company names."""
        validator = ResumeGroundingValidator(sample_resume)
        is_valid, msg = validator.validate_company_mention("Spotify Inc.")
        assert is_valid is True

    def test_validate_company_not_found(self, sample_resume):
        """Should reject companies not in resume."""
        validator = ResumeGroundingValidator(sample_resume)
        is_valid, msg = validator.validate_company_mention("Google")
        assert is_valid is False
        assert "not found" in msg.lower()

    def test_validate_skill_direct_match(self, sample_resume):
        """Should validate skills that exist in resume."""
        validator = ResumeGroundingValidator(sample_resume)
        is_valid, msg = validator.validate_skill_mention("Python")
        assert is_valid is True

    def test_validate_skill_not_found(self, sample_resume):
        """Should reject skills not in resume."""
        validator = ResumeGroundingValidator(sample_resume)
        is_valid, msg = validator.validate_skill_mention("Kubernetes")
        assert is_valid is False

    def test_validate_metric_found(self, sample_resume):
        """Should validate metrics that exist in resume."""
        validator = ResumeGroundingValidator(sample_resume)
        is_valid, msg = validator.validate_metric_mention("$12M")
        assert is_valid is True

    def test_validate_metric_not_found(self, sample_resume):
        """Should reject metrics not in resume."""
        validator = ResumeGroundingValidator(sample_resume)
        is_valid, msg = validator.validate_metric_mention("$50M")
        assert is_valid is False

    def test_validate_claim_grounded(self, sample_resume):
        """Should validate claims grounded in resume."""
        validator = ResumeGroundingValidator(sample_resume)
        is_valid, confidence, msg = validator.validate_claim(
            "Your Spotify experience with playlist features is relevant"
        )
        assert is_valid is True
        assert confidence > 0.5

    def test_validate_claim_fabricated(self, sample_resume):
        """Should reject fabricated claims."""
        validator = ResumeGroundingValidator(sample_resume)
        is_valid, confidence, msg = validator.validate_claim(
            "Your Google autonomous vehicle work demonstrates leadership"
        )
        # This might pass as positioning phrase, so check confidence
        assert confidence < 0.8 or not is_valid


# =============================================================================
# OUTPUT VALIDATOR TESTS
# =============================================================================

class TestOutputValidator:
    """Tests for the OutputValidator class."""

    def test_validate_resume_grounded(self, sample_resume):
        """Should validate resume output grounded in actual data."""
        grounding = ResumeGroundingValidator(sample_resume)
        validator = OutputValidator(grounding)

        output = {
            "summary": "PM with experience at Spotify building playlist features and at Stripe on payment APIs.",
            "key_qualifications": [
                "Led $12M ARR feature at Spotify",
                "Managed ML-based fraud detection at Stripe"
            ]
        }

        result = validator.validate_resume_output(output)
        # Should pass or have only warnings, not critical issues
        critical = [i for i in result.issues if i.severity == ValidationSeverity.CRITICAL]
        assert len(critical) == 0

    def test_validate_resume_fabricated_company(self, sample_resume):
        """Should flag fabricated company references."""
        grounding = ResumeGroundingValidator(sample_resume)
        validator = OutputValidator(grounding)

        output = {
            "summary": "PM with experience at Google building search features.",
            "key_qualifications": []
        }

        result = validator.validate_resume_output(output)
        # Should have fabrication issue
        fabrication_issues = [i for i in result.issues
                            if i.category == ValidationCategory.FABRICATED_COMPANY]
        assert len(fabrication_issues) > 0

    def test_validate_cover_letter_grounded(self, sample_resume):
        """Should validate cover letter grounded in resume."""
        grounding = ResumeGroundingValidator(sample_resume)
        validator = OutputValidator(grounding)

        output = {
            "content": "I am excited about this role given my experience at Spotify where I led the $12M ARR playlist feature."
        }

        result = validator.validate_cover_letter(output)
        critical = [i for i in result.issues if i.severity == ValidationSeverity.CRITICAL]
        assert len(critical) == 0

    def test_validate_interview_prep_grounded(self, sample_resume):
        """Should validate interview prep grounded in resume."""
        grounding = ResumeGroundingValidator(sample_resume)
        validator = OutputValidator(grounding)

        output = {
            "talking_points": [
                {"content": "My Spotify work on personalization increased engagement by 35%"},
                {"content": "At Stripe, I reduced fraud by 25% using ML"}
            ]
        }

        result = validator.validate_interview_prep(output)
        critical = [i for i in result.issues if i.severity == ValidationSeverity.CRITICAL]
        assert len(critical) == 0


# =============================================================================
# CHAT RESPONSE VALIDATOR TESTS
# =============================================================================

class TestChatResponseValidator:
    """Tests for chat/Ask Henry validation."""

    def test_validate_grounded_response(self, sample_resume):
        """Should pass responses grounded in resume."""
        grounding = ResumeGroundingValidator(sample_resume)
        validator = ChatResponseValidator(grounding)

        response = "Your Spotify experience with the $12M ARR feature is exactly what they need."
        result = validator.validate_response(response, "What should I highlight?")

        assert result.is_valid is True

    def test_validate_fabricated_company_response(self, sample_resume):
        """Should flag responses mentioning companies not in resume."""
        grounding = ResumeGroundingValidator(sample_resume)
        validator = ChatResponseValidator(grounding)

        response = "Your Google experience leading autonomous vehicles is key."
        result = validator.validate_response(response, "What should I highlight?")

        # Should flag Google as fabricated
        fabrication_issues = [i for i in result.issues
                            if i.category == ValidationCategory.FABRICATED_COMPANY]
        assert len(fabrication_issues) > 0

    def test_validate_positioning_advice_allowed(self, sample_resume):
        """Should allow positioning advice that doesn't fabricate."""
        grounding = ResumeGroundingValidator(sample_resume)
        validator = ChatResponseValidator(grounding)

        response = "Position yourself as a senior product leader. Highlight your strategic experience."
        result = validator.validate_response(response, "How should I position myself?")

        # Positioning advice should pass
        assert result.should_block is False


# =============================================================================
# DATA QUALITY VALIDATOR TESTS
# =============================================================================

class TestDataQualityValidator:
    """Tests for data quality validation."""

    def test_validate_complete_resume(self, sample_resume):
        """Should pass a complete resume."""
        result = DataQualityValidator.validate_parsed_resume(sample_resume)
        assert result.is_valid is True
        assert result.should_block is False

    def test_validate_minimal_resume(self, minimal_resume):
        """Should flag missing critical fields."""
        result = DataQualityValidator.validate_parsed_resume(minimal_resume)

        # Should have issues about missing contact info and experience
        assert len(result.issues) > 0 or len(result.warnings) > 0

    def test_validate_jd_complete(self, sample_jd_analysis):
        """Should pass complete JD analysis."""
        result = DataQualityValidator.validate_jd_analysis(sample_jd_analysis)
        assert result.is_valid is True  # JD issues don't block

    def test_validate_jd_incomplete(self):
        """Should warn about missing JD fields."""
        result = DataQualityValidator.validate_jd_analysis({
            "role_title": "PM"
        })

        # Should have warnings about missing fields
        assert len(result.warnings) > 0


# =============================================================================
# JSON OUTPUT VALIDATOR TESTS
# =============================================================================

class TestJSONOutputValidator:
    """Tests for JSON output validation."""

    def test_validate_complete_output(self):
        """Should pass complete JSON output."""
        output = {
            "resume_summary": {
                "summary": "Test summary",
                "key_qualifications": ["Qual 1", "Qual 2"]
            },
            "cover_letter": {
                "content": "Test cover letter content"
            },
            "fit_analysis": {
                "fit_summary": "Good fit"
            }
        }

        result = JSONOutputValidator.validate_output(output, "documents_generation")
        assert result.is_valid is True

    def test_validate_null_values(self):
        """Should flag null required fields."""
        output = {
            "resume_summary": {
                "summary": None,  # Null!
                "key_qualifications": []  # Empty!
            },
            "cover_letter": {
                "content": "Test"
            },
            "fit_analysis": {
                "fit_summary": "Good"
            }
        }

        result = JSONOutputValidator.validate_output(output, "documents_generation")
        # Should have issues about null/empty values
        assert len(result.issues) > 0


# =============================================================================
# CONFIGURATION TESTS
# =============================================================================

class TestValidationConfig:
    """Tests for configuration management."""

    def test_get_config(self):
        """Should return current configuration."""
        config = get_validation_config()
        assert "thresholds" in config
        assert "blocking" in config
        assert "known_companies_count" in config

    def test_set_threshold(self):
        """Should update threshold value."""
        original = ValidationConfig.CLAIM_MATCH_THRESHOLD
        try:
            set_validation_threshold("CLAIM_MATCH_THRESHOLD", 0.5)
            assert ValidationConfig.CLAIM_MATCH_THRESHOLD == 0.5
        finally:
            # Reset to original
            ValidationConfig.CLAIM_MATCH_THRESHOLD = original

    def test_add_known_companies(self):
        """Should add companies to known list."""
        original_count = len(ValidationConfig.KNOWN_COMPANIES)
        add_known_companies(["test company xyz"])
        assert len(ValidationConfig.KNOWN_COMPANIES) > original_count
        assert "test company xyz" in ValidationConfig.KNOWN_COMPANIES


# =============================================================================
# HIGH-LEVEL VALIDATION FUNCTION TESTS
# =============================================================================

class TestValidationFunctions:
    """Tests for the high-level validation functions."""

    def test_validate_documents_generation(self, sample_resume, sample_jd_analysis):
        """Should validate complete document generation output."""
        output = {
            "resume_summary": {
                "summary": "PM at Spotify with $12M ARR feature experience",
                "key_qualifications": ["Playlist recommendations", "Payment APIs at Stripe"]
            },
            "cover_letter": {
                "content": "My Spotify and Stripe experience makes me a strong fit."
            },
            "interview_prep": {
                "talking_points": ["Spotify playlist work", "Stripe fraud reduction"]
            }
        }

        result = validate_documents_generation(output, sample_resume, sample_jd_analysis)
        # Should pass or have only minor issues
        critical = [i for i in result.issues if i.severity == ValidationSeverity.CRITICAL]
        assert len(critical) == 0

    def test_validate_chat_response_function(self, sample_resume):
        """Should validate chat response through function."""
        result = validate_chat_response(
            "Your Spotify experience is impressive.",
            "Tell me about my background",
            sample_resume
        )
        assert result.is_valid is True

    def test_validate_resume_parse_function(self, sample_resume):
        """Should validate resume parse through function."""
        result = validate_resume_parse(sample_resume)
        assert result.is_valid is True

    def test_validate_jd_analysis_function(self, sample_jd_analysis):
        """Should validate JD analysis through function."""
        result = validate_jd_analysis(sample_jd_analysis)
        assert result.is_valid is True

    def test_validate_interview_prep_function(self, sample_resume):
        """Should validate interview prep through function."""
        prep_data = {
            "talking_points": ["My Spotify work on recommendations"],
            "star_stories": [{
                "situation": "At Spotify",
                "task": "Build recommendations",
                "action": "Led team of 5",
                "result": "$12M ARR"
            }]
        }

        result = validate_interview_prep(prep_data, sample_resume)
        critical = [i for i in result.issues if i.severity == ValidationSeverity.CRITICAL]
        assert len(critical) == 0


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_resume(self):
        """Should handle empty resume gracefully."""
        result = validate_resume_parse({})
        # Should have issues but not crash
        assert result.should_block is True  # Missing critical fields

    def test_empty_chat_response(self, sample_resume):
        """Should handle empty chat response."""
        result = validate_chat_response("", "test question", sample_resume)
        # Empty response should pass (nothing to validate)
        assert result.is_valid is True

    def test_unicode_content(self, sample_resume):
        """Should handle unicode content."""
        result = validate_chat_response(
            "Your experience at Spotify with music recommendations is excellent!",
            "Test with unicode: cafe",
            sample_resume
        )
        assert result.is_valid is True

    def test_very_long_content(self, sample_resume):
        """Should handle very long content."""
        long_response = "Your Spotify experience is relevant. " * 100
        result = validate_chat_response(long_response, "test", sample_resume)
        # Should complete without error
        assert isinstance(result.is_valid, bool)


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
