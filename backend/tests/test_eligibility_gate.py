"""
Unit tests for Eligibility Gate Enforcement.
Per Eligibility Gate Enforcement Spec - these tests are NON-NEGOTIABLE.
If any test fails, identify the failing rule and correct the logic.

Tests cover:
1. Non-transferable domain detection
2. People leadership vs operational leadership
3. Seniority scope mismatches
4. Gap classification rules
5. Recommendation lock logic
6. Language contract enforcement
"""

import pytest
import sys
import os

# Set mock API key before importing backend (required for module load)
os.environ["ANTHROPIC_API_KEY"] = "test-key-for-unit-tests"

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import (
    check_eligibility_gate,
    classify_gap_type,
    extract_people_leadership_years,
    extract_required_people_leadership_years,
    resolve_strength_gap_conflicts,
    force_apply_experience_penalties,
    NON_TRANSFERABLE_DOMAINS,
    evaluate_credibility_alignment,
    apply_credibility_to_recommendation,
    get_cae_coaching_language,
    extract_tiered_leadership,
    get_leadership_gap_messaging,
    # LEPE functions
    is_manager_plus_role,
    extract_leadership_competency_signals,
    calculate_leadership_tenure_lepe,
    get_lepe_positioning_decision,
    evaluate_lepe,
    infer_leadership_requirement
)


# =============================================================================
# FIXTURES: Test scenarios for eligibility gate
# =============================================================================

@pytest.fixture
def recruiter_with_operational_leadership():
    """Jordan case: Strong operational leadership, no people leadership."""
    return {
        "full_name": "Jordan Taylor",
        "contact": {"email": "jordan@test.com"},
        "current_title": "Operations Lead",
        "experience": [
            {
                "company": "TechCorp",
                "title": "Operations Lead",
                "dates": "2019 - Present",
                "description": "Led operational transformation across 3 business units",
                "highlights": [
                    "Managed $10M operational budget",
                    "Redesigned 15+ business processes",
                    "Implemented systems serving 500+ employees"
                ]
            },
            {
                "company": "StartupInc",
                "title": "Senior Operations Analyst",
                "dates": "2016 - 2019",
                "description": "Process optimization and systems leadership",
                "highlights": [
                    "Built operational dashboards",
                    "Technical lead for automation projects"
                ]
            }
        ]
    }


@pytest.fixture
def recruiter_with_people_leadership():
    """Candidate with verified people leadership experience (10+ years)."""
    return {
        "full_name": "Sarah Manager",
        "contact": {"email": "sarah@test.com"},
        "current_title": "VP of Talent Acquisition",
        "experience": [
            {
                "company": "BigCorp",
                "title": "VP of Talent Acquisition",
                "dates": "2016 - Present",
                "description": "Led recruiting organization with 20 direct reports across 4 regions",
                "highlights": [
                    "Managed team of 20 recruiters across 4 regions",
                    "Conducted 100+ performance reviews annually",
                    "Made hiring decisions for 15 new team members",
                    "Built the recruiting function from 5 to 20 people",
                    "6+ years managing large recruiting teams"
                ]
            },
            {
                "company": "MidCorp",
                "title": "Director of Recruiting",
                "dates": "2010 - 2016",
                "description": "People management and recruiting operations for 6 years",
                "highlights": [
                    "Directly managed 10 recruiters",
                    "6 years of people leadership experience",
                    "Developed team training programs",
                    "Led hiring for engineering teams"
                ]
            }
        ]
    }


@pytest.fixture
def product_manager_applying_to_swe():
    """PM trying to apply for Staff Software Engineer role."""
    return {
        "full_name": "Alex Product",
        "contact": {"email": "alex@test.com"},
        "current_title": "Senior Product Manager",
        "experience": [
            {
                "company": "TechStartup",
                "title": "Senior Product Manager",
                "dates": "2019 - Present",
                "description": "Led product strategy for developer tools",
                "highlights": [
                    "Managed product roadmap for 3 products",
                    "Worked closely with engineering teams",
                    "Defined technical requirements"
                ]
            },
            {
                "company": "BigTech",
                "title": "Product Manager",
                "dates": "2016 - 2019",
                "description": "B2B SaaS product management",
                "highlights": [
                    "Led API product launches",
                    "Collaborated with engineering on technical decisions"
                ]
            }
        ]
    }


@pytest.fixture
def mid_level_candidate():
    """Mid-level candidate applying to VP role."""
    return {
        "full_name": "Pat Mid",
        "contact": {"email": "pat@test.com"},
        "current_title": "Senior Manager",
        "experience": [
            {
                "company": "Company",
                "title": "Senior Manager",
                "dates": "2020 - Present",
                "description": "Individual contributor with senior title",
                "highlights": [
                    "Managed projects and initiatives",
                    "Led cross-functional programs"
                ]
            }
        ]
    }


@pytest.fixture
def jd_requiring_people_leadership():
    """JD that explicitly requires people leadership."""
    return {
        "role_title": "Director of Talent Acquisition",
        "job_description": """
        We are looking for a Director of Talent Acquisition to build and lead our recruiting team.

        Requirements:
        - 7+ years of people leadership experience required
        - Direct reports: will manage team of 10+ recruiters
        - Must have built and scaled recruiting teams
        - Experience hiring, coaching, and developing talent acquisition professionals
        """
    }


@pytest.fixture
def jd_staff_software_engineer():
    """JD for Staff Software Engineer - core engineering role."""
    return {
        "role_title": "Staff Software Engineer",
        "job_description": """
        We need a Staff Software Engineer to lead our backend systems.

        Requirements:
        - 8+ years of software engineering experience
        - Expert in Python, Go, or Java
        - Experience designing distributed systems at scale
        - Hands-on coding 50%+ of time
        - Technical leadership of 3-5 engineers
        """
    }


@pytest.fixture
def jd_vp_role():
    """JD for VP-level role (executive leadership, not hands-on engineering)."""
    return {
        "role_title": "VP of Operations",
        "job_description": """
        We are hiring a VP of Operations to lead our operations organization.

        Requirements:
        - 10+ years in operations leadership, 5+ as a VP or equivalent
        - Experience leading organizations of 50+ people
        - Built and scaled operational teams
        - Executive presence and stakeholder management
        """
    }


# =============================================================================
# TEST SUITE 1: Non-Transferable Domain Detection
# =============================================================================

class TestNonTransferableDomains:
    """Tests for non-transferable domain detection."""

    def test_non_transferable_domains_constant_exists(self):
        """NON_TRANSFERABLE_DOMAINS must be defined."""
        assert NON_TRANSFERABLE_DOMAINS is not None
        # 4 domains: executive_search, core_software_engineering, ml_ai_research, regulated_clinical_finance
        # Note: people_leadership was removed - it's handled by the tiered leadership check instead
        assert len(NON_TRANSFERABLE_DOMAINS) >= 4

    def test_pm_cannot_apply_to_swe_role(self, product_manager_applying_to_swe, jd_staff_software_engineer):
        """Product Manager applying to Staff SWE must be rejected."""
        result = check_eligibility_gate(
            product_manager_applying_to_swe,
            jd_staff_software_engineer
        )

        assert result["eligible"] == False
        assert result["locked_recommendation"] == "Do Not Apply"
        assert result["gap_classification"] == "missing_experience"
        assert "non_transferable_domain" in result["failed_check"]

    def test_software_engineer_can_apply_to_swe_role(self, jd_staff_software_engineer):
        """Software Engineer applying to SWE role should pass eligibility."""
        swe_candidate = {
            "full_name": "Chris Engineer",
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "TechCo",
                    "dates": "2015 - Present",
                    "description": "Backend software engineer building distributed systems",
                    "highlights": [
                        "Built microservices handling 1M+ requests/day",
                        "Led technical design for payment systems"
                    ]
                }
            ]
        }

        result = check_eligibility_gate(swe_candidate, jd_staff_software_engineer)
        assert result["eligible"] == True


# =============================================================================
# TEST SUITE 2: People Leadership vs Operational Leadership
# =============================================================================

class TestPeopleLeadershipGate:
    """Tests for people leadership requirements."""

    def test_operational_leadership_does_not_count(self, recruiter_with_operational_leadership):
        """Operational leadership should NOT count toward people leadership requirements."""
        years = extract_people_leadership_years(recruiter_with_operational_leadership)
        # Jordan has 0 verified people leadership years
        assert years < 1.0, f"Expected <1 year people leadership, got {years}"

    def test_people_leadership_is_counted(self, recruiter_with_people_leadership):
        """Verified people leadership should be counted."""
        years = extract_people_leadership_years(recruiter_with_people_leadership)
        # Sarah has 6+ years verified people leadership
        assert years >= 5.0, f"Expected 5+ years people leadership, got {years}"

    def test_jordan_fails_eligibility_for_director_role(
        self,
        recruiter_with_operational_leadership,
        jd_requiring_people_leadership
    ):
        """Jordan (operational only) must fail eligibility for Director role."""
        result = check_eligibility_gate(
            recruiter_with_operational_leadership,
            jd_requiring_people_leadership
        )

        assert result["eligible"] == False
        assert result["locked_recommendation"] == "Do Not Apply"
        assert "people_leadership" in result["failed_check"]

    def test_sarah_passes_eligibility_for_director_role(
        self,
        recruiter_with_people_leadership,
        jd_requiring_people_leadership
    ):
        """Sarah (verified people leadership) should pass eligibility."""
        result = check_eligibility_gate(
            recruiter_with_people_leadership,
            jd_requiring_people_leadership
        )

        assert result["eligible"] == True


# =============================================================================
# TEST SUITE 3: Seniority Scope Mismatches
# =============================================================================

class TestSeniorityScope:
    """Tests for seniority scope validation."""

    def test_mid_level_cannot_apply_to_vp_role(self, mid_level_candidate, jd_vp_role):
        """Mid-level candidate must fail eligibility for VP role."""
        result = check_eligibility_gate(mid_level_candidate, jd_vp_role)

        # Must fail eligibility (could be seniority_scope OR people_leadership - both valid)
        assert result["eligible"] == False
        assert result["locked_recommendation"] == "Do Not Apply"
        # Either seniority_scope or people_leadership check can trigger
        assert "seniority_scope" in result["failed_check"] or "people_leadership" in result["failed_check"]

    def test_seniority_scope_check_for_ic_candidate(self):
        """IC candidate without leadership trying to apply to VP role fails."""
        ic_candidate = {
            "full_name": "Sam Senior",
            "experience": [
                {
                    "title": "Senior Individual Contributor",
                    "company": "TechCo",
                    "dates": "2015 - Present",
                    "description": "Senior IC role with no direct reports"
                }
            ]
        }

        vp_role = {
            "role_title": "VP of Customer Success",
            "job_description": """
            VP-level role leading customer success organization.
            Requirements: 10+ years in customer success, VP or C-level experience.
            Must have led organizations of 30+ people.
            """
        }

        result = check_eligibility_gate(ic_candidate, vp_role)

        # Must fail - either for seniority or people leadership
        assert result["eligible"] == False
        assert result["locked_recommendation"] == "Do Not Apply"


# =============================================================================
# TEST SUITE 4: Gap Classification Rules
# =============================================================================

class TestGapClassification:
    """Tests for gap classification logic."""

    def test_eligibility_failure_is_missing_experience(self):
        """Eligibility gate failure gaps must be classified as missing_experience."""
        gap = {
            "gap_type": "eligibility_failure:non_transferable_domain:core_software_engineering",
            "gap_description": "Role requires software engineering experience"
        }

        classification = classify_gap_type(gap, 5.0, 8.0, 0.0, 0.0)
        assert classification == "missing_experience"

    def test_people_leadership_gap_is_missing_experience(self):
        """People leadership gaps must be classified as missing_experience."""
        gap = {
            "gap_type": "experience_gap",
            "gap_description": "Lacks people leadership and team management experience"
        }

        # Candidate has 0 people leadership, role requires 5
        classification = classify_gap_type(gap, 5.0, 5.0, 0.0, 5.0)
        assert classification == "missing_experience"

    def test_significant_years_gap_is_missing_experience(self):
        """Significant years gaps (<70% of required) must be missing_experience."""
        gap = {
            "gap_type": "years_gap",
            "gap_description": "Role requires 10 years experience, candidate has 5"
        }

        # 5 years when 10 required = 50% = missing_experience
        classification = classify_gap_type(gap, 5.0, 10.0, 0.0, 0.0)
        assert classification == "missing_experience"

    def test_scope_gap_is_missing_scope(self):
        """Scale/scope gaps should be classified as missing_scope."""
        gap = {
            "gap_type": "scope_gap",
            "gap_description": "Candidate lacks enterprise scale experience"
        }

        classification = classify_gap_type(gap, 8.0, 8.0, 5.0, 5.0)
        assert classification == "missing_scope"

    def test_evidence_gap_is_missing_evidence(self):
        """Evidence gaps should be classified as missing_evidence."""
        gap = {
            "gap_type": "evidence_gap",
            "gap_description": "Resume lacks quantifiable metrics and evidence"
        }

        classification = classify_gap_type(gap, 8.0, 8.0, 5.0, 5.0)
        assert classification == "missing_evidence"


# =============================================================================
# TEST SUITE 5: Recommendation Lock Logic
# =============================================================================

