# Phase 1 SaaS Development Guide: Firebase Auth + Stripe + Rate Limiting

## Overview
This guide transforms your AI Insights Generator Flask app into a commercial SaaS product with authentication, subscription billing, and rate limiting. Designed for AI coding assistants (Cursor, Claude Code) to implement systematically.

## Prerequisites
- Existing Flask app (`app.py`) with CrewAI functionality
- Google Cloud project with Firestore enabled
- Firebase project created
- Stripe account with test/live API keys
- Python 3.11+ environment

## Phase 1 Architecture Overview
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Flask App      │────▶│   Firestore     │
│  (Templates)    │     │                  │     │                 │
└─────────────────┘     │  - Auth Routes   │     └─────────────────┘
                        │  - API Routes     │              │
                        │  - Billing Routes │              │
                        └──────────────────┘              │
                                │                          │
                        ┌───────▼────────┐        ┌───────▼────────┐
                        │ Firebase Auth  │        │ Stripe Billing │
                        └────────────────┘        └────────────────┘
```

## Step 1: Install Required Dependencies

Add these to your `requirements-flask.txt`:

```txt
# Existing dependencies...

# Authentication
firebase-admin==6.5.0
PyJWT==2.8.0

# Stripe Billing
stripe==10.12.0

# Rate Limiting & Caching
Flask-Limiter==3.5.0
redis==5.0.1
Flask-Caching==2.1.0

# Session Management
Flask-Session==0.8.0

# Security
python-jose[cryptography]==3.3.0
cryptography==42.0.5

# reCAPTCHA Protection
google-cloud-recaptcha-enterprise==1.17.0

