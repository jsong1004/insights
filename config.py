import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    FIREBASE_API_KEY = "AIzaSyBAX9Fa4LHB1Kk0Q6rrOfm6M6xAZezvT1U"
    FIREBASE_AUTH_DOMAIN = "ai-biz-6b7ec.firebaseapp.com"
    FIREBASE_PROJECT_ID = "ai-biz-6b7ec"
    FIREBASE_STORAGE_BUCKET = "ai-biz-6b7ec.firebasestorage.app"
    FIREBASE_MESSAGING_SENDER_ID = "22835475779"
    FIREBASE_APP_ID = "1:22835475779:web:121c3ef155a7838eac2bf6"
    FIREBASE_MEASUREMENT_ID = "G-XB962NM878"
