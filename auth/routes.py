from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
import firebase_admin.auth as firebase_auth
from datetime import datetime, timedelta
from auth.firebase_auth import login_required
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
        session['last_activity'] = datetime.utcnow()
        session.permanent = True
        
        logger.info(f"User login successful: {decoded_token['uid']}")
        
        # Update last login in Firestore (if available)
        try:
            from app import firestore_manager
            firestore_manager.update_user_login(decoded_token['uid'])
            
            # Track login activity
            firestore_manager.track_activity(
                decoded_token['uid'], 
                'login', 
                'User logged in',
                {'email': decoded_token.get('email')}
            )
        except ImportError:
            logger.warning("Firestore manager not available - skipping login tracking")
        
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

@auth_bp.route('/api/signup', methods=['POST'])
def api_signup():
    """API endpoint for signup"""
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
        
        # Create user session
        session['user_id'] = decoded_token['uid']
        session['user_email'] = decoded_token.get('email')
        session['email_verified'] = decoded_token.get('email_verified', False)
        session['last_activity'] = datetime.utcnow()
        session.permanent = True
        
        logger.info(f"New user signup: {decoded_token['uid']}")
        
        # Initialize user in Firestore (if available)
        try:
            from app import firestore_manager
            
            user_data = {
                'email': decoded_token.get('email'),
                'email_verified': decoded_token.get('email_verified', False),
                'created_at': datetime.now(),
                'last_login': datetime.now(),
                'subscription': None,
                'bio': '',
                'preferences': {
                    'email_notifications': True,
                    'share_insights_by_default': True,
                    'theme': 'light'
                },
                'usage': {
                    'insights_generated': 0,
                    'insights_remaining': 5,  # Free trial insights
                    'last_reset': datetime.now()
                }
            }
            
            firestore_manager.create_user(decoded_token['uid'], user_data)
            
            # Track signup activity
            firestore_manager.track_activity(
                decoded_token['uid'], 
                'signup', 
                'User signed up',
                {'email': decoded_token.get('email')}
            )
        except ImportError:
            logger.warning("Firestore manager not available - skipping user data initialization")
        
        return jsonify({
            'success': True,
            'user': {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'emailVerified': decoded_token.get('email_verified', False),
                'isNewUser': True
            }
        })
        
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({'error': 'Signup failed'}), 500

@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    """API endpoint for logout"""
    user_id = session.get('user_id')
    
    # Track logout activity before clearing session
    if user_id:
        try:
            from app import firestore_manager
            firestore_manager.track_activity(
                user_id, 
                'logout', 
                'User logged out'
            )
        except ImportError:
            logger.warning("Firestore manager not available - skipping logout tracking")
    
    session.clear()
    logger.info(f"User logout: {user_id}")
    return redirect(url_for('auth.login'))

