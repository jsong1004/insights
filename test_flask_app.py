#!/usr/bin/env python3
"""
Test script for AI Insights Generator Flask App
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment setup"""
    print("🔧 Testing Environment Setup...")
    
    load_dotenv()
    
    # Check required environment variables
    required_vars = ['OPENAI_API_KEY']
    search_vars = ['TAVILY_API_KEY', 'SERPER_API_KEY']
    
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"✅ {var} is set")
    
    # Check search API keys (at least one required)
    search_keys_found = any(os.getenv(var) for var in search_vars)
    if not search_keys_found:
        missing_vars.extend(search_vars)
        print("❌ No search API keys found (need at least one of: TAVILY_API_KEY, SERPER_API_KEY)")
    else:
        for var in search_vars:
            if os.getenv(var):
                print(f"✅ {var} is set")
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease create a .env file with the following variables:")
        print("OPENAI_API_KEY=your_openai_key_here")
        print("TAVILY_API_KEY=your_tavily_key_here  # OR")
        print("SERPER_API_KEY=your_serper_key_here  # OR")
        return False
    
    print("✅ Environment setup is complete!")
    return True

def test_imports():
    """Test required imports"""
    print("\n📦 Testing Required Imports...")
    
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError:
        print("❌ Flask not installed")
        return False
    
    try:
        import crewai
        print(f"✅ CrewAI {crewai.__version__}")
    except ImportError:
        print("❌ CrewAI not installed")
        return False
    
    try:
        import openai
        print(f"✅ OpenAI {openai.__version__}")
    except ImportError:
        print("❌ OpenAI not installed")
        return False
    
    try:
        import pydantic
        print(f"✅ Pydantic {pydantic.__version__}")
    except ImportError:
        print("❌ Pydantic not installed")
        return False
    
    print("✅ All required packages are installed!")
    return True

def test_flask_app():
    """Test Flask app initialization"""
    print("\n🌐 Testing Flask App Initialization...")
    
    try:
        from app import create_app
        app = create_app()
        print("✅ Flask app created successfully")
        
        # Test if the app has the expected extensions
        if not app.extensions.get('firebase_auth'):
            print("❌ Firebase Auth not initialized")
            return False
        print("✅ Firebase Auth initialized")

        if not app.extensions.get('firestore_manager'):
            print("❌ Firestore Manager not initialized")
            return False
        print("✅ Firestore Manager initialized")

        print("✅ Flask app is ready to run!")
        return True
        
    except Exception as e:
        print(f"❌ Flask app initialization failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧠 AI Insights Generator - Flask App Test")
    print("=" * 50)
    
    tests = [
        test_environment,
        test_imports,
        test_flask_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"\n❌ Test failed. Please fix the issues above before running the app.")
            sys.exit(1)
    
    print(f"\n🎉 All tests passed! ({passed}/{total})")
    print("\n🚀 You can now run the Flask app with:")
    print("   python app.py")
    print("\n📱 Then visit: http://localhost:5000")

if __name__ == "__main__":
    main() 