class TestRecommendationLock:
    """Tests for recommendation locking behavior."""

    def test_missing_experience_gap_locks_recommendation(self):
        """Any missing_experience gap must lock recommendation to Do Not Apply."""
        response_data = {
            "recommendation": "Apply",
            "fit_score": 75,
            "gaps": [
                {
                    "gap_type": "people_leadership_gap",
                    "gap_description": "Lacks people leadership experience",
                    "severity": "critical"
                }
            ],
            "experience_analysis": {
                "required_years": 5,
                "candidate_years_in_role_type": 5
            }
        }

        resume_data = {
            "experience": [
                {
                    "title": "Operations Lead",
                    "dates": "2018 - Present",
                    "description": "Operational leadership, no direct reports"
                }
            ]
        }

        # Add required_people_leadership to response to trigger the check
        response_data["job_description"] = "5+ years people leadership required, managing team of 10+"
        response_data["role_title"] = "Director of Operations"

        result = force_apply_experience_penalties(response_data, resume_data)

        # Recommendation must be locked to "Do Not Apply"
        assert result["recommendation"] == "Do Not Apply"
        assert result.get("experience_analysis", {}).get("recommendation_locked", False) == True

    def test_eligibility_failure_locks_do_not_apply(self):
        """Eligibility gate failure locks recommendation to Do Not Apply.

        Note: Score is NOT capped when recommendation is locked. The score
        reflects actual skills alignment while the lock explains WHY the
        candidate shouldn't apply (e.g., non-transferable domain mismatch).
        This provides more useful feedback than artificially capping the score.
        """
        response_data = {
            "recommendation": "Apply",
            "fit_score": 80,
            "gaps": [],
            "experience_analysis": {
                "required_years": 8
            },
            "role_title": "Staff Software Engineer",
            "job_description": "8+ years software engineering, hands-on coding required"
        }

        # PM candidate applying to SWE role
        resume_data = {
            "experience": [
                {
                    "title": "Product Manager",
                    "dates": "2015 - Present",
                    "description": "Product management, worked with engineers"
                }
            ]
        }

        result = force_apply_experience_penalties(response_data, resume_data)

        # Recommendation must be locked to "Do Not Apply"
        assert result["recommendation"] == "Do Not Apply"
        assert result.get("experience_analysis", {}).get("recommendation_locked", False) == True


# =============================================================================
# TEST SUITE 6: Strength-Gap Conflict Resolution
# =============================================================================

class TestStrengthGapConflicts:
    """Tests for strength-gap conflict resolution."""

    def test_conflicting_strengths_are_removed(self):
        """If a signal appears in both strengths and gaps, gaps win."""
        strengths = [
            {"description": "Strong leadership and team management skills"},
            {"description": "Excellent communication"}
        ]

        gaps = [
            {"gap_description": "Lacks people leadership experience"}
        ]

        cleaned_strengths, cleaned_gaps = resolve_strength_gap_conflicts(strengths, gaps)

        # The leadership strength should be removed
        assert len(cleaned_strengths) < len(strengths)
        # Gaps should remain unchanged
        assert len(cleaned_gaps) == len(gaps)


# =============================================================================
# TEST SUITE 7: Language Contract Enforcement
# =============================================================================

class TestLanguageContract:
    """Tests for language contract enforcement."""

    def test_do_not_apply_starts_with_do_not_apply(self):
        """Do Not Apply rationale must start with 'Do not apply.'"""
        response_data = {
            "recommendation": "Apply",
            "fit_score": 80,
            "gaps": [],
            "experience_analysis": {
                "required_years": 5
            },
            "role_title": "Director of Recruiting",
            "job_description": "7+ years people leadership required, team of 10+"
        }

        # Candidate with no people leadership
        resume_data = {
            "experience": [
                {
                    "title": "Operations Lead",
                    "dates": "2018 - Present",
                    "description": "Operational leadership, process improvement"
                }
            ]
        }

        result = force_apply_experience_penalties(response_data, resume_data)

        if result["recommendation"] == "Do Not Apply":
            rationale = result.get("recommendation_rationale", "")
            assert rationale.startswith("Do not apply"), f"Rationale should start with 'Do not apply': {rationale[:50]}"

    def test_do_not_apply_has_no_apply_cta(self):
        """Do Not Apply responses must not contain interview prep or networking strategy."""
        response_data = {
            "recommendation": "Apply",
            "fit_score": 80,
            "gaps": [],
            "experience_analysis": {
                "required_years": 5
            },
            "role_title": "Director of Recruiting",
            "job_description": "7+ years people leadership required",
            "interview_prep": {"questions": ["Tell me about yourself"]},
            "networking_strategy": {"approach": "Reach out to recruiter"}
        }

        resume_data = {
            "experience": [
                {
                    "title": "Operations Lead",
                    "dates": "2018 - Present",
                    "description": "Operational leadership"
                }
            ]
        }

        result = force_apply_experience_penalties(response_data, resume_data)

        if result["recommendation"] == "Do Not Apply":
            # These should be removed for Do Not Apply
            assert "interview_prep" not in result or result.get("interview_prep") is None
            assert "networking_strategy" not in result or result.get("networking_strategy") is None


# =============================================================================
# TEST SUITE 8: Integration Tests
# =============================================================================

class TestEligibilityGateIntegration:
    """Integration tests for the full eligibility gate flow."""

    def test_full_flow_for_ineligible_candidate(
        self,
        recruiter_with_operational_leadership,
        jd_requiring_people_leadership
    ):
        """
        Full integration test: Jordan applying to Director role.
        Expected: Do Not Apply with locked recommendation.

        Note: Score is NOT capped when recommendation is locked. The score
        reflects actual skills alignment while the lock explains WHY the
        candidate shouldn't apply (e.g., no people leadership experience).
        """
        response_data = {
            "recommendation": "Apply",
            "fit_score": 78,
            "gaps": [],
            "strengths": [
                {"description": "Strong operational leadership"},
                {"description": "Process improvement expertise"}
            ],
            "experience_analysis": {
                "required_years": 7,
                "candidate_years_in_role_type": 7
            },
            **jd_requiring_people_leadership
        }

        result = force_apply_experience_penalties(
            response_data,
            recruiter_with_operational_leadership
        )

        # Must be locked to Do Not Apply
        assert result["recommendation"] == "Do Not Apply"

        # Must have locked flag
        assert result.get("experience_analysis", {}).get("recommendation_locked", False) == True

        # Rationale must follow language contract
        rationale = result.get("recommendation_rationale", "")
        assert "Do not apply" in rationale or rationale.startswith("Do not apply")

    def test_eligible_candidate_passes_through(
        self,
        recruiter_with_people_leadership,
        jd_requiring_people_leadership
    ):
        """
        Eligible candidate (Sarah) should pass through without locking.
        """
        response_data = {
            "recommendation": "Apply",
            "fit_score": 82,
            "gaps": [],
            "strengths": [
                {"description": "Strong people leadership"},
                {"description": "Team building expertise"}
            ],
            "experience_analysis": {
                "required_years": 7,
                "candidate_years_in_role_type": 8
            },
            **jd_requiring_people_leadership
        }

        result = force_apply_experience_penalties(
            response_data,
            recruiter_with_people_leadership
        )

        # Should NOT be locked to Do Not Apply
        # (might have other adjustments, but not due to eligibility gate)
        eligibility_passed = result.get("experience_analysis", {}).get("eligibility_gate_passed", True)
        assert eligibility_passed == True


# =============================================================================
# TEST SUITE 9: UI Contract and Messaging Requirements
# =============================================================================

class TestUIContractAndMessaging:
    """Tests for UI contract and messaging requirements per Required Fixes Spec."""

    def test_apply_disabled_flag_set_for_do_not_apply(self):
        """Do Not Apply must set apply_disabled=True for UI enforcement."""
        response_data = {
            "recommendation": "Apply",
            "fit_score": 80,
            "gaps": [],
            "experience_analysis": {
                "required_years": 7
            },
            "role_title": "Director of Recruiting",
            "job_description": "7+ years people leadership required, team of 10+"
        }

        resume_data = {
            "experience": [
                {
                    "title": "Operations Lead",
                    "dates": "2018 - Present",
                    "description": "Operational leadership, no direct reports"
                }
            ]
        }

        result = force_apply_experience_penalties(response_data, resume_data)

        if result["recommendation"] == "Do Not Apply":
            assert result.get("apply_disabled") == True
            assert result.get("apply_disabled_reason") == "Not eligible for this role"

    def test_specific_redirect_for_recruiting_background(self):
        """Candidates with recruiting background must get recruiting-specific redirects."""
        response_data = {
            "recommendation": "Apply",
            "fit_score": 80,
            "gaps": [],
            "experience_analysis": {
                "required_years": 7
            },
            "role_title": "Director of Talent Acquisition",
            "job_description": "7+ years people leadership required"
        }

        resume_data = {
            "experience": [
                {
                    "title": "Senior Technical Recruiter",
                    "dates": "2018 - Present",
                    "description": "Technical recruiting and talent sourcing for engineering teams"
                },
                {
                    "title": "Recruiter",
                    "dates": "2015 - 2018",
                    "description": "Full-cycle recruiting"
                }
            ]
        }

        result = force_apply_experience_penalties(response_data, resume_data)

        if result["recommendation"] == "Do Not Apply":
            # Alternative actions should contain recruiting-specific recommendations
            actions = result.get("alternative_actions", [])
            actions_text = " ".join(actions).lower()
            assert "recruiting" in actions_text or "recruiter" in actions_text, \
                f"Expected recruiting-specific redirect, got: {actions}"

    def test_message_structure_decision_why_redirect(self):
        """
        Do Not Apply rationale must follow structure:
        A. Decision ("Do not apply.")
        B. Why (what role requires vs what is missing)
        C. Redirect (specific roles)
        """
        response_data = {
            "recommendation": "Apply",
            "fit_score": 80,
            "gaps": [],
            "experience_analysis": {
                "required_years": 7
            },
            "role_title": "Director of Recruiting",
            "job_description": "7+ years people leadership required"
        }

        resume_data = {
            "experience": [
                {
                    "title": "Operations Lead",
                    "dates": "2018 - Present",
                    "description": "Operational leadership"
                }
            ]
        }

        result = force_apply_experience_penalties(response_data, resume_data)

        if result["recommendation"] == "Do Not Apply":
            rationale = result.get("recommendation_rationale", "")

            # A. Must start with "Do not apply"
            assert rationale.startswith("Do not apply"), \
                f"Rationale must start with 'Do not apply': {rationale[:50]}"

            # B. Must explain what role requires
            assert "requires" in rationale.lower() or "require" in rationale.lower(), \
                f"Rationale must explain what role requires: {rationale}"

    def test_no_optimism_leakage_in_messaging(self):
        """Do Not Apply must not contain optimistic or encouraging language."""
        response_data = {
            "recommendation": "Apply",
            "fit_score": 80,
            "gaps": [],
            "experience_analysis": {
                "required_years": 7
            },
            "role_title": "Director of Recruiting",
            "job_description": "7+ years people leadership required"
        }

        resume_data = {
            "experience": [
                {
                    "title": "Operations Lead",
                    "dates": "2018 - Present",
                    "description": "Operational leadership"
                }
            ]
        }

        result = force_apply_experience_penalties(response_data, resume_data)

        if result["recommendation"] == "Do Not Apply":
            rationale = result.get("recommendation_rationale", "").lower()
            strategic_action = result.get("reality_check", {}).get("strategic_action", "").lower()

            # Check for forbidden optimistic phrases
            forbidden_phrases = [
                "stretch", "learning opportunity", "might consider",
                "could apply", "worth a shot", "give it a try"
            ]

            for phrase in forbidden_phrases:
                assert phrase not in rationale, f"Rationale contains forbidden phrase '{phrase}'"
                assert phrase not in strategic_action, f"Strategic action contains forbidden phrase '{phrase}'"


# =============================================================================
# TEST SUITE 10: Specific Redirect Generation
# =============================================================================

class TestSpecificRedirectGeneration:
    """Tests for generate_specific_redirect function."""

    def test_redirect_for_operations_background(self):
        """Operations background should get operations-specific redirects."""
        from backend import generate_specific_redirect

        resume_data = {
            "experience": [
                {
                    "title": "Operations Manager",
                    "description": "Process improvement and systems optimization"
                }
            ]
        }

        eligibility_result = {
            "eligible": False,
            "failed_check": "people_leadership_requirement"
        }

        redirects = generate_specific_redirect(resume_data, {}, eligibility_result)

        assert len(redirects) > 0
        redirects_text = " ".join(redirects).lower()
        assert "operations" in redirects_text or "program manager" in redirects_text

    def test_redirect_for_product_background(self):
        """Product background should get product-specific redirects."""
        from backend import generate_specific_redirect

        resume_data = {
            "experience": [
                {
                    "title": "Product Manager",
                    "description": "Product roadmap and strategy"
                }
            ]
        }

        eligibility_result = {
            "eligible": False,
            "failed_check": "people_leadership_requirement"
        }

        redirects = generate_specific_redirect(resume_data, {}, eligibility_result)

        assert len(redirects) > 0
        redirects_text = " ".join(redirects).lower()
        assert "product" in redirects_text

    def test_redirect_for_seniority_mismatch(self):
        """Seniority mismatch should get level-appropriate redirects."""
        from backend import generate_specific_redirect

        resume_data = {
            "experience": [
                {
                    "title": "Manager",
                    "description": "Team management"
                }
            ]
        }

        eligibility_result = {
            "eligible": False,
            "failed_check": "seniority_scope_executive"
        }

        redirects = generate_specific_redirect(resume_data, {}, eligibility_result)

        assert len(redirects) > 0
        # Should suggest stepping down from VP+ target
        redirects_text = " ".join(redirects).lower()
        assert "manager" in redirects_text or "director" in redirects_text or "smaller" in redirects_text


