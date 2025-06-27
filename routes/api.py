import logging
from flask import Blueprint, jsonify, session, request, current_app
from core.insights_manager import FirestoreManager
from auth.firebase_auth import login_required

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')

insights_firestore_manager = FirestoreManager()

@api_bp.route('/insights')
def api_insights():
    """API endpoint to get all insights"""
    insights_list = insights_firestore_manager.get_all_insights()
    return jsonify([insights.model_dump() for insights in insights_list])

@api_bp.route('/insights/<insight_id>')
def api_get_insights(insight_id):
    """API endpoint to get specific insights"""
    insights = insights_firestore_manager.get_insights(insight_id)
    if insights:
        return jsonify(insights.model_dump())
    return jsonify({'error': 'Insights not found'}), 404

@api_bp.route('/insights/<insight_id>/like', methods=['POST'])
@login_required
def api_toggle_like(insight_id):
    """API endpoint to toggle like for an insight"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    success = insights_firestore_manager.toggle_like(insight_id, user_id)
    
    if success:
        insights = insights_firestore_manager.get_insights(insight_id)
        if insights:
            return jsonify({
                'success': True,
                'likes': insights.likes,
                'liked': user_id in insights.liked_by
            })
    
    return jsonify({'error': 'Failed to toggle like'}), 500

@api_bp.route('/insights/<insight_id>/share', methods=['POST'])
@login_required
def api_toggle_sharing(insight_id):
    """API endpoint to toggle sharing status for an insight"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    is_shared = data.get('is_shared', True)
    
    success = insights_firestore_manager.update_sharing_status(insight_id, is_shared, user_id)
    
    if success:
        return jsonify({
            'success': True,
            'is_shared': is_shared
        })
    
    return jsonify({'error': 'Failed to update sharing status'}), 500

@api_bp.route('/shared-insights')
def api_shared_insights():
    """API endpoint to get all shared insights"""
    insights_list = insights_firestore_manager.get_shared_insights()
    return jsonify([insights.model_dump() for insights in insights_list])

@api_bp.route('/my-insights')
@login_required
def api_my_insights():
    """API endpoint to get current user's insights"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        insights_list = insights_firestore_manager.get_user_insights(user_id)
        
        # Transform the data for the table
        insights_data = []
        for insight in insights_list:
            insights_data.append({
                'id': insight.id,
                'title': insight.topic,
                'tokens': insight.total_tokens,
                'date': insight.timestamp,
                'processing_time': insight.processing_time,
                'total_insights': insight.total_insights,
                'is_shared': insight.is_shared,
                'likes': insight.likes
            })
        
        return jsonify({
            'success': True,
            'insights': insights_data
        })
        
    except Exception as e:
        logger.error(f"Error getting user insights: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve user insights'
        }), 500

@api_bp.route('/usage-stats')
@login_required
def get_usage_stats():
    """Get current user's usage statistics"""
    try:
        user_id = session.get('user_id')
        firestore_manager = current_app.extensions.get('firestore_manager')
        
        stats = firestore_manager.get_usage_stats(user_id)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve usage statistics'
        }), 500

@api_bp.route('/dashboard-analytics')
@login_required
def get_dashboard_analytics():
    """Get comprehensive dashboard analytics"""
    try:
        user_id = session.get('user_id')
        firestore_manager = current_app.extensions.get('firestore_manager')
        
        analytics = firestore_manager.get_dashboard_analytics(user_id)
        
        return jsonify({
            'success': True,
            'analytics': analytics
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve dashboard analytics'
        }), 500

@api_bp.route('/recent-activities')
@login_required
def get_recent_activities():
    """Get recent activities for the current user"""
    try:
        user_id = session.get('user_id')
        limit = request.args.get('limit', 10, type=int)
        firestore_manager = current_app.extensions.get('firestore_manager')
        
        activities = firestore_manager.get_recent_activities(user_id, limit=limit)
        
        return jsonify({
            'success': True,
            'activities': activities
        })
        
    except Exception as e:
        logger.error(f"Error getting recent activities: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve recent activities'
        }), 500

@api_bp.route('/track-activity', methods=['POST'])
@login_required
def track_activity():
    """Track a user activity"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        activity_type = data.get('type')
        description = data.get('description')
        metadata = data.get('metadata', {})
        
        if not activity_type or not description:
            return jsonify({
                'success': False,
                'error': 'Activity type and description are required'
            }), 400
        
        firestore_manager = current_app.extensions.get('firestore_manager')
        success = firestore_manager.track_activity(user_id, activity_type, description, metadata)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Activity tracked successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to track activity'
            }), 500
        
    except Exception as e:
        logger.error(f"Error tracking activity: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to track activity'
        }), 500
