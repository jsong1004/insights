from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, make_response, session, current_app
from core.crew_ai import AIInsightsCrew
from core.insights_manager import FirestoreManager
from auth.firebase_auth import login_required
import os
import logging

logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)

insights_firestore_manager = FirestoreManager()

@main_bp.route('/status')
def health_check():
    """Health check endpoint for Docker and monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'ai-insights-generator',
        'version': '2.0'
    }), 200

@main_bp.route('/')
def index():
    """Public home page"""
    return render_template('index.html')

@main_bp.route('/insights')
@login_required
def insights():
    """Insights generation form page for authenticated users"""
    user_id = session.get('user_id')
    insights_list = insights_firestore_manager.get_all_insights()
    return render_template('insights_form.html', insights_list=insights_list)

@main_bp.route('/generate', methods=['POST'])
@login_required
def generate_insights():
    """Generate insights based on user input"""
    try:
        # Get user firestore manager
        firestore_manager = current_app.extensions.get('firestore_manager')
        user_id = session.get('user_id')
        
        # Check usage limits
        usage_limits = firestore_manager.check_usage_limits(user_id)
        
        if not usage_limits['can_generate']:
            if usage_limits['daily_insights_exceeded']:
                flash('Daily insight limit reached. Please try again tomorrow or upgrade your plan.', 'error')
            elif usage_limits['monthly_insights_exceeded']:
                flash('Monthly insight limit reached. Please upgrade your plan to continue.', 'error')
            else:
                flash('Usage limit reached. Please upgrade your plan.', 'error')
            return redirect(url_for('main.index'))
        
        # Your existing insight generation code...
        topic = request.form.get('topic', '').strip()
        instructions = request.form.get('instructions', '').strip()
        source = request.form.get('source', 'general').strip()
        time_range = request.form.get('time_range', 'none').strip()
        
        # ... existing validation and CrewAI code ...
        tavily_key = os.getenv('TAVILY_API_KEY')
        serper_key = os.getenv('SERPER_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')

        crew_system = AIInsightsCrew(tavily_key, serper_key, openai_key)
        
        # Generate insights
        insights = crew_system.generate_insights(topic, instructions, source, time_range)
        
        # Set author information from session
        insights.author_id = user_id
        insights.author_email = session.get('user_email', 'unknown@example.com')
        
        # Try to get display name from Firestore user data
        try:
            user_data = firestore_manager.get_user_data(user_id)
            if user_data and user_data.get('display_name'):
                insights.author_name = user_data['display_name']
            else:
                # Fallback: Try to get from Firebase Auth
                firebase_auth_manager = current_app.extensions.get('firebase_auth')
                if firebase_auth_manager and firebase_auth_manager.initialized:
                    firebase_user = firebase_auth_manager.get_user(user_id)
                    if firebase_user and firebase_user.display_name:
                        insights.author_name = firebase_user.display_name
                    else:
                        # Final fallback: extract username from email
                        insights.author_name = insights.author_email.split('@')[0] if insights.author_email else 'Anonymous'
                else:
                    # Firebase not available, use email fallback
                    insights.author_name = insights.author_email.split('@')[0] if insights.author_email else 'Anonymous'
        except Exception as e:
            logger.warning(f"Could not get user display name: {e}")
            # Fallback to email-based name
            insights.author_name = insights.author_email.split('@')[0] if insights.author_email else 'Anonymous'
        
        # Track usage with actual token count
        tokens_used = insights.total_tokens
        search_requests = len(insights.insights) if insights.insights else 1
        
        firestore_manager.track_insight_generation(
            user_id, 
            tokens_used, 
            search_requests
        )
        
        # Save insights with author information
        saved = insights_firestore_manager.save_insights(insights)
        
        # Track insight generation activity
        try:
            processing_time = getattr(insights, 'processing_time', 0)
            firestore_manager.track_activity(
                user_id,
                'insight_generated',
                f'Generated insights for "{topic}"',
                {
                    'topic': topic,
                    'tokens': tokens_used,
                    'processing_time': processing_time,
                    'source': source,
                    'insights_count': len(insights.insights) if insights.insights else 0,
                    'status': 'success' if saved else 'partial'
                }
            )
        except Exception as e:
            logger.warning(f"Failed to track insight generation activity: {e}")
        
        # ... rest of your existing code ...
        if saved:
            flash(f'Successfully generated and saved insights for "{topic}"!', 'success')
        else:
            flash(f'Generated insights for "{topic}" (saved to temporary storage)', 'warning')
        
        return redirect(url_for('main.view_insight', insight_id=insights.id))
        
    except Exception as e:
        logger.error(f"❌ Error generating insights: {e}")
        flash(f'Error generating insights: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@main_bp.route('/insight/<insight_id>')
def view_insight(insight_id):
    """View specific insight (public access for shared insights)"""
    insights = insights_firestore_manager.get_insights(insight_id)
    if not insights:
        flash('Insight not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Check if insight is private and user has access
    user_id = session.get('user_id')
    if not insights.is_shared and (not user_id or insights.author_id != user_id):
        flash('This insight is private.', 'error')
        return redirect(url_for('main.index'))
    
    # Track insights viewing activity (only for logged-in users)
    if user_id:
        try:
            firestore_manager = current_app.extensions.get('firestore_manager')
            firestore_manager.track_activity(
                user_id,
                'insights_viewed',
                f'Viewed insights: "{insights.topic}"',
                {
                    'insight_id': insight_id,
                    'topic': insights.topic,
                    'insights_count': len(insights.insights) if insights.insights else 0
                }
            )
        except Exception as e:
            logger.warning(f"Failed to track insights viewing activity: {e}")
    
    return render_template('insights.html', insights=insights)

@main_bp.route('/delete/<insight_id>', methods=['POST'])
@login_required
def delete_insights(insight_id):
    """Delete specific insights"""
    deleted = insights_firestore_manager.delete_insights(insight_id)
    if deleted:
        flash('Insights deleted successfully.', 'success')
    else:
        flash('Insights not found.', 'error')
    
    return redirect(url_for('main.index'))

@main_bp.route('/download/<insight_id>')
@login_required
def download_insights(insight_id):
    """Download insights as formatted HTML file"""
    insights = insights_firestore_manager.get_insights(insight_id)
    if not insights:
        flash('Insights not found.', 'error')
        return redirect(url_for('main.index'))
    
    html_content = render_template('download_report.html', insights=insights)
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename="insights_{insight_id}.html"'
    
    return response

@main_bp.route('/community')
def community():
    """Community page showing shared insights with modern social features"""
    sort_by = request.args.get('sort', 'recent')  # recent, trending, most_liked, featured
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    try:
        # Get insights based on sort type
        if sort_by == 'trending':
            insights_list = insights_firestore_manager.get_trending_insights(limit=per_page * 5)
        elif sort_by == 'most_liked':
            insights_list = insights_firestore_manager.get_most_liked_insights(limit=per_page * 5)
        elif sort_by == 'featured':
            insights_list = insights_firestore_manager.get_featured_insights(limit=per_page * 5)
        else:  # recent
            insights_list = insights_firestore_manager.get_shared_insights()
        
        # Simple pagination
        total_insights = len(insights_list)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_insights = insights_list[start_idx:end_idx]
        
        # Create pagination object
        total_pages = (total_insights + per_page - 1) // per_page if total_insights > 0 else 1
        
        class SimplePagination:
            def __init__(self, page, per_page, total, items):
                self.page = page
                self.per_page = per_page
                self.total = total
                self.pages = total_pages
                self.has_prev = page > 1
                self.has_next = page < total_pages
                self.prev_num = page - 1 if self.has_prev else None
                self.next_num = page + 1 if self.has_next else None
                self.items = items
            
            def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
                last = self.pages
                for num in range(1, last + 1):
                    if num <= left_edge or \
                       (self.page - left_current - 1 < num < self.page + right_current) or \
                       num > last - right_edge:
                        yield num
        
        pagination = SimplePagination(page, per_page, total_insights, paginated_insights)
        
        return render_template('community.html', 
                             insights=paginated_insights,
                             sort_by=sort_by,
                             pagination=pagination)
        
    except Exception as e:
        logger.error(f"Error loading community page: {e}")
        flash('Failed to load community insights. Please try again.', 'error')
        return redirect(url_for('main.index'))

# Route alias for backward compatibility
@main_bp.route('/view_insights/<insight_id>')
def view_insights(insight_id):
    """Alias for view_insight for backward compatibility"""
    return view_insight(insight_id)
