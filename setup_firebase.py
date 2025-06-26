#!/usr/bin/env python3
"""
Firebase Setup Script for AI Insights Generator
Helps configure Firebase Authentication for the ai-biz-6b7ec project
"""

import os
import json
from pathlib import Path

def create_env_file():
    """Create .env file with Firebase configuration"""
    env_content = """# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Firebase Configuration (for ai-biz-6b7ec project)
FIREBASE_API_KEY=AIzaSyBAX9Fa4LHB1Kk0Q6rrOfm6M6xAZezvT1U
FIREBASE_AUTH_DOMAIN=ai-biz-6b7ec.firebaseapp.com
FIREBASE_PROJECT_ID=ai-biz-6b7ec
FIREBASE_STORAGE_BUCKET=ai-biz-6b7ec.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=22835475779
FIREBASE_APP_ID=1:22835475779:web:121c3ef155a7838eac2bf6
FIREBASE_MEASUREMENT_ID=G-XB962NM878

# Firebase Admin SDK (Backend)
# For local development - path to service account JSON file
FIREBASE_SERVICE_ACCOUNT_PATH=service-account-key.json

# For production - Google Cloud configuration
# GOOGLE_CLOUD_PROJECT=711582759542
# Secret Manager path: projects/711582759542/secrets/AI-Biz-Service-Account-Key

# AI Service API Keys
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key
SERPER_API_KEY=your-serper-api-key

# Firestore Database
FIRESTORE_DATABASE=ai-biz
"""
    
    env_path = Path('.env')
    if not env_path.exists():
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with Firebase configuration")
    else:
        print("⚠️ .env file already exists")

def check_firebase_service_account():
    """Check if Firebase service account file exists"""
    local_files = [
        'service-account-key.json',
        'firebase-service-account.json'
    ]
    
    found_file = None
    for file_path in local_files:
        if Path(file_path).exists():
            found_file = file_path
            break
    
    if not found_file:
        print("❌ Firebase service account file not found!")
        print("📝 To set up Firebase Admin SDK for LOCAL DEVELOPMENT:")
        print("   1. Go to Firebase Console: https://console.firebase.google.com/")
        print("   2. Select your project: ai-biz-6b7ec")
        print("   3. Go to Project Settings > Service Accounts")
        print("   4. Click 'Generate new private key'")
        print("   5. Save the file as 'service-account-key.json' in this directory")
        print("")
        print("📝 For PRODUCTION deployment:")
        print("   1. Upload the service account key to Google Cloud Secret Manager")
        print("   2. Secret path: projects/711582759542/secrets/AI-Biz-Service-Account-Key")
        print("   3. Set GOOGLE_CLOUD_PROJECT=711582759542 environment variable")
        return False
    else:
        print(f"✅ Firebase service account file found: {found_file}")
        return True

def check_requirements():
    """Check if required packages are installed"""
    try:
        import firebase_admin
        import google.cloud.firestore
        print("✅ Firebase packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing Firebase packages: {e}")
        print("📦 Install with: pip3 install firebase-admin google-cloud-firestore")
        return False

def test_app_startup():
    """Test if the app can start without Firebase credentials"""
    try:
        print("🧪 Testing app startup...")
        # Import the app to test initialization
        import sys
        sys.path.append('.')
        from app import app
        print("✅ App can start successfully (Firebase will be initialized when credentials are available)")
        return True
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        print("   This might be due to missing dependencies or other configuration issues")
        return False

def main():
    """Main setup function"""
    print("🔧 Firebase Setup for AI Insights Generator")
    print("=" * 50)
    
    # Create .env file
    create_env_file()
    
    # Check requirements
    requirements_ok = check_requirements()
    
    # Check service account
    service_account_ok = check_firebase_service_account()
    
    # Test app startup
    app_ok = test_app_startup() if requirements_ok else False
    
    print("\n📋 Setup Summary:")
    print(f"   Requirements: {'✅' if requirements_ok else '❌'}")
    print(f"   Service Account: {'✅' if service_account_ok else '⚠️  (optional for testing)'}")
    print(f"   App Startup: {'✅' if app_ok else '❌'}")
    
    if requirements_ok and app_ok:
        print("\n🎉 Basic setup is complete!")
        if service_account_ok:
            print("🚀 You can now run: python3 app.py (with full Firebase authentication)")
        else:
            print("🚀 You can run: python3 app.py (without Firebase authentication)")
            print("   Add service-account-key.json for full functionality")
    else:
        print("\n⚠️ Please complete the missing steps above")
    
    print("\n🔗 Firebase Project: ai-biz-6b7ec")
    print("🌐 Console: https://console.firebase.google.com/project/ai-biz-6b7ec")
    print("📊 Secret Manager: https://console.cloud.google.com/security/secret-manager?project=711582759542")

if __name__ == "__main__":
    main() 