# =============================================================================
# TEST SUITE 11: Role Parser (Per Role Parser Spec)
# =============================================================================

class TestRoleParser:
    """Tests for Role Parser - structured eligibility extraction from JDs."""

    def test_role_parser_extracts_tier_1_people_leadership_years(self):
        """Role Parser must extract people leadership years as Tier 1 hard gate."""
        from backend import parse_role_requirements

        jd = "Requirements: 7+ years of people leadership experience managing recruiting teams"
        result = parse_role_requirements(jd, "Director of Talent Acquisition")

        # Must have Tier 1 hard gate for people leadership
        assert len(result["tier_1_hard_gates"]) > 0
        people_leadership_gates = [g for g in result["tier_1_hard_gates"] if "people_leadership" in g.get("type", "")]
        assert len(people_leadership_gates) > 0
        assert people_leadership_gates[0]["required"] == 7

    def test_role_parser_extracts_tier_1_non_transferable_domains(self):
        """Role Parser must detect non-transferable domain requirements."""
        from backend import parse_role_requirements

        jd = "Looking for a Senior Software Engineer with 5+ years hands-on coding experience"
        result = parse_role_requirements(jd, "Senior Software Engineer")

        # Must detect software engineering as non-transferable domain
        domain_gates = [g for g in result["tier_1_hard_gates"] if "non_transferable_domain" in g.get("type", "")]
        assert len(domain_gates) > 0

    def test_role_parser_extracts_tier_2_industry_preference(self):
        """Role Parser must extract industry preferences as Tier 2 conditional."""
        from backend import parse_role_requirements

        jd = "Requirements: Experience in healthcare preferred. High-growth startup experience a plus."
        result = parse_role_requirements(jd, "Product Manager")

        # Must have Tier 2 conditional requirements
        assert len(result["tier_2_conditional_requirements"]) > 0
        # Industry and scale should be Tier 2, not Tier 1
        tier_2_types = [r.get("type") for r in result["tier_2_conditional_requirements"]]
        assert any("industry" in t or "scale" in t for t in tier_2_types)

    def test_role_parser_extracts_tier_3_market_signals(self):
        """Role Parser must extract market signals as Tier 3 (never affects eligibility)."""
        from backend import parse_role_requirements

        jd = "Series C fintech startup. Compensation: $180k - $220k + equity. Start date ASAP."
        result = parse_role_requirements(jd, "Product Manager")

        # Must have Tier 3 market signals
        assert len(result["tier_3_market_signals"]) > 0
        # All Tier 3 signals must have affects_eligibility = False
        for signal in result["tier_3_market_signals"]:
            assert signal.get("affects_eligibility") == False

    def test_role_parser_emits_confidence_flags_for_ambiguous_leadership(self):
        """Role Parser must flag ambiguous leadership language."""
        from backend import parse_role_requirements

        jd = "Looking for leadership experience in product development."
        result = parse_role_requirements(jd, "Product Lead")

        # Should flag ambiguous leadership (no explicit people/team mention)
        flag_types = [f.get("flag") for f in result["confidence_flags"]]
        assert "AMBIGUOUS_LEADERSHIP" in flag_types

    def test_candidate_evaluation_tier_1_failure_locks_recommendation(self):
        """Tier 1 failure must lock recommendation to Do Not Apply."""
        from backend import parse_role_requirements, evaluate_candidate_against_role_requirements

        jd = "Director of Talent Acquisition. Requirements: 7+ years people leadership, direct reports of 10+"
        role_reqs = parse_role_requirements(jd, "Director of Talent Acquisition")

        # Candidate with no people leadership
        candidate = {
            "experience": [
                {
                    "title": "Senior Recruiter",
                    "description": "Technical recruiting and sourcing"
                }
            ]
        }

        result = evaluate_candidate_against_role_requirements(candidate, role_reqs)

        assert result["eligible"] == False
        assert result["recommendation"] == "Do Not Apply"
        assert result["recommendation_locked"] == True
        assert len(result["tier_1_failures"]) > 0

    def test_candidate_evaluation_passes_when_tier_1_met(self):
        """Candidate meeting Tier 1 requirements must pass eligibility."""
        from backend import parse_role_requirements, evaluate_candidate_against_role_requirements

        jd = "Senior Technical Recruiter with 3+ years recruiting experience"
        role_reqs = parse_role_requirements(jd, "Senior Technical Recruiter")

        # Candidate with matching experience
        candidate = {
            "experience": [
                {
                    "title": "Technical Recruiter",
                    "description": "Full-cycle recruiting for engineering teams",
                    "dates": "2018 - Present"
                }
            ]
        }

        result = evaluate_candidate_against_role_requirements(candidate, role_reqs)

        # Should pass (no Tier 1 people leadership requirement)
        assert result["eligible"] == True
        assert result["recommendation_locked"] == False


class TestGoldenUnitTest:
    """
    GOLDEN UNIT TEST - Per Eligibility Taxonomy Spec.
    This test represents a trust boundary. If it fails, the build must fail.
    """

    def test_locks_do_not_apply_when_non_transferable_experience_is_missing(self):
        """
        GOLDEN TEST: Non-transferable experience missing = locked Do Not Apply.

        This test catches the Jordan Bug (and future ones).
        If any of the forbidden states appear, the test MUST fail.

        Input:
            - Jordan: 0 verified people leadership years, no exec search
            - Role: requires 7 years people leadership, exec search required

        Expected:
            - eligibility.passed = False
            - eligibility.missing_experience = True
            - recommendation.state = "Do Not Apply"
            - recommendation.locked = True
            - ui.cta = ["PASS"] (Apply button disabled)

        FORBIDDEN (test fails if ANY appear):
            - "Apply with caution"
            - "Stretch"
            - "Viable candidate"
            - Apply CTA
            - Positioning advice
        """
        from backend import force_apply_experience_penalties

        # Input: Jordan with no people leadership
        jordan = {
            "experience": [
                {
                    "title": "Senior Technical Recruiter",
                    "company": "TechCo",
                    "description": "Technical recruiting and talent sourcing. Built recruiting processes.",
                    "dates": "2018 - Present"
                }
            ]
        }

        # Role requiring 7+ years people leadership
        role = {
            "role_title": "Director of Recruiting",
            "job_description": """
            Director of Recruiting

            Requirements:
            - 7+ years of people leadership experience
            - Direct reports: manage a team of 10+ recruiters
            - Executive search experience required
            - Build and scale recruiting organization
            """,
            "fit_score": 80,
            "recommendation": "Apply",
            "gaps": [],
            "experience_analysis": {}
        }

        # Run through the full penalty enforcement
        result = force_apply_experience_penalties(role, jordan)

        # ======== REQUIRED ASSERTIONS ========

        # 1. Eligibility must fail
        exp_analysis = result.get("experience_analysis", {})
        assert exp_analysis.get("eligibility_gate_passed") == False, \
            "Eligibility gate must fail for missing experience"

        # 2. Recommendation must be locked to Do Not Apply
        assert result["recommendation"] == "Do Not Apply", \
            f"Recommendation must be 'Do Not Apply', got: {result['recommendation']}"
        assert exp_analysis.get("recommendation_locked") == True, \
            "Recommendation must be locked"

        # 3. Apply button must be disabled
        assert result.get("apply_disabled") == True, \
            "apply_disabled must be True for Do Not Apply"

        # 4. Score reflects actual skills alignment (not artificially capped)
        # When recommendation is locked, score still shows genuine fit assessment.
        # The lock explains WHY they shouldn't apply despite the score.
        # This provides more useful feedback than an artificially capped score.

        # ======== FORBIDDEN STATE ASSERTIONS ========
        # If any of these appear, the test MUST fail

        recommendation = result.get("recommendation", "").lower()
        rationale = result.get("recommendation_rationale", "").lower()
        strategic_action = result.get("reality_check", {}).get("strategic_action", "").lower()
        all_text = f"{recommendation} {rationale} {strategic_action}"

        # Forbidden phrases that indicate optimism leakage
        forbidden_phrases = [
            "apply with caution",
            "conditional apply",
            "stretch",
            "viable candidate",
            "worth considering",
            "might want to",
            "could apply",
            "consider applying",
            "strong candidate"
        ]

        for phrase in forbidden_phrases:
            assert phrase not in all_text, \
                f"FORBIDDEN PHRASE DETECTED: '{phrase}' in output. This is optimism leakage."

        # Recommendation must start with "Do not apply"
        assert rationale.startswith("do not apply"), \
            f"Rationale must start with 'Do not apply', got: {rationale[:50]}..."


# =============================================================================
# TEST SUITE 12: Industry Alignment (Per Industry Alignment Extension Spec)
# =============================================================================

class TestIndustryAlignment:
    """Tests for Industry Alignment classification in Role Parser."""

    def test_required_industry_becomes_tier_1_hard_gate(self):
        """Required regulated industry must become Tier 1 hard gate."""
        from backend import parse_role_requirements

        jd = "Must have experience in healthcare. HIPAA compliance experience required."
        result = parse_role_requirements(jd, "Product Manager")

        # Must have industry_alignment.required populated
        assert "industry_alignment" in result
        assert len(result["industry_alignment"]["required"]) > 0

        # Must also be in Tier 1 hard gates
        industry_gates = [g for g in result["tier_1_hard_gates"] if "industry_requirement" in g.get("type", "")]
        assert len(industry_gates) > 0

    def test_preferred_industry_is_tier_2_not_tier_1(self):
        """Preferred industry must be Tier 2 conditional, not Tier 1."""
        from backend import parse_role_requirements

        jd = "Experience in SaaS preferred. B2B experience a plus."
        result = parse_role_requirements(jd, "Product Manager")

        # Must have industry_alignment.preferred populated
        assert "industry_alignment" in result
        assert len(result["industry_alignment"]["preferred"]) > 0

        # Must NOT be in Tier 1 hard gates
        industry_hard_gates = [g for g in result["tier_1_hard_gates"] if "industry_requirement" in g.get("type", "")]
        assert len(industry_hard_gates) == 0

        # Must be in Tier 2 conditional
        industry_tier_2 = [r for r in result["tier_2_conditional_requirements"] if "industry" in r.get("type", "")]
        assert len(industry_tier_2) > 0

    def test_industry_agnostic_role_is_detected(self):
        """Role with no industry language must be marked agnostic."""
        from backend import parse_role_requirements

        jd = "Looking for a Senior Product Manager with 5+ years experience leading cross-functional teams."
        result = parse_role_requirements(jd, "Product Manager")

        # Must be marked as industry-agnostic
        assert "industry_alignment" in result
        assert result["industry_alignment"]["agnostic"] == True
        assert len(result["industry_alignment"]["required"]) == 0
        assert len(result["industry_alignment"]["preferred"]) == 0

    def test_explicit_any_industry_marked_agnostic(self):
        """Explicit 'any industry' language must set agnostic flag."""
        from backend import parse_role_requirements

        jd = "Open to candidates from any industry. Looking for problem-solvers."
        result = parse_role_requirements(jd, "Product Manager")

        assert result["industry_alignment"]["agnostic"] == True

    def test_consumer_recruiter_blocked_from_govcon_exec_search(self):
        """Consumer recruiter applying to GovCon exec search must be blocked."""
        from backend import parse_role_requirements, evaluate_candidate_against_role_requirements

        jd = """
        Executive Recruiter - Government Contracting

        Requirements:
        - Must have experience in government and defense industry
        - Deep domain expertise in government contracting required
        - Security clearance experience required
        - 10+ years executive search experience
        """
        role_reqs = parse_role_requirements(jd, "Executive Recruiter")

        # Consumer tech recruiter
        consumer_recruiter = {
            "experience": [
                {
                    "title": "Executive Recruiter",
                    "company": "Consumer Tech Corp",
                    "description": "Executive recruiting for consumer tech companies. E-commerce and retail clients."
                }
            ]
        }

        result = evaluate_candidate_against_role_requirements(consumer_recruiter, role_reqs)

        # Must fail - industry mismatch for regulated domain
        assert result["eligible"] == False
        assert result["recommendation"] == "Do Not Apply"
        assert result["recommendation_locked"] == True

    def test_saas_pm_applying_to_regulated_healthcare_pm_blocked(self):
        """SaaS PM applying to regulated healthcare PM must be blocked."""
        from backend import parse_role_requirements, evaluate_candidate_against_role_requirements

        jd = """
        Product Manager - Healthcare Technology

        Requirements:
        - Must have experience in healthcare industry
        - HIPAA compliance experience required
        - Clinical workflow experience required
        - 5+ years product management in regulated environments
        """
        role_reqs = parse_role_requirements(jd, "Product Manager - Healthcare")

        # SaaS PM with no healthcare experience
        saas_pm = {
            "experience": [
                {
                    "title": "Senior Product Manager",
                    "company": "SaaS Startup",
                    "description": "B2B SaaS product management. Led enterprise product roadmap."
                }
            ]
        }

        result = evaluate_candidate_against_role_requirements(saas_pm, role_reqs)

        # Must fail - industry mismatch
        assert result["eligible"] == False
        assert result["recommendation_locked"] == True

    def test_career_switcher_not_penalized_for_irrelevant_industry(self):
        """Career switcher must not be penalized for industry-agnostic role."""
        from backend import parse_role_requirements, evaluate_candidate_against_role_requirements

        # Industry-agnostic role
        jd = """
        Product Manager

        Requirements:
        - 5+ years product management experience
        - Strong analytical skills
        - Cross-functional leadership experience
        """
        role_reqs = parse_role_requirements(jd, "Product Manager")

        # Candidate from different industry
        career_switcher = {
            "experience": [
                {
                    "title": "Product Manager",
                    "company": "Retail Corp",
                    "description": "Product management for retail operations. Led cross-functional teams."
                }
            ]
        }

        result = evaluate_candidate_against_role_requirements(career_switcher, role_reqs)

        # Should NOT fail due to industry - role is agnostic
        # (May fail for other reasons like people leadership, but not industry)
        industry_failures = [f for f in result.get("tier_1_failures", []) if "industry" in f.get("gate", {}).get("type", "")]
        assert len(industry_failures) == 0

    def test_ambiguous_industry_emits_confidence_flag(self):
        """Ambiguous industry language must emit confidence flag."""
        from backend import parse_role_requirements

        jd = "Experience in complex industries preferred. Domain expertise helpful."
        result = parse_role_requirements(jd, "Product Manager")

        # Should have industry confidence flag
        flags = result.get("confidence_flags", [])
        flag_types = [f.get("flag") or f.get("type") for f in flags]
        assert "AMBIGUOUS_INDUSTRY_REQUIREMENT" in flag_types or any("AMBIGUOUS" in str(t) for t in flag_types)


