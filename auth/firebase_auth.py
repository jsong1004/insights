import os
import json
from functools import wraps
from flask import request, jsonify, session, redirect, url_for, current_app
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from firebase_admin import firestore
import logging

logger = logging.getLogger(__name__)

class FirebaseAuthManager:
    """Manages Firebase Authentication for the Flask app"""
    
    def __init__(self, app=None):
        self.app = app
        self.cred = None
        self.firebase_app = None
        self.initialized = False
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Firebase Admin SDK"""
        try:
            # Get Firebase credentials from environment or file
            firebase_config = self._get_firebase_config()
            
            if firebase_config and not firebase_admin._apps:
                self.cred = credentials.Certificate(firebase_config)
                self.firebase_app = firebase_admin.initialize_app(self.cred)
                self.initialized = True
                logger.info("✅ Firebase Admin SDK initialized")
            elif firebase_admin._apps:
                self.firebase_app = firebase_admin.get_app()
                self.initialized = True
                logger.info("✅ Using existing Firebase app")
            else:
                logger.warning("⚠️ Firebase Admin SDK not initialized - authentication will be limited")
                self.initialized = False
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase: {e}")
            logger.warning("⚠️ Continuing without Firebase Admin SDK - authentication will be limited")
            self.initialized = False
    
    def _get_firebase_config(self):
        """Get Firebase service account configuration"""
        # Option 1: From environment variable (JSON string) - for production
        if os.getenv('FIREBASE_SERVICE_ACCOUNT'):
            try:
                config = json.loads(os.getenv('FIREBASE_SERVICE_ACCOUNT'))
                logger.info("🔐 Using Firebase credentials from environment variable")
                return config
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in FIREBASE_SERVICE_ACCOUNT: {e}")
        
        # Option 2: From Secret Manager - for production
        if os.getenv('GOOGLE_CLOUD_PROJECT'):
            try:
                from google.cloud import secretmanager
                project_id = os.getenv('GOOGLE_CLOUD_PROJECT', '711582759542')
                secret_name = f"projects/{project_id}/secrets/AI-Biz-Service-Account-Key/versions/latest"
                
                client = secretmanager.SecretManagerServiceClient()
                response = client.access_secret_version(request={"name": secret_name})
                secret_value = response.payload.data.decode("UTF-8")
                config = json.loads(secret_value)
                logger.info("🔐 Using Firebase credentials from Secret Manager")
                return config
            except Exception as e:
                logger.warning(f"Failed to get credentials from Secret Manager: {e}")
        
        # Option 3: From local file - for development
        local_files = [
            'service-account-key.json',
            'firebase-service-account.json',
            os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', 'service-account-key.json')
        ]
        
        for file_path in local_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        config = json.load(f)
                    logger.info(f"🔐 Using Firebase credentials from local file: {file_path}")
                    return config
                except Exception as e:
                    logger.warning(f"Failed to read {file_path}: {e}")
        
        logger.warning("🔐 No Firebase service account credentials found")
        return None
    
    def verify_token(self, id_token):
        """Verify Firebase ID token"""
        if not self.initialized:
            logger.warning("Firebase not initialized - cannot verify token")
            return None
            
        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    def get_user(self, uid):
        """Get user details from Firebase"""
        if not self.initialized:
            logger.warning("Firebase not initialized - cannot get user")
            return None
            
        try:
            user = firebase_auth.get_user(uid)
            return user
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    def create_custom_token(self, uid):
        """Create custom token for user"""
        if not self.initialized:
            logger.warning("Firebase not initialized - cannot create custom token")
            return None
            
        try:
            custom_token = firebase_auth.create_custom_token(uid)
            return custom_token
        except Exception as e:
            logger.error(f"Failed to create custom token: {e}")
            return None

# Decorator for protecting routes
def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check session first
        if 'user_id' in session:
            return f(*args, **kwargs)
        
        # Check Authorization header for API requests
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                # Extract token from "Bearer <token>"
                token = auth_header.split(' ')[1]
                firebase_auth_manager = current_app.extensions.get('firebase_auth')
                
                if firebase_auth_manager and firebase_auth_manager.initialized:
                    decoded_token = firebase_auth_manager.verify_token(token)
                    
                    if decoded_token:
                        # Add user info to request context
                        request.user = {
                            'uid': decoded_token['uid'],
                            'email': decoded_token.get('email'),
                            'email_verified': decoded_token.get('email_verified', False)
                        }
                        return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Auth error: {e}")
        
        # Not authenticated
        if request.is_json:
            return jsonify({'error': 'Authentication required'}), 401
        else:
            return redirect(url_for('auth.login'))
    
    return decorated_function

def subscription_required(plan_types=['basic', 'pro', 'enterprise']):
    """Decorator to require active subscription"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First check if user is logged in
            if 'user_id' not in session and not hasattr(request, 'user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_id = session.get('user_id') or request.user['uid']
            
            # Check subscription status in Firestore
            try:
                from app import firestore_manager
                user_data = firestore_manager.get_user_data(user_id)
            except:
                user_data = None
            
            if not user_data or not user_data.get('subscription'):
                return jsonify({'error': 'Active subscription required'}), 403
            
            subscription = user_data['subscription']
            if subscription.get('status') != 'active':
                return jsonify({'error': 'Active subscription required'}), 403
            
            if subscription.get('plan') not in plan_types:
                return jsonify({'error': f'Subscription plan {plan_types} required'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator 