from flask import Blueprint, jsonify, session, request
from core.insights_manager import FirestoreManager
from auth.firebase_auth import login_required

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