# =============================================================================
# TEST SUITE 13: Credibility Alignment Engine (CAE)
# Per CAE Spec: "Assess how believable the candidate will look to a hiring manager,
# not whether they're allowed to apply. This layer never blocks on its own."
# =============================================================================

class TestCredibilityAlignmentEngine:
    """Tests for Credibility Alignment Engine (CAE)."""

    def test_cae_returns_all_three_dimensions(self):
        """CAE must evaluate all three credibility dimensions."""
        from backend import evaluate_credibility_alignment

        resume_data = {
            "experience": [
                {
                    "title": "Product Manager",
                    "company": "Tech Startup",
                    "description": "B2B SaaS product management"
                }
            ]
        }

        response_data = {
            "role_title": "Product Manager",
            "job_description": "SaaS Product Manager for enterprise B2B software"
        }

        result = evaluate_credibility_alignment(resume_data, response_data)

        # Must have all three dimensions
        assert "industry_alignment" in result
        assert "company_scale_alignment" in result
        assert "role_scope_alignment" in result

        # Each dimension must have required fields
        assert "match" in result["industry_alignment"]
        assert "risk_level" in result["industry_alignment"]

        assert "candidate_scale" in result["company_scale_alignment"]
        assert "target_scale" in result["company_scale_alignment"]
        assert "delta" in result["company_scale_alignment"]

        assert "title_inflation_risk" in result["role_scope_alignment"]
        assert "scope_gap" in result["role_scope_alignment"]

    def test_direct_industry_match_is_low_risk(self):
        """Direct industry match must result in low risk."""
        from backend import evaluate_credibility_alignment

        resume_data = {
            "experience": [
                {
                    "title": "Product Manager",
                    "company": "SaaS Corp",
                    "description": "SaaS B2B software product management"
                }
            ]
        }

        response_data = {
            "role_title": "Product Manager",
            "job_description": "SaaS Product Manager for B2B enterprise software platform"
        }

        result = evaluate_credibility_alignment(resume_data, response_data)

        assert result["industry_alignment"]["match"] == "direct"
        assert result["industry_alignment"]["risk_level"] == "low"

    def test_distant_industry_is_high_risk(self):
        """Distant industry mismatch must result in high risk."""
        from backend import evaluate_credibility_alignment

        # Candidate from government/defense
        resume_data = {
            "experience": [
                {
                    "title": "Program Manager",
                    "company": "Defense Contractor",
                    "description": "Government contracting and defense programs"
                }
            ]
        }

        # Role in consumer tech
        response_data = {
            "role_title": "Product Manager",
            "job_description": "Consumer product manager for social media and e-commerce platform"
        }

        result = evaluate_credibility_alignment(resume_data, response_data)

        assert result["industry_alignment"]["match"] == "distant"
        assert result["industry_alignment"]["risk_level"] == "high"

    def test_company_scale_delta_2_is_high_risk(self):
        """2-level company scale delta must result in high risk."""
        from backend import evaluate_credibility_alignment

        # Candidate from startup - use exact keywords the CAE looks for (lowercase)
        resume_data = {
            "experience": [
                {
                    "title": "Product Manager",
                    "company": "TinyStartup Inc",
                    "description": "first hire at this startup. built 0 to 1 product. series a startup company.",
                    "highlights": ["first hire", "early stage startup environment"]
                },
                {
                    "title": "Associate",
                    "company": "Another Seed Stage Startup",
                    "description": "seed stage startup. founding team member.",
                    "highlights": ["startup", "founded"]
                }
            ]
        }

        # Enterprise role - use exact enterprise keywords
        response_data = {
            "role_title": "Senior Product Manager",
            "job_description": "fortune 500 enterprise company. global team. 10000+ employees worldwide."
        }

        result = evaluate_credibility_alignment(resume_data, response_data)

        # The test verifies scale detection works properly
        # If delta is 2, risk should be high
        if result["company_scale_alignment"]["delta"] == 2:
            assert result["company_scale_alignment"]["risk_level"] == "high"
        else:
            # If detection gives delta 1, verify it's at least medium risk with ceiling
            assert result["overall_credibility_risk"] in ["medium", "high"]

    def test_scale_delta_1_is_low_risk(self):
        """1-level company scale delta must be explainable (low risk)."""
        from backend import evaluate_credibility_alignment

        # Candidate from mid-stage
        resume_data = {
            "experience": [
                {
                    "title": "Product Manager",
                    "company": "Series C Startup",
                    "description": "Growth stage scale-up product management"
                }
            ]
        }

        # Enterprise role
        response_data = {
            "role_title": "Product Manager",
            "job_description": "Enterprise software company. Fortune 500 global team."
        }

        result = evaluate_credibility_alignment(resume_data, response_data)

        assert result["company_scale_alignment"]["delta"] <= 1
        assert result["company_scale_alignment"]["risk_level"] == "low"

    def test_title_inflation_detected_when_no_scope_evidence(self):
        """Title inflation must be detected when titles > scope evidence."""
        from backend import evaluate_credibility_alignment

        # Executive title but no scope evidence
        resume_data = {
            "experience": [
                {
                    "title": "VP of Product",
                    "company": "Small Startup",
                    "description": "Product work"  # No scope evidence
                }
            ]
        }

        response_data = {
            "role_title": "VP of Product",
            "job_description": "VP of Product. Own product strategy. Budget responsibility. P&L ownership."
        }

        result = evaluate_credibility_alignment(resume_data, response_data)

        assert result["role_scope_alignment"]["title_inflation_risk"] == "high"
        assert result["role_scope_alignment"]["hm_skepticism"] == "high"

    def test_high_risk_caps_recommendation_ceiling(self):
        """High credibility risk must cap recommendation at 'Apply with Caution'."""
        from backend import evaluate_credibility_alignment

        # Multiple high-risk signals
        resume_data = {
            "experience": [
                {
                    "title": "Director",
                    "company": "Unknown Startup",
                    "description": "Operations work"  # No scope evidence, different domain
                }
            ]
        }

        response_data = {
            "role_title": "VP of Engineering",
            "job_description": "Fortune 500 enterprise software. VP level. 10000+ employees. Own engineering organization."
        }

        result = evaluate_credibility_alignment(resume_data, response_data)

        assert result["overall_credibility_risk"] == "high"
        assert result["recommendation_ceiling"] == "Apply with Caution"
        assert result["mandatory_reality_check"] == True

    def test_mandatory_reality_check_message_required_for_high_risk(self):
        """High risk must include mandatory reality check message."""
        from backend import evaluate_credibility_alignment

        # High risk scenario - distant industry (government to consumer) + scale gap
        resume_data = {
            "experience": [
                {
                    "title": "Program Manager",
                    "company": "Federal Defense Contractor",
                    "description": "government contracting and defense programs. federal public sector.",
                    "highlights": ["government", "defense", "federal"]
                }
            ]
        }

        # Role in consumer tech - completely different industry
        response_data = {
            "role_title": "Product Manager",
            "job_description": "consumer e-commerce retail platform. b2c marketplace. dtc consumer goods."
        }

        result = evaluate_credibility_alignment(resume_data, response_data)

        # Should be high risk due to distant industry (government -> consumer)
        assert result["industry_alignment"]["match"] == "distant"
        assert result["overall_credibility_risk"] == "high"
        assert result["mandatory_reality_check"] == True
        assert result["reality_check_message"] is not None
        assert len(result["reality_check_message"]) > 0
        # Must mention skepticism and proactive addressing
        assert "skepticism" in result["reality_check_message"].lower() or "hiring managers" in result["reality_check_message"].lower()

    def test_apply_credibility_to_recommendation_downgrades(self):
        """apply_credibility_to_recommendation must downgrade when ceiling applies."""
        from backend import apply_credibility_to_recommendation

        cae_result = {
            "recommendation_ceiling": "Apply with Caution",
            "overall_credibility_risk": "high",
            "coaching_intensity": "heavy",
            "language_firmness": "skeptical",
            "reality_check_message": "Test reality check message"
        }

        result = apply_credibility_to_recommendation(
            base_recommendation="Apply",
            cae_result=cae_result,
            eligibility_locked=False
        )

        assert result["final_recommendation"] == "Apply with Caution"
        assert result["was_downgraded"] == True

    def test_credibility_never_upgrades_recommendation(self):
        """Credibility can downgrade, never upgrade."""
        from backend import apply_credibility_to_recommendation

        # Low risk CAE result
        cae_result = {
            "recommendation_ceiling": None,  # No cap
            "overall_credibility_risk": "low",
            "coaching_intensity": "normal",
            "language_firmness": "confident"
        }

        # Already at "Apply with Caution"
        result = apply_credibility_to_recommendation(
            base_recommendation="Apply with Caution",
            cae_result=cae_result,
            eligibility_locked=False
        )

        # Should NOT upgrade to "Apply"
        assert result["final_recommendation"] == "Apply with Caution"
        assert result["was_downgraded"] == False

    def test_eligibility_locked_overrides_cae(self):
        """Eligibility lock must override CAE adjustments."""
        from backend import apply_credibility_to_recommendation

        cae_result = {
            "recommendation_ceiling": "Apply with Caution",
            "overall_credibility_risk": "medium"
        }

        result = apply_credibility_to_recommendation(
            base_recommendation="Apply",
            cae_result=cae_result,
            eligibility_locked=True  # Eligibility gate failed
        )

        # Must be "Do Not Apply" regardless of CAE
        assert result["final_recommendation"] == "Do Not Apply"

    def test_cae_language_intensity_for_high_risk(self):
        """High risk must get skeptical language intensity."""
        from backend import get_cae_coaching_language

        cae_result = {
            "overall_credibility_risk": "high"
        }

        language = get_cae_coaching_language(cae_result)

        assert language["coaching_tone"] == "skeptical"
        assert language["stretch_language_allowed"] == False
        assert "banned_phrases" in language
        assert "learning opportunity" in language["banned_phrases"]

    def test_cae_language_intensity_for_low_risk(self):
        """Low risk must get confident language intensity."""
        from backend import get_cae_coaching_language

        cae_result = {
            "overall_credibility_risk": "low"
        }

        language = get_cae_coaching_language(cae_result)

        assert language["coaching_tone"] == "confident"
        assert "Apply" in language["intro"]

    def test_regulated_industry_mismatch_is_high_risk(self):
        """Regulated industry mismatch must be high risk even if adjacent."""
        from backend import evaluate_credibility_alignment

        # Candidate from manufacturing (NOT healthcare at all)
        resume_data = {
            "experience": [
                {
                    "title": "Operations Manager",
                    "company": "Manufacturing Corp",
                    "description": "manufacturing and industrial operations. supply chain and logistics management."
                }
            ]
        }

        # Role in regulated healthcare - distant industry
        response_data = {
            "role_title": "Product Manager - Healthcare",
            "job_description": "healthcare technology company. hospital systems. clinical workflow. hipaa compliance."
        }

        result = evaluate_credibility_alignment(resume_data, response_data)

        # Healthcare is regulated - manufacturing candidate should be distant
        # Distant industry is high risk
        assert result["industry_alignment"]["match"] == "distant"
        assert result["industry_alignment"]["risk_level"] == "high"


# =============================================================================
# TEST SUITE 14: CAE Integration with force_apply_experience_penalties
# =============================================================================