# Additional utilities
Flask-CORS==4.0.0
python-dateutil==2.9.0
```

## Step 2: Firebase Authentication Setup

### 2.1 Firebase Admin SDK Configuration

Create `auth/firebase_auth.py`:

```python
import os
import json
from functools import wraps
from flask import request, jsonify, session, redirect, url_for
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
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Firebase Admin SDK"""
        try:
            # Get Firebase credentials from environment or file
            firebase_config = self._get_firebase_config()
            
            if not firebase_admin._apps:
                self.cred = credentials.Certificate(firebase_config)
                self.firebase_app = firebase_admin.initialize_app(self.cred)
                logger.info("✅ Firebase Admin SDK initialized")
            else:
                self.firebase_app = firebase_admin.get_app()
                logger.info("✅ Using existing Firebase app")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase: {e}")
            raise
    
    def _get_firebase_config(self):
        """Get Firebase service account configuration"""
        # Option 1: From environment variable (JSON string)
        if os.getenv('FIREBASE_SERVICE_ACCOUNT'):
            return json.loads(os.getenv('FIREBASE_SERVICE_ACCOUNT'))
        
        # Option 2: From file path
        firebase_key_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', 'firebase-service-account.json')
        if os.path.exists(firebase_key_path):
            with open(firebase_key_path, 'r') as f:
                return json.load(f)
        
        raise ValueError("Firebase service account credentials not found")
    
    def verify_token(self, id_token):
        """Verify Firebase ID token"""
        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    def get_user(self, uid):
        """Get user details from Firebase"""
        try:
            user = firebase_auth.get_user(uid)
            return user
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    def create_custom_token(self, uid):
        """Create custom token for user"""
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
            from app import firestore_manager
            user_data = firestore_manager.get_user_data(user_id)
            
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
```

### 2.2 Authentication Routes

Create `auth/routes.py`:

```python
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
import firebase_admin.auth as firebase_auth
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET'])
def login():
    """Login page"""
    return render_template('auth/login.html')

@auth_bp.route('/signup', methods=['GET'])
def signup():
    """Signup page"""
    return render_template('auth/signup.html')

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for login - verifies Firebase token"""
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'error': 'ID token required'}), 400
        
        # Verify token with Firebase
        firebase_auth_manager = current_app.extensions.get('firebase_auth')
        decoded_token = firebase_auth_manager.verify_token(id_token)
        
        if not decoded_token:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Create session
        session['user_id'] = decoded_token['uid']
        session['user_email'] = decoded_token.get('email')
        session['email_verified'] = decoded_token.get('email_verified', False)
        session.permanent = True
        
        # Update last login in Firestore
        from app import firestore_manager
        firestore_manager.update_user_login(decoded_token['uid'])
        
        return jsonify({
            'success': True,
            'user': {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'emailVerified': decoded_token.get('email_verified', False)
            }
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    """API endpoint for logout"""
    session.clear()
    return jsonify({'success': True})

@auth_bp.route('/api/user', methods=['GET'])
def get_current_user():
    """Get current user info"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    from app import firestore_manager
    user_data = firestore_manager.get_user_data(session['user_id'])
    
    return jsonify({
        'user': {
            'uid': session['user_id'],
            'email': session.get('user_email'),
            'subscription': user_data.get('subscription') if user_data else None,
            'usage': user_data.get('usage') if user_data else None
        }
    })

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    from app import firestore_manager
    user_data = firestore_manager.get_user_data(session['user_id'])
    
    return render_template('auth/dashboard.html', user_data=user_data)
```

### 2.3 Frontend Authentication Templates

Create `templates/auth/login.html`:

```html
{% extends "base.html" %}

{% block title %}Login - AI Insights Generator{% endblock %}

{% block content %}
<div class="auth-container">
    <div class="auth-card">
        <h2 class="text-center mb-4">
            <i class="fas fa-brain text-primary me-2"></i>Login to AI Insights
        </h2>
        
        <div id="auth-error" class="alert alert-danger d-none" role="alert"></div>
        
        <form id="login-form">
            <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" required>
            </div>
            
            <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-control" id="password" required>
            </div>
            
            <div class="mb-3 form-check">
                <input type="checkbox" class="form-check-input" id="remember">
                <label class="form-check-label" for="remember">Remember me</label>
            </div>
            
            <button type="submit" class="btn btn-primary w-100 mb-3">
                <span class="btn-text">Login</span>
                <span class="spinner-border spinner-border-sm d-none" role="status"></span>
            </button>
            
            <div class="text-center">
                <p class="mb-2">Don't have an account? <a href="{{ url_for('auth.signup') }}">Sign up</a></p>
                <p><a href="#" id="forgot-password">Forgot password?</a></p>
            </div>
        </form>
        
        <hr class="my-4">
        
        <button id="google-signin" class="btn btn-outline-secondary w-100">
            <i class="fab fa-google me-2"></i>Continue with Google
        </button>
    </div>
</div>

<!-- Firebase SDK -->
<script src="https://www.gstatic.com/firebasejs/10.11.0/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.11.0/firebase-auth-compat.js"></script>

<script>
// Firebase configuration (replace with your config)
const firebaseConfig = {
    apiKey: "{{ config.FIREBASE_API_KEY }}",
    authDomain: "{{ config.FIREBASE_AUTH_DOMAIN }}",
    projectId: "{{ config.FIREBASE_PROJECT_ID }}",
    storageBucket: "{{ config.FIREBASE_STORAGE_BUCKET }}",
    messagingSenderId: "{{ config.FIREBASE_MESSAGING_SENDER_ID }}",
    appId: "{{ config.FIREBASE_APP_ID }}"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

// Login form handler
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const spinner = submitBtn.querySelector('.spinner-border');
    const btnText = submitBtn.querySelector('.btn-text');
    
    // Show loading state
    spinner.classList.remove('d-none');
    btnText.textContent = 'Logging in...';
    submitBtn.disabled = true;
    
    try {
        // Sign in with Firebase
        const userCredential = await auth.signInWithEmailAndPassword(email, password);
        const idToken = await userCredential.user.getIdToken();
        
        // Send token to backend
        const response = await fetch('/auth/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ idToken })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Redirect to dashboard or original page
            const next = new URLSearchParams(window.location.search).get('next');
            window.location.href = next || '/auth/dashboard';
        } else {
            throw new Error(data.error || 'Login failed');
        }
        
    } catch (error) {
        document.getElementById('auth-error').textContent = error.message;
        document.getElementById('auth-error').classList.remove('d-none');
    } finally {
        spinner.classList.add('d-none');
        btnText.textContent = 'Login';
        submitBtn.disabled = false;
    }
});

// Google Sign-in
document.getElementById('google-signin').addEventListener('click', async () => {
    const provider = new firebase.auth.GoogleAuthProvider();
    
    try {
        const result = await auth.signInWithPopup(provider);
        const idToken = await result.user.getIdToken();
        
        // Send token to backend
        const response = await fetch('/auth/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ idToken })
        });
        
        if (response.ok) {
            window.location.href = '/auth/dashboard';
        }
        
    } catch (error) {
        console.error('Google sign-in error:', error);
        document.getElementById('auth-error').textContent = 'Google sign-in failed';
        document.getElementById('auth-error').classList.remove('d-none');
    }
});
</script>

<style>
.auth-container {
    min-height: 80vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

.auth-card {
    background: white;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
}
</style>
{% endblock %}
```

## Step 3: reCAPTCHA Enterprise Setup

### 3.1 reCAPTCHA Enterprise Configuration

Create `security/recaptcha_manager.py`:

```python
import os
import logging
from google.cloud import recaptchaenterprise_v1
from google.oauth2 import service_account
from typing import Dict, Optional, Tuple
import json

logger = logging.getLogger(__name__)

class RecaptchaManager:
    """Manages Google reCAPTCHA Enterprise for bot protection"""
    
    def __init__(self, app=None):
        self.client = None
        self.project_id = None
        self.site_key = None
        self.api_key = None
        self.score_threshold = 0.5  # Default threshold for bot detection
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize reCAPTCHA Enterprise client"""
        try:
            self.project_id = app.config.get('GOOGLE_CLOUD_PROJECT_ID')
            self.site_key = app.config.get('RECAPTCHA_SITE_KEY')
            self.api_key = app.config.get('RECAPTCHA_API_KEY')
            self.score_threshold = app.config.get('RECAPTCHA_SCORE_THRESHOLD', 0.5)
            
            # Initialize the client with credentials
            credentials_path = app.config.get('GOOGLE_APPLICATION_CREDENTIALS')
            if credentials_path and os.path.exists(credentials_path):
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
                self.client = recaptchaenterprise_v1.RecaptchaEnterpriseServiceClient(credentials=credentials)
            else:
                # Use environment default credentials
                self.client = recaptchaenterprise_v1.RecaptchaEnterpriseServiceClient()
            
            logger.info("✅ reCAPTCHA Enterprise initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize reCAPTCHA Enterprise: {e}")
            raise
    
    def verify_token(self, token: str, action: str, user_ip: str = None) -> Tuple[bool, float, Dict]:
        """
        Verify reCAPTCHA token and return validation result
        
        Args:
            token: reCAPTCHA response token
            action: Expected action name (LOGIN, SIGNUP, GENERATE_INSIGHT, etc.)
            user_ip: Optional user IP address for additional validation
            
        Returns:
            Tuple of (is_valid, score, assessment_details)
        """
        try:
            # Create assessment request
            event = recaptchaenterprise_v1.Event({
                "token": token,
                "site_key": self.site_key,
                "expected_action": action
            })
            
            if user_ip:
                event.user_ip_address = user_ip
            
            assessment = recaptchaenterprise_v1.Assessment({
                "event": event,
            })
            
            # Create the assessment
            project_name = f"projects/{self.project_id}"
            request = recaptchaenterprise_v1.CreateAssessmentRequest({
                "parent": project_name,
                "assessment": assessment,
            })
            
            response = self.client.create_assessment(request=request)
            
            # Check if the token is valid
            if not response.token_properties.valid:
                logger.warning(f"Invalid reCAPTCHA token: {response.token_properties.invalid_reason}")
                return False, 0.0, {
                    "valid": False,
                    "invalid_reason": response.token_properties.invalid_reason.name,
                    "action": response.token_properties.action
                }
            
            # Check if the expected action matches
            if response.token_properties.action != action:
                logger.warning(f"Action mismatch: expected {action}, got {response.token_properties.action}")
                return False, 0.0, {
                    "valid": False,
                    "invalid_reason": "ACTION_MISMATCH",
                    "expected_action": action,
                    "actual_action": response.token_properties.action
                }
            
            # Get the risk score (0.0 = very likely bot, 1.0 = very likely human)
            score = response.risk_analysis.score
            is_human = score >= self.score_threshold
            
            assessment_details = {
                "valid": True,
                "score": score,
                "action": response.token_properties.action,
                "is_human": is_human,
                "threshold": self.score_threshold,
                "reasons": [reason.name for reason in response.risk_analysis.reasons]
            }
            
            logger.info(f"reCAPTCHA assessment: score={score}, action={action}, human={is_human}")
            
            return is_human, score, assessment_details
            
        except Exception as e:
            logger.error(f"reCAPTCHA verification failed: {e}")
            return False, 0.0, {
                "valid": False,
                "error": str(e)
            }
    
    def get_site_key(self) -> str:
        """Get the site key for frontend integration"""
        return self.site_key

# Decorator for protecting routes with reCAPTCHA
def recaptcha_required(action: str, score_threshold: float = None):
    """
    Decorator to require reCAPTCHA verification for routes
    
    Args:
        action: Expected reCAPTCHA action name
        score_threshold: Custom score threshold (optional)
    """
    def decorator(f):
        from functools import wraps
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify, current_app
            
            # Get reCAPTCHA token from request
            if request.is_json:
                data = request.get_json()
                recaptcha_token = data.get('recaptcha_token') if data else None
            else:
                recaptcha_token = request.form.get('recaptcha_token')
            
            if not recaptcha_token:
                return jsonify({
                    'error': 'reCAPTCHA token required',
                    'code': 'RECAPTCHA_MISSING'
                }), 400
            
            # Verify with reCAPTCHA Enterprise
            recaptcha_manager = current_app.extensions.get('recaptcha')
            if not recaptcha_manager:
                logger.error("reCAPTCHA manager not initialized")
                return jsonify({'error': 'Security verification unavailable'}), 500
            
            user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            is_human, score, details = recaptcha_manager.verify_token(
                recaptcha_token, 
                action, 
                user_ip
            )
            
            # Use custom threshold if provided
            if score_threshold is not None:
                is_human = score >= score_threshold
            
            if not is_human:
                logger.warning(f"reCAPTCHA failed: score={score}, details={details}")
                return jsonify({
                    'error': 'Security verification failed',
                    'code': 'RECAPTCHA_FAILED',
                    'score': score if current_app.debug else None
                }), 403
            
            # Add assessment details to request context for logging
            request.recaptcha_score = score
            request.recaptcha_details = details
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
```

### 3.2 Frontend reCAPTCHA Integration

Create `static/js/recaptcha.js`:

```javascript
/**
 * reCAPTCHA Enterprise Integration
 * Handles bot protection for forms and API calls
 */

class RecaptchaManager {
    constructor(siteKey) {
        this.siteKey = siteKey;
        this.ready = false;
        this.init();
    }
    
    async init() {
        // Wait for reCAPTCHA to be ready
        await new Promise((resolve) => {
            if (typeof grecaptcha !== 'undefined' && grecaptcha.enterprise) {
                grecaptcha.enterprise.ready(resolve);
            } else {
                // Fallback: wait for script to load
                window.addEventListener('load', () => {
                    if (typeof grecaptcha !== 'undefined' && grecaptcha.enterprise) {
                        grecaptcha.enterprise.ready(resolve);
                    } else {
                        console.error('reCAPTCHA Enterprise not loaded');
                        resolve();
                    }
                });
            }
        });
        
        this.ready = true;
        console.log('✅ reCAPTCHA Enterprise ready');
    }
    
    /**
     * Execute reCAPTCHA for a specific action
     * @param {string} action - Action name (LOGIN, SIGNUP, GENERATE_INSIGHT, etc.)
     * @returns {Promise<string>} reCAPTCHA token
     */
    async execute(action) {
        if (!this.ready) {
            throw new Error('reCAPTCHA not ready');
        }
        
        try {
            const token = await grecaptcha.enterprise.execute(this.siteKey, {
                action: action.toUpperCase()
            });
            
            console.log(`✅ reCAPTCHA token generated for action: ${action}`);
            return token;
            
        } catch (error) {
            console.error('❌ reCAPTCHA execution failed:', error);
            throw new Error('Security verification failed');
        }
    }
    
    /**
     * Add reCAPTCHA protection to a form
     * @param {HTMLFormElement} form - Form element to protect
     * @param {string} action - reCAPTCHA action name
     * @param {Function} submitHandler - Optional custom submit handler
     */
    protectForm(form, action, submitHandler = null) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                // Show loading state
                const submitBtn = form.querySelector('button[type="submit"]');
                const originalText = submitBtn.textContent;
                const spinner = submitBtn.querySelector('.spinner-border');
                
                if (spinner) spinner.classList.remove('d-none');
                submitBtn.disabled = true;
                submitBtn.textContent = 'Verifying...';
                
                // Get reCAPTCHA token
                const token = await this.execute(action);
                
                // Add token to form data
                const formData = new FormData(form);
                formData.append('recaptcha_token', token);
                
                // Use custom handler or default submission
                if (submitHandler) {
                    await submitHandler(formData, token);
                } else {
                    await this.defaultSubmitHandler(form, formData);
                }
                
            } catch (error) {
                console.error('Form submission failed:', error);
                this.showError(form, error.message);
            } finally {
                // Reset loading state
                const submitBtn = form.querySelector('button[type="submit"]');
                const spinner = submitBtn.querySelector('.spinner-border');
                
                if (spinner) spinner.classList.add('d-none');
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }
    
    /**
     * Default form submission handler
     * @param {HTMLFormElement} form - Form element
     * @param {FormData} formData - Form data with reCAPTCHA token
     */
    async defaultSubmitHandler(form, formData) {
        const response = await fetch(form.action, {
            method: form.method,
            body: formData
        });
        
        if (response.ok) {
            // Handle successful submission
            const data = await response.json();
            if (data.redirect) {
                window.location.href = data.redirect;
            } else {
                this.showSuccess(form, 'Success!');
            }
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Submission failed');
        }
    }
    
    /**
     * Add reCAPTCHA to API requests
     * @param {string} url - API endpoint
     * @param {Object} data - Request data
     * @param {string} action - reCAPTCHA action
     * @param {Object} options - Fetch options
     * @returns {Promise<Response>} Fetch response
     */
    async protectedFetch(url, data, action, options = {}) {
        const token = await this.execute(action);
        
        const requestData = {
            ...data,
            recaptcha_token: token
        };
        
        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            body: JSON.stringify(requestData),
            ...options
        });
    }
    
    /**
     * Show error message in form
     * @param {HTMLFormElement} form - Form element
     * @param {string} message - Error message
     */
    showError(form, message) {
        let errorDiv = form.querySelector('.recaptcha-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger recaptcha-error';
            form.insertBefore(errorDiv, form.firstChild);
        }
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
    
    /**
     * Show success message in form
     * @param {HTMLFormElement} form - Form element
     * @param {string} message - Success message
     */
    showSuccess(form, message) {
        let successDiv = form.querySelector('.recaptcha-success');
        if (!successDiv) {
            successDiv = document.createElement('div');
            successDiv.className = 'alert alert-success recaptcha-success';
            form.insertBefore(successDiv, form.firstChild);
        }
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        
        // Hide error if exists
        const errorDiv = form.querySelector('.recaptcha-error');
        if (errorDiv) errorDiv.style.display = 'none';
    }
}

