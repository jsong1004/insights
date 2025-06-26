from flask import Flask
from dotenv import load_dotenv
import logging
import os
import re

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

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)