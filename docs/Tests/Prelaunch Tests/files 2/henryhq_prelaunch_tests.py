"""
HenryHQ Pre-Launch Test Suite v1.0
Generated: January 5, 2026
Based on: Claude Code priority checklist for 01/15 launch

Priority Levels:
- P0: Launch blockers (must pass before 01/15)
- P1: Critical functionality (should pass before 01/15)
- P2: Important features (nice to have for 01/15)
- P3: Future features (post-launch)

Test Categories:
1. QA Validation (regex fix + re-enable)
2. Strengthen Resume Integration
3. Full User Flow (Tests 1-9)
4. Screening Questions Edge Cases
5. Document Refinement
6. Success Metrics Tracking
"""

import pytest
import json
import time
import requests
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30


class Priority(Enum):
    P0 = "P0 - Launch Blocker"
    P1 = "P1 - Critical"
    P2 = "P2 - Important"
    P3 = "P3 - Future"


@dataclass
class TestResult:
    name: str
    priority: Priority
    passed: bool
    message: str
    duration: float
    details: Optional[Dict] = None


# =============================================================================
# TEST FIXTURES - Synthetic Data
# =============================================================================

SAMPLE_RESUME = """
SARAH CHEN
Senior Product Manager | San Francisco, CA
sarah.chen@email.com | linkedin.com/in/sarahchen

EXPERIENCE

Senior Product Manager | Stripe | 2021-Present
- Led payment infrastructure team of 8 engineers
- Launched merchant dashboard serving 50,000+ businesses
- Increased payment success rate by 12% through ML-based retry logic
- Managed $2M annual budget for product development

Product Manager | Airbnb | 2018-2021
- Owned host onboarding experience, reducing time-to-first-booking by 35%
- Collaborated with design and engineering teams across 3 time zones
- Shipped 15+ features using agile methodology

Associate Product Manager | Google | 2016-2018
- Rotational program across Search, Ads, and Cloud
- Built internal tooling used by 500+ engineers

EDUCATION
MBA, Stanford Graduate School of Business, 2016
BS Computer Science, UC Berkeley, 2014

SKILLS
Product Strategy, Agile/Scrum, SQL, Python, Figma, A/B Testing
"""

SAMPLE_JD_GOOD_FIT = """
Senior Product Manager - Payments

About the Role:
We're looking for an experienced Product Manager to lead our payments team.
You'll own the end-to-end payment experience for our platform.

Requirements:
- 5+ years of product management experience
- Experience with payment systems or fintech
- Strong technical background (CS degree preferred)
- Track record of shipping products at scale
- Experience managing cross-functional teams

Nice to Have:
- MBA from top program
- Experience at high-growth startups
- SQL and data analysis skills

Compensation: $180,000 - $220,000 + equity
Location: San Francisco, CA (Hybrid)
"""

SAMPLE_JD_STRETCH_FIT = """
VP of Product - Enterprise Platform

We need a seasoned product leader to build our enterprise product org from the ground up.

Requirements:
- 10+ years of product management experience
- 5+ years managing product teams
- Enterprise SaaS experience required
- Track record of $50M+ revenue products
- Board-level presentation experience

Compensation: $300,000 - $400,000 + equity
"""

SAMPLE_JD_POOR_FIT = """
Junior Frontend Developer

Entry-level position for recent graduates.

Requirements:
- 0-2 years experience
- React/JavaScript skills
- No product experience required

Compensation: $70,000 - $90,000
"""

SAMPLE_SCREENING_QUESTIONS = {
    "yes_no_exact": {
        "question": "Do you have 5+ years of product management experience?",
        "type": "yes_no",
        "expected_answer": "yes",
        "candidate_years": 8
    },
    "yes_no_near_miss": {
        "question": "Do you have 10+ years of product management experience?",
        "type": "yes_no",
        "expected_answer": "no",
        "candidate_years": 8,
        "should_flag": True
    },
    "salary_range": {
        "question": "What are your salary expectations?",
        "type": "salary",
        "job_range": "$180,000 - $220,000",
        "candidate_expectation": "$200,000"
    },
    "essay_keywords": {
        "question": "Describe your experience with payment systems.",
        "type": "essay",
        "required_keywords": ["payment", "transaction", "fintech"],
        "candidate_background": "Led payment infrastructure at Stripe"
    },
    "knockout_dealbreaker": {
        "question": "Are you authorized to work in the US without sponsorship?",
        "type": "yes_no",
        "is_knockout": True,
        "candidate_answer": "yes"
    }
}