// Global instance
let recaptchaManager = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const siteKey = document.querySelector('meta[name="recaptcha-site-key"]')?.content;
    if (siteKey) {
        recaptchaManager = new RecaptchaManager(siteKey);
    }
});

// Export for global use
window.RecaptchaManager = RecaptchaManager;
window.recaptchaManager = recaptchaManager;
```

## Step 4: Stripe Subscription Billing

### 4.1 Stripe Configuration

Create `billing/stripe_manager.py`:

```python
import os
import stripe
import logging
from datetime import datetime
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class StripeManager:
    """Manages Stripe subscription billing"""
    
    def __init__(self, app=None):
        self.stripe_key = None
        self.webhook_secret = None
        self.price_ids = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Stripe with configuration"""
        self.stripe_key = app.config.get('STRIPE_SECRET_KEY')
        self.webhook_secret = app.config.get('STRIPE_WEBHOOK_SECRET')
        
        # Configure price IDs for different plans
        self.price_ids = {
            'basic': app.config.get('STRIPE_BASIC_PRICE_ID'),
            'pro': app.config.get('STRIPE_PRO_PRICE_ID'),
            'enterprise': app.config.get('STRIPE_ENTERPRISE_PRICE_ID')
        }
        
        stripe.api_key = self.stripe_key
        logger.info("✅ Stripe initialized")
    
    def create_customer(self, user_id: str, email: str, metadata: Dict = None) -> Optional[str]:
        """Create Stripe customer for user"""
        try:
            customer = stripe.Customer.create(
                email=email,
                metadata={
                    'user_id': user_id,
                    **(metadata or {})
                }
            )
            logger.info(f"Created Stripe customer: {customer.id}")
            return customer.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create customer: {e}")
            return None
    
    def create_checkout_session(self, 
                              customer_id: str, 
                              price_id: str,
                              success_url: str,
                              cancel_url: str,
                              trial_days: int = 14) -> Optional[str]:
        """Create Stripe checkout session for subscription"""
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                subscription_data={
                    'trial_period_days': trial_days,
                    'metadata': {
                        'plan': self._get_plan_name(price_id)
                    }
                },
                allow_promotion_codes=True
            )
            
            logger.info(f"Created checkout session: {session.id}")
            return session.url
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {e}")
            return None
    
    def create_billing_portal_session(self, customer_id: str, return_url: str) -> Optional[str]:
        """Create billing portal session for customer to manage subscription"""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            return session.url
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create billing portal session: {e}")
            return None
    
    def get_subscription(self, subscription_id: str) -> Optional[Dict]:
        """Get subscription details"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_end': subscription.current_period_end,
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'plan': self._get_plan_name(subscription.items.data[0].price.id),
                'trial_end': subscription.trial_end
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get subscription: {e}")
            return None
    
    def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> bool:
        """Cancel subscription (at period end or immediately)"""
        try:
            if immediate:
                stripe.Subscription.delete(subscription_id)
            else:
                stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            
            logger.info(f"Cancelled subscription: {subscription_id}")
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {e}")
            return False
    
    def handle_webhook(self, payload: bytes, sig_header: str) -> Dict:
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            
            logger.info(f"Received webhook: {event['type']}")
            
            # Handle different event types
            if event['type'] == 'checkout.session.completed':
                return self._handle_checkout_completed(event['data']['object'])
                
            elif event['type'] == 'customer.subscription.updated':
                return self._handle_subscription_updated(event['data']['object'])
                
            elif event['type'] == 'customer.subscription.deleted':
                return self._handle_subscription_deleted(event['data']['object'])
                
            elif event['type'] == 'invoice.payment_failed':
                return self._handle_payment_failed(event['data']['object'])
            
            return {'status': 'unhandled', 'type': event['type']}
            
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise
    
    def _get_plan_name(self, price_id: str) -> str:
        """Get plan name from price ID"""
        for plan, pid in self.price_ids.items():
            if pid == price_id:
                return plan
        return 'unknown'
    
    def _handle_checkout_completed(self, session: Dict) -> Dict:
        """Handle successful checkout"""
        customer_id = session['customer']
        subscription_id = session['subscription']
        
        # Get customer details
        customer = stripe.Customer.retrieve(customer_id)
        user_id = customer.metadata.get('user_id')
        
        # Get subscription details
        subscription = self.get_subscription(subscription_id)
        
        return {
            'status': 'success',
            'user_id': user_id,
            'customer_id': customer_id,
            'subscription': subscription
        }
    
    def _handle_subscription_updated(self, subscription: Dict) -> Dict:
        """Handle subscription update"""
        customer_id = subscription['customer']
        customer = stripe.Customer.retrieve(customer_id)
        user_id = customer.metadata.get('user_id')
        
        return {
            'status': 'updated',
            'user_id': user_id,
            'subscription': {
                'id': subscription['id'],
                'status': subscription['status'],
                'plan': self._get_plan_name(subscription['items']['data'][0]['price']['id'])
            }
        }
    
    def _handle_subscription_deleted(self, subscription: Dict) -> Dict:
        """Handle subscription cancellation"""
        customer_id = subscription['customer']
        customer = stripe.Customer.retrieve(customer_id)
        user_id = customer.metadata.get('user_id')
        
        return {
            'status': 'cancelled',
            'user_id': user_id,
            'subscription_id': subscription['id']
        }
    
    def _handle_payment_failed(self, invoice: Dict) -> Dict:
        """Handle failed payment"""
        customer_id = invoice['customer']
        customer = stripe.Customer.retrieve(customer_id)
        user_id = customer.metadata.get('user_id')
        
        return {
            'status': 'payment_failed',
            'user_id': user_id,
            'amount': invoice['amount_due'],
            'attempt_count': invoice['attempt_count']
        }
