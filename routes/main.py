from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, make_response, session
from core.crew_ai import AIInsightsCrew
from core.insights_manager import FirestoreManager
from auth.firebase_auth import login_required
import os
import logging

logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)

insights_firestore_manager = FirestoreManager()

def get_api_keys() -> tuple:
    """Get API keys from environment variables"""
    tavily_key = os.getenv('TAVILY_API_KEY')
    serper_key = os.getenv('SERPER_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    return tavily_key, serper_key, openai_key

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
    """Main page with insights generator form"""
    user_id = session.get('user_id')
    
    if user_id:
        insights_list = insights_firestore_manager.get_all_insights()
    else:
        insights_list = insights_firestore_manager.get_shared_insights()
    
    return render_template('index.html', insights_list=insights_list)

@main_bp.route('/generate', methods=['POST'])
@login_required
def generate_insights():
    """Generate insights based on user input"""
    try:
        topic = request.form.get('topic', '').strip()
        instructions = request.form.get('instructions', '').strip()
        source = request.form.get('source', 'general').strip()
        time_range = request.form.get('time_range', 'none').strip()
        
        # Convert 'none' to None for consistent handling
        if time_range == 'none' or time_range == '':
            time_range = None
        
        if not topic:
            flash('Please provide a topic for research.', 'error')
            return redirect(url_for('main.index'))
        
        tavily_key, serper_key, openai_key = get_api_keys()
        
        if not openai_key:
            flash('OpenAI API key is required. Please set OPENAI_API_KEY environment variable.', 'error')
            return redirect(url_for('main.index'))
        
        if not tavily_key and not serper_key:
            flash('At least one search API key (Tavily or Serper) is required.', 'error')
            return redirect(url_for('main.index'))
        
        try:
            crew_system = AIInsightsCrew(tavily_key, serper_key, openai_key)
        except Exception as init_error:
            logger.error(f"❌ Error initializing AI crew system: {init_error}")
            if "proxies" in str(init_error).lower():
                flash('Search tool configuration issue detected. Please try again or contact support if the problem persists.', 'error')
            else:
                flash(f'Failed to initialize AI system: {str(init_error)}', 'error')
            return redirect(url_for('main.index'))
        
        insights = crew_system.generate_insights(topic, instructions, source, time_range)
        
        user_id = session.get('user_id')
        user_email = session.get('user_email', '')
        author_name = user_email.split('@')[0] if user_email else "Anonymous"
        
        insights.author_id = user_id
        insights.author_name = author_name
        insights.author_email = user_email
        
        saved = insights_firestore_manager.save_insights(insights)
        
        if saved:
            flash(f'Successfully generated and saved insights for "{topic}"!', 'success')
        else:
            flash(f'Generated insights for "{topic}" (saved to temporary storage)', 'warning')
        
        return redirect(url_for('main.view_insights', insight_id=insights.id))
        
    except Exception as e:
        logger.error(f"❌ Error generating insights: {e}")
        flash(f'Error generating insights: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@main_bp.route('/insights/<insight_id>')
def view_insights(insight_id):
    """View specific insights"""
    insights = insights_firestore_manager.get_insights(insight_id)
    if not insights:
        flash('Insights not found.', 'error')
        return redirect(url_for('main.index'))
    
    insights_list = insights_firestore_manager.get_all_insights()
    return render_template('insights.html', insights=insights, insights_list=insights_list)

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
    response.headers['Content-Disposition'] = f'attachment; filename="AI_Insights_Report_{insights.topic.replace(" ", "_")}_{insights.timestamp[:10]}.html"'
    
    return response