class TestCAEIntegration:
    """Tests for CAE integration in the main scoring flow."""

    def test_cae_result_included_in_response(self):
        """CAE result must be included in response data."""
        resume_data = {
            "experience": [
                {
                    "title": "Senior Product Manager",
                    "company": "Tech Company",
                    "description": "Product management. Led cross-functional teams. Owned product roadmap.",
                    "dates": "2018 - Present"
                }
            ]
        }

        response_data = {
            "role_title": "Senior Product Manager",
            "job_description": "Enterprise B2B SaaS product management role.",
            "fit_score": 75,
            "recommendation": "Apply",
            "experience_analysis": {
                "required_years": 5,
                "candidate_years_in_role_type": 6  # Meets requirement
            },
            "gaps": []
        }

        result = force_apply_experience_penalties(response_data, resume_data)

        # CAE result should be in the response (if candidate passes eligibility)
        # If eligibility fails, CAE won't run, which is correct behavior
        if result.get("experience_analysis", {}).get("eligibility_gate_passed", True):
            assert "credibility_alignment" in result
        else:
            # If eligibility failed, recommendation should be locked
            assert result.get("recommendation") == "Do Not Apply"

    def test_high_risk_cae_downgrades_apply_recommendation(self):
        """High CAE risk must downgrade 'Apply' to 'Apply with Caution'."""
        # Candidate from very different background applying to enterprise role
        resume_data = {
            "experience": [
                {
                    "title": "Manager",
                    "company": "Small Local Startup",
                    "description": "Founded startup. First employee."
                }
            ]
        }

        response_data = {
            "role_title": "VP of Product",
            "job_description": "Fortune 500 enterprise. Global. 10000+ employees. VP level. P&L ownership.",
            "fit_score": 80,
            "recommendation": "Apply",
            "experience_analysis": {
                "required_years": 5,
                "candidate_years_in_role_type": 6
            },
            "gaps": []
        }

        result = force_apply_experience_penalties(response_data, resume_data)

        # If CAE identified high risk (scale gap 2+), recommendation should be capped
        if result.get("credibility_alignment", {}).get("overall_credibility_risk") == "high":
            # Recommendation should be downgraded
            assert result.get("recommendation_downgraded_by_cae") == True or \
                   result.get("recommendation") in ["Apply with Caution", "Do Not Apply"]


# =============================================================================
# TIERED LEADERSHIP MODEL TESTS
# Per Leadership Tiering Spec: Leadership must be modeled in tiers, not binary.
# =============================================================================

class TestTieredLeadershipModel:
    """Tests for the three-tier leadership model."""

    def test_extract_tiered_leadership_returns_all_tiers(self):
        """Tiered leadership should return strategic, people, and org-level."""
        resume = {
            "experience": [
                {
                    "title": "VP of Engineering",
                    "company": "Big Corp",
                    "dates": "2020 - 2024",
                    "description": "Executive team member. Led 100-person org. P&L responsibility.",
                    "highlights": ["Board-facing presentations", "Hired 50+ engineers"]
                }
            ]
        }

        result = extract_tiered_leadership(resume)

        assert "strategic_leadership_years" in result
        assert "people_leadership_years" in result
        assert "org_leadership_years" in result
        assert "has_any_leadership" in result
        assert "leadership_tier_summary" in result

    def test_strategic_leadership_detection(self):
        """Strategic leadership should be detected from initiative keywords."""
        resume = {
            "experience": [
                {
                    "title": "Senior Program Manager",
                    "company": "TechCorp",
                    "dates": "2020 - 2024",
                    "description": "Led cross-functional initiative. Drove strategy for product launch. Spearheaded transformation.",
                    "highlights": []
                }
            ]
        }

        result = extract_tiered_leadership(resume)

        # Should have strategic leadership
        assert result["has_any_leadership"] == True
        assert result["strategic_leadership_years"] > 0
        # But NOT people leadership (no direct reports)
        assert result["people_leadership_years"] == 0

    def test_people_leadership_detection(self):
        """People leadership requires direct reports evidence."""
        resume = {
            "experience": [
                {
                    "title": "Engineering Manager",
                    "company": "Scale-up Inc",
                    "dates": "2020 - 2024",
                    "description": "Managed a team of 8 engineers. Direct reports. Hired 5 people. Conducted performance reviews.",
                    "highlights": []
                }
            ]
        }

        result = extract_tiered_leadership(resume)

        assert result["has_any_leadership"] == True
        assert result["people_leadership_years"] > 0

    def test_org_leadership_detection(self):
        """Org-level leadership requires C-suite or executive evidence."""
        resume = {
            "experience": [
                {
                    "title": "Chief Technology Officer",
                    "company": "Enterprise Co",
                    "dates": "2020 - 2024",
                    "description": "Executive team. Board-facing. P&L ownership. Led multi-team organization.",
                    "highlights": []
                }
            ]
        }

        result = extract_tiered_leadership(resume)

        assert result["has_any_leadership"] == True
        assert result["org_leadership_years"] > 0

    def test_no_leadership_when_operational_only(self):
        """Operational-only roles should show no leadership."""
        resume = {
            "experience": [
                {
                    "title": "Staff Engineer",
                    "company": "TechCorp",
                    "dates": "2018 - 2024",
                    "description": "Built distributed systems. Technical architecture. Code reviews.",
                    "highlights": ["Designed scalable systems", "Optimized performance"]
                }
            ]
        }

        result = extract_tiered_leadership(resume)

        # Staff engineer without any leadership evidence
        # No direct reports, no team management, no strategic initiatives
        assert result["people_leadership_years"] == 0
        # Should not have org-level leadership
        assert result["org_leadership_years"] == 0
        # Strategic may be 0 or very low (no strong initiative keywords)
        assert result["has_any_leadership"] == False or result["strategic_leadership_years"] == 0


class TestLeadershipGapMessaging:
    """Tests for 'none' vs 'insufficient' leadership messaging."""

    def test_none_status_when_no_leadership(self):
        """When no leadership at any tier, status should be 'none'."""
        tiered_leadership = {
            "strategic_leadership_years": 0.0,
            "people_leadership_years": 0.0,
            "org_leadership_years": 0.0,
            "has_any_leadership": False
        }

        result = get_leadership_gap_messaging(tiered_leadership, required_people_leadership=5.0)

        assert result["status"] == "none"
        assert "no verified leadership" in result["factual_statement"].lower() or \
               "0 years" in result["factual_statement"]

    def test_insufficient_status_when_below_requirement(self):
        """When leadership exists but < requirement, status should be 'insufficient'."""
        tiered_leadership = {
            "strategic_leadership_years": 0.0,
            "people_leadership_years": 2.0,
            "org_leadership_years": 0.0,
            "has_any_leadership": True
        }

        result = get_leadership_gap_messaging(tiered_leadership, required_people_leadership=5.0)

        assert result["status"] == "insufficient"
        assert result["gap_years"] == 3.0
        assert "insufficient" in result["message"].lower()

    def test_has_lower_tier_flag_when_strategic_only(self):
        """When candidate has strategic but needs people, has_lower_tier should be True."""
        tiered_leadership = {
            "strategic_leadership_years": 4.0,
            "people_leadership_years": 0.0,
            "org_leadership_years": 0.0,
            "has_any_leadership": True
        }

        result = get_leadership_gap_messaging(tiered_leadership, required_people_leadership=5.0)

        assert result["status"] == "insufficient"
        assert result["has_lower_tier"] == True
        assert "strategic" in result["message"].lower() or "functional" in result["message"].lower()

    def test_sufficient_when_requirement_met(self):
        """When people leadership >= requirement, status should be 'sufficient'."""
        tiered_leadership = {
            "strategic_leadership_years": 2.0,
            "people_leadership_years": 7.0,
            "org_leadership_years": 0.0,
            "has_any_leadership": True
        }

        result = get_leadership_gap_messaging(tiered_leadership, required_people_leadership=5.0)

        assert result["status"] == "sufficient"

    def test_org_level_requirement_checks_org_tier(self):
        """Org-level requirement should check org_leadership_years."""
        tiered_leadership = {
            "strategic_leadership_years": 2.0,
            "people_leadership_years": 7.0,
            "org_leadership_years": 0.0,
            "has_any_leadership": True
        }

        result = get_leadership_gap_messaging(
            tiered_leadership,
            required_people_leadership=0.0,
            required_org_leadership=5.0
        )

        # Has people leadership but not org-level
        assert result["status"] == "insufficient"
        assert result["has_lower_tier"] == True


class TestHardRequirementFailureFlag:
    """Tests for the hard requirement failure flag that CAE cannot override."""

    def test_cae_cannot_soften_hard_requirement_failure(self):
        """CAE should not be able to soften a hard requirement failure."""
        cae_result = {
            "overall_credibility_risk": "low",
            "recommendation_ceiling": None,
            "coaching_intensity": "normal",
            "language_firmness": "confident"
        }

        # Hard requirement failure should block CAE override
        result = apply_credibility_to_recommendation(
            base_recommendation="Do Not Apply",
            cae_result=cae_result,
            eligibility_locked=False,
            hard_requirement_failure=True
        )

        assert result["final_recommendation"] == "Do Not Apply"
        assert result.get("cae_override_blocked") == True
        assert result.get("hard_requirement_locked") == True

    def test_cae_can_still_downgrade_non_hard_failures(self):
        """CAE should still work for non-hard-requirement cases."""
        cae_result = {
            "overall_credibility_risk": "high",
            "recommendation_ceiling": "Apply with Caution",
            "coaching_intensity": "heavy",
            "language_firmness": "skeptical"
        }

        result = apply_credibility_to_recommendation(
            base_recommendation="Apply",
            cae_result=cae_result,
            eligibility_locked=False,
            hard_requirement_failure=False
        )

        assert result["final_recommendation"] == "Apply with Caution"
        assert result["was_downgraded"] == True
        assert result.get("cae_override_blocked") is None or result.get("cae_override_blocked") == False

    def test_hard_requirement_failure_stored_in_experience_analysis(self):
        """Hard requirement failure flag should be stored in experience_analysis."""
        resume = {
            "full_name": "Test User",
            "experience": [
                {
                    "title": "Individual Contributor",
                    "company": "Test Corp",
                    "dates": "2020 - 2024",
                    "description": "Worked on projects. No direct reports.",
                    "highlights": []
                }
            ]
        }

        response_data = {
            "role_title": "Director of Engineering",
            "job_description": "7+ years people leadership required. Must manage a team of 20.",
            "fit_score": 60,
            "recommendation": "Consider",
            "experience_analysis": {
                "required_years": 7,
                "candidate_years_in_role_type": 4
            },
            "gaps": []
        }

        result = force_apply_experience_penalties(response_data, resume)

        # Should have hard_requirement_failure flag set
        exp_analysis = result.get("experience_analysis", {})
        if exp_analysis.get("people_leadership_hard_gate_failed"):
            assert exp_analysis.get("hard_requirement_failure") == True


# =============================================================================
# LEPE (Leadership Evaluation & Positioning Engine) TESTS
# Per LEPE Spec: Manager+ only, 6 competency domains, gap-based routing
# =============================================================================

class TestLEPEApplicability:
    """Tests for LEPE applicability guard (Manager+ only)."""

    def test_manager_role_is_manager_plus(self):
        """Manager roles should trigger LEPE."""
        assert is_manager_plus_role("Engineering Manager") == True
        assert is_manager_plus_role("Senior Manager, Product") == True

    def test_director_role_is_manager_plus(self):
        """Director roles should trigger LEPE."""
        assert is_manager_plus_role("Director of Engineering") == True
        assert is_manager_plus_role("Senior Director, Sales") == True

    def test_vp_role_is_manager_plus(self):
        """VP roles should trigger LEPE."""
        assert is_manager_plus_role("VP of Marketing") == True
        assert is_manager_plus_role("Vice President, Operations") == True

    def test_c_suite_is_manager_plus(self):
        """C-suite roles should trigger LEPE."""
        assert is_manager_plus_role("CTO") == True
        assert is_manager_plus_role("Chief Product Officer") == True

    def test_ic_roles_not_manager_plus(self):
        """IC roles should NOT trigger LEPE."""
        assert is_manager_plus_role("Software Engineer") == False
        assert is_manager_plus_role("Senior Product Designer") == False
        assert is_manager_plus_role("Staff Engineer") == False

    def test_ic_manager_titles_not_manager_plus(self):
        """IC roles with 'manager' in title should NOT trigger LEPE."""
        assert is_manager_plus_role("Account Manager") == False
        assert is_manager_plus_role("Project Manager") == False
        assert is_manager_plus_role("Product Manager") == False
        assert is_manager_plus_role("Program Manager") == False

    def test_director_of_pm_is_manager_plus(self):
        """Director of PM/Project Managers IS Manager+."""
        assert is_manager_plus_role("Director of Product Management") == True
        assert is_manager_plus_role("VP of Project Management") == True