```

### 4.2 Billing Routes

Create `billing/routes.py`:

```python
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from auth.firebase_auth import login_required
import logging

logger = logging.getLogger(__name__)

billing_bp = Blueprint('billing', __name__, url_prefix='/billing')

@billing_bp.route('/plans')
def plans():
    """Pricing plans page"""
    plans_data = {
        'basic': {
            'name': 'Basic',
            'price': 20,
            'features': [
                '100 AI insights per month',
                'Basic research sources',
                'Email support',
                '14-day free trial'
            ]
        },
        'pro': {
            'name': 'Professional',
            'price': 49,
            'features': [
                '500 AI insights per month',
                'Premium research sources',
                'Priority support',
                'API access',
                'Custom integrations',
                '14-day free trial'
            ]
        },
        'enterprise': {
            'name': 'Enterprise',
            'price': 'Custom',
            'features': [
                'Unlimited AI insights',
                'All research sources',
                'Dedicated support',
                'Advanced API access',
                'Custom AI training',
                'SLA guarantee'
            ]
        }
    }
    
    return render_template('billing/plans.html', plans=plans_data)

@billing_bp.route('/api/create-checkout', methods=['POST'])
@login_required
def create_checkout():
    """Create Stripe checkout session"""
    try:
        data = request.get_json()
        plan = data.get('plan', 'basic')
        
        if plan not in ['basic', 'pro', 'enterprise']:
            return jsonify({'error': 'Invalid plan'}), 400
        
        # Get or create Stripe customer
        from app import firestore_manager, stripe_manager
        
        user_id = session.get('user_id')
        user_email = session.get('user_email')
        user_data = firestore_manager.get_user_data(user_id)
        
        # Check if user already has active subscription
        if user_data and user_data.get('subscription', {}).get('status') == 'active':
            return jsonify({'error': 'You already have an active subscription'}), 400
        
        # Get or create Stripe customer ID
        customer_id = user_data.get('stripe_customer_id') if user_data else None
        
        if not customer_id:
            customer_id = stripe_manager.create_customer(user_id, user_email)
            if customer_id:
                firestore_manager.update_user_data(user_id, {
                    'stripe_customer_id': customer_id
                })
        
        # Create checkout session
        price_id = stripe_manager.price_ids.get(plan)
        if not price_id:
            return jsonify({'error': 'Invalid plan configuration'}), 500
        
        success_url = url_for('billing.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = url_for('billing.plans', _external=True)
        
        checkout_url = stripe_manager.create_checkout_session(
            customer_id=customer_id,
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        if checkout_url:
            return jsonify({'checkout_url': checkout_url})
        else:
            return jsonify({'error': 'Failed to create checkout session'}), 500
            
    except Exception as e:
        logger.error(f"Checkout creation error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@billing_bp.route('/api/portal', methods=['POST'])
@login_required
def create_portal():
    """Create Stripe billing portal session"""
    try:
        from app import firestore_manager, stripe_manager
        
        user_id = session.get('user_id')
        user_data = firestore_manager.get_user_data(user_id)
        
        if not user_data or not user_data.get('stripe_customer_id'):
            return jsonify({'error': 'No billing account found'}), 404
        
        return_url = url_for('auth.dashboard', _external=True)
        portal_url = stripe_manager.create_billing_portal_session(
            user_data['stripe_customer_id'],
            return_url
        )
        
        if portal_url:
            return jsonify({'portal_url': portal_url})
        else:
            return jsonify({'error': 'Failed to create portal session'}), 500
            
    except Exception as e:
        logger.error(f"Portal creation error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@billing_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        from app import stripe_manager, firestore_manager
        
        result = stripe_manager.handle_webhook(payload, sig_header)
        
        # Update user data based on webhook event
        if result['status'] == 'success':
            # New subscription created
            firestore_manager.update_user_data(result['user_id'], {
                'subscription': result['subscription'],
                'subscription_updated_at': datetime.now()
            })
            
        elif result['status'] == 'updated':
            # Subscription updated
            firestore_manager.update_user_subscription(
                result['user_id'],
                result['subscription']
            )
            
        elif result['status'] == 'payment_failed':
            # Handle payment failure
            firestore_manager.update_user_data(result['user_id'], {
                'subscription': None,
                'subscription_updated_at': None
            })
            
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
```

### 2.3 Protecting Main Application Routes

Update your main `app.py` to include reCAPTCHA protection for the insights generation:

```python
# Add to your existing app.py imports
from security.recaptcha_manager import RecaptchaManager, recaptcha_required

# Initialize reCAPTCHA manager in your app setup
recaptcha_manager = RecaptchaManager()
recaptcha_manager.init_app(app)
app.extensions['recaptcha'] = recaptcha_manager

# Protect the insights generation endpoint
@app.route('/api/generate', methods=['POST'])
@login_required
@subscription_required(['basic', 'pro', 'enterprise'])
@recaptcha_required('GENERATE_INSIGHT', score_threshold=0.3)  # Lower threshold for paid users
def generate_insights_protected():
    """Generate insights with reCAPTCHA and subscription protection"""
    try:
        data = request.get_json()
        
        # Log security metrics
        recaptcha_score = getattr(request, 'recaptcha_score', None)
        user_id = session.get('user_id')
        
        logger.info(f"Insight generation: user={user_id}, recaptcha_score={recaptcha_score}")
        
        # Check rate limits (implement this in Step 4)
        from app import rate_limiter
        if not rate_limiter.check_user_limits(user_id):
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        # Your existing insights generation logic here
        topic = data.get('topic')
        specific_instructions = data.get('specific_instructions', '')
        
        # Generate insights using CrewAI (your existing code)
        insights = your_existing_generate_function(topic, specific_instructions)
        
        # Update usage metrics
        from app import firestore_manager
        firestore_manager.increment_usage(user_id, 'insights_generated')
        
        return jsonify({
            'success': True,
            'insights': insights,
            'security_score': recaptcha_score if app.debug else None  # Only show in debug
        })
        
    except Exception as e:
        logger.error(f"Insights generation error: {e}")
        return jsonify({'error': 'Failed to generate insights'}), 500

# Add template context processor for reCAPTCHA site key
@app.context_processor
def inject_recaptcha_site_key():
    """Make reCAPTCHA site key available to all templates"""
    return {
        'recaptcha_site_key': recaptcha_manager.get_site_key()
    }
```

### 2.4 Environment Configuration

Add these environment variables to your `.env` file:

```bash
# reCAPTCHA Enterprise Configuration
RECAPTCHA_SITE_KEY=6LeOTG4rAAAAAMEQOLsHLEX5T5WS6ShIsK5VyRdr
RECAPTCHA_API_KEY=your-recaptcha-api-key
RECAPTCHA_SCORE_THRESHOLD=0.5
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

### 2.5 Base Template Update

Update your `templates/base.html` to include reCAPTCHA:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}AI Insights Generator{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- reCAPTCHA Enterprise (if site key available) -->
    {% if config.RECAPTCHA_SITE_KEY %}
    <script src="https://www.google.com/recaptcha/enterprise.js?render={{ config.RECAPTCHA_SITE_KEY }}"></script>
    <meta name="recaptcha-site-key" content="{{ config.RECAPTCHA_SITE_KEY }}">
    {% endif %}
    
    {% block head %}{% endblock %}
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <i class="fas fa-brain me-2"></i>AI Insights Generator
            </a>
            
            <div class="navbar-nav ms-auto">
                {% if session.user_id %}
                <a class="nav-link" href="{{ url_for('auth.dashboard') }}">Dashboard</a>
                <a class="nav-link" href="#" onclick="logout()">Logout</a>
                {% else %}
                <a class="nav-link" href="{{ url_for('auth.login') }}">Login</a>
                <a class="nav-link" href="{{ url_for('auth.signup') }}">Sign Up</a>
                {% endif %}
            </div>
        </div>
    </nav>
    
    <!-- Main Content -->
    <main class="container-fluid py-4">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- reCAPTCHA Manager (if site key available) -->
    {% if config.RECAPTCHA_SITE_KEY %}
    <script src="{{ url_for('static', filename='js/recaptcha.js') }}"></script>
    {% endif %}
    
    <script>
        // Logout function
        async function logout() {
            const response = await fetch('/auth/api/logout', {
                method: 'POST'
            });
            
            if (response.ok) {
                window.location.href = '/';
            }
        }
    </script>
    
    {% block scripts %}{% endblock %}
</body>
</html>