#!/usr/bin/env python3
"""
Phase 1 Backend Test Script
Validates that all Phase 1 features are working correctly
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change if different
TEST_TIMEOUT = 30  # seconds

# Test data
TEST_REQUEST = {
    "company": "Coast",
    "role_title": "Director of Talent Acquisition",
    "job_description": """
    Coast is hiring a Director of Talent Acquisition to build and scale our recruiting function.
    
    Responsibilities:
    - Build recruiting strategy and processes from scratch
    - Hire 50+ people across engineering, product, and go-to-market
    - Manage small team of 2-3 recruiters
    - Partner with leadership on hiring plans
    - Implement ATS and recruiting tools
    
    Requirements:
    - 8+ years recruiting experience, preferably in B2B SaaS
    - Track record building recruiting functions at startups
    - Experience hiring engineers and product managers
    - Strong stakeholder management skills
    - Hands-on and strategic
    
    Compensation: $180K-$220K base + equity
    Location: San Francisco (hybrid)
    """,
    "resume": {
        "full_name": "Henry Bolden",
        "contact": {
            "email": "henry@example.com",
            "location": "San Francisco, CA"
        },
        "experience": [
            {
                "company": "Spotify",
                "title": "Global Recruiting Lead",
                "dates": "2020-2023",
                "bullets": [
                    "Built recruiting team from 5 to 25 people globally",
                    "Hired 200+ employees across engineering, product, and design",
                    "Implemented Greenhouse ATS and recruiting workflows"
                ]
            },
            {
                "company": "Uber",
                "title": "Technical Recruiting Lead",
                "dates": "2019-2020",
                "bullets": [
                    "Led recruiting for Uber Payments and Uber Eats products",
                    "Hired 50+ engineers and product managers",
                    "Partnered with VP of Product on hiring strategy"
                ]
            },
            {
                "company": "National Grid",
                "title": "Talent Acquisition Manager",
                "dates": "2015-2019",
                "bullets": [
                    "Managed team of 10 recruiters",
                    "Hired 150+ employees across utilities operations",
                    "Implemented diversity recruiting initiatives"
                ]
            }
        ],
        "skills": [
            "Technical recruiting",
            "ATS implementation",
            "Recruiting strategy",
            "Stakeholder management",
            "Team building"
        ]
    }
}

def print_section(title):
    """Print a section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)

def print_result(test_name, passed, message=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_name}")
    if message:
        print(f"       {message}")

def test_health_check():
    """Test that server is running"""
    print_section("1. HEALTH CHECK")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        passed = response.status_code == 200
        print_result("Health endpoint", passed, 
                    f"Status: {response.status_code}")
        return passed
    except requests.exceptions.RequestException as e:
        print_result("Health endpoint", False, f"Error: {str(e)}")
        return False

def test_jd_analyze():
    """Test JD analyze endpoint with Phase 1 fields"""
    print_section("2. JD ANALYZE ENDPOINT")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/jd/analyze",
            json=TEST_REQUEST,
            timeout=TEST_TIMEOUT
        )
        
        # Check status code
        status_ok = response.status_code == 200
        print_result("API response status", status_ok, 
                    f"Status: {response.status_code}")
        
        if not status_ok:
            print(f"Error response: {response.text[:500]}")
            return False
        
        # Parse response
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print_result("JSON parsing", False, f"Error: {str(e)}")
            return False
        
        print_result("JSON parsing", True)
        
        # Test Phase 1 fields
        return test_phase1_fields(data)
        
    except requests.exceptions.Timeout:
        print_result("API response", False, 
                    f"Timeout after {TEST_TIMEOUT}s")
        return False
    except requests.exceptions.RequestException as e:
        print_result("API response", False, f"Error: {str(e)}")
        return False

