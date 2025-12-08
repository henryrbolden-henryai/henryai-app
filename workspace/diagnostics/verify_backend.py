#!/usr/bin/env python3
"""
Quick verification that all endpoints are defined in backend.py
"""

import sys

# Check if backend.py exists and has all required endpoints
REQUIRED_ENDPOINTS = [
    "/api/resume/parse",
    "/api/resume/parse/text",
    "/api/jd/analyze",
    "/api/documents/generate",
    "/api/tasks/prioritize",
    "/api/outcomes/log",
    "/api/strategy/review",
    "/api/network/recommend",
    "/api/interview/parse",
    "/api/interview/feedback",
    "/api/interview/thank_you"
]

def verify_backend():
    try:
        with open('backend.py', 'r') as f:
            content = f.read()
        
        print("✅ backend.py found")
        print("\nVerifying endpoints...")
        
        missing = []
        for endpoint in REQUIRED_ENDPOINTS:
            # Check if endpoint is defined
            if f'@app.post("{endpoint}")' in content or f"@app.post('{endpoint}')" in content:
                print(f"  ✓ {endpoint}")
            else:
                print(f"  ✗ {endpoint} - NOT FOUND")
                missing.append(endpoint)
        
        if missing:
            print(f"\n❌ Missing {len(missing)} endpoints")
            return False
        else:
            print(f"\n✅ All {len(REQUIRED_ENDPOINTS)} endpoints found")
            
            # Check for FastAPI and CORS
            if "from fastapi import" in content:
                print("✅ FastAPI imported")
            if "CORSMiddleware" in content:
                print("✅ CORS configured")
            if 'allow_origins=["*"]' in content or "allow_origins = ['*']" in content:
                print("✅ CORS allows all origins")
            
            print("\n" + "="*50)
            print("Backend verification PASSED")
            print("="*50)
            print("\nTo start the server:")
            print("  export ANTHROPIC_API_KEY='your-key'")
            print("  python backend.py")
            return True
            
    except FileNotFoundError:
        print("❌ backend.py not found in current directory")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = verify_backend()
    sys.exit(0 if success else 1)
