# Update your app.py to include admin context processor

from flask import Flask, session
from dotenv import load_dotenv
import logging
import os
import re
from datetime import datetime, timedelta, timezone

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Add custom Jinja2 filter for URL linkification
    @app.template_filter('linkify_urls')
    def linkify_urls(text):
        """Convert URLs in text to clickable links"""
        if not text:
            return text
        
        # Pattern to match URLs
        url_pattern = r'(https?://[^\s<>"]+)'
        
        def replace_url(match):
            url = match.group(1)
            return f'<a href="{url}" target="_blank" rel="noopener noreferrer" class="source-link">{url} <span class="external-icon">↗</span></a>'
        
        return re.sub(url_pattern, replace_url, text)

    # Initialize Firebase Authentication
    try:
        from auth.firebase_auth import FirebaseAuthManager
        from auth.routes import auth_bp
        firebase_auth_manager = FirebaseAuthManager()
        firebase_auth_manager.init_app(app)
        app.extensions['firebase_auth'] = firebase_auth_manager
        app.register_blueprint(auth_bp)
        logging.info("✅ Firebase Authentication initialized")
        
        from auth.firestore_manager import UserFirestoreManager
        firestore_manager = UserFirestoreManager()
        app.extensions['firestore_manager'] = firestore_manager
        logging.info("✅ User Firestore Manager initialized")
    except ImportError:
        logging.warning("❌ Firebase Authentication not available")

    # Register blueprints
    from routes.main import main_bp
    from routes.api import api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    # Add admin context processor
    @app.context_processor
    def inject_admin_status():
        """Make admin status available to all templates"""
        user_id = session.get('user_id')
        is_admin = False
        
        if user_id:
            try:
                firestore_manager = app.extensions.get('firestore_manager')
                if firestore_manager:
                    is_admin = firestore_manager.is_user_admin(user_id)
            except Exception as e:
                logging.warning(f"Error checking admin status in template context: {e}")
        
        return {'is_admin': is_admin}

    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=15)
        session.modified = True
        if 'user_id' in session and 'last_activity' in session:
            last_activity = session['last_activity']
            # Ensure both datetimes are timezone-aware for proper comparison
            if isinstance(last_activity, str):
                # If last_activity is stored as string, parse it
                try:
                    last_activity = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    # If parsing fails, reset the session
                    session.pop('user_id', None)
                    session.pop('last_activity', None)
                    return
            elif last_activity.tzinfo is None:
                # If naive datetime, assume UTC
                last_activity = last_activity.replace(tzinfo=timezone.utc)
            
            # Use timezone-aware current time
            current_time = datetime.now(timezone.utc)
            if current_time - last_activity > app.permanent_session_lifetime:
                session.pop('user_id', None)
                session.pop('last_activity', None)
        if 'user_id' in session:
            # Store timezone-aware datetime
            session['last_activity'] = datetime.now(timezone.utc)

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)