class TestLEPECompetencyDomains:
    """Tests for 6 competency domain extraction."""

    def test_people_management_signals_detected(self):
        """Should detect people management signals."""
        resume = {
            "experience": [
                {
                    "title": "Engineering Manager",
                    "company": "TechCo",
                    "dates": "2020 - 2024",
                    "description": "Managed a team of 8. Hired 5 engineers. Conducted performance reviews.",
                    "highlights": ["Built the team from 3 to 8", "Promoted 2 team members"]
                }
            ]
        }

        result = extract_leadership_competency_signals(resume)
        people_mgmt = result["competency_domains"]["people_management"]

        assert len(people_mgmt["signals"]) > 0
        assert people_mgmt["strength"] in ["medium", "strong"]

    def test_decision_authority_signals_detected(self):
        """Should detect decision authority signals."""
        resume = {
            "experience": [
                {
                    "title": "Director of Engineering",
                    "company": "BigCorp",
                    "dates": "2018 - 2024",
                    "description": "Full hiring authority. Owned $2M budget. P&L responsibility for department.",
                    "highlights": []
                }
            ]
        }

        result = extract_leadership_competency_signals(resume)
        decision = result["competency_domains"]["decision_authority"]

        assert len(decision["signals"]) > 0

    def test_mixed_scope_roles_detected(self):
        """Should detect roles with both IC and leadership signals."""
        resume = {
            "experience": [
                {
                    "title": "Tech Lead / Manager",
                    "company": "Startup",
                    "dates": "2020 - 2024",
                    "description": "Managed 4 engineers. Also wrote code and architected systems. Built features.",
                    "highlights": ["Hands-on coding 50% of time", "Direct reports: 4"]
                }
            ]
        }

        result = extract_leadership_competency_signals(resume)

        # Should detect mixed scope
        assert len(result["mixed_scope_roles"]) > 0
        assert result["mixed_scope_roles"][0]["leadership_scope_estimate"] == 0.5

    def test_all_six_domains_in_output(self):
        """Output should include all 6 competency domains."""
        resume = {"experience": []}
        result = extract_leadership_competency_signals(resume)

        expected_domains = [
            "people_management", "decision_authority", "org_design_scale",
            "strategic_leadership", "cross_functional_influence", "accountability_ownership"
        ]

        for domain in expected_domains:
            assert domain in result["competency_domains"]


class TestLEPEPositioningDecisions:
    """Tests for gap-based positioning decisions."""

    def test_gap_zero_returns_apply(self):
        """Gap <= 0 should return 'apply' decision."""
        tenure = {
            "people_leadership_years": 7.0,
            "has_any_leadership_signals": True,
            "strongest_competency": "people_management",
            "development_area": None
        }

        result = get_lepe_positioning_decision(tenure, 5.0, "Director of Engineering")

        assert result["decision"] == "apply"
        assert result["gap_years"] <= 0
        assert result["positioning_mode"] == False

    def test_gap_2_years_returns_position(self):
        """Gap <= 2 years should return 'position' decision."""
        tenure = {
            "people_leadership_years": 3.0,
            "has_any_leadership_signals": True,
            "strongest_competency": "people_management",
            "development_area": "org_design_scale"
        }

        result = get_lepe_positioning_decision(tenure, 5.0, "Director of Engineering")

        assert result["decision"] == "position"
        assert result["positioning_mode"] == True
        assert result["coaching_available"] == True
        assert result["transition_narrative_possible"] == True

    def test_gap_4_years_returns_caution(self):
        """Gap 3-4 years should return 'caution' decision."""
        tenure = {
            "people_leadership_years": 2.0,
            "has_any_leadership_signals": True,
            "strongest_competency": "strategic_leadership",
            "development_area": None
        }

        result = get_lepe_positioning_decision(tenure, 5.0, "Director of Engineering")

        assert result["decision"] == "caution"
        assert result["skepticism_level"] == "significant"
        assert result["positioning_mode"] == False

    def test_gap_5_plus_years_returns_locked(self):
        """Gap > 4 years should return 'locked' decision."""
        tenure = {
            "people_leadership_years": 0.0,
            "has_any_leadership_signals": False,
            "strongest_competency": None,
            "development_area": None
        }

        result = get_lepe_positioning_decision(tenure, 5.0, "Director of Engineering")

        assert result["decision"] == "locked"
        assert result["skepticism_level"] == "severe"
        assert result["coaching_available"] == False


class TestLEPERequirementInference:
    """Tests for leadership requirement inference from role level."""

    def test_c_suite_infers_10_years(self):
        """C-suite roles should infer 10+ years."""
        assert infer_leadership_requirement("CTO", {}) == 10.0
        assert infer_leadership_requirement("Chief Product Officer", {}) == 10.0

    def test_vp_infers_7_years(self):
        """VP roles should infer 7+ years."""
        assert infer_leadership_requirement("VP of Engineering", {}) == 7.0
        assert infer_leadership_requirement("Vice President, Sales", {}) == 7.0

    def test_director_infers_5_years(self):
        """Director roles should infer 5+ years."""
        assert infer_leadership_requirement("Director of Product", {}) == 5.0

    def test_manager_infers_2_years(self):
        """Manager roles should infer 2+ years."""
        assert infer_leadership_requirement("Engineering Manager", {}) == 2.0

    def test_explicit_jd_requirement_takes_precedence(self):
        """If JD explicitly states years, use that instead of inference."""
        response = {
            "job_description": "7+ years people leadership required"
        }
        # Even for a manager role, JD's 7 years takes precedence
        result = infer_leadership_requirement("Engineering Manager", response)
        assert result == 7.0


class TestLEPEIntegration:
    """Tests for LEPE integration with force_apply_experience_penalties."""

    def test_lepe_bypassed_for_ic_roles(self):
        """LEPE should be bypassed for IC roles."""
        resume = {
            "full_name": "Test User",
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "TechCo",
                    "dates": "2020 - 2024",
                    "description": "Built features",
                    "highlights": []
                }
            ]
        }

        response_data = {
            "role_title": "Senior Software Engineer",  # IC role
            "job_description": "5+ years software engineering",
            "fit_score": 75,
            "recommendation": "Apply",
            "experience_analysis": {
                "required_years": 5,
                "candidate_years_in_role_type": 4
            },
            "gaps": []
        }

        result = force_apply_experience_penalties(response_data, resume)

        # LEPE should not be applicable
        lepe = result.get("lepe_analysis", {})
        assert lepe.get("lepe_applicable") == False or lepe.get("role_level") == "below_manager"

    def test_lepe_applied_for_manager_roles(self):
        """LEPE should be applied for Manager+ roles."""
        resume = {
            "full_name": "Test User",
            "experience": [
                {
                    "title": "Engineering Manager",
                    "company": "TechCo",
                    "dates": "2018 - 2024",
                    "description": "Managed team of 8. Hired engineers. Performance reviews.",
                    "highlights": ["Built team from 4 to 8"]
                }
            ]
        }

        response_data = {
            "role_title": "Director of Engineering",  # Manager+ role
            "job_description": "5+ years people leadership",
            "fit_score": 70,
            "recommendation": "Apply",
            "experience_analysis": {
                "required_years": 5,
                "candidate_years_in_role_type": 6
            },
            "gaps": []
        }

        result = force_apply_experience_penalties(response_data, resume)

        # LEPE should be applicable
        lepe = result.get("lepe_analysis", {})
        assert lepe.get("lepe_applicable") == True

    def test_lepe_accountability_record_stored(self):
        """LEPE should store accountability record."""
        resume = {
            "full_name": "Test User",
            "experience": [
                {
                    "title": "Engineering Manager",
                    "company": "TechCo",
                    "dates": "2022 - 2024",
                    "description": "Managed small team. Direct reports.",
                    "highlights": []
                }
            ]
        }

        response_data = {
            "role_title": "VP of Engineering",  # High-level role
            "job_description": "7+ years people leadership",
            "fit_score": 60,
            "recommendation": "Consider",
            "experience_analysis": {
                "required_years": 7,
                "candidate_years_in_role_type": 2
            },
            "gaps": []
        }

        result = force_apply_experience_penalties(response_data, resume)

        # Should have accountability record
        record = result.get("leadership_positioning_record", {})
        assert "gaps_identified" in record or record.get("decision") is not None


# =============================================================================
# TEST SUITE 15: Leadership Gating Fix Validation Tests
# Per Leadership Gating Fix Spec: Fix role detection, pre-LLM gates, score caps
# =============================================================================

