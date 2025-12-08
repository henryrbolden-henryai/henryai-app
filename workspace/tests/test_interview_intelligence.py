"""
Test script for Interview Intelligence features:
1. Parse interview transcript and classify questions
2. Get performance feedback
3. Generate thank-you email

Usage: 
    python test_interview_intelligence.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Sample interview transcript
SAMPLE_TRANSCRIPT = """
Interviewer: Thanks for joining us today, Henry. I'm Sarah, and I'll be your interviewer. Let's start with you telling me about your experience scaling recruiting teams.

Candidate: Thanks for having me, Sarah. Absolutely. At National Grid, I led a global recruiting team of 12 recruiters across 15 countries. We achieved 95% hiring plan attainment while reducing time-to-fill by 22%. The key was implementing a data-driven framework that gave us real-time visibility into pipeline health and conversion metrics. We used that data to identify bottlenecks and continuously optimize our process.

Interviewer: That's impressive. Can you tell me about a time when you had to deal with a difficult hiring situation or challenge?

Candidate: Sure. At Spotify during our hypergrowth phase, we were competing for engineering talent in an incredibly tight market. We had a situation where we needed to hire 150+ engineers in 18 months, but we were losing candidates to offers at the final stage. I analyzed our data and discovered our time-from-final-interview-to-offer was 7 days on average, while competitors were at 2-3 days. I worked with leadership to streamline approvals and got us down to 48 hours. That change improved our offer acceptance rate from 65% to 82%.

Interviewer: Excellent problem-solving. How do you think about building diverse and inclusive recruiting pipelines?

Candidate: DEI is core to how I think about recruiting. At National Grid, I championed initiatives that increased diverse candidate representation in our pipeline by 45%. The key was going beyond surface-level tactics. We partnered with HBCUs, developed relationships with affinity groups, and most importantly, we audited our job descriptions and interview processes for bias. We also implemented structured interviews with standardized rubrics to reduce subjective decision-making.

Interviewer: Let's switch gears. How would you approach building a recruiting strategy for a company going through significant growth?

Candidate: Great question. I'd start by understanding the business strategy and growth targets. What roles are critical? What's the timeline? Then I'd assess current state - what's working, what's not, where are the gaps. From there, I'd build a three-phase plan: First, quick wins to stabilize and improve what exists. Second, build scalable infrastructure - ATS optimization, sourcing tools, employer brand. Third, long-term strategic initiatives like university partnerships or internal mobility programs. Throughout, I'd establish clear metrics to track progress and ROI.

Interviewer: Tell me about your experience with metrics and data in recruiting.

Candidate: Metrics are essential. I'm a big believer in tracking both operational and outcome metrics. Operationally, I look at time-to-fill, pipeline conversion rates, source effectiveness. For outcomes, quality-of-hire metrics like 90-day retention, hiring manager satisfaction, and performance ratings. At National Grid, I built a recruiting analytics dashboard that gave leadership real-time visibility. That data drove decisions - like when we saw our employee referral program had 30% better quality-of-hire scores, we doubled down on it.

Interviewer: Last question - why Stripe specifically?

Candidate: Stripe's mission to increase the GDP of the internet really resonates with me. I've been following the company for years and I'm impressed by how you've scaled while maintaining a strong engineering culture. The recruiting challenges at this stage - competing for top-tier technical talent, scaling globally, maintaining bar while moving quickly - these are exactly the problems I want to solve. Plus, fintech is a space I'm genuinely excited about, especially given my financial services experience at National Grid.

Interviewer: Wonderful. Do you have any questions for me?

