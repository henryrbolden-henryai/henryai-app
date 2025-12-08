#!/usr/bin/env python3
"""
Diagnostic script to test the resume parse endpoint
"""

import requests
import sys
import os

BASE_URL = "http://localhost:8000"

def test_backend_running():
    """Check if backend is running"""
    print("1. Checking if backend is running...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        print(f"   ✅ Backend is running (status {response.status_code})")
        print(f"   Version: {response.json().get('version', 'unknown')}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Backend is NOT running at {BASE_URL}")
        print(f"\n   To start backend:")
        print(f"   export ANTHROPIC_API_KEY='your-key'")
        print(f"   python backend.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_cors():
    """Check CORS configuration"""
    print("\n2. Checking CORS configuration...")
    try:
        # Make OPTIONS request to check CORS headers
        response = requests.options(
            f"{BASE_URL}/api/resume/parse",
            headers={
                "Origin": "null",  # file:// protocol sends "null" origin
                "Access-Control-Request-Method": "POST"
            }
        )
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin", "NOT SET"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods", "NOT SET"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers", "NOT SET")
        }
        
        print("   CORS Headers:")
        for header, value in cors_headers.items():
            print(f"     {header}: {value}")
        
        if cors_headers["Access-Control-Allow-Origin"] in ["*", "null"]:
            print("   ✅ CORS should work with file:// protocol")
            return True
        else:
            print("   ⚠️  CORS may not work with file:// protocol")
            print("   Recommendation: Serve index.html via simple HTTP server")
            return False
            
    except Exception as e:
        print(f"   ⚠️  Could not check CORS: {e}")
        return False

def test_file_upload():
    """Test file upload with a dummy PDF"""
    print("\n3. Testing file upload endpoint...")
    
    # Create a minimal test PDF
    test_pdf = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Test Resume) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000214 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n315\n%%EOF"
    
    try:
        files = {'file': ('test_resume.pdf', test_pdf, 'application/pdf')}
        response = requests.post(f"{BASE_URL}/api/resume/parse", files=files, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ File upload works (status {response.status_code})")
            try:
                data = response.json()
                print(f"   Response has {len(data)} fields")
                return True
            except:
                print(f"   ⚠️  Response is not JSON: {response.text[:100]}")
                return False
        else:
            print(f"   ❌ File upload failed (status {response.status_code})")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing file upload: {e}")
        return False

def test_text_endpoint():
    """Test text parse endpoint"""
    print("\n4. Testing text parse endpoint...")
    
    test_text = """
    John Doe
    Senior Software Engineer
    
    Experience:
    - 5 years Python development
    - Built web applications
    
    Education:
    BS Computer Science
    """
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/resume/parse/text",
            json={"resume_text": test_text},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"   ✅ Text endpoint works (status {response.status_code})")
            return True
        else:
            print(f"   ❌ Text endpoint failed (status {response.status_code})")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing text endpoint: {e}")
        return False

def main():
    print("="*60)
    print("HENRY BACKEND DIAGNOSTIC")
    print("="*60)
    
    results = []
    
    # Test 1: Is backend running?
    backend_running = test_backend_running()
    results.append(("Backend Running", backend_running))
    
    if not backend_running:
        print("\n" + "="*60)
        print("❌ Backend is not running. Cannot continue tests.")
        print("="*60)
        sys.exit(1)
    
    # Test 2: CORS
    cors_ok = test_cors()
    results.append(("CORS Configuration", cors_ok))
    
    # Test 3: File upload
    file_ok = test_file_upload()
    results.append(("File Upload", file_ok))
    
    # Test 4: Text endpoint
    text_ok = test_text_endpoint()
    results.append(("Text Endpoint", text_ok))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✅ All tests passed! Backend is working correctly.")
        print("\nIf frontend still has issues, check browser console:")
        print("  1. Open browser DevTools (F12)")
        print("  2. Go to Console tab")
        print("  3. Try uploading resume again")
        print("  4. Look for detailed error messages")
    else:
        print("\n❌ Some tests failed. See details above.")
        
        if not cors_ok:
            print("\n💡 TIP: Serve index.html via HTTP server instead of file://")
            print("   python3 -m http.server 8080")
            print("   Then open: http://localhost:8080/index.html")
    
    print("="*60)

if __name__ == "__main__":
    main()
