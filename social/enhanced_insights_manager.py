# Add these methods to your core/insights_manager.py FirestoreManager class

def get_community_insights(self, sort_by='recent', page=1, per_page=12) -> List[GeneratedInsights]:
    """Get paginated community insights with sorting"""
    try:
        if not self.use_firestore or not self.db:
            # Fallback to in-memory storage
            shared_insights = [insights for insights in insights_storage.values() if insights.is_shared]
            return self._sort_and_paginate_insights(shared_insights, sort_by, page, per_page)
        
        # Build Firestore query
        query = self.db.collection(FIRESTORE_COLLECTION).where('is_shared', '==', True)
        
        # Apply sorting
        if sort_by == 'likes':
            query = query.order_by('likes', direction=firestore.Query.DESCENDING)
        elif sort_by == 'pinned':
            query = query.order_by('is_pinned', direction=firestore.Query.DESCENDING)\
                         .order_by('created_at', direction=firestore.Query.DESCENDING)
        else:  # recent
            query = query.order_by('created_at', direction=firestore.Query.DESCENDING)
        
        # Apply pagination
        offset = (page - 1) * per_page
        docs = query.offset(offset).limit(per_page).stream()
        
        insights_list = []
        for doc in docs:
            try:
                data = doc.to_dict()
                data.pop('created_at', None)
                data.pop('updated_at', None)
                
                insights = GeneratedInsights(**data)
                insights_list.append(insights)
                
            except Exception as e:
                logger.warning(f"Error parsing community insight document {doc.id}: {e}")
                continue
        
        return insights_list
        
    except Exception as e:
        logger.error(f"Error retrieving community insights: {e}")
        return []

def get_community_insights_count(self) -> int:
    """Get total count of shared insights"""
    try:
        if not self.use_firestore or not self.db:
            return len([insights for insights in insights_storage.values() if insights.is_shared])
        
        query = self.db.collection(FIRESTORE_COLLECTION).where('is_shared', '==', True)
        return len(list(query.stream()))
        
    except Exception as e:
        logger.error(f"Error counting community insights: {e}")
        return 0

def search_community_insights(self, query: str, sort_by='recent', page=1, per_page=12) -> List[GeneratedInsights]:
    """Search shared insights by topic or content"""
    try:
        if not self.use_firestore or not self.db:
            # Fallback search in memory
            shared_insights = [insights for insights in insights_storage.values() 
                             if insights.is_shared and 
                             (query.lower() in insights.topic.lower() or 
                              any(query.lower() in insight.title.lower() for insight in insights.insights))]
            return self._sort_and_paginate_insights(shared_insights, sort_by, page, per_page)
        
        # For Firestore, we'll do a simple topic search first
        # Note: Full-text search would require additional setup
        base_query = self.db.collection(FIRESTORE_COLLECTION).where('is_shared', '==', True)
        
        # Search in topic field (case-insensitive search requires some workarounds in Firestore)
        # This is a simplified approach - for production, consider using Algolia or Elasticsearch
        all_docs = base_query.stream()
        
        filtered_insights = []
        for doc in all_docs:
            try:
                data = doc.to_dict()
                
                # Check if query matches topic or any insight content
                if (query.lower() in data.get('topic', '').lower() or
                    any(query.lower() in insight.get('title', '').lower() 
                        for insight in data.get('insights', []))):
                    
                    data.pop('created_at', None)
                    data.pop('updated_at', None)
                    insights = GeneratedInsights(**data)
                    filtered_insights.append(insights)
                    
            except Exception as e:
                logger.warning(f"Error parsing search result {doc.id}: {e}")
                continue
        
        return self._sort_and_paginate_insights(filtered_insights, sort_by, page, per_page)
        
    except Exception as e:
        logger.error(f"Error searching community insights: {e}")
        return []

def get_search_results_count(self, query: str) -> int:
    """Get count of search results"""
    try:
        if not self.use_firestore or not self.db:
            return len([insights for insights in insights_storage.values() 
                       if insights.is_shared and 
                       (query.lower() in insights.topic.lower() or 
                        any(query.lower() in insight.title.lower() for insight in insights.insights))])
        
        # Similar search logic as above but just counting
        base_query = self.db.collection(FIRESTORE_COLLECTION).where('is_shared', '==', True)
        all_docs = base_query.stream()
        
        count = 0
        for doc in all_docs:
            try:
                data = doc.to_dict()
                if (query.lower() in data.get('topic', '').lower() or
                    any(query.lower() in insight.get('title', '').lower() 
                        for insight in data.get('insights', []))):
                    count += 1
            except Exception as e:
                continue
        
        return count
        
    except Exception as e:
        logger.error(f"Error counting search results: {e}")
        return 0