@auth_bp.route('/api/user', methods=['GET'])
def get_current_user():
    """Get current user info"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from app import firestore_manager
        user_data = firestore_manager.get_user_data(session['user_id'])
    except ImportError:
        user_data = None
    
    return jsonify({
        'user': {
            'uid': session['user_id'],
            'email': session.get('user_email'),
            'emailVerified': session.get('email_verified', False),
            'subscription': user_data.get('subscription') if user_data else None,
            'usage': user_data.get('usage') if user_data else None
        }
    })

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    try:
        from app import firestore_manager
        user_data = firestore_manager.get_user_data(session['user_id'])
    except ImportError:
        user_data = None
    
    return render_template('auth/dashboard.html', user_data=user_data)

@auth_bp.route('/membership', methods=['GET'])
@login_required
def membership():
    """Membership plans page"""
    try:
        from app import firestore_manager
        user_data = firestore_manager.get_user_data(session['user_id'])
        
        # Compute member type based on subscription
        member_type = 'free'  # Default to free
        if user_data and user_data.get('subscription'):
            subscription = user_data['subscription']
            plan = subscription.get('plan', 'free')
            status = subscription.get('status', 'inactive')
            
            # Determine member type
            if status == 'active' and plan in ['basic', 'pro', 'enterprise']:
                member_type = 'freemium'
            elif plan == 'freemium' or (status == 'active' and plan != 'free'):
                member_type = 'freemium'
            elif plan == 'max' or (status == 'active' and plan == 'max'):
                member_type = 'max'
        
        user_context = {
            'uid': session['user_id'],
            'email': session.get('user_email'),
            'member_type': member_type
        }
        
        return render_template('auth/membership.html', user_data=user_context)
        
    except ImportError:
        # Fallback when Firestore is not available
        user_context = {
            'uid': session['user_id'],
            'email': session.get('user_email'),
            'member_type': 'free'
        }
        return render_template('auth/membership.html', user_data=user_context)

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """User profile page"""
    try:
        from app import firestore_manager
        user_data = firestore_manager.get_user_data(session['user_id'])
        
        # Get Firebase user data for additional info
        firebase_auth_manager = current_app.extensions.get('firebase_auth')
        firebase_user = None
        try:
            firebase_user = firebase_auth.get_user(session['user_id'])
        except Exception as e:
            logger.warning(f"Could not get Firebase user data: {e}")
        
        # Combine data sources
        profile_data = {
            'uid': session['user_id'],
            'email': session.get('user_email'),
            'email_verified': session.get('email_verified', False),
            'display_name': '',
            'phone_number': '',
            'bio': '',
            'preferences': {
                'email_notifications': True,
                'share_insights_by_default': True,
                'theme': 'light'
            }
        }
        
        # Add Firebase data if available
        if firebase_user:
            profile_data.update({
                'display_name': firebase_user.display_name or '',
                'phone_number': firebase_user.phone_number or '',
                'photo_url': getattr(firebase_user, 'photo_url', '')
            })
        
        # Add Firestore data if available
        if user_data:
            profile_data.update({
                'bio': user_data.get('bio', ''),
                'preferences': user_data.get('preferences', profile_data['preferences']),
                'created_at': user_data.get('created_at'),
                'last_login': user_data.get('last_login')
            })
        
        # Compute member type based on subscription
        member_type = 'free'  # Default to free
        if user_data and user_data.get('subscription'):
            subscription = user_data['subscription']
            plan = subscription.get('plan', 'free')
            status = subscription.get('status', 'inactive')
            
            # Determine member type
            if status == 'active' and plan in ['basic', 'pro', 'enterprise']:
                member_type = 'freemium'
            elif plan == 'freemium' or (status == 'active' and plan != 'free' and plan != 'max'):
                member_type = 'freemium'
            elif plan == 'max' or (status == 'active' and plan == 'max'):
                member_type = 'max'
        
        profile_data['member_type'] = member_type
        
        return render_template('auth/profile.html', profile_data=profile_data)
        
    except ImportError:
        # Fallback when Firestore is not available
        profile_data = {
            'uid': session['user_id'],
            'email': session.get('user_email'),
            'email_verified': session.get('email_verified', False),
            'display_name': '',
            'phone_number': '',
            'bio': '',
            'preferences': {
                'email_notifications': True,
                'share_insights_by_default': True,
                'theme': 'light'
            },
            'member_type': 'free'  # Default to free when no data available
        }
        return render_template('auth/profile.html', profile_data=profile_data)

@auth_bp.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    """API endpoint to update user profile"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate and sanitize input data
        allowed_fields = ['display_name', 'bio', 'preferences']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                if field == 'display_name':
                    # Validate display name
                    display_name = data[field].strip()
                    if len(display_name) > 100:
                        return jsonify({'error': 'Display name too long (max 100 characters)'}), 400
                    update_data[field] = display_name
                    
                elif field == 'bio':
                    # Validate bio
                    bio = data[field].strip()
                    if len(bio) > 500:
                        return jsonify({'error': 'Bio too long (max 500 characters)'}), 400
                    update_data[field] = bio
                    
                elif field == 'preferences':
                    # Validate preferences
                    preferences = data[field]
                    if isinstance(preferences, dict):
                        # Only allow specific preference keys
                        allowed_prefs = ['email_notifications', 'share_insights_by_default', 'theme']
                        filtered_prefs = {}
                        for pref_key in allowed_prefs:
                            if pref_key in preferences:
                                if pref_key in ['email_notifications', 'share_insights_by_default']:
                                    filtered_prefs[pref_key] = bool(preferences[pref_key])
                                elif pref_key == 'theme':
                                    theme = preferences[pref_key]
                                    if theme in ['light', 'dark', 'auto']:
                                        filtered_prefs[pref_key] = theme
                        update_data[field] = filtered_prefs
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Update display name in Firebase if provided
        if 'display_name' in update_data:
            try:
                firebase_auth.update_user(
                    session['user_id'],
                    display_name=update_data['display_name']
                )
                logger.info(f"Updated Firebase display name for user: {session['user_id']}")
            except Exception as e:
                logger.warning(f"Could not update Firebase display name: {e}")
        
        # Update data in Firestore
        try:
            from app import firestore_manager
            success = firestore_manager.update_user_data(session['user_id'], update_data)
            
            if success:
                logger.info(f"Profile updated for user: {session['user_id']}")
                return jsonify({
                    'success': True,
                    'message': 'Profile updated successfully',
                    'updated_data': update_data
                })
            else:
                return jsonify({'error': 'Failed to update profile in database'}), 500
                
        except ImportError:
            logger.warning("Firestore not available - profile update not persisted")
            return jsonify({
                'success': True,
                'message': 'Profile updated (not persisted - Firestore unavailable)',
                'updated_data': update_data
            })
        
    except Exception as e:
        logger.error(f"Error updating profile for user {session.get('user_id')}: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500 