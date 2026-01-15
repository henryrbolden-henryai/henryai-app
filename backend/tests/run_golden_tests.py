#!/usr/bin/env python3
"""
Golden JD Test Runner for Leadership Gating Validation

Run with:
    python run_golden_tests.py --dry-run

Expected:
- Zero Claude calls
- Identical, boring, predictable output every run
- $0 API spend
"""

import json
import sys
import os
import argparse
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set mock API key to prevent real API calls
os.environ["ANTHROPIC_API_KEY"] = "test-key-for-golden-tests"

from backend import (
    extract_role_title_from_jd,
    detect_leadership_role_level,
    apply_pre_llm_leadership_gate,
    extract_required_people_leadership_years,
    check_people_leadership_requirement_isolated,
    extract_people_leadership_years
)


def load_golden_tests() -> List[Dict[str, Any]]:
    """Load golden test cases from JSON file."""
    test_file = Path(__file__).parent / "golden_jds" / "golden_jds.json"
    with open(test_file, "r") as f:
        data = json.load(f)
    return data["test_cases"]


def run_deterministic_analysis(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run deterministic leadership analysis on a test case.

    This replicates the dry_run logic from the API endpoint.
    ZERO Claude calls - purely deterministic.
    """
    analysis_id = f"golden-{test_case['id']}"
    jd = test_case["jd"]
    resume = test_case["resume"]

    jd_text = jd.get("job_description", "")
    role_title_provided = jd.get("role_title", "")

    # Step 1: Extract role title (ignore non-semantic headers)
    extracted_title = extract_role_title_from_jd(jd_text, analysis_id)

    # Step 2: Detect leadership role level
    role_level_info = detect_leadership_role_level(extracted_title, jd_text, analysis_id)

    # Step 3: Extract candidate leadership years
    candidate_leadership_years = extract_people_leadership_years(resume)

    # Step 4: Get required leadership years from title
    temp_response = {"job_description": jd_text, "role_title": extracted_title}
    required_years, is_hard = extract_required_people_leadership_years(temp_response)

    # Step 5: Apply pre-LLM leadership gate
    gate_result = apply_pre_llm_leadership_gate(
        role_level_info,
        candidate_leadership_years,
        analysis_id
    )

    # Build result
    result = {
        "test_id": test_case["id"],
        "role_title_extracted": extracted_title,
        "role_seniority": "LEADERSHIP" if role_level_info.get("is_leadership_role") else "IC",
        "role_level": role_level_info.get("role_level", "IC"),
        "leadership_required": role_level_info.get("is_leadership_role", False),
        "leadership_keywords_found": role_level_info.get("leadership_keywords_found", []),
        "leadership_years_required": required_years,
        "leadership_years_detected": candidate_leadership_years,
        "hard_gate": gate_result.get("gate_status", "PASS"),
        "fit_cap": gate_result.get("fit_cap"),
        "decision": "DO_NOT_APPLY" if gate_result.get("gate_status") == "FAIL" else (
            "APPLY_WITH_CAUTION" if gate_result.get("gate_status") == "WARN" else "APPLY"
        ),
        "gate_reason": gate_result.get("gate_reason", "")
    }

    return result


def validate_result(result: Dict[str, Any], expected: Dict[str, Any]) -> List[str]:
    """
    Validate the result against expected values.
    Returns list of failures (empty if all pass).
    """
    failures = []

    for key, expected_value in expected.items():
        actual_value = result.get(key)

        if actual_value != expected_value:
            failures.append(
                f"  - {key}: expected '{expected_value}', got '{actual_value}'"
            )

    return failures


def run_all_tests(verbose: bool = False) -> bool:
    """
    Run all golden tests and report results.
    Returns True if all tests pass.
    """
    print("\n" + "=" * 80)
    print(" GOLDEN JD TEST RUNNER - Leadership Gating Validation")
    print(" Mode: DRY-RUN (Zero Claude Calls, $0 API Spend)")
    print("=" * 80 + "\n")

    test_cases = load_golden_tests()
    total = len(test_cases)
    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases, 1):
        test_id = test_case["id"]
        test_name = test_case["name"]
        expected = test_case["expected"]

        print(f"[{i}/{total}] {test_name}")
        print(f"       ID: {test_id}")

        # Run deterministic analysis
        result = run_deterministic_analysis(test_case)

        # Validate against expected
        failures = validate_result(result, expected)

        if failures:
            failed += 1
            print(f"       Status: FAIL")
            for failure in failures:
                print(failure)
        else:
            passed += 1
            print(f"       Status: PASS")

        if verbose:
            print(f"       Extracted Title: {result['role_title_extracted']}")
            print(f"       Role Seniority: {result['role_seniority']}")
            print(f"       Leadership Required: {result['leadership_required']}")
            print(f"       Leadership Years: {result['leadership_years_detected']}/{result['leadership_years_required']}")
            print(f"       Hard Gate: {result['hard_gate']}")
            print(f"       Decision: {result['decision']}")

        print()

    # Summary
    print("=" * 80)
    print(" SUMMARY")
    print("=" * 80)
    print(f" Total Tests: {total}")
    print(f" Passed: {passed}")
    print(f" Failed: {failed}")
    print(f" Claude Calls: 0 (dry-run mode)")
    print(f" API Spend: $0.00")
    print("=" * 80 + "\n")

    if failed > 0:
        print(" RESULT: SOME TESTS FAILED - Fix deterministic logic before deployment")
        return False
    else:
        print(" RESULT: ALL TESTS PASSED - Deterministic logic is working correctly")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Run golden JD tests for leadership gating validation"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Run in dry-run mode (no Claude calls, default=True)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output for each test"
    )

    args = parser.parse_args()

    success = run_all_tests(verbose=args.verbose)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
