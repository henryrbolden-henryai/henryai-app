"""
Test script for MVP+1 features:
1. Daily Command Center (POST /api/tasks/prioritize)
2. Learning/Feedback Loop (POST /api/outcomes/log, POST /api/strategy/review)
3. Network Engine Lite (POST /api/network/recommend)

Usage: 
    python test_mvp_plus_features.py
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def test_tasks_prioritize():
    """Test Feature 1: Daily Command Center"""
    print_section("TEST 1: Daily Command Center - Task Prioritization")
    
    # Sample application data
    today = datetime.now().isoformat()
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    two_weeks_ago = (datetime.now() - timedelta(days=14)).isoformat()
    
    payload = {
        "applications": [
            {
                "id": "app-001",
                "company": "Stripe",
                "role_title": "Director of Talent Acquisition",
                "fit_score": 92,
                "stage": "applied",
                "last_activity_date": week_ago,
                "has_outreach": False
            },
            {
                "id": "app-002",
                "company": "Airbnb",
                "role_title": "Head of Recruiting",
                "fit_score": 88,
                "stage": "screen",
                "last_activity_date": two_weeks_ago,
                "has_outreach": True
            },
            {
                "id": "app-003",
                "company": "Notion",
                "role_title": "VP Talent Acquisition",
                "fit_score": 95,
                "stage": "applied",
                "last_activity_date": today,
                "has_outreach": False
            },
            {
                "id": "app-004",
                "company": "Figma",
                "role_title": "Senior Recruiting Lead",
                "fit_score": 78,
                "stage": "applied",
                "last_activity_date": week_ago,
                "has_outreach": False
            },
            {
                "id": "app-005",
                "company": "Linear",
                "role_title": "Talent Partner",
                "fit_score": 85,
                "stage": "onsite",
                "last_activity_date": "2024-11-15T10:00:00",
                "has_outreach": True
            }
        ],
        "today": today
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/tasks/prioritize", json=payload)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Task Prioritization Response:")
        print(json.dumps(result, indent=2))
        
        print(f"\n📋 Generated {len(result['tasks'])} tasks:")
        for task in result['tasks']:
            priority_icon = "🔴" if task['priority'] == 1 else "🟡" if task['priority'] == 2 else "🟢"
            print(f"\n{priority_icon} Priority {task['priority']}: {task['type'].upper()}")
            print(f"   Application: {task['application_id']}")
            print(f"   Reason: {task['reason']}")
            if task.get('suggested_message_stub'):
                print(f"   Message: {task['suggested_message_stub'][:80]}...")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return False

def test_outcomes_logging():
    """Test Feature 2a: Outcome Logging"""
    print_section("TEST 2a: Learning/Feedback Loop - Log Outcomes")
    
    outcomes = [
        {
            "application_id": "app-001",
            "stage": "viewed",
            "outcome": "Application viewed by recruiter",
            "date": datetime.now().isoformat()
        },
        {
            "application_id": "app-002",
            "stage": "replied",
            "outcome": "Received response requesting availability for phone screen",
            "date": datetime.now().isoformat()
        },
        {
            "application_id": "app-004",
            "stage": "rejected",
            "outcome": "Rejection email - moved forward with other candidates",
            "date": datetime.now().isoformat()
        }
    ]
    
    try:
        for outcome in outcomes:
            response = requests.post(f"{BASE_URL}/api/outcomes/log", json=outcome)
            response.raise_for_status()
            result = response.json()
            print(f"✅ Logged: {outcome['application_id']} - {outcome['stage']}")
            print(f"   Total outcomes stored: {result['total_outcomes']}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return False

def test_strategy_review():
    """Test Feature 2b: Strategy Review"""
    print_section("TEST 2b: Learning/Feedback Loop - Strategy Review")
    
    payload = {
        "applications": [
            {
                "id": "app-001",
                "company": "Stripe",
                "role_title": "Director of Talent Acquisition",
                "fit_score": 92,
                "stage": "viewed",
                "applied_date": "2024-11-10"
            },
            {
                "id": "app-002",
                "company": "Airbnb",
                "role_title": "Head of Recruiting",
                "fit_score": 88,
                "stage": "screen",
                "applied_date": "2024-11-05"
            },
            {
                "id": "app-003",
                "company": "Meta",
                "role_title": "Recruiting Manager",
                "fit_score": 72,
                "stage": "rejected",
                "applied_date": "2024-10-28"
            },
            {
                "id": "app-004",
                "company": "Figma",
                "role_title": "Senior Recruiting Lead",
                "fit_score": 78,
                "stage": "rejected",
                "applied_date": "2024-11-01"
            },
            {
                "id": "app-005",
                "company": "Linear",
                "role_title": "Talent Partner",
                "fit_score": 85,
                "stage": "interview",
                "applied_date": "2024-11-12"
            }
        ],
        "outcomes": [
            {
                "application_id": "app-001",
                "stage": "viewed",
                "outcome": "Application viewed by recruiter",
                "date": "2024-11-15"
            },
            {
                "application_id": "app-002",
                "stage": "screen",
                "outcome": "Phone screen scheduled",
                "date": "2024-11-08"
            },
            {
                "application_id": "app-003",
                "stage": "rejected",
                "outcome": "Rejection - seeking more startup experience",
                "date": "2024-11-05"
            },
            {
                "application_id": "app-004",
                "stage": "rejected",
                "outcome": "Rejection - looking for more design recruiting background",
                "date": "2024-11-10"
            },
            {
                "application_id": "app-005",
                "stage": "interview",
                "outcome": "Onsite interview scheduled",
                "date": "2024-11-18"
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/strategy/review", json=payload)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Strategy Review Response:")
        
        print("\n🔍 INSIGHTS:")
        for i, insight in enumerate(result['insights'], 1):
            print(f"{i}. {insight}")
        
        print("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"{i}. {rec}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return False

def test_network_recommend():
    """Test Feature 3: Network Engine"""
    print_section("TEST 3: Network Engine - Contact Recommendations")
    
    payload = {
        "company": "Stripe",
        "role_title": "Director of Talent Acquisition",
        "contacts": [
            {
                "name": "Sarah Chen",
                "company": "Stripe",
                "title": "Engineering Manager",
                "relationship": "former colleague from Spotify"
            },
            {
                "name": "Michael Torres",
                "company": "Stripe",
                "title": "Head of People Operations",
                "relationship": "LinkedIn connection, met at conference"
            },
            {
                "name": "Jessica Lee",
                "company": "Square",
                "title": "VP Talent Acquisition",
                "relationship": "close friend and mentee"
            },
            {
                "name": "David Kim",
                "company": "Coinbase",
                "title": "Director of Recruiting",
                "relationship": "former manager at Uber"
            },
            {
                "name": "Amanda Rodriguez",
                "company": "Stripe",
                "title": "Recruiting Coordinator",
                "relationship": "LinkedIn connection"
            },
            {
                "name": "Robert Chang",
                "company": "PayPal",
                "title": "Senior Technical Recruiter",
                "relationship": "industry peer, met at recruiting events"
            },
            {
                "name": "Emily Watson",
                "company": "Stripe",
                "title": "Director of Engineering",
                "relationship": "worked together on cross-functional project at National Grid"
            },
            {
                "name": "James Park",
                "company": "Airbnb",
                "title": "VP People",
                "relationship": "former colleague from Heidrick & Struggles"
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/network/recommend", json=payload)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Network Recommendations Response:")
        print(f"\n🤝 Found {len(result['recommendations'])} recommended contacts:")
        
        for rec in result['recommendations']:
            priority_icon = "🔴" if rec['priority'] == 1 else "🟡" if rec['priority'] == 2 else "🟢"
            print(f"\n{priority_icon} Priority {rec['priority']}: {rec['name']}")
            print(f"   {rec['title']} at {rec['company']}")
            print(f"   Relationship: {rec['relationship']}")
            print(f"   Reason: {rec['reason']}")
            print(f"   Suggested message: {rec['suggested_message_stub'][:100]}...")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return False

def main():
    """Run all tests"""
    print("\n" + "🧪" * 40)
    print("HENRY JOB SEARCH ENGINE - MVP+1 FEATURES TEST")
    print("🧪" * 40)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"\n✅ Server is running at {BASE_URL}")
        print(f"Version: {response.json().get('version', 'unknown')}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Cannot connect to server at {BASE_URL}")
        print("Please start the backend server first:")
        print("  python backend.py")
        return
    
    # Run tests
    results = {
        "Task Prioritization": test_tasks_prioritize(),
        "Outcome Logging": test_outcomes_logging(),
        "Strategy Review": test_strategy_review(),
        "Network Recommendations": test_network_recommend()
    }
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*80}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