Candidate: Yes, a few. First, what are the biggest recruiting challenges you're facing right now? Second, how does the recruiting team partner with engineering leadership? And lastly, what does success look like for this role in the first 90 days?
"""

def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def test_parse_interview():
    """Test parsing interview and extracting questions"""
    print_section("TEST 1: Parse Interview Transcript")
    
    payload = {
        "transcript_text": SAMPLE_TRANSCRIPT,
        "role_title": "Director of Talent Acquisition",
        "company": "Stripe",
        "jd_analysis": {
            "key_responsibilities": [
                "Build and scale recruiting team",
                "Implement data-driven processes",
                "Partner with leadership"
            ],
            "required_skills": [
                "10+ years recruiting experience",
                "Team leadership",
                "Metrics-driven approach"
            ]
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/interview/parse", json=payload)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Interview Parsing Response:")
        
        print(f"\n📝 QUESTIONS EXTRACTED: {len(result['questions'])}")
        for i, q in enumerate(result['questions'], 1):
            print(f"\nQuestion {i}:")
            print(f"  Type: {q['type']}")
            print(f"  Competency: {q['competency_tag']}")
            print(f"  Difficulty: {q['difficulty']}/5")
            print(f"  Q: {q['question'][:80]}...")
        
        print(f"\n🎯 THEMES IDENTIFIED: {len(result['themes'])}")
        for theme in result['themes']:
            print(f"  • {theme}")
        
        if result['warnings']:
            print(f"\n⚠️  WARNINGS: {len(result['warnings'])}")
            for warning in result['warnings']:
                print(f"  • {warning}")
        else:
            print("\n✅ No warnings - clean interview structure")
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def test_interview_feedback(questions):
    """Test getting performance feedback"""
    print_section("TEST 2: Interview Performance Feedback")
    
    payload = {
        "transcript_text": SAMPLE_TRANSCRIPT,
        "role_title": "Director of Talent Acquisition",
        "company": "Stripe",
        "questions": questions
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/interview/feedback", json=payload)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Performance Feedback Response:")
        
        print(f"\n📊 OVERALL SCORE: {result['overall_score']}/100")
        
        score = result['overall_score']
        if score >= 90:
            rating = "🌟 EXCEPTIONAL"
        elif score >= 80:
            rating = "💪 STRONG"
        elif score >= 70:
            rating = "👍 GOOD"
        elif score >= 60:
            rating = "📈 FAIR"
        else:
            rating = "⚠️  NEEDS WORK"
        print(f"Rating: {rating}")
        
        print(f"\n✨ STRENGTHS ({len(result['strengths'])}):")
        for strength in result['strengths']:
            print(f"  ✓ {strength}")
        
        print(f"\n📝 AREAS FOR IMPROVEMENT ({len(result['areas_for_improvement'])}):")
        for area in result['areas_for_improvement']:
            print(f"  → {area}")
        
        print("\n🎤 DELIVERY FEEDBACK:")
        for aspect, feedback in result['delivery_feedback'].items():
            print(f"\n  {aspect.upper()}:")
            print(f"  {feedback}")
        
        print(f"\n💡 RECOMMENDATIONS ({len(result['recommendations'])}):")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def test_thank_you_email():
    """Test generating thank-you email"""
    print_section("TEST 3: Generate Thank-You Email")
    
    payload = {
        "transcript_text": SAMPLE_TRANSCRIPT,
        "role_title": "Director of Talent Acquisition",
        "company": "Stripe",
        "interviewer_name": "Sarah",
        "jd_analysis": {
            "company_context": "Leading fintech company focused on scaling payment infrastructure",
            "key_responsibilities": [
                "Build and scale recruiting team",
                "Implement data-driven processes"
            ]
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/interview/thank_you", json=payload)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Thank-You Email Generated:")
        
        print(f"\n📧 SUBJECT:")
        print(f"  {result['subject']}")
        
        print(f"\n📝 EMAIL BODY:")
        print("-" * 80)
        print(result['body'])
        print("-" * 80)
        
        print(f"\n🔑 KEY POINTS USED ({len(result['key_points_used'])}):")
        for point in result['key_points_used']:
            print(f"  • {point}")
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def main():
    """Run all tests"""
    print("\n" + "🎯" * 40)
    print("INTERVIEW INTELLIGENCE - TEST SUITE")
    print("🎯" * 40)
    
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
    
    # Run tests in sequence
    print("\n" + "🔍" * 40)
    print("Starting Interview Intelligence Tests...")
    print("🔍" * 40)
    
    # Test 1: Parse interview
    parse_result = test_parse_interview()
    if not parse_result:
        print("\n❌ Parsing failed - stopping tests")
        return
    
    # Test 2: Get feedback
    feedback_result = test_interview_feedback(parse_result['questions'])
    if not feedback_result:
        print("\n❌ Feedback failed")
    
    # Test 3: Generate thank-you email
    thank_you_result = test_thank_you_email()
    if not thank_you_result:
        print("\n❌ Thank-you email failed")
    
    # Summary
    print_section("TEST SUMMARY")
    
    results = {
        "Interview Parsing": parse_result is not None,
        "Performance Feedback": feedback_result is not None,
        "Thank-You Email": thank_you_result is not None
    }
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*80}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Interview Intelligence features working perfectly!")
        print("\nNext steps:")
        print("  1. Integrate frontend stubs from interview_intelligence_stubs.js")
        print("  2. Build UI to capture interview transcripts")
        print("  3. Display feedback and thank-you emails")
    
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