def test_phase1_fields(data):
    """Test that all Phase 1 fields are present and valid"""
    print_section("3. PHASE 1 FIELDS VALIDATION")
    
    all_passed = True
    
    # Check positioning_strategy
    ps = data.get("positioning_strategy", {})
    
    emphasize_ok = (isinstance(ps.get("emphasize"), list) and 
                   len(ps.get("emphasize", [])) >= 3)
    print_result("positioning_strategy.emphasize", emphasize_ok,
                f"Found {len(ps.get('emphasize', []))} items")
    all_passed = all_passed and emphasize_ok
    
    de_emphasize_ok = (isinstance(ps.get("de_emphasize"), list) and 
                       len(ps.get("de_emphasize", [])) >= 2)
    print_result("positioning_strategy.de_emphasize", de_emphasize_ok,
                f"Found {len(ps.get('de_emphasize', []))} items")
    all_passed = all_passed and de_emphasize_ok
    
    framing_ok = bool(ps.get("framing"))
    print_result("positioning_strategy.framing", framing_ok,
                f"Length: {len(ps.get('framing', ''))}")
    all_passed = all_passed and framing_ok
    
    # Check action_plan
    ap = data.get("action_plan", {})
    
    today_ok = (isinstance(ap.get("today"), list) and 
                len(ap.get("today", [])) >= 3)
    print_result("action_plan.today", today_ok,
                f"Found {len(ap.get('today', []))} tasks")
    all_passed = all_passed and today_ok
    
    tomorrow_ok = (isinstance(ap.get("tomorrow"), list) and 
                   len(ap.get("tomorrow", [])) >= 2)
    print_result("action_plan.tomorrow", tomorrow_ok,
                f"Found {len(ap.get('tomorrow', []))} tasks")
    all_passed = all_passed and tomorrow_ok
    
    this_week_ok = (isinstance(ap.get("this_week"), list) and 
                    len(ap.get("this_week", [])) >= 3)
    print_result("action_plan.this_week", this_week_ok,
                f"Found {len(ap.get('this_week', []))} tasks")
    all_passed = all_passed and this_week_ok
    
    # Check salary_strategy
    ss = data.get("salary_strategy", {})
    
    their_range_ok = bool(ss.get("their_range"))
    print_result("salary_strategy.their_range", their_range_ok,
                f"Value: {ss.get('their_range', 'MISSING')[:50]}")
    all_passed = all_passed and their_range_ok
    
    your_target_ok = bool(ss.get("your_target"))
    print_result("salary_strategy.your_target", your_target_ok,
                f"Value: {ss.get('your_target', 'MISSING')[:50]}")
    all_passed = all_passed and your_target_ok
    
    market_data_ok = bool(ss.get("market_data"))
    print_result("salary_strategy.market_data", market_data_ok,
                f"Length: {len(ss.get('market_data', ''))}")
    all_passed = all_passed and market_data_ok
    
    approach_ok = bool(ss.get("approach"))
    print_result("salary_strategy.approach", approach_ok,
                f"Length: {len(ss.get('approach', ''))}")
    all_passed = all_passed and approach_ok
    
    talking_points_ok = (isinstance(ss.get("talking_points"), list) and 
                        len(ss.get("talking_points", [])) >= 3)
    print_result("salary_strategy.talking_points", talking_points_ok,
                f"Found {len(ss.get('talking_points', []))} points")
    all_passed = all_passed and talking_points_ok
    
    # Check hiring_intel
    hi = data.get("hiring_intel", {})
    
    hm = hi.get("hiring_manager", {})
    hm_ok = (bool(hm.get("likely_title")) and 
             bool(hm.get("search_instructions")) and 
             bool(hm.get("filters")))
    print_result("hiring_intel.hiring_manager", hm_ok,
                f"Title: {hm.get('likely_title', 'MISSING')[:30]}")
    all_passed = all_passed and hm_ok
    
    rec = hi.get("recruiter", {})
    rec_ok = (bool(rec.get("likely_title")) and 
              bool(rec.get("search_instructions")) and 
              bool(rec.get("filters")))
    print_result("hiring_intel.recruiter", rec_ok,
                f"Title: {rec.get('likely_title', 'MISSING')[:30]}")
    all_passed = all_passed and rec_ok
    
    return all_passed

def test_content_quality(data):
    """Test that content is specific, not generic"""
    print_section("4. CONTENT QUALITY CHECKS")
    
    all_passed = True
    
    # Check for generic placeholders
    ps = data.get("positioning_strategy", {})
    emphasize_text = " ".join(ps.get("emphasize", []))
    
    has_company = "Spotify" in emphasize_text or "Uber" in emphasize_text
    print_result("Emphasize mentions specific companies", has_company,
                "Checks for Spotify/Uber references")
    all_passed = all_passed and has_company
    
    # Check action plan uses actual company name
    ap = data.get("action_plan", {})
    today_text = " ".join(ap.get("today", []))
    
    uses_company = "Coast" in today_text
    print_result("Action plan uses actual company name", uses_company,
                "Checks for 'Coast' references")
    all_passed = all_passed and uses_company
    
    # Check salary strategy is specific
    ss = data.get("salary_strategy", {})
    approach = ss.get("approach", "")
    
    has_specifics = "$" in approach and len(approach) > 100
    print_result("Salary approach is detailed", has_specifics,
                f"Length: {len(approach)} chars")
    all_passed = all_passed and has_specifics
    
    return all_passed

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  PHASE 1 BACKEND TEST SUITE")
    print("=" * 60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Timeout: {TEST_TIMEOUT}s")
    
    # Run tests
    health_ok = test_health_check()
    if not health_ok:
        print("\n❌ Health check failed. Is server running?")
        print(f"   Try: curl {API_BASE_URL}/health")
        sys.exit(1)
    
    analyze_ok = test_jd_analyze()
    if not analyze_ok:
        print("\n❌ JD analyze endpoint failed")
        sys.exit(1)
    
    # Final summary
    print_section("TEST SUMMARY")
    print("✅ All tests passed!")
    print("\nPhase 1 backend is working correctly.")
    print("\nNext steps:")
    print("1. Deploy updated frontend (package.html)")
    print("2. Test full user flow in browser")
    print("3. Start beta testing")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