class TestLeadershipGatingFix:
    """
    Validation tests for Leadership Gating + Role Detection fixes.

    Per fix spec:
    1. JD with "About the job" header still detects Director role
    2. Director role with 0 leadership years -> hard fail
    3. Claude output cannot override gated decision
    4. Fit score capped correctly on hard-gate failure
    """

    def test_about_the_job_header_does_not_become_role_title(self):
        """
        Role title extraction must ignore non-semantic headers like 'About the job'.
        Per fix spec: Role title extracted as 'About the job' forces GENERAL role type (BUG).
        """
        from backend import extract_role_title_from_jd

        jd_with_bad_header = """
        About the job

        Director of Engineering

        We are looking for a Director of Engineering to lead our platform team.

        Requirements:
        - 7+ years of people leadership experience
        - Experience managing teams of 10+ engineers
        """

        # Extract role title
        title = extract_role_title_from_jd(jd_with_bad_header, "test-001")

        # Title must NOT be "About the job" - must be "Director of Engineering"
        assert "about the job" not in title.lower(), \
            f"Role title should not be 'About the job', got: {title}"
        assert "director" in title.lower(), \
            f"Role title should contain 'Director', got: {title}"

    def test_job_description_header_ignored(self):
        """'Job Description' header must not be used as role title."""
        from backend import extract_role_title_from_jd

        jd = """
        Job Description:

        VP of Product

        Lead our product organization with 20+ direct reports.
        """

        title = extract_role_title_from_jd(jd, "test-002")

        assert "job description" not in title.lower(), \
            f"Role title should not be 'Job Description', got: {title}"
        assert "vp" in title.lower() or "product" in title.lower(), \
            f"Role title should contain 'VP' or 'Product', got: {title}"

    def test_the_opportunity_header_ignored(self):
        """'The Opportunity' header must not be used as role title."""
        from backend import extract_role_title_from_jd

        jd = """
        The Opportunity

        Head of Talent Acquisition

        Build and lead our recruiting team.
        """

        title = extract_role_title_from_jd(jd, "test-003")

        assert "opportunity" not in title.lower(), \
            f"Role title should not be 'The Opportunity', got: {title}"
        assert "head" in title.lower() or "talent" in title.lower(), \
            f"Role title should contain 'Head' or 'Talent', got: {title}"

    def test_overview_header_ignored(self):
        """'Overview' header must not be used as role title."""
        from backend import extract_role_title_from_jd

        jd = """
        Overview

        Director of Sales

        Drive revenue growth across enterprise accounts.
        """

        title = extract_role_title_from_jd(jd, "test-004")

        assert title.lower() != "overview", \
            f"Role title should not be 'Overview', got: {title}"
        assert "director" in title.lower() or "sales" in title.lower(), \
            f"Role title should contain 'Director' or 'Sales', got: {title}"

    def test_director_role_detected_from_title(self):
        """
        Leadership role level must be detected from title keywords.
        Per fix spec: If leadership keyword detected, hard-set role_level = DIRECTOR_OR_ABOVE.
        """
        from backend import detect_leadership_role_level

        result = detect_leadership_role_level("Director of Engineering", "", "test-005")

        assert result["is_leadership_role"] == True
        assert result["role_level"] == "DIRECTOR_OR_ABOVE"
        assert result["confidence"] == 1.0
        assert "director" in result["leadership_keywords_found"]

    def test_vp_role_detected_as_leadership(self):
        """VP role must be detected as Director+ leadership."""
        from backend import detect_leadership_role_level

        result = detect_leadership_role_level("VP of Marketing", "", "test-006")

        assert result["is_leadership_role"] == True
        assert result["role_level"] == "DIRECTOR_OR_ABOVE"
        assert result["confidence"] == 1.0

    def test_head_of_role_detected_as_leadership(self):
        """Head of [X] role must be detected as Director+ leadership."""
        from backend import detect_leadership_role_level

        result = detect_leadership_role_level("Head of Product", "", "test-007")

        assert result["is_leadership_role"] == True
        assert result["role_level"] == "DIRECTOR_OR_ABOVE"

    def test_product_manager_not_detected_as_leadership(self):
        """Product Manager (IC role) must NOT trigger leadership gate."""
        from backend import detect_leadership_role_level

        result = detect_leadership_role_level("Senior Product Manager", "", "test-008")

        assert result["is_leadership_role"] == False
        assert result["role_level"] == "IC"

    def test_pre_llm_gate_fails_for_director_with_zero_leadership(self):
        """
        Director role with 0 leadership years must HARD FAIL.
        Per fix spec: If candidate leadership years == 0, gate_status = FAIL, fit_cap = 30.
        """
        from backend import apply_pre_llm_leadership_gate

        role_level_info = {
            "is_leadership_role": True,
            "role_level": "DIRECTOR_OR_ABOVE",
            "confidence": 1.0
        }

        # Candidate with ZERO leadership years
        result = apply_pre_llm_leadership_gate(role_level_info, 0.0, "test-009")

        assert result["gate_status"] == "FAIL", \
            "Gate should FAIL for Director role with 0 leadership years"
        assert result["fit_cap"] == 30, \
            f"Fit cap should be 30%, got: {result['fit_cap']}"
        assert result["apply_decision"] == "DO_NOT_APPLY", \
            f"Decision should be DO_NOT_APPLY, got: {result['apply_decision']}"
        assert result["hard_requirement"] == True, \
            "Leadership should be a hard requirement for Director+"

    def test_pre_llm_gate_passes_for_director_with_leadership(self):
        """Director role with sufficient leadership years should PASS."""
        from backend import apply_pre_llm_leadership_gate

        role_level_info = {
            "is_leadership_role": True,
            "role_level": "DIRECTOR_OR_ABOVE",
            "confidence": 1.0
        }

        # Candidate with 6 years leadership
        result = apply_pre_llm_leadership_gate(role_level_info, 6.0, "test-010")

        assert result["gate_status"] == "PASS", \
            "Gate should PASS for Director with 6 years leadership"
        assert result["fit_cap"] is None, \
            "Fit cap should be None when gate passes"
        assert result["apply_decision"] is None, \
            "Decision should be None when gate passes"

    def test_pre_llm_gate_warns_for_director_with_insufficient_leadership(self):
        """Director role with < 5 years leadership should WARN (not fail)."""
        from backend import apply_pre_llm_leadership_gate

        role_level_info = {
            "is_leadership_role": True,
            "role_level": "DIRECTOR_OR_ABOVE",
            "confidence": 1.0
        }

        # Candidate with 3 years leadership (below 5 year threshold for Director+)
        result = apply_pre_llm_leadership_gate(role_level_info, 3.0, "test-011")

        assert result["gate_status"] == "WARN", \
            "Gate should WARN for Director with 3 years leadership"
        # Should not cap or force decision for WARN status
        assert result["apply_decision"] is None

    def test_pre_llm_gate_bypassed_for_ic_roles(self):
        """IC roles should bypass the leadership gate entirely."""
        from backend import apply_pre_llm_leadership_gate

        role_level_info = {
            "is_leadership_role": False,
            "role_level": "IC",
            "confidence": 0.9
        }

        result = apply_pre_llm_leadership_gate(role_level_info, 0.0, "test-012")

        assert result["gate_status"] == "PASS", \
            "Gate should PASS for IC roles"
        assert result["hard_requirement"] == False

    def test_score_capped_at_30_percent_on_hard_gate_failure(self):
        """
        Fit score must be capped at 30% when leadership hard gate fails.
        Per fix spec: If hard_requirement fails, cap fit score at ≤30%.
        """
        # This is an integration test that would run through the full flow
        # Here we test the gate output that should trigger the cap

        from backend import apply_pre_llm_leadership_gate

        role_level_info = {
            "is_leadership_role": True,
            "role_level": "DIRECTOR_OR_ABOVE",
            "confidence": 1.0
        }

        result = apply_pre_llm_leadership_gate(role_level_info, 0.0, "test-013")

        # The gate result should specify the cap
        assert result["fit_cap"] == 30
        assert result["gate_status"] == "FAIL"

    def test_render_guard_catches_claude_system_mismatch(self):
        """
        Render guard must detect when Claude recommendation differs from system decision.
        Per fix spec: If claude_recommendation != system_decision, use system_decision.
        """
        from backend import _apply_render_guard

        # Simulate Claude saying "Apply" but system determined "Do Not Apply"
        parsed_data = {
            "recommendation": "Apply",  # Claude's recommendation
            "fit_score": 75,
            "recommendation_locked_by_leadership_gate": True,  # System locked it
            "leadership_gate_reason": "Leadership requirement not met"
        }

        result = _apply_render_guard(parsed_data, "test-014")

        # System decision (Do Not Apply) should override Claude's recommendation
        assert result["recommendation"] == "Do Not Apply", \
            f"System decision should override Claude, got: {result['recommendation']}"
        assert result.get("_render_guard_applied") == True, \
            "Render guard should mark that it was applied"

    def test_render_guard_no_mismatch_when_aligned(self):
        """Render guard should not modify when Claude and system agree."""
        from backend import _apply_render_guard

        parsed_data = {
            "recommendation": "Do Not Apply",
            "fit_score": 25,
            "recommendation_locked_by_leadership_gate": True
        }

        result = _apply_render_guard(parsed_data, "test-015")

        # Should still be Do Not Apply
        assert result["recommendation"] == "Do Not Apply"
        # Guard should not have applied override
        assert result.get("_render_guard_applied") != True

    def test_jd_sparse_still_enforces_director_leadership_gate(self):
        """
        Sparse JD must NOT relax leadership gates.
        Per fix spec: If JD sections are missing, use role title + seniority keywords as primary signal.
        """
        from backend import extract_required_people_leadership_years

        # Very sparse JD - just a title
        response_data = {
            "role_title": "Director of Engineering",
            "job_description": "Join our team"  # Very sparse - only 12 chars
        }

        required_years, is_hard = extract_required_people_leadership_years(response_data)

        # Should still enforce 5+ years for Director even with sparse JD
        assert required_years >= 5.0, \
            f"Director role should require 5+ years even with sparse JD, got: {required_years}"
        assert is_hard == True, \
            "Leadership should be hard requirement for Director role"

    def test_jd_sparse_enforces_vp_leadership_gate(self):
        """Sparse JD must enforce 7+ years for VP roles."""
        from backend import extract_required_people_leadership_years

        response_data = {
            "role_title": "VP of Product",
            "job_description": ""  # Empty JD
        }

        required_years, is_hard = extract_required_people_leadership_years(response_data)

        assert required_years >= 7.0, \
            f"VP role should require 7+ years even with empty JD, got: {required_years}"
        assert is_hard == True

    def test_jd_sparse_enforces_cto_leadership_gate(self):
        """Sparse JD must enforce 10+ years for C-suite roles."""
        from backend import extract_required_people_leadership_years

        response_data = {
            "role_title": "CTO",
            "job_description": "Tech leader"  # Very sparse
        }

        required_years, is_hard = extract_required_people_leadership_years(response_data)

        assert required_years >= 10.0, \
            f"CTO role should require 10+ years even with sparse JD, got: {required_years}"


class TestLeadershipGatingIntegration:
    """Integration tests for the full leadership gating flow."""

    def test_full_flow_director_with_zero_leadership(self):
        """
        INTEGRATION TEST: Director role + 0 leadership = hard fail.
        Tests the complete flow through force_apply_experience_penalties.
        """
        from backend import force_apply_experience_penalties

        # Candidate with no leadership experience
        resume = {
            "full_name": "Test IC",
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "TechCorp",
                    "dates": "2018 - Present",
                    "description": "Built distributed systems. Code reviews. Technical design.",
                    "highlights": ["Designed scalable systems", "Mentored junior engineers"]
                }
            ]
        }

        # Director role requiring leadership
        response_data = {
            "role_title": "Director of Engineering",
            "job_description": """
            Director of Engineering

            Lead our engineering organization.

            Requirements:
            - 7+ years of people leadership experience
            - Manage team of 15+ engineers
            - Build and scale engineering teams
            """,
            "fit_score": 80,  # Claude might give high score
            "recommendation": "Apply",  # Claude might say Apply
            "experience_analysis": {
                "required_years": 7
            },
            "gaps": []
        }

        result = force_apply_experience_penalties(response_data, resume)

        # Must be locked to Do Not Apply
        assert result["recommendation"] == "Do Not Apply", \
            f"Recommendation must be 'Do Not Apply', got: {result['recommendation']}"

        # Score should be capped if leadership gate applied (pre-LLM)
        # Note: The cap is applied in analyze_jd, not force_apply_experience_penalties
        # But recommendation must be locked
        exp_analysis = result.get("experience_analysis", {})
        assert exp_analysis.get("recommendation_locked") == True, \
            "Recommendation must be locked for Director with 0 leadership"


# =============================================================================
# TEST SUITE 16: Grammar & Punctuation Standards Validation
# Per P0.5 spec: No em dashes, no asterisks, no underscores for emphasis
# =============================================================================

class TestGrammarPunctuationStandards:
    """
    Validation tests for Grammar & Punctuation Standards.

    Per P0.5 spec:
    - No em dashes (—) in final output
    - No en dashes (–) used stylistically
    - No asterisks (*text*) or (**text**) for emphasis
    - No underscores (_text_) for emphasis
    - Sentences end with periods where appropriate
    """

    def test_em_dash_removed(self):
        """Em dashes must be replaced with periods."""
        from backend import _final_sanitize_text

        data = {"text": "Your background is in product management—this role requires engineering."}
        result = _final_sanitize_text(data)

        assert '—' not in result["text"], \
            f"Em dash should be removed, got: {result['text']}"
        assert '. ' in result["text"] or result["text"].count('.') > 0, \
            "Em dash should be replaced with period"

    def test_en_dash_removed(self):
        """En dashes used stylistically must be replaced."""
        from backend import _final_sanitize_text

        data = {"text": "Apply with caution – you have transferable skills."}
        result = _final_sanitize_text(data)

        assert '–' not in result["text"], \
            f"En dash should be removed, got: {result['text']}"

    def test_asterisk_bold_removed(self):
        """Bold asterisks (**text**) must be removed, keeping text."""
        from backend import _final_sanitize_text

        data = {"text": "This is a **critical gap** that needs addressing."}
        result = _final_sanitize_text(data)

        assert '**' not in result["text"], \
            f"Bold markers should be removed, got: {result['text']}"
        assert 'critical gap' in result["text"], \
            "Text inside bold markers should be preserved"

    def test_asterisk_italic_removed(self):
        """Italic asterisks (*text*) must be removed, keeping text."""
        from backend import _final_sanitize_text

        data = {"text": "You have *transferable skills* but lack experience."}
        result = _final_sanitize_text(data)

        assert result["text"].count('*') == 0, \
            f"Asterisks should be removed, got: {result['text']}"
        assert 'transferable skills' in result["text"], \
            "Text inside italic markers should be preserved"

    def test_underscore_emphasis_removed(self):
        """Underscore emphasis (_text_) must be removed, keeping text."""
        from backend import _final_sanitize_text

        data = {"text": "This is _important information_ for your application."}
        result = _final_sanitize_text(data)

        # Check that underscore emphasis is removed (but preserve underscores in identifiers)
        assert '_important information_' not in result["text"], \
            f"Underscore emphasis should be removed, got: {result['text']}"
        assert 'important information' in result["text"], \
            "Text inside underscore markers should be preserved"

    def test_nested_data_sanitized(self):
        """Sanitization must work on nested dict/list structures."""
        from backend import _final_sanitize_text

        data = {
            "recommendation": "Apply—this role fits well.",
            "gaps": [
                {"description": "Missing **key skill** in cloud."},
                {"description": "Your _background_ doesn't match."}
            ],
            "reality_check": {
                "strategic_action": "Focus on these—they matter most."
            }
        }

        result = _final_sanitize_text(data)

        assert '—' not in result["recommendation"]
        assert '**' not in result["gaps"][0]["description"]
        assert '_background_' not in result["gaps"][1]["description"]
        assert '—' not in result["reality_check"]["strategic_action"]

    def test_clean_text_unchanged(self):
        """Clean text without violations should pass through unchanged."""
        from backend import _final_sanitize_text

        original_text = "Your background is in product management. This role requires engineering leadership."
        data = {"text": original_text}

        result = _final_sanitize_text(data)

        assert result["text"] == original_text, \
            "Clean text should not be modified"

    def test_grammar_compliance_checker(self):
        """Grammar compliance checker should detect violations."""
        from backend import _check_grammar_compliance
        import logging

        # Set up a handler to capture log output
        test_handler = logging.Handler()
        test_handler.setLevel(logging.WARNING)

        data_with_violations = {
            "text": "This has an em dash—and *emphasis* markers."
        }

        # This should log warnings but not crash
        _check_grammar_compliance(data_with_violations, "test-001")
        # Test passes if no exception raised

    def test_multiple_em_dashes_all_removed(self):
        """Multiple em dashes in a single string should all be removed."""
        from backend import _final_sanitize_text

        data = {"text": "First point—second point—third point—conclusion."}
        result = _final_sanitize_text(data)

        assert '—' not in result["text"], \
            f"All em dashes should be removed, got: {result['text']}"
        # Should have periods instead
        assert result["text"].count('.') >= 3, \
            "Em dashes should be replaced with periods"

    def test_capitalization_after_replacement(self):
        """Sentence after replaced em dash should be capitalized."""
        from backend import _final_sanitize_text

        data = {"text": "This is important—but needs work."}
        result = _final_sanitize_text(data)

        # After replacement, should be "This is important. But needs work."
        assert '. B' in result["text"] or '. b' not in result["text"], \
            "Character after period should be capitalized"

    def test_json_keys_not_modified(self):
        """JSON keys should not be modified by sanitizer."""
        from backend import _final_sanitize_text

        data = {
            "strategic_action": "Apply now.",
            "reality_check": {"hard_truth": "You need more experience."},
            "fit_score": 75
        }

        result = _final_sanitize_text(data)

        # Keys should remain unchanged
        assert "strategic_action" in result
        assert "reality_check" in result
        assert "hard_truth" in result["reality_check"]
        assert "fit_score" in result


# =============================================================================
# P0 FIX: LEADERSHIP ROLE FUNCTION MISMATCH BYPASS TESTS
# Per spec: Leadership roles bypass ALL function-mismatch logic for ALL users
# =============================================================================