SAMPLE_DOCUMENT_REFINE_REQUESTS = [
    {
        "command": "Make it more senior",
        "expected_changes": ["leadership", "strategic", "executive"],
        "document_type": "resume"
    },
    {
        "command": "Add more ATS keywords",
        "expected_changes": ["keyword_count_increase"],
        "document_type": "resume"
    },
    {
        "command": "Make the summary shorter",
        "expected_changes": ["summary_length_decrease"],
        "document_type": "resume"
    },
    {
        "command": "Make it more confident",
        "expected_changes": ["tone_adjustment"],
        "document_type": "cover_letter"
    }
]


# =============================================================================
# P0 TESTS - LAUNCH BLOCKERS
# =============================================================================

class TestP0_QAValidation:
    """
    P0: QA Validation Regex Fix
    
    Issue: QA validation disabled at backend/backend.py:14088 due to false 
    positives on phrases like "improved pipeline"
    
    Action: Fix regex detection logic and re-enable
    """
    
    @pytest.mark.p0
    def test_qa_validation_enabled(self):
        """Verify QA validation is enabled (not bypassed)"""
        # This test checks if the validation endpoint is active
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "resume": SAMPLE_RESUME,
                "job_description": SAMPLE_JD_GOOD_FIT,
                "validate": True
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        
        # Validation should be present in response
        assert "validation" in data or "_validation" in data, \
            "QA validation appears to be disabled - no validation field in response"
    
    @pytest.mark.p0
    def test_qa_no_false_positive_improved_pipeline(self):
        """Verify 'improved pipeline' doesn't trigger false fabrication flag"""
        resume_with_pipeline = SAMPLE_RESUME + "\n- Improved CI/CD pipeline reducing deploy time by 40%"
        
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "resume": resume_with_pipeline,
                "job_description": SAMPLE_JD_GOOD_FIT
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        
        # Should not be blocked
        assert response.status_code == 200, f"Request blocked: {data}"
        assert "error" not in data or data.get("error") != "validation_failed", \
            "False positive: 'improved pipeline' triggered fabrication block"
    
    @pytest.mark.p0
    def test_qa_catches_actual_fabrication(self):
        """Verify QA catches obviously fabricated content"""
        # Send minimal resume but expect document generation to NOT invent experience
        minimal_resume = """
        John Doe
        Entry Level
        No experience
        """
        
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "resume": minimal_resume,
                "job_description": SAMPLE_JD_GOOD_FIT
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        
        # Check generated content doesn't contain fabricated company names
        if "resume_output" in data:
            resume_text = json.dumps(data["resume_output"]).lower()
            fabricated_companies = ["google", "stripe", "meta", "amazon"]
            
            for company in fabricated_companies:
                assert company not in resume_text, \
                    f"Fabrication detected: '{company}' appears in output but not in input resume"
    
    @pytest.mark.p0
    def test_qa_company_detection_regex(self):
        """Test company name detection regex patterns"""
        test_cases = [
            ("Worked at Google on search", ["Google"]),
            ("Led team at Stripe payments", ["Stripe"]),
            ("improved pipeline efficiency", []),  # Should NOT detect as company
            ("Improved Pipeline LLC", ["Improved Pipeline LLC"]),  # Should detect as company
        ]
        
        for text, expected_companies in test_cases:
            response = requests.post(
                f"{BASE_URL}/api/validate/extract-entities",
                json={"text": text},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                detected = data.get("companies", [])
                
                for expected in expected_companies:
                    assert expected in detected, \
                        f"Failed to detect company '{expected}' in '{text}'"
                
                # Check for false positives
                if not expected_companies:
                    assert len(detected) == 0, \
                        f"False positive: detected {detected} in '{text}'"
    
    @pytest.mark.p0
    def test_qa_metric_detection_regex(self):
        """Test metric/number detection regex patterns"""
        test_cases = [
            ("increased revenue by 50%", True),
            ("led team of 8 engineers", True),
            ("managed $2M budget", True),
            ("improved process efficiency", False),  # No specific metric
        ]
        
        for text, should_have_metric in test_cases:
            response = requests.post(
                f"{BASE_URL}/api/validate/extract-entities",
                json={"text": text},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                has_metric = len(data.get("metrics", [])) > 0
                
                assert has_metric == should_have_metric, \
                    f"Metric detection failed for '{text}': expected {should_have_metric}, got {has_metric}"


class TestP0_StrengthenResume:
    """
    P0: Strengthen Resume Integration Tests
    
    Must complete and merge to main before launch.
    Tests the full strengthen resume flow.
    """
    
    @pytest.mark.p0
    def test_leveling_api_returns_bullet_audit(self):
        """Leveling API returns bullet_audit array"""
        response = requests.post(
            f"{BASE_URL}/api/resume/level",
            json={"resume": SAMPLE_RESUME},
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "bullet_audit" in data, "Missing bullet_audit in leveling response"
        assert isinstance(data["bullet_audit"], list), "bullet_audit should be a list"
        assert len(data["bullet_audit"]) > 0, "bullet_audit should not be empty"
    
    @pytest.mark.p0
    def test_flagged_bullets_load_from_leveling_data(self):
        """Flagged bullets load correctly from levelingData"""
        response = requests.post(
            f"{BASE_URL}/api/resume/level",
            json={"resume": SAMPLE_RESUME},
            timeout=TIMEOUT
        )
        
        data = response.json()
        bullet_audit = data.get("bullet_audit", [])
        
        # Check structure of flagged bullets
        for bullet in bullet_audit:
            assert "original" in bullet, "Bullet missing 'original' field"
            assert "flag_type" in bullet, "Bullet missing 'flag_type' field"
            assert bullet["flag_type"] in ["UNVERIFIED", "WEAK", "STRONG"], \
                f"Invalid flag_type: {bullet['flag_type']}"
    
    @pytest.mark.p0
    def test_questions_generate_without_example_answers(self):
        """Questions generate without example answers"""
        response = requests.post(
            f"{BASE_URL}/api/resume/strengthen/questions",
            json={
                "resume": SAMPLE_RESUME,
                "bullets_to_strengthen": [
                    "Led payment infrastructure team of 8 engineers"
                ]
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        questions = data.get("questions", [])
        
        for q in questions:
            assert "example_answer" not in q or q.get("example_answer") is None, \
                "Questions should not include example answers"
    
    @pytest.mark.p0
    def test_blank_answers_marked_unverified(self):
        """Blank answers marked as UNVERIFIED"""
        response = requests.post(
            f"{BASE_URL}/api/resume/strengthen/process",
            json={
                "resume": SAMPLE_RESUME,
                "answers": {
                    "q1": "",  # Blank answer
                    "q2": "I led a team of 8"  # Provided answer
                }
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        processed = data.get("processed_bullets", [])
        
        blank_bullet = next((b for b in processed if b.get("question_id") == "q1"), None)
        if blank_bullet:
            assert blank_bullet.get("status") == "UNVERIFIED", \
                "Blank answers should be marked UNVERIFIED"
    
    @pytest.mark.p0
    def test_no_answers_downgrade_claims(self):
        """'No' answers downgrade or remove claims"""
        response = requests.post(
            f"{BASE_URL}/api/resume/strengthen/process",
            json={
                "resume": SAMPLE_RESUME,
                "answers": {
                    "q1": "no",  # Denying the claim
                }
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        
        # Check that claims are downgraded or removed
        assert "downgraded_claims" in data or "removed_claims" in data, \
            "'No' answers should trigger claim downgrade or removal"
    
    @pytest.mark.p0
    def test_enhanced_bullets_use_only_candidate_info(self):
        """Enhanced bullets use ONLY candidate-provided info"""
        candidate_answer = "I managed a budget of exactly $1.5M for cloud infrastructure"
        
        response = requests.post(
            f"{BASE_URL}/api/resume/strengthen/enhance",
            json={
                "original_bullet": "Managed cloud budget",
                "candidate_answer": candidate_answer
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        enhanced = data.get("enhanced_bullet", "")
        
        # Should contain info from answer
        assert "$1.5M" in enhanced or "1.5M" in enhanced, \
            "Enhanced bullet should include candidate-provided specifics"
        
        # Should NOT invent metrics not provided
        assert "$2M" not in enhanced, \
            "Enhanced bullet should not fabricate different metrics"
    
    @pytest.mark.p0
    def test_skip_option_works_and_logs(self):
        """Skip option works and logs reason"""
        response = requests.post(
            f"{BASE_URL}/api/resume/strengthen/skip",
            json={
                "bullet_id": "bullet_123",
                "reason": "I don't have specifics for this"
            },
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("skipped") == True, "Skip should return skipped=True"
        assert "reason" in data, "Skip should log the reason"
    
    @pytest.mark.p0
    def test_strengthened_data_persists_to_session(self):
        """strengthenedData persists to sessionStorage (integration test)"""
        # This is more of a frontend test, but we can verify the API returns
        # data in a format suitable for sessionStorage
        response = requests.post(
            f"{BASE_URL}/api/resume/strengthen/complete",
            json={
                "resume": SAMPLE_RESUME,
                "strengthened_bullets": [
                    {"id": "1", "original": "Led team", "enhanced": "Led team of 8 engineers"}
                ]
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        
        # Should return serializable data
        assert "strengthened_resume" in data, "Should return strengthened resume"
        
        # Verify it's JSON serializable
        try:
            json.dumps(data)
        except TypeError:
            pytest.fail("Response data is not JSON serializable for sessionStorage")
    
    @pytest.mark.p0
    def test_document_generation_respects_declined_items(self):
        """Document generation respects declined_items"""
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "resume": SAMPLE_RESUME,
                "job_description": SAMPLE_JD_GOOD_FIT,
                "declined_items": ["Managed $2M annual budget"]  # User declined this bullet
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        
        if "resume_output" in data:
            resume_text = json.dumps(data["resume_output"])
            assert "$2M" not in resume_text, \
                "Document should not include declined items"


class TestP0_FullUserFlow:
    """
    P0: Full User Flow Tests (Tests 1-9 from TESTING_CHECKLIST.md)
    
    End-to-end tests of the core user journey.
    """
    
    @pytest.mark.p0
    def test_1_upload_resume_and_parse(self):
        """Test 1: Resume upload and parsing"""
        response = requests.post(
            f"{BASE_URL}/api/resume/parse",
            json={"resume_text": SAMPLE_RESUME},
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify core fields extracted
        assert "name" in data, "Missing candidate name"
        assert "experience" in data, "Missing experience"
        assert len(data.get("experience", [])) > 0, "No experience entries parsed"
    
    @pytest.mark.p0
    def test_2_upload_jd_and_analyze(self):
        """Test 2: JD upload and analysis"""
        response = requests.post(
            f"{BASE_URL}/api/jd/analyze",
            json={
                "resume": SAMPLE_RESUME,
                "job_description": SAMPLE_JD_GOOD_FIT
            },
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify fit analysis fields
        assert "fit_score" in data, "Missing fit_score"
        assert "recommendation" in data, "Missing recommendation"
        assert "strengths" in data, "Missing strengths"
        assert "gaps" in data, "Missing gaps"
    
    @pytest.mark.p0
    def test_3_strategic_positioning(self):
        """Test 3: Strategic positioning generated"""
        response = requests.post(
            f"{BASE_URL}/api/jd/analyze",
            json={
                "resume": SAMPLE_RESUME,
                "job_description": SAMPLE_JD_GOOD_FIT
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        
        assert "positioning_strategy" in data, "Missing positioning_strategy"
        ps = data["positioning_strategy"]
        
        assert "emphasize" in ps, "Missing emphasize in positioning"
        assert "avoid" in ps, "Missing avoid in positioning"
    
    @pytest.mark.p0
    def test_4_action_plan_generated(self):
        """Test 4: Action plan generated"""
        response = requests.post(
            f"{BASE_URL}/api/jd/analyze",
            json={
                "resume": SAMPLE_RESUME,
                "job_description": SAMPLE_JD_GOOD_FIT
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        
        assert "action_plan" in data, "Missing action_plan"
        ap = data["action_plan"]
        
        assert "today" in ap, "Missing today actions"
        assert "this_week" in ap, "Missing this_week actions"
    
    @pytest.mark.p0
    def test_5_salary_strategy(self):
        """Test 5: Salary strategy generated"""
        response = requests.post(
            f"{BASE_URL}/api/jd/analyze",
            json={
                "resume": SAMPLE_RESUME,
                "job_description": SAMPLE_JD_GOOD_FIT
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        
        assert "salary_strategy" in data, "Missing salary_strategy"
        ss = data["salary_strategy"]
        
        assert "typical_range" in ss or "recommended_expectations" in ss, \
            "Missing salary range information"
    
    @pytest.mark.p0
    def test_6_hiring_intel(self):
        """Test 6: Hiring intel generated"""
        response = requests.post(
            f"{BASE_URL}/api/jd/analyze",
            json={
                "resume": SAMPLE_RESUME,
                "job_description": SAMPLE_JD_GOOD_FIT
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        
        assert "hiring_intel" in data, "Missing hiring_intel"
        hi = data["hiring_intel"]
        
        assert "hiring_manager" in hi or "recruiter" in hi, \
            "Missing hiring manager or recruiter intel"
    
    @pytest.mark.p0
    def test_7_edge_case_minimal_resume(self):
        """Test 7: Edge case - minimal resume"""
        minimal_resume = "John Doe\njohn@email.com\nNo experience"
        
        response = requests.post(
            f"{BASE_URL}/api/jd/analyze",
            json={
                "resume": minimal_resume,
                "job_description": SAMPLE_JD_GOOD_FIT
            },
            timeout=TIMEOUT
        )
        
        # Should handle gracefully, not crash
        assert response.status_code in [200, 400], \
            f"Unexpected status code: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            # Should have low fit score
            assert data.get("fit_score", 100) < 50, \
                "Minimal resume should have low fit score"
    
    @pytest.mark.p0
    def test_8_edge_case_overqualified(self):
        """Test 8: Edge case - overqualified candidate"""
        response = requests.post(
            f"{BASE_URL}/api/jd/analyze",
            json={
                "resume": SAMPLE_RESUME,  # Senior PM
                "job_description": SAMPLE_JD_POOR_FIT  # Junior dev role
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        
        # Should flag overqualification
        recommendation = data.get("recommendation", "").lower()
        assert "overqualified" in recommendation or \
               "not apply" in recommendation or \
               data.get("fit_score", 100) < 50, \
            "Should identify overqualification"
    
    @pytest.mark.p0
    def test_9_document_download(self):
        """Test 9: Document download works"""
        # First analyze
        analyze_response = requests.post(
            f"{BASE_URL}/api/jd/analyze",
            json={
                "resume": SAMPLE_RESUME,
                "job_description": SAMPLE_JD_GOOD_FIT
            },
            timeout=TIMEOUT
        )
        
        # Then download
        download_response = requests.post(
            f"{BASE_URL}/api/documents/download",
            json={
                "resume": SAMPLE_RESUME,
                "job_description": SAMPLE_JD_GOOD_FIT,
                "analysis": analyze_response.json()
            },
            timeout=TIMEOUT
        )
        
        assert download_response.status_code == 200
        
        # Check content type is ZIP or DOCX
        content_type = download_response.headers.get("content-type", "")
        assert "zip" in content_type or "docx" in content_type or \
               "octet-stream" in content_type, \
            f"Unexpected content type: {content_type}"


# =============================================================================
# P1 TESTS - CRITICAL FUNCTIONALITY
# =============================================================================

class TestP1_ScreeningQuestions:
    """
    P1: Screening Questions Edge Cases
    
    Tests various screening question scenarios.
    """
    
    @pytest.mark.p1
    def test_yes_no_exact_match(self):
        """Yes/No questions with exact match"""
        response = requests.post(
            f"{BASE_URL}/api/screening-questions/analyze",
            json={
                "resume": SAMPLE_RESUME,
                "questions": [SAMPLE_SCREENING_QUESTIONS["yes_no_exact"]]
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        analysis = data.get("screening_analysis", [{}])[0]
        
        assert analysis.get("recommended_answer") == "yes", \
            "Should recommend 'yes' for exact match"
        assert analysis.get("confidence") == "HIGH", \
            "Should have HIGH confidence for exact match"
    
    @pytest.mark.p1
    def test_yes_no_near_miss(self):
        """Yes/No questions with near-miss (e.g., 4.5 vs 5 years)"""
        near_miss_question = {
            "question": "Do you have 10+ years of product management experience?",
            "type": "yes_no",
            "candidate_years": 8
        }
        
        response = requests.post(
            f"{BASE_URL}/api/screening-questions/analyze",
            json={
                "resume": SAMPLE_RESUME,
                "questions": [near_miss_question]
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        analysis = data.get("screening_analysis", [{}])[0]
        
        # Should flag this as a stretch
        assert analysis.get("is_stretch") == True or \
               analysis.get("recommended_answer") == "no", \
            "Should flag near-miss as stretch or recommend 'no'"
    
    @pytest.mark.p1
    def test_salary_range_detection(self):
        """Salary questions with range detection"""
        response = requests.post(
            f"{BASE_URL}/api/screening-questions/analyze",
            json={
                "resume": SAMPLE_RESUME,
                "questions": [SAMPLE_SCREENING_QUESTIONS["salary_range"]]
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        analysis = data.get("screening_analysis", [{}])[0]
        
        assert "recommended_answer" in analysis, "Should provide salary guidance"
        assert "$" in analysis.get("recommended_answer", ""), \
            "Salary answer should include dollar amount"
    
    @pytest.mark.p1
    def test_essay_keyword_coverage(self):
        """Essay questions with keyword coverage"""
        response = requests.post(
            f"{BASE_URL}/api/screening-questions/analyze",
            json={
                "resume": SAMPLE_RESUME,
                "questions": [SAMPLE_SCREENING_QUESTIONS["essay_keywords"]]
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        analysis = data.get("screening_analysis", [{}])[0]
        
        recommended = analysis.get("recommended_answer", "").lower()
        
        # Should include relevant keywords
        assert "payment" in recommended or "stripe" in recommended, \
            "Essay answer should leverage candidate's relevant experience"
    
    @pytest.mark.p1
    def test_knockout_question_handling(self):
        """Multiple knockout questions in same application"""
        knockout_questions = [
            {
                "question": "Are you authorized to work in the US?",
                "type": "yes_no",
                "is_knockout": True
            },
            {
                "question": "Do you have a valid driver's license?",
                "type": "yes_no",
                "is_knockout": True
            }
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/screening-questions/analyze",
            json={
                "resume": SAMPLE_RESUME,
                "questions": knockout_questions
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        
        # Should identify knockout questions
        assert "critical_dealbreakers" in data, \
            "Should identify knockout questions as dealbreakers"
    
    @pytest.mark.p1
    def test_career_gap_questions(self):
        """Resume with gaps vs continuous employment questions"""
        resume_with_gap = SAMPLE_RESUME.replace(
            "Product Manager | Airbnb | 2018-2021",
            "Product Manager | Airbnb | 2018-2019"
        )  # Creates a gap
        
        gap_question = {
            "question": "Have you had continuous employment for the past 5 years?",
            "type": "yes_no"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/screening-questions/analyze",
            json={
                "resume": resume_with_gap,
                "questions": [gap_question]
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        analysis = data.get("screening_analysis", [{}])[0]
        
        # Should detect the gap
        assert analysis.get("detected_gap") == True or \
               analysis.get("recommended_answer") != "yes", \
            "Should detect employment gap"


class TestP1_DocumentRefine:
    """
    P1: Document Refinement Tests
    
    Tests document refinement functionality.
    """
    
    @pytest.mark.p1
    def test_make_more_senior(self):
        """'Make it more senior' increases leadership language"""
        response = requests.post(
            f"{BASE_URL}/api/documents/refine",
            json={
                "document_type": "resume",
                "current_document": {"summary": "Product manager with experience in B2B SaaS"},
                "refinement_request": "Make it more senior",
                "resume": SAMPLE_RESUME
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        refined = data.get("updated_document", {}).get("summary", "").lower()
        
        senior_keywords = ["led", "strategic", "executive", "director", "vp", "head"]
        has_senior_language = any(kw in refined for kw in senior_keywords)
        
        assert has_senior_language, \
            "Refined document should include more senior language"
    
    @pytest.mark.p1
    def test_add_more_ats_keywords(self):
        """'Add more ATS keywords' improves keyword coverage"""
        response = requests.post(
            f"{BASE_URL}/api/documents/refine",
            json={
                "document_type": "resume",
                "current_document": {"summary": "PM with fintech experience"},
                "refinement_request": "Add more ATS keywords",
                "resume": SAMPLE_RESUME,
                "job_description": SAMPLE_JD_GOOD_FIT
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        
        # Check keyword count increased
        original_keywords = 2  # "PM", "fintech"
        new_keyword_count = len(data.get("ats_keywords", []))
        
        assert new_keyword_count > original_keywords, \
            "Should add more ATS keywords"
    
    @pytest.mark.p1
    def test_make_summary_shorter(self):
        """'Make the summary shorter' reduces summary length"""
        long_summary = "A" * 500  # 500 character summary
        
        response = requests.post(
            f"{BASE_URL}/api/documents/refine",
            json={
                "document_type": "resume",
                "current_document": {"summary": long_summary},
                "refinement_request": "Make the summary shorter",
                "resume": SAMPLE_RESUME
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        new_summary = data.get("updated_document", {}).get("summary", "")
        
        assert len(new_summary) < len(long_summary), \
            "Refined summary should be shorter"
    
    @pytest.mark.p1
    def test_version_tracking(self):
        """Version tracking increments correctly"""
        # First refinement
        response1 = requests.post(
            f"{BASE_URL}/api/documents/refine",
            json={
                "document_type": "resume",
                "current_document": {"summary": "Original"},
                "refinement_request": "Improve it",
                "resume": SAMPLE_RESUME,
                "version": 1
            },
            timeout=TIMEOUT
        )
        
        data1 = response1.json()
        
        # Second refinement
        response2 = requests.post(
            f"{BASE_URL}/api/documents/refine",
            json={
                "document_type": "resume",
                "current_document": data1.get("updated_document"),
                "refinement_request": "Improve more",
                "resume": SAMPLE_RESUME,
                "version": data1.get("version", 1)
            },
            timeout=TIMEOUT
        )
        
        data2 = response2.json()
        
        assert data2.get("version", 0) > data1.get("version", 0), \
            "Version should increment with each refinement"
    
    @pytest.mark.p1
    def test_changes_tracked_and_displayed(self):
        """Changes are tracked and displayed"""
        response = requests.post(
            f"{BASE_URL}/api/documents/refine",
            json={
                "document_type": "resume",
                "current_document": {"summary": "Original summary"},
                "refinement_request": "Make it better",
                "resume": SAMPLE_RESUME
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        
        assert "changes_summary" in data, "Should include changes summary"
        changes = data["changes_summary"]
        
        assert "resume" in changes or "summary_rationale" in str(changes), \
            "Should explain what changed"
    
    @pytest.mark.p1
    def test_fabrication_blocked_in_refinement(self):
        """Fabrication is blocked during refinement"""
        response = requests.post(
            f"{BASE_URL}/api/documents/refine",
            json={
                "document_type": "resume",
                "current_document": {"summary": "Entry level PM"},
                "refinement_request": "Add 10 years of Google experience",
                "resume": "John Doe\nEntry level\nNo experience"
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        updated = json.dumps(data.get("updated_document", {})).lower()
        
        # Should not fabricate Google experience
        assert "google" not in updated or data.get("blocked") == True, \
            "Should not fabricate experience not in original resume"
    
    @pytest.mark.p1
    def test_original_facts_unchanged(self):
        """Original resume facts remain unchanged"""
        response = requests.post(
            f"{BASE_URL}/api/documents/refine",
            json={
                "document_type": "resume",
                "current_document": {
                    "experience": [
                        {"company": "Stripe", "years": "2021-Present"}
                    ]
                },
                "refinement_request": "Make it more impressive",
                "resume": SAMPLE_RESUME
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        updated_exp = data.get("updated_document", {}).get("experience", [])
        
        # Company and dates should remain accurate
        if updated_exp:
            first_exp = updated_exp[0]
            assert first_exp.get("company") == "Stripe", \
                "Company name should not change"
            assert "2021" in first_exp.get("years", ""), \
                "Dates should not change"


# =============================================================================
# P2 TESTS - IMPORTANT FEATURES
# =============================================================================

class TestP2_SuccessMetrics:
    """
    P2: Success Metrics Tracking
    
    Tests that success metrics are being captured.
    """
    
    @pytest.mark.p2
    def test_quality_score_tracked(self):
        """Quality score: 80+ average (target: 85+)"""
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "resume": SAMPLE_RESUME,
                "job_description": SAMPLE_JD_GOOD_FIT
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        
        quality_score = data.get("validation", {}).get("quality_score") or \
                       data.get("quality_score")
        
        assert quality_score is not None, "Quality score should be tracked"
        assert quality_score >= 80, f"Quality score {quality_score} below target 80"
    
    @pytest.mark.p2
    def test_keyword_coverage_tracked(self):
        """Keyword coverage: 90%+ average (target: 95%+)"""
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "resume": SAMPLE_RESUME,
                "job_description": SAMPLE_JD_GOOD_FIT
            },
            timeout=TIMEOUT
        )
        
        data = response.json()
        
        keyword_coverage = data.get("validation", {}).get("keyword_coverage") or \
                          data.get("keyword_coverage")
        
        assert keyword_coverage is not None, "Keyword coverage should be tracked"
        assert keyword_coverage >= 0.9, f"Keyword coverage {keyword_coverage} below target 90%"
    
    @pytest.mark.p2
    def test_api_response_time(self):
        """API response time: <3 seconds"""
        start = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/jd/analyze",
            json={
                "resume": SAMPLE_RESUME,
                "job_description": SAMPLE_JD_GOOD_FIT
            },
            timeout=TIMEOUT
        )
        
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 5, f"API response took {duration:.2f}s, should be <5s"
        
        # Log if above target but below limit
        if duration > 3:
            print(f"WARNING: Response time {duration:.2f}s above 3s target")
    
    @pytest.mark.p2
    def test_no_critical_errors_in_validation(self):
        """No critical errors in validation layer"""
        test_cases = [
            (SAMPLE_RESUME, SAMPLE_JD_GOOD_FIT),
            (SAMPLE_RESUME, SAMPLE_JD_STRETCH_FIT),
            (SAMPLE_RESUME, SAMPLE_JD_POOR_FIT),
        ]
        
        errors = []
        for resume, jd in test_cases:
            response = requests.post(
                f"{BASE_URL}/api/documents/generate",
                json={"resume": resume, "job_description": jd},
                timeout=TIMEOUT
            )
            
            if response.status_code >= 500:
                errors.append(f"Server error for JD: {jd[:50]}...")
            
            data = response.json()
            if data.get("validation", {}).get("critical_errors"):
                errors.append(f"Critical validation error: {data['validation']['critical_errors']}")
        
        assert len(errors) == 0, f"Critical errors found: {errors}"


class TestP2_BrowserCompatibility:
    """
    P2: Browser Compatibility Tests
    
    Note: These are integration tests that would typically run in a browser.
    This Python version tests the API responses that browsers would receive.
    """
    
    @pytest.mark.p2
    def test_cors_headers(self):
        """CORS headers present for browser requests"""
        response = requests.options(
            f"{BASE_URL}/api/jd/analyze",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # Check CORS headers
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods"
        ]
        
        for header in cors_headers:
            assert header in [h.lower() for h in response.headers.keys()], \
                f"Missing CORS header: {header}"
    
    @pytest.mark.p2
    def test_content_type_json(self):
        """API returns proper JSON content type"""
        response = requests.post(
            f"{BASE_URL}/api/jd/analyze",
            json={
                "resume": SAMPLE_RESUME,
                "job_description": SAMPLE_JD_GOOD_FIT
            },
            timeout=TIMEOUT
        )
        
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type, \
            f"Expected JSON content type, got: {content_type}"


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_tests_by_priority(priority: Priority = None):
    """Run tests filtered by priority"""
    args = ["-v", "--tb=short"]
    
    if priority:
        args.append(f"-m {priority.name.lower()}")
    
    pytest.main(args + [__file__])


def generate_test_report():
    """Generate a test report summary"""
    print("\n" + "=" * 70)
    print("HENRYHQ PRE-LAUNCH TEST SUMMARY")
    print("=" * 70)
    
    print("\n📋 TEST CATEGORIES:")
    print("-" * 40)
    print("P0 - Launch Blockers:")
    print("  • QA Validation (regex fix)")
    print("  • Strengthen Resume Integration")
    print("  • Full User Flow (Tests 1-9)")
    print()
    print("P1 - Critical:")
    print("  • Screening Questions Edge Cases")
    print("  • Document Refinement")
    print()
    print("P2 - Important:")
    print("  • Success Metrics Tracking")
    print("  • Browser Compatibility")
    
    print("\n📊 TIER COVERAGE:")
    print("-" * 40)
    print("Sourcer (Free): Basic fit analysis")
    print("Recruiter ($25): Doc generation, screening questions")
    print("Principal ($69): Quality validation, interview prep")
    print("Partner ($129): Doc refinement, mock interviews")
    print("Coach ($199): Full feature set")
    
    print("\n🎯 RUN COMMANDS:")
    print("-" * 40)
    print("All tests:        pytest henryhq_prelaunch_tests.py -v")
    print("P0 only:          pytest henryhq_prelaunch_tests.py -v -m p0")
    print("P1 only:          pytest henryhq_prelaunch_tests.py -v -m p1")
    print("P2 only:          pytest henryhq_prelaunch_tests.py -v -m p2")
    print("With coverage:    pytest henryhq_prelaunch_tests.py --cov")
    print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        generate_test_report()
    else:
        # Run all tests by default
        pytest.main(["-v", "--tb=short", __file__])
