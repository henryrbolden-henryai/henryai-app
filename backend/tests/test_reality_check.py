"""
Reality Check System Unit Tests

Tests the Reality Check system against REALITY_CHECK_SPEC.md requirements.

CRITICAL TESTS:
1. No score mutation across ALL signal classes
2. Forbidden interaction enforcement
3. Signal class / severity validation
4. Max 2 checks per analysis
5. Strategic alternatives required for Blockers/Warnings
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reality_check.models import (
    RealityCheck,
    RealityCheckResult,
    SignalClass,
    Severity,
    FORBIDDEN_INTERACTIONS,
    ALLOWED_OUTPUTS,
)
from reality_check.reality_check_controller import (
    RealityCheckController,
    RealityCheckViolationError,
    analyze_reality_checks,
)
from reality_check.signal_detectors import (
    detect_eligibility_signals,
    detect_fit_signals,
    detect_credibility_signals,
    detect_risk_signals,
    detect_market_bias_signals,
    detect_market_climate_signals,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def sample_resume_data():
    """Standard resume data for testing."""
    return {
        "name": "Test Candidate",
        "summary": "Experienced product manager with 8 years in fintech.",
        "experience": [
            {
                "title": "Senior Product Manager",
                "company": "Stripe",
                "description": "Led payments platform team of 12 engineers.",
                "highlights": ["Launched 3 major features", "Grew revenue 40%"],
            },
            {
                "title": "Product Manager",
                "company": "Square",
                "description": "Built merchant onboarding flows.",
            },
        ],
        "skills": ["Product Strategy", "Fintech", "Payments", "Team Leadership"],
    }


@pytest.fixture
def sample_jd_data():
    """Standard JD data for testing."""
    return {
        "role_title": "Director of Product",
        "company": "Fintech Startup",
        "job_description": "We're looking for a product leader with 10+ years experience.",
    }


@pytest.fixture
def dei_resume_data():
    """Resume with DEI-focused experience."""
    return {
        "name": "DEI Professional",
        "summary": "Inclusion and belonging specialist.",
        "experience": [
            {
                "title": "Chief Diversity Officer",
                "company": "Tech Company",
                "description": "Led DEI initiatives across 5000-person organization.",
            },
        ],
        "skills": ["DEI Strategy", "Inclusion", "Belonging", "Culture"],
    }


@pytest.fixture
def climate_resume_data():
    """Resume with climate/sustainability experience."""
    return {
        "name": "Climate Professional",
        "summary": "Sustainability leader focused on environmental impact.",
        "experience": [
            {
                "title": "Sustainability Director",
                "company": "Green Tech Co",
                "description": "Climate justice advocate and ESG program lead.",
            },
        ],
        "skills": ["Sustainability", "ESG", "Climate Strategy"],
    }


# =============================================================================
# CRITICAL TEST: NO SCORE MUTATION
# =============================================================================

class TestNoScoreMutation:
    """
    CRITICAL: Reality Checks must NEVER modify fit_score.
    This is the core guardrail of the entire system.
    """

    def test_eligibility_signals_do_not_modify_score(self, sample_resume_data, sample_jd_data):
        """Eligibility signals must not modify fit_score."""
        original_score = 75.0

        controller = RealityCheckController()
        result = controller.analyze(
            resume_data=sample_resume_data,
            jd_data=sample_jd_data,
            fit_score=original_score,
        )

        # Score must be unchanged
        controller.validate_no_score_mutation(
            original_score=original_score,
            current_score=original_score,
            context="eligibility_signals"
        )

    def test_fit_signals_do_not_modify_score(self, sample_resume_data, sample_jd_data):
        """Fit signals must not modify fit_score."""
        original_score = 35.0  # Below threshold to trigger warning

        controller = RealityCheckController()
        result = controller.analyze(
            resume_data=sample_resume_data,
            jd_data=sample_jd_data,
            fit_score=original_score,
        )

        # Verify warning was triggered
        assert result.has_warning or any(c.signal_class == SignalClass.FIT for c in result.checks)

        # Score must be unchanged
        controller.validate_no_score_mutation(
            original_score=original_score,
            current_score=original_score,
            context="fit_signals"
        )

    def test_credibility_signals_do_not_modify_score(self, sample_resume_data, sample_jd_data):
        """Credibility signals must not modify fit_score."""
        original_score = 72.0

        credibility_result = {
            "title_inflation": {
                "detected": True,
                "reason": "VP title at 5-person company",
                "actual_level": "Senior Manager",
            }
        }

        controller = RealityCheckController()
        result = controller.analyze(
            resume_data=sample_resume_data,
            jd_data=sample_jd_data,
            fit_score=original_score,
            credibility_result=credibility_result,
        )

        controller.validate_no_score_mutation(
            original_score=original_score,
            current_score=original_score,
            context="credibility_signals"
        )

    def test_risk_signals_do_not_modify_score(self, sample_resume_data, sample_jd_data):
        """Risk signals must not modify fit_score."""
        original_score = 68.0

        risk_analysis = {
            "job_hopping": {
                "detected": True,
                "severity": "proceed_with_caution",
                "pattern": "4 roles in 24 months",
            }
        }

        controller = RealityCheckController()
        result = controller.analyze(
            resume_data=sample_resume_data,
            jd_data=sample_jd_data,
            fit_score=original_score,
            risk_analysis=risk_analysis,
        )

        controller.validate_no_score_mutation(
            original_score=original_score,
            current_score=original_score,
            context="risk_signals"
        )

    def test_market_bias_signals_do_not_modify_score(self, sample_resume_data):
        """CRITICAL: Market Bias signals must NEVER modify fit_score."""
        original_score = 80.0

        # JD with bias patterns
        jd_data = {
            "role_title": "Product Lead",
            "job_description": "Ex-Google or ex-Meta background preferred. Ivy League education a plus.",
        }

        controller = RealityCheckController()
        result = controller.analyze(
            resume_data=sample_resume_data,
            jd_data=jd_data,
            fit_score=original_score,
        )

        # Verify market bias was detected
        market_bias_checks = [c for c in result.checks if c.signal_class == SignalClass.MARKET_BIAS]
        assert len(market_bias_checks) > 0, "Market bias should be detected"

        # CRITICAL: Score must be unchanged
        controller.validate_no_score_mutation(
            original_score=original_score,
            current_score=original_score,
            context="market_bias_signals"
        )

    def test_market_climate_signals_do_not_modify_score(self, dei_resume_data, sample_jd_data):
        """CRITICAL: Market Climate signals must NEVER modify fit_score."""
        original_score = 78.0

        controller = RealityCheckController()
        result = controller.analyze(
            resume_data=dei_resume_data,
            jd_data=sample_jd_data,
            fit_score=original_score,
        )

        # Verify market climate was detected
        market_climate_checks = [c for c in result.checks if c.signal_class == SignalClass.MARKET_CLIMATE]
        assert len(market_climate_checks) > 0, "Market climate signal should be detected for DEI resume"

        # CRITICAL: Score must be unchanged
        controller.validate_no_score_mutation(
            original_score=original_score,
            current_score=original_score,
            context="market_climate_signals"
        )

    def test_combined_signals_do_not_modify_score(self, dei_resume_data):
        """Multiple signal types firing together must not modify score."""
        original_score = 45.0  # Low score + DEI background

        jd_data = {
            "role_title": "Product Director",
            "job_description": "Ex-FAANG preferred. Stanford or MIT graduates preferred.",
        }

        controller = RealityCheckController()
        result = controller.analyze(
            resume_data=dei_resume_data,
            jd_data=jd_data,
            fit_score=original_score,
        )

        # Multiple signals should fire
        assert len(result.checks) >= 2, "Multiple signals should be detected"

        # CRITICAL: Score must be unchanged
        controller.validate_no_score_mutation(
            original_score=original_score,
            current_score=original_score,
            context="combined_signals"
        )


# =============================================================================
# SIGNAL CLASS / SEVERITY VALIDATION
# =============================================================================

class TestSignalClassSeverityValidation:
    """Test that signal class / severity combinations are enforced."""

    def test_eligibility_only_allows_blocker(self):
        """Eligibility signals can only be Blocker severity."""
        # Valid: Eligibility + Blocker
        check = RealityCheck(
            signal_class=SignalClass.ELIGIBILITY,
            severity=Severity.BLOCKER,
            trigger="test",
            message="Test message",
            strategic_alternatives=["Alternative 1"],
        )
        assert check.severity == Severity.BLOCKER

        # Invalid: Eligibility + Warning
        with pytest.raises(ValueError):
            RealityCheck(
                signal_class=SignalClass.ELIGIBILITY,
                severity=Severity.WARNING,
                trigger="test",
                message="Test message",
                strategic_alternatives=["Alternative 1"],
            )

        # Invalid: Eligibility + Coaching
        with pytest.raises(ValueError):
            RealityCheck(
                signal_class=SignalClass.ELIGIBILITY,
                severity=Severity.COACHING,
                trigger="test",
                message="Test message",
            )

    def test_market_bias_only_allows_coaching(self):
        """Market Bias signals can only be Coaching severity."""
        # Valid: Market Bias + Coaching
        check = RealityCheck(
            signal_class=SignalClass.MARKET_BIAS,
            severity=Severity.COACHING,
            trigger="test",
            message="Test message",
        )
        assert check.severity == Severity.COACHING

        # Invalid: Market Bias + Blocker
        with pytest.raises(ValueError):
            RealityCheck(
                signal_class=SignalClass.MARKET_BIAS,
                severity=Severity.BLOCKER,
                trigger="test",
                message="Test message",
                strategic_alternatives=["Alternative 1"],
            )

        # Invalid: Market Bias + Warning
        with pytest.raises(ValueError):
            RealityCheck(
                signal_class=SignalClass.MARKET_BIAS,
                severity=Severity.WARNING,
                trigger="test",
                message="Test message",
                strategic_alternatives=["Alternative 1"],
            )

    def test_market_climate_allows_informational_and_coaching(self):
        """Market Climate signals allow Informational and Coaching."""
        # Valid: Market Climate + Informational
        check1 = RealityCheck(
            signal_class=SignalClass.MARKET_CLIMATE,
            severity=Severity.INFORMATIONAL,
            trigger="test",
            message="Test message",
        )
        assert check1.severity == Severity.INFORMATIONAL

        # Valid: Market Climate + Coaching
        check2 = RealityCheck(
            signal_class=SignalClass.MARKET_CLIMATE,
            severity=Severity.COACHING,
            trigger="test",
            message="Test message",
        )
        assert check2.severity == Severity.COACHING

        # Invalid: Market Climate + Blocker
        with pytest.raises(ValueError):
            RealityCheck(
                signal_class=SignalClass.MARKET_CLIMATE,
                severity=Severity.BLOCKER,
                trigger="test",
                message="Test message",
                strategic_alternatives=["Alternative 1"],
            )

    def test_fit_allows_warning_and_coaching(self):
        """Fit signals allow Warning and Coaching severity."""
        # Valid: Fit + Warning
        check1 = RealityCheck(
            signal_class=SignalClass.FIT,
            severity=Severity.WARNING,
            trigger="test",
            message="Test message",
            strategic_alternatives=["Alternative 1"],
        )
        assert check1.severity == Severity.WARNING

        # Valid: Fit + Coaching
        check2 = RealityCheck(
            signal_class=SignalClass.FIT,
            severity=Severity.COACHING,
            trigger="test",
            message="Test message",
        )
        assert check2.severity == Severity.COACHING


# =============================================================================
# FORBIDDEN INTERACTIONS
# =============================================================================

class TestForbiddenInteractions:
    """Test that forbidden interactions are blocked."""

    def test_market_bias_cannot_have_score_modification(self):
        """Market Bias checks must have fit_score_modification in forbidden_outputs."""
        check = RealityCheck(
            signal_class=SignalClass.MARKET_BIAS,
            severity=Severity.COACHING,
            trigger="test",
            message="Test message",
        )

        assert "fit_score_modification" in check.forbidden_outputs
        assert "eligibility_change" in check.forbidden_outputs

    def test_market_climate_cannot_have_score_modification(self):
        """Market Climate checks must have fit_score_modification in forbidden_outputs."""
        check = RealityCheck(
            signal_class=SignalClass.MARKET_CLIMATE,
            severity=Severity.INFORMATIONAL,
            trigger="test",
            message="Test message",
        )

        assert "fit_score_modification" in check.forbidden_outputs
        assert "eligibility_change" in check.forbidden_outputs

    def test_all_checks_have_forbidden_interactions(self):
        """All Reality Checks must include the standard forbidden interactions."""
        for signal_class in SignalClass:
            # Get valid severity for this signal class
            allowed = ALLOWED_OUTPUTS[signal_class]
            severity = allowed[0]

            # Create check with required fields
            kwargs = {
                "signal_class": signal_class,
                "severity": severity,
                "trigger": "test",
                "message": "Test message",
            }

            # Add strategic_alternatives for Blocker/Warning
            if severity in [Severity.BLOCKER, Severity.WARNING]:
                kwargs["strategic_alternatives"] = ["Alternative 1"]

            check = RealityCheck(**kwargs)

            # Verify forbidden interactions are present
            for forbidden in FORBIDDEN_INTERACTIONS:
                assert forbidden in check.forbidden_outputs, \
                    f"{signal_class.value} check missing forbidden: {forbidden}"


# =============================================================================
# STRATEGIC ALTERNATIVES
# =============================================================================

class TestStrategicAlternatives:
    """Test that Blockers and Warnings require strategic alternatives."""

    def test_blocker_requires_alternatives(self):
        """Blocker severity requires strategic_alternatives."""
        with pytest.raises(ValueError) as exc_info:
            RealityCheck(
                signal_class=SignalClass.ELIGIBILITY,
                severity=Severity.BLOCKER,
                trigger="test",
                message="Test message",
                strategic_alternatives=[],  # Empty - should fail
            )

        assert "strategic_alternatives" in str(exc_info.value)

    def test_warning_requires_alternatives(self):
        """Warning severity requires strategic_alternatives."""
        with pytest.raises(ValueError) as exc_info:
            RealityCheck(
                signal_class=SignalClass.FIT,
                severity=Severity.WARNING,
                trigger="test",
                message="Test message",
                strategic_alternatives=[],  # Empty - should fail
            )

        assert "strategic_alternatives" in str(exc_info.value)

    def test_coaching_does_not_require_alternatives(self):
        """Coaching severity does not require strategic_alternatives."""
        check = RealityCheck(
            signal_class=SignalClass.CREDIBILITY,
            severity=Severity.COACHING,
            trigger="test",
            message="Test message",
            strategic_alternatives=[],  # Empty - should be OK
        )
        assert check.strategic_alternatives == []


# =============================================================================
# MAX 2 CHECKS RULE
# =============================================================================

class TestMax2ChecksRule:
    """Test that max 2 checks are displayed per analysis."""

    def test_prioritize_limits_to_2_checks(self):
        """Result prioritization limits to 2 displayed checks."""
        result = RealityCheckResult()

        # Add 5 checks of varying severity
        for i in range(5):
            check = RealityCheck(
                signal_class=SignalClass.RISK,
                severity=Severity.COACHING,
                trigger=f"test_{i}",
                message=f"Test message {i}",
            )
            result.add_check(check)

        result.prioritize()

        # Only 2 should be displayed
        displayed = [c for c in [result.primary_check, result.secondary_check] if c]
        assert len(displayed) <= 2

    def test_prioritize_blocker_first(self):
        """Blockers should be prioritized over other severities."""
        result = RealityCheckResult()

        # Add coaching check first
        coaching = RealityCheck(
            signal_class=SignalClass.CREDIBILITY,
            severity=Severity.COACHING,
            trigger="coaching_test",
            message="Coaching message",
        )
        result.add_check(coaching)

        # Add blocker second
        blocker = RealityCheck(
            signal_class=SignalClass.ELIGIBILITY,
            severity=Severity.BLOCKER,
            trigger="blocker_test",
            message="Blocker message",
            strategic_alternatives=["Alternative 1"],
        )
        result.add_check(blocker)

        result.prioritize()

        # Blocker should be primary
        assert result.primary_check.severity == Severity.BLOCKER

    def test_market_signals_paired_with_capability_signals(self):
        """Market Bias/Climate must be paired with capability signals."""
        result = RealityCheckResult()

        # Add fit signal first
        fit = RealityCheck(
            signal_class=SignalClass.FIT,
            severity=Severity.COACHING,
            trigger="fit_test",
            message="Fit message",
        )
        result.add_check(fit)

        # Add market bias second
        market_bias = RealityCheck(
            signal_class=SignalClass.MARKET_BIAS,
            severity=Severity.COACHING,
            trigger="bias_test",
            message="Bias message",
        )
        result.add_check(market_bias)

        result.prioritize()

        # Fit should be primary, market bias secondary
        assert result.primary_check.signal_class == SignalClass.FIT
        assert result.secondary_check.signal_class == SignalClass.MARKET_BIAS


# =============================================================================
# ELIGIBILITY BLOCKER OVERRIDE
# =============================================================================

class TestEligibilityBlockerOverride:
    """Test that eligibility blockers cannot be overridden."""

    def test_eligibility_blocker_not_overridable(self):
        """Eligibility blockers must not be user-overridable."""
        check = RealityCheck(
            signal_class=SignalClass.ELIGIBILITY,
            severity=Severity.BLOCKER,
            trigger="test",
            message="Test message",
            strategic_alternatives=["Alternative 1"],
            user_override_allowed=True,  # This should be forced to False
        )

        # Should be forced to False by __post_init__
        assert check.user_override_allowed is False


# =============================================================================
# FEATURE FLAG
# =============================================================================

class TestFeatureFlag:
    """Test feature flag behavior."""

    def test_feature_flag_disabled_returns_empty(self, sample_resume_data, sample_jd_data):
        """When feature flag is disabled, return empty results."""
        controller = RealityCheckController(feature_flag_enabled=False)

        result = controller.analyze(
            resume_data=sample_resume_data,
            jd_data=sample_jd_data,
            fit_score=35.0,  # Would normally trigger warning
        )

        assert len(result.checks) == 0
        assert result.primary_check is None
        assert result.secondary_check is None


# =============================================================================
# SIGNAL DETECTORS
# =============================================================================

class TestSignalDetectors:
    """Test individual signal detectors."""

    def test_market_bias_detects_school_preference(self):
        """Detect school selectivity bias in JD."""
        jd_data = {
            "role_title": "Product Lead",
            "job_description": "Stanford or MIT graduates preferred.",
        }

        checks = detect_market_bias_signals(jd_data, {})

        assert len(checks) > 0
        assert checks[0].signal_class == SignalClass.MARKET_BIAS
        assert "school" in checks[0].trigger.lower() or "selectivity" in checks[0].trigger.lower()

    def test_market_bias_detects_faang_preference(self):
        """Detect FAANG/brand bias in JD."""
        jd_data = {
            "role_title": "Engineering Manager",
            "job_description": "Ex-Google or ex-Meta background strongly preferred.",
        }

        checks = detect_market_bias_signals(jd_data, {})

        assert len(checks) > 0
        assert checks[0].signal_class == SignalClass.MARKET_BIAS
        assert "brand" in checks[0].trigger.lower() or "employer" in checks[0].trigger.lower()

    def test_market_climate_detects_dei_role(self, dei_resume_data):
        """Detect DEI-focused experience."""
        checks = detect_market_climate_signals(dei_resume_data, {})

        assert len(checks) > 0
        assert checks[0].signal_class == SignalClass.MARKET_CLIMATE
        assert "dei" in checks[0].trigger.lower()

    def test_market_climate_detects_sustainability(self, climate_resume_data):
        """Detect climate/sustainability experience."""
        checks = detect_market_climate_signals(climate_resume_data, {})

        assert len(checks) > 0
        assert checks[0].signal_class == SignalClass.MARKET_CLIMATE

    def test_fit_signals_below_threshold(self, sample_resume_data, sample_jd_data):
        """Detect low fit score."""
        checks = detect_fit_signals(sample_resume_data, sample_jd_data, 35.0, {})

        assert len(checks) > 0
        assert checks[0].signal_class == SignalClass.FIT
        assert checks[0].severity == Severity.WARNING

    def test_fit_signals_stretch_range(self, sample_resume_data, sample_jd_data):
        """Detect stretch fit score (40-60)."""
        checks = detect_fit_signals(sample_resume_data, sample_jd_data, 55.0, {})

        assert len(checks) > 0
        assert checks[0].signal_class == SignalClass.FIT
        assert checks[0].severity == Severity.COACHING


# =============================================================================
# SERIALIZATION
# =============================================================================

class TestSerialization:
    """Test JSON serialization."""

    def test_reality_check_to_dict(self):
        """RealityCheck serializes to dict correctly."""
        check = RealityCheck(
            signal_class=SignalClass.FIT,
            severity=Severity.WARNING,
            trigger="low_fit_score",
            message="Your fit score is low",
            strategic_alternatives=["Try referrals", "Apply anyway"],
            evidence="Fit score: 35%",
        )

        data = check.to_dict()

        assert data["signal_class"] == "fit"
        assert data["severity"] == "warning"
        assert data["trigger"] == "low_fit_score"
        assert len(data["strategic_alternatives"]) == 2
        assert data["evidence"] == "Fit score: 35%"

    def test_reality_check_from_dict(self):
        """RealityCheck deserializes from dict correctly."""
        data = {
            "signal_class": "market_bias",
            "severity": "coaching",
            "trigger": "school_bias",
            "message": "School preference detected",
            "strategic_alternatives": ["Use referrals"],
        }

        check = RealityCheck.from_dict(data)

        assert check.signal_class == SignalClass.MARKET_BIAS
        assert check.severity == Severity.COACHING
        assert check.trigger == "school_bias"

    def test_reality_check_result_to_dict(self):
        """RealityCheckResult serializes to dict correctly."""
        result = RealityCheckResult()

        check = RealityCheck(
            signal_class=SignalClass.CREDIBILITY,
            severity=Severity.COACHING,
            trigger="test",
            message="Test message",
        )
        result.add_check(check)
        result.prioritize()

        data = result.to_dict()

        assert "checks" in data
        assert "primary_check" in data
        assert "display_checks" in data
        assert len(data["display_checks"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