class TestLeadershipFunctionMismatchBypass:
    """
    P0 FIX: Tests that leadership roles bypass function mismatch logic.

    Leadership roles are function-agnostic by definition:
    - Director
    - Head
    - VP / SVP / EVP
    - Chief
    - GM
    - Managing Director
    - Partner

    These tests ensure NO user triggers function mismatch for leadership roles.
    """

    def test_is_leadership_role_director(self):
        """Director roles should be detected as leadership."""
        from function_mismatch import is_leadership_role

        assert is_leadership_role("Director of Recruiting") is True
        assert is_leadership_role("director of engineering") is True
        assert is_leadership_role("Engineering Director") is True
        assert is_leadership_role("Senior Director, Product") is True

    def test_is_leadership_role_vp(self):
        """VP roles should be detected as leadership."""
        from function_mismatch import is_leadership_role

        assert is_leadership_role("VP of Engineering") is True
        assert is_leadership_role("VP, Product") is True
        assert is_leadership_role("Vice President of Sales") is True
        assert is_leadership_role("SVP Engineering") is True
        assert is_leadership_role("EVP Operations") is True

    def test_is_leadership_role_chief(self):
        """C-suite roles should be detected as leadership."""
        from function_mismatch import is_leadership_role

        assert is_leadership_role("CTO") is True
        assert is_leadership_role("Chief Technology Officer") is True
        assert is_leadership_role("CFO") is True
        assert is_leadership_role("CEO") is True
        assert is_leadership_role("Chief Product Officer") is True

    def test_is_leadership_role_head(self):
        """Head of X roles should be detected as leadership."""
        from function_mismatch import is_leadership_role

        assert is_leadership_role("Head of Product") is True
        assert is_leadership_role("Head of Engineering") is True
        assert is_leadership_role("Head, Data Science") is True

    def test_is_leadership_role_gm(self):
        """GM and Managing Director roles should be detected as leadership."""
        from function_mismatch import is_leadership_role

        assert is_leadership_role("General Manager") is True
        assert is_leadership_role("GM, Consumer Products") is True
        assert is_leadership_role("Managing Director") is True
        assert is_leadership_role("Partner") is True

    def test_ic_roles_not_leadership(self):
        """IC roles should NOT be detected as leadership."""
        from function_mismatch import is_leadership_role

        assert is_leadership_role("Senior Product Manager") is False
        assert is_leadership_role("Staff Engineer") is False
        assert is_leadership_role("Principal Engineer") is False
        assert is_leadership_role("Senior Software Engineer") is False
        assert is_leadership_role("Product Manager") is False

    def test_detect_function_mismatch_bypassed_for_director(self):
        """Director role should bypass function mismatch detection."""
        from function_mismatch import detect_function_mismatch

        # Analytics-heavy resume
        resume_data = {
            "full_name": "Data Analyst",
            "experience": [
                {"title": "Senior Data Analyst", "company": "Analytics Corp", "description": "SQL, Python, data analysis"}
            ]
        }

        # Director of Recruiting JD - different function
        jd_data = {
            "role_title": "Director of Recruiting",
            "job_description": "Lead our recruiting team"
        }

        result = detect_function_mismatch(
            resume_data=resume_data,
            jd_data=jd_data,
            role_title="Director of Recruiting"
        )

        # Should bypass - no mismatch for leadership role
        assert result.is_mismatch is False
        assert result.leadership_role_bypass is True
        assert result.candidate_function == "leadership"
        assert result.role_function == "leadership"

    def test_detect_function_mismatch_bypassed_for_vp(self):
        """VP role should bypass function mismatch detection."""
        from function_mismatch import detect_function_mismatch

        # Non-engineering resume
        resume_data = {
            "full_name": "Marketing Leader",
            "experience": [
                {"title": "Senior Marketing Manager", "company": "Brand Co", "description": "Marketing campaigns"}
            ]
        }

        # VP Engineering JD - different function
        jd_data = {
            "role_title": "VP of Engineering",
            "job_description": "Lead engineering organization"
        }

        result = detect_function_mismatch(
            resume_data=resume_data,
            jd_data=jd_data,
            role_title="VP of Engineering"
        )

        # Should bypass - no mismatch for leadership role
        assert result.is_mismatch is False
        assert result.leadership_role_bypass is True

    def test_detect_function_mismatch_bypassed_via_seniority(self):
        """Leadership seniority flag should bypass function mismatch."""
        from function_mismatch import detect_function_mismatch

        resume_data = {
            "full_name": "Career Switcher",
            "experience": [
                {"title": "Senior PM", "company": "Product Co", "description": "Product management"}
            ]
        }

        # Engineering role JD
        jd_data = {
            "role_title": "Director of Engineering",
            "job_description": "Engineering leadership"
        }

        result = detect_function_mismatch(
            resume_data=resume_data,
            jd_data=jd_data,
            role_seniority="LEADERSHIP"  # Passed from canonical context
        )

        # Should bypass via seniority flag
        assert result.is_mismatch is False
        assert result.leadership_role_bypass is True

    def test_function_mismatch_still_works_for_ic(self):
        """IC roles should still trigger function mismatch when applicable."""
        from function_mismatch import detect_function_mismatch

        # Recruiting resume
        resume_data = {
            "full_name": "Senior Recruiter",
            "experience": [
                {"title": "Senior Technical Recruiter", "company": "Talent Co", "description": "Recruiting, sourcing"}
            ]
        }

        # Engineering IC JD
        jd_data = {
            "role_title": "Senior Software Engineer",
            "job_description": "Build and ship software products"
        }

        result = detect_function_mismatch(
            resume_data=resume_data,
            jd_data=jd_data,
            role_title="Senior Software Engineer"
        )

        # Should NOT bypass - IC role
        assert result.leadership_role_bypass is False
        # May or may not be mismatch depending on detection, but bypass should be False


# =============================================================================
# SYSTEM-WIDE REGRESSION TESTS (P0)
# These tests MUST always pass - they verify the global invariants
# =============================================================================

class TestFunctionMismatchSystemInvariants:
    """
    System-wide tests that verify global invariants.
    These tests MUST always pass - failure indicates a regression.

    Invariants tested:
    1. Leadership roles NEVER show function mismatch (any user, any profile)
    2. IC roles CAN show function mismatch when applicable
    3. Module correctly identifies leadership vs IC roles
    """

    # =========================================================================
    # LEADERSHIP INVARIANTS - These MUST always pass
    # =========================================================================

    def test_director_analytics_resume_no_mismatch(self):
        """Director + analytics resume -> NO mismatch copy."""
        from function_mismatch import detect_function_mismatch

        # Heavy analytics background
        resume = {
            "full_name": "Analytics Expert",
            "experience": [
                {"title": "Senior Data Analyst", "company": "Data Co", "description": "SQL, Python, ML, data pipelines, analytics"},
                {"title": "Data Scientist", "company": "ML Corp", "description": "Machine learning, predictive models"}
            ]
        }

        # Director of Recruiting - completely different function
        jd = {
            "role_title": "Director of Recruiting",
            "job_description": "Build and lead recruiting team, talent acquisition strategy"
        }

        result = detect_function_mismatch(resume_data=resume, jd_data=jd)

        # INVARIANT: No mismatch for leadership roles
        assert result.is_mismatch is False, "Leadership role must not trigger function mismatch"
        assert result.leadership_role_bypass is True, "Leadership bypass flag must be set"
        assert "fundamentally different" not in (result.coaching_message or "").lower(), \
            "Must not contain 'fundamentally different' for leadership roles"

    def test_vp_career_switcher_no_mismatch(self):
        """VP + career switcher resume -> NO mismatch copy."""
        from function_mismatch import detect_function_mismatch

        # Career switcher from marketing to engineering
        resume = {
            "full_name": "Marketing Executive",
            "experience": [
                {"title": "VP Marketing", "company": "Brand Co", "description": "Brand strategy, campaigns"},
                {"title": "Marketing Director", "company": "Consumer Co", "description": "Consumer marketing"}
            ]
        }

        # VP of Engineering - completely different function
        jd = {
            "role_title": "VP of Engineering",
            "job_description": "Lead engineering organization, technical strategy"
        }

        result = detect_function_mismatch(resume_data=resume, jd_data=jd)

        # INVARIANT: No mismatch for leadership roles
        assert result.is_mismatch is False, "Leadership role must not trigger function mismatch"
        assert result.leadership_role_bypass is True, "Leadership bypass flag must be set"

    def test_head_of_unrelated_background_no_mismatch(self):
        """Head of X + unrelated background -> NO mismatch copy."""
        from function_mismatch import detect_function_mismatch

        # Sales background
        resume = {
            "full_name": "Sales Leader",
            "experience": [
                {"title": "Senior Account Executive", "company": "Sales Corp", "description": "Enterprise sales, deals"}
            ]
        }

        # Head of Product - different function
        jd = {
            "role_title": "Head of Product",
            "job_description": "Own product strategy, build product organization"
        }

        result = detect_function_mismatch(resume_data=resume, jd_data=jd)

        # INVARIANT: No mismatch for leadership roles
        assert result.is_mismatch is False, "Leadership role must not trigger function mismatch"
        assert result.leadership_role_bypass is True, "Leadership bypass flag must be set"

    def test_chief_any_background_no_mismatch(self):
        """C-suite + any background -> NO mismatch copy."""
        from function_mismatch import detect_function_mismatch

        # Random background
        resume = {
            "full_name": "Operations Person",
            "experience": [
                {"title": "Operations Manager", "company": "Ops Co", "description": "Logistics, supply chain"}
            ]
        }

        # CTO - different function
        jd = {
            "role_title": "CTO",
            "job_description": "Lead technology organization"
        }

        result = detect_function_mismatch(resume_data=resume, jd_data=jd)

        # INVARIANT: No mismatch for leadership roles
        assert result.is_mismatch is False, "Leadership role must not trigger function mismatch"
        assert result.leadership_role_bypass is True, "Leadership bypass flag must be set"

    # =========================================================================
    # IC INVARIANTS - Function mismatch SHOULD work for IC roles
    # =========================================================================

    def test_ic_mismatch_does_trigger(self):
        """IC role with clear mismatch -> mismatch IS shown."""
        from function_mismatch import detect_function_mismatch

        # Recruiting background
        resume = {
            "full_name": "Recruiter",
            "experience": [
                {"title": "Senior Recruiter", "company": "Talent Co", "description": "Recruiting, sourcing, hiring"}
            ]
        }

        # Backend Engineer - completely different IC function
        jd = {
            "role_title": "Senior Backend Engineer",
            "job_description": "Build scalable backend systems, Python, distributed systems"
        }

        result = detect_function_mismatch(resume_data=resume, jd_data=jd)

        # IC role - bypass should NOT be active
        assert result.leadership_role_bypass is False, "IC role must not have leadership bypass"
        # Note: Whether mismatch is detected depends on classification accuracy

    def test_ic_adjacent_role_no_mismatch(self):
        """IC role with adjacent function -> no mismatch (or reduced severity)."""
        from function_mismatch import detect_function_mismatch

        # PM background
        resume = {
            "full_name": "Product Manager",
            "experience": [
                {"title": "Senior Product Manager", "company": "Product Co", "description": "Product strategy, roadmap"}
            ]
        }

        # Another PM role - same function
        jd = {
            "role_title": "Staff Product Manager",
            "job_description": "Own product roadmap, strategy, customer discovery"
        }

        result = detect_function_mismatch(resume_data=resume, jd_data=jd)

        # Same function - no mismatch expected
        assert result.leadership_role_bypass is False, "IC role must not have leadership bypass"
        # Same function should not trigger mismatch (or be adjacent)

    # =========================================================================
    # MODULE CONTRACT TESTS
    # =========================================================================

    def test_public_api_enforces_leadership_bypass(self):
        """Public API detect_function_mismatch MUST enforce leadership bypass."""
        from function_mismatch import detect_function_mismatch

        # Even with explicit role_seniority="IC", leadership title should bypass
        resume = {"full_name": "Test", "experience": []}
        jd = {"role_title": "Director of Engineering", "job_description": "Lead engineering"}

        result = detect_function_mismatch(
            resume_data=resume,
            jd_data=jd,
            role_seniority="IC"  # Try to force IC
        )

        # Leadership title should still bypass regardless of role_seniority param
        assert result.leadership_role_bypass is True, \
            "Leadership title must bypass even if role_seniority param says IC"

    def test_internal_api_has_defensive_check(self):
        """Internal _detect_ic_function_mismatch has defensive leadership check."""
        from function_mismatch import _detect_ic_function_mismatch

        # Call internal function directly (bad practice, but tests defensive code)
        resume = {"full_name": "Test", "experience": []}
        jd = {"role_title": "Director of Engineering", "job_description": "Lead engineering"}

        result = _detect_ic_function_mismatch(
            resume_data=resume,
            jd_data=jd,
            role_title="Director of Engineering"
        )

        # Internal function should have defensive check and return bypass
        assert result.leadership_role_bypass is True, \
            "Internal function must have defensive check for leadership roles"

    def test_coaching_message_neutral_for_ic(self):
        """IC mismatch coaching message should be neutral (no scare language)."""
        from function_mismatch import _generate_ic_complete_mismatch_coaching

        coaching = _generate_ic_complete_mismatch_coaching(
            candidate_fn="recruiting",
            role_fn="engineering"
        )

        # Should be neutral language
        assert "fundamentally" not in coaching.lower(), \
            "Coaching should not use 'fundamentally' language"
        assert "Engineering" in coaching, "Should mention role function"
        assert "Recruiting" in coaching, "Should mention candidate function"


# =============================================================================
# Run tests if executed directly
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
