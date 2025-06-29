# Add these routes to your routes/main.py

@main_bp.route('/community')
def community():
    """Community page showing shared insights with sorting options"""
    sort_by = request.args.get('sort', 'recent')  # recent, likes, pinned
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    try:
        # Get shared insights with pagination
        insights_list = insights_firestore_manager.get_community_insights(
            sort_by=sort_by, 
            page=page, 
            per_page=per_page
        )
        
        # Get pagination info
        total_insights = insights_firestore_manager.get_community_insights_count()
        total_pages = (total_insights + per_page - 1) // per_page
        
        # Pagination object
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total_insights,
            'pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_num': page - 1 if page > 1 else None,
            'next_num': page + 1 if page < total_pages else None
        }
        
        return render_template('community.html', 
                             insights_list=insights_list,
                             sort_by=sort_by,
                             pagination=pagination)
        
    except Exception as e:
        logger.error(f"Error loading community page: {e}")
        flash('Failed to load community insights. Please try again.', 'error')
        return redirect(url_for('main.index'))

@main_bp.route('/community/search')
def community_search():
    """Search shared insights"""
    query = request.args.get('q', '').strip()
    sort_by = request.args.get('sort', 'recent')
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    if not query:
        return redirect(url_for('main.community'))
    
    try:
        # Search insights
        insights_list = insights_firestore_manager.search_community_insights(
            query=query,
            sort_by=sort_by,
            page=page,
            per_page=per_page
        )
        
        total_insights = insights_firestore_manager.get_search_results_count(query)
        total_pages = (total_insights + per_page - 1) // per_page
        
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total_insights,
            'pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_num': page - 1 if page > 1 else None,
            'next_num': page + 1 if page < total_pages else None
        }
        
        return render_template('community.html',
                             insights_list=insights_list,
                             sort_by=sort_by,
                             pagination=pagination,
                             search_query=query)
        
    except Exception as e:
        logger.error(f"Error searching community insights: {e}")
        flash('Search failed. Please try again.', 'error')
        return redirect(url_for('main.community'))

# Add these API routes to your routes/api.py

@api_bp.route('/insights/<insight_id>/pin', methods=['POST'])
@login_required
def api_pin_insight(insight_id):
    """Pin/unpin insight (admin only)"""
    user_id = session.get('user_id')
    
    # Check if user is admin
    firestore_manager = current_app.extensions.get('firestore_manager')
    user_data = firestore_manager.get_user_data(user_id)
    
    if not user_data or not user_data.get('is_admin', False):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        is_pinned = data.get('is_pinned', False)
        
        success = insights_firestore_manager.update_pin_status(insight_id, is_pinned, user_id)
        
        if success:
            return jsonify({
                'success': True,
                'is_pinned': is_pinned,
                'message': f'Insight {"pinned" if is_pinned else "unpinned"} successfully'
            })
        else:
            return jsonify({'error': 'Failed to update pin status'}), 500
            
    except Exception as e:
        logger.error(f"Error pinning insight: {e}")
        return jsonify({'error': 'Failed to update pin status'}), 500

@api_bp.route('/community-stats')
def get_community_stats():
    """Get community statistics"""
    try:
        stats = insights_firestore_manager.get_community_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error getting community stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve community statistics'
        }), 500

@api_bp.route('/trending-topics')
def get_trending_topics():
    """Get trending topics from community insights"""
    try:
        topics = insights_firestore_manager.get_trending_topics(limit=10)
        return jsonify({
            'success': True,
            'topics': topics
        })
    except Exception as e:
        logger.error(f"Error getting trending topics: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve trending topics'
        }), 500