def update_pin_status(self, insight_id: str, is_pinned: bool, admin_user_id: str) -> bool:
    """Update pinned status of an insight (admin only)"""
    try:
        if not self.use_firestore or not self.db:
            if insight_id in insights_storage:
                insights_storage[insight_id].is_pinned = is_pinned
                return True
            return False
        
        doc_ref = self.db.collection(FIRESTORE_COLLECTION).document(insight_id)
        doc = doc_ref.get()
        
        if doc.exists:
            doc_ref.update({
                'is_pinned': is_pinned,
                'pinned_by': admin_user_id if is_pinned else None,
                'pinned_at': firestore.SERVER_TIMESTAMP if is_pinned else None,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            # Update in-memory storage too
            if insight_id in insights_storage:
                insights_storage[insight_id].is_pinned = is_pinned
            
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error updating pin status for insight {insight_id}: {e}")
        return False

def get_community_stats(self) -> dict:
    """Get community statistics"""
    try:
        if not self.use_firestore or not self.db:
            shared_insights = [insights for insights in insights_storage.values() if insights.is_shared]
            return {
                'total_insights': len(shared_insights),
                'total_likes': sum(getattr(insights, 'likes', 0) for insights in shared_insights),
                'total_authors': len(set(insights.author_id for insights in shared_insights if insights.author_id)),
                'trending_topics': []
            }
        
        # Get all shared insights
        docs = self.db.collection(FIRESTORE_COLLECTION).where('is_shared', '==', True).stream()
        
        total_insights = 0
        total_likes = 0
        authors = set()
        topics = {}
        
        for doc in docs:
            try:
                data = doc.to_dict()
                total_insights += 1
                total_likes += data.get('likes', 0)
                
                if data.get('author_id'):
                    authors.add(data['author_id'])
                
                # Count topic frequencies
                topic = data.get('topic', '').lower().strip()
                if topic:
                    topics[topic] = topics.get(topic, 0) + 1
                    
            except Exception as e:
                continue
        
        # Get top topics
        trending_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_insights': total_insights,
            'total_likes': total_likes,
            'total_authors': len(authors),
            'trending_topics': [{'topic': topic, 'count': count} for topic, count in trending_topics]
        }
        
    except Exception as e:
        logger.error(f"Error getting community stats: {e}")
        return {
            'total_insights': 0,
            'total_likes': 0,
            'total_authors': 0,
            'trending_topics': []
        }

def get_trending_topics(self, limit=10) -> List[dict]:
    """Get trending topics from recent insights"""
    try:
        from datetime import datetime, timedelta
        
        # Get insights from last 7 days
        one_week_ago = datetime.now() - timedelta(days=7)
        
        if not self.use_firestore or not self.db:
            recent_insights = [insights for insights in insights_storage.values() 
                             if insights.is_shared]
            topics = {}
            for insights in recent_insights:
                topic = insights.topic.lower().strip()
                if topic:
                    topics[topic] = topics.get(topic, 0) + 1
        else:
            query = self.db.collection(FIRESTORE_COLLECTION)\
                         .where('is_shared', '==', True)\
                         .where('created_at', '>=', one_week_ago)\
                         .stream()
            
            topics = {}
            for doc in query:
                try:
                    data = doc.to_dict()
                    topic = data.get('topic', '').lower().strip()
                    if topic:
                        topics[topic] = topics.get(topic, 0) + 1
                except Exception as e:
                    continue
        
        # Sort by frequency and return top topics
        trending = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [{'topic': topic.title(), 'count': count} for topic, count in trending]
        
    except Exception as e:
        logger.error(f"Error getting trending topics: {e}")
        return []

def _sort_and_paginate_insights(self, insights_list: List[GeneratedInsights], sort_by: str, page: int, per_page: int) -> List[GeneratedInsights]:
    """Helper method to sort and paginate insights"""
    # Sort insights
    if sort_by == 'likes':
        insights_list.sort(key=lambda x: getattr(x, 'likes', 0), reverse=True)
    elif sort_by == 'pinned':
        insights_list.sort(key=lambda x: (getattr(x, 'is_pinned', False), x.timestamp), reverse=True)
    else:  # recent
        insights_list.sort(key=lambda x: x.timestamp, reverse=True)
    
    # Apply pagination
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    return insights_list[start_idx:end_idx]