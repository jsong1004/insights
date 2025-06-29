import logging
import os
from typing import List, Optional
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials
from google.cloud import secretmanager
import json
from .crew_ai import GeneratedInsights

logger = logging.getLogger(__name__)

# In-memory storage for insights (fallback when Firestore is not available)
insights_storage = {}

# Firestore configuration
FIRESTORE_DATABASE = "ai-biz"
FIRESTORE_COLLECTION = "insights"

def get_service_account_from_secret_manager() -> Optional[dict]:
    """Retrieve service account key from Google Cloud Secret Manager"""
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            logger.warning("GOOGLE_CLOUD_PROJECT environment variable not set.")
            return None
        secret_name = f"projects/{project_id}/secrets/AI-Biz-Service-Account-Key/versions/latest"
        
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(request={"name": secret_name})
        secret_value = response.payload.data.decode("UTF-8")
        service_account_info = json.loads(secret_value)
        
        logger.info("✅ Successfully retrieved service account from Secret Manager")
        return service_account_info
        
    except Exception as e:
        logger.warning(f"Failed to retrieve service account from Secret Manager: {e}")
        return None

class FirestoreManager:
    """Manages Firestore database operations for insights"""
    
    def __init__(self):
        self.db = None
        self.use_firestore = False
        
        try:
            if not firebase_admin._apps:
                service_account_info = get_service_account_from_secret_manager()
                if service_account_info:
                    cred = credentials.Certificate(service_account_info)
                    firebase_admin.initialize_app(cred)
                    logger.info("🔐 Using service account from Secret Manager")
                else:
                    service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                    if service_account_path and os.path.exists(service_account_path):
                        cred = credentials.Certificate(service_account_path)
                        firebase_admin.initialize_app(cred)
                        logger.info("🔐 Using local service account file")
                    else:
                        firebase_admin.initialize_app()
                        logger.info("🔐 Using Application Default Credentials")
            
            self.db = firestore.Client(database=FIRESTORE_DATABASE)
            self.use_firestore = True
            logger.info(f"✅ Connected to Firestore database: {FIRESTORE_DATABASE}")
            
            try:
                collection_ref = self.db.collection(FIRESTORE_COLLECTION)
                logger.info(f"✅ Firestore collection '{FIRESTORE_COLLECTION}' is accessible")
            except Exception as test_e:
                logger.warning(f"⚠️ Firestore connection test failed: {test_e}")
                self.use_firestore = False
            
        except Exception as e:
            logger.warning(f"Failed to initialize Firestore: {e}")
            logger.info("Falling back to in-memory storage")
            self.use_firestore = False
    
    def save_insights(self, insights: GeneratedInsights) -> bool:
        """Save insights to Firestore or in-memory storage"""
        logger.info(f"🔄 Attempting to save insights: {insights.id}")
        logger.info(f"🔄 Firestore enabled: {self.use_firestore}, DB object: {self.db is not None}")
        
        try:
            if self.use_firestore and self.db:
                insights_dict = insights.model_dump()
                insights_dict['created_at'] = firestore.SERVER_TIMESTAMP
                insights_dict['updated_at'] = firestore.SERVER_TIMESTAMP
                
                doc_ref = self.db.collection(FIRESTORE_COLLECTION).document(insights.id)
                doc_ref.set(insights_dict)
                
                logger.info(f"✅ Successfully saved insights to Firestore: {insights.id}")
                insights_storage[insights.id] = insights
                return True
            else:
                logger.info(f"🔄 Firestore not available, using in-memory storage for: {insights.id}")
                insights_storage[insights.id] = insights
                logger.info(f"💾 Saved insights to memory: {insights.id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error saving insights to Firestore: {e}")
            insights_storage[insights.id] = insights
            logger.info(f"💾 Fallback: Saved insights to memory: {insights.id}")
            return False
    
    def get_insights(self, insight_id: str) -> Optional[GeneratedInsights]:
        """Get insights by ID from Firestore or in-memory storage"""
        try:
            if insight_id in insights_storage:
                return insights_storage[insight_id]
            
            if self.use_firestore and self.db:
                doc_ref = self.db.collection(FIRESTORE_COLLECTION).document(insight_id)
                doc = doc_ref.get()
                
                if doc.exists:
                    data = doc.to_dict()
                    data.pop('created_at', None)
                    data.pop('updated_at', None)
                    
                    insights = GeneratedInsights(**data)
                    insights_storage[insight_id] = insights
                    return insights
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving insights: {e}")
            return insights_storage.get(insight_id)
    
    def get_all_insights(self) -> List[GeneratedInsights]:
        """Get all insights from Firestore and in-memory storage"""
        all_insights = []
        
        try:
            if self.use_firestore and self.db:
                docs = self.db.collection(FIRESTORE_COLLECTION).order_by('created_at', direction=firestore.Query.DESCENDING).stream()
                
                for doc in docs:
                    try:
                        data = doc.to_dict()
                        data.pop('created_at', None)
                        data.pop('updated_at', None)
                        
                        insights = GeneratedInsights(**data)
                        all_insights.append(insights)
                        insights_storage[insights.id] = insights
                        
                    except Exception as e:
                        logger.warning(f"Error parsing Firestore document {doc.id}: {e}")
                        continue
            
            for insight_id, insights in insights_storage.items():
                if not any(i.id == insight_id for i in all_insights):
                    all_insights.append(insights)
            
            all_insights.sort(key=lambda x: x.timestamp, reverse=True)
            
            return all_insights
            
        except Exception as e:
            logger.error(f"Error retrieving all insights: {e}")
            return list(insights_storage.values())
    
    def delete_insights(self, insight_id: str) -> bool:
        """Delete insights from Firestore and in-memory storage"""
        try:
            deleted = False
            
            if self.use_firestore and self.db:
                doc_ref = self.db.collection(FIRESTORE_COLLECTION).document(insight_id)
                doc_ref.delete()
                deleted = True
                logger.info(f"🗑️ Deleted insights from Firestore: {insight_id}")
            
            if insight_id in insights_storage:
                del insights_storage[insight_id]
                deleted = True
                logger.info(f"🗑️ Deleted insights from memory: {insight_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting insights: {e}")
            if insight_id in insights_storage:
                del insights_storage[insight_id]
                return True
            return False

    def get_user_insights(self, user_id: str) -> List[GeneratedInsights]:
        """Get all insights for a specific user"""
        user_insights = []
        
        try:
            if self.use_firestore and self.db:
                docs = self.db.collection(FIRESTORE_COLLECTION)\
                    .where('author_id', '==', user_id)\
                    .order_by('created_at', direction=firestore.Query.DESCENDING)\
                    .stream()
                
                for doc in docs:
                    try:
                        data = doc.to_dict()
                        data.pop('created_at', None)
                        data.pop('updated_at', None)
                        
                        insights = GeneratedInsights(**data)
                        user_insights.append(insights)
                        insights_storage[insights.id] = insights
                        
                    except Exception as e:
                        logger.warning(f"Error parsing user insight document {doc.id}: {e}")
                        continue
            
            # Also check in-memory storage for user insights
            for insight_id, insights in insights_storage.items():
                if (insights.author_id == user_id and 
                    not any(i.id == insight_id for i in user_insights)):
                    user_insights.append(insights)
            
            # Sort by timestamp (most recent first)
            user_insights.sort(key=lambda x: x.timestamp, reverse=True)
            
            return user_insights
            
        except Exception as e:
            logger.error(f"Error retrieving user insights: {e}")
            # Fallback to in-memory storage
            user_insights = [insights for insights in insights_storage.values() 
                           if insights.author_id == user_id]
            user_insights.sort(key=lambda x: x.timestamp, reverse=True)
            return user_insights

    def get_shared_insights(self) -> List[GeneratedInsights]:
        """Get all publicly shared insights"""
        all_insights = []
        
        try:
            if self.use_firestore and self.db:
                docs = self.db.collection(FIRESTORE_COLLECTION)\
                    .where('is_shared', '==', True)\
                    .order_by('created_at', direction=firestore.Query.DESCENDING)\
                    .stream()
                
                for doc in docs:
                    try:
                        data = doc.to_dict()
                        data.pop('created_at', None)
                        data.pop('updated_at', None)
                        
                        insights = GeneratedInsights(**data)
                        all_insights.append(insights)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing shared insight document {doc.id}: {e}")
                        continue
            
            for insight_id, insights in insights_storage.items():
                if insights.is_shared and not any(i.id == insight_id for i in all_insights):
                    all_insights.append(insights)
            
            all_insights.sort(key=lambda x: x.timestamp, reverse=True)
            
            return all_insights
            
        except Exception as e:
            logger.error(f"Error retrieving shared insights: {e}")
            return [insights for insights in insights_storage.values() if insights.is_shared]
    
    def get_featured_insights(self, limit: int = 5) -> List[GeneratedInsights]:
        """Get featured insights (top liked insights from the past week)"""
        from datetime import datetime, timedelta
        
        featured_insights = []
        
        try:
            # Calculate date one week ago
            one_week_ago = datetime.now() - timedelta(days=7)
            
            if self.use_firestore and self.db:
                # Query Firestore for shared insights from the past week, ordered by likes
                docs = self.db.collection(FIRESTORE_COLLECTION)\
                    .where('is_shared', '==', True)\
                    .where('created_at', '>=', one_week_ago)\
                    .order_by('created_at')\
                    .order_by('likes', direction=firestore.Query.DESCENDING)\
                    .limit(limit)\
                    .stream()
                
                for doc in docs:
                    try:
                        data = doc.to_dict()
                        data.pop('created_at', None)
                        data.pop('updated_at', None)
                        
                        insights = GeneratedInsights(**data)
                        featured_insights.append(insights)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing featured insight document {doc.id}: {e}")
                        continue
            
            # If Firestore query didn't return enough results, supplement with in-memory storage
            if len(featured_insights) < limit:
                memory_insights = []
                for insight_id, insights in insights_storage.items():
                    if (insights.is_shared and 
                        not any(i.id == insight_id for i in featured_insights)):
                        # Parse timestamp for comparison
                        try:
                            if isinstance(insights.timestamp, str):
                                insight_date = datetime.fromisoformat(insights.timestamp.replace('Z', '+00:00'))
                            else:
                                insight_date = insights.timestamp
                            
                            if insight_date >= one_week_ago:
                                memory_insights.append(insights)
                        except Exception as e:
                            logger.warning(f"Error parsing timestamp for insight {insight_id}: {e}")
                            # Include it anyway if we can't parse the date
                            memory_insights.append(insights)
                
                # Sort by likes (descending) and take remaining needed
                memory_insights.sort(key=lambda x: getattr(x, 'likes', 0), reverse=True)
                remaining_needed = limit - len(featured_insights)
                featured_insights.extend(memory_insights[:remaining_needed])
            
            # Final sort by likes to ensure proper ordering
            featured_insights.sort(key=lambda x: getattr(x, 'likes', 0), reverse=True)
            
            # If still not enough, get the most liked shared insights regardless of date
            if len(featured_insights) < limit:
                all_shared = self.get_shared_insights()
                for insight in all_shared:
                    if (len(featured_insights) >= limit or 
                        any(i.id == insight.id for i in featured_insights)):
                        break
                    featured_insights.append(insight)
            
            return featured_insights[:limit]
            
        except Exception as e:
            logger.error(f"Error retrieving featured insights: {e}")
            # Fallback: return most liked shared insights from memory
            shared_insights = [insights for insights in insights_storage.values() if insights.is_shared]
            shared_insights.sort(key=lambda x: getattr(x, 'likes', 0), reverse=True)
            return shared_insights[:limit]

    def add_like(self, insight_id, user_id):
        """Add a like to an insight (one-time only)"""
        try:
            insight_ref = self.db.collection('insights').document(insight_id)
            
            # Use transaction to ensure atomicity
            @firestore.transactional
            def add_like_transaction(transaction):
                # Get current insight data
                insight_doc = insight_ref.get(transaction=transaction)
                if not insight_doc.exists:
                    return None
                
                insight_data = insight_doc.to_dict()
                
                # Check if user already liked
                liked_by = insight_data.get('liked_by', [])
                if user_id in liked_by:
                    return None  # User already liked this insight
                
                # Add user to liked_by list and increment likes count
                liked_by.append(user_id)
                likes_count = insight_data.get('likes', 0) + 1
                
                # Update the document
                transaction.update(insight_ref, {
                    'liked_by': liked_by,
                    'likes': likes_count
                })
                
                # Return updated data
                insight_data['liked_by'] = liked_by
                insight_data['likes'] = likes_count
                return insight_data
            
            # Execute transaction
            transaction = self.db.transaction()
            result = add_like_transaction(transaction)
            
            if result:
                print(f"Successfully added like to insight {insight_id} by user {user_id}")
                return result
            else:
                print(f"Failed to add like - user {user_id} already liked insight {insight_id}")
                return None
                
        except Exception as e:
            print(f"Error adding like to insight {insight_id}: {str(e)}")
            return None

    def toggle_like(self, insight_id, user_id):
        """Toggle like for an insight (deprecated - use add_like for one-time likes)"""
        try:
            insight_ref = self.db.collection('insights').document(insight_id)
            
            # Use transaction to ensure atomicity
            @firestore.transactional
            def toggle_like_transaction(transaction):
                # Get current insight data
                insight_doc = insight_ref.get(transaction=transaction)
                if not insight_doc.exists:
                    return False
                
                insight_data = insight_doc.to_dict()
                
                # Get current liked_by list
                liked_by = insight_data.get('liked_by', [])
                likes_count = insight_data.get('likes', 0)
                
                if user_id in liked_by:
                    # Remove like
                    liked_by.remove(user_id)
                    likes_count = max(0, likes_count - 1)
                else:
                    # Add like
                    liked_by.append(user_id)
                    likes_count += 1
                
                # Update the document
                transaction.update(insight_ref, {
                    'liked_by': liked_by,
                    'likes': likes_count
                })
                
                return True
            
            # Execute transaction
            transaction = self.db.transaction()
            return toggle_like_transaction(transaction)
            
        except Exception as e:
            print(f"Error toggling like for insight {insight_id}: {str(e)}")
            return False

    def toggle_dislike(self, insight_id, user_id):
        """Toggle dislike for an insight (deprecated - dislike functionality removed)"""
        print(f"Dislike functionality has been removed")
        return False

    def get_trending_insights(self, limit: int = 10) -> List[GeneratedInsights]:
        """Get trending insights based on recent activity (likes/dislikes in past 24-48 hours)"""
        from datetime import datetime, timedelta
        
        trending_insights = []
        
        try:
            # Calculate trending score based on recent activity
            now = datetime.now()
            two_days_ago = now - timedelta(days=2)
            
            if self.use_firestore and self.db:
                # Get recent shared insights
                docs = self.db.collection(FIRESTORE_COLLECTION)\
                    .where('is_shared', '==', True)\
                    .where('created_at', '>=', two_days_ago)\
                    .stream()
                
                for doc in docs:
                    try:
                        data = doc.to_dict()
                        data.pop('created_at', None)
                        data.pop('updated_at', None)
                        
                        insights = GeneratedInsights(**data)
                        trending_insights.append(insights)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing trending insight document {doc.id}: {e}")
                        continue
            
            # Add insights from memory
            for insight_id, insights in insights_storage.items():
                if (insights.is_shared and 
                    not any(i.id == insight_id for i in trending_insights)):
                    try:
                        if isinstance(insights.timestamp, str):
                            insight_date = datetime.fromisoformat(insights.timestamp.replace('Z', '+00:00'))
                        else:
                            insight_date = insights.timestamp
                        
                        if insight_date >= two_days_ago:
                            trending_insights.append(insights)
                    except Exception as e:
                        logger.warning(f"Error parsing timestamp for trending insight {insight_id}: {e}")
                        # Include recent ones anyway
                        trending_insights.append(insights)
            
            # Calculate trending score: (likes - dislikes) / hours_since_creation
            def calculate_trending_score(insight):
                try:
                    likes = getattr(insight, 'likes', 0) or 0
                    dislikes = getattr(insight, 'dislikes', 0) or 0
                    
                    if isinstance(insight.timestamp, str):
                        created_date = datetime.fromisoformat(insight.timestamp.replace('Z', '+00:00'))
                    else:
                        created_date = insight.timestamp
                    
                    hours_since = max(1, (now - created_date).total_seconds() / 3600)  # Minimum 1 hour
                    
                    # Trending score: engagement rate adjusted by time decay
                    engagement = likes - (dislikes * 0.5)  # Dislikes have less negative impact
                    score = max(0, engagement) / (hours_since ** 0.5)  # Square root decay
                    
                    return score
                except Exception as e:
                    logger.warning(f"Error calculating trending score for insight {insight.id}: {e}")
                    return 0
            
            # Sort by trending score
            trending_insights.sort(key=calculate_trending_score, reverse=True)
            
            return trending_insights[:limit]
            
        except Exception as e:
            logger.error(f"Error retrieving trending insights: {e}")
            # Fallback: return most recent shared insights
            shared_insights = self.get_shared_insights()
            return shared_insights[:limit]

    def get_most_liked_insights(self, limit: int = 10) -> List[GeneratedInsights]:
        """Get most liked insights"""
        try:
            most_liked = []
            
            if self.use_firestore and self.db:
                # Get all shared insights first (simpler query without composite index)
                docs = self.db.collection(FIRESTORE_COLLECTION)\
                    .where('is_shared', '==', True)\
                    .stream()
                
                # Filter and sort in Python to avoid needing composite index
                firestore_insights = []
                for doc in docs:
                    try:
                        data = doc.to_dict()
                        likes = data.get('likes', 0) or 0
                        
                        # Only include insights with likes > 0
                        if likes > 0:
                            data.pop('created_at', None)
                            data.pop('updated_at', None)
                            
                            insights = GeneratedInsights(**data)
                            firestore_insights.append(insights)
                            
                    except Exception as e:
                        logger.warning(f"Error parsing most liked insight document {doc.id}: {e}")
                        continue
                
                # Sort by likes in Python
                firestore_insights.sort(key=lambda x: getattr(x, 'likes', 0), reverse=True)
                most_liked.extend(firestore_insights[:limit])
            
            # Supplement with memory storage if needed
            if len(most_liked) < limit:
                memory_insights = []
                for insight_id, insights in insights_storage.items():
                    if (insights.is_shared and 
                        getattr(insights, 'likes', 0) > 0 and
                        not any(i.id == insight_id for i in most_liked)):
                        memory_insights.append(insights)
                
                # Sort by likes
                memory_insights.sort(key=lambda x: getattr(x, 'likes', 0), reverse=True)
                remaining_needed = limit - len(most_liked)
                most_liked.extend(memory_insights[:remaining_needed])
            
            # Final sort to ensure proper ordering
            most_liked.sort(key=lambda x: getattr(x, 'likes', 0), reverse=True)
            
            return most_liked[:limit]
            
        except Exception as e:
            logger.error(f"Error retrieving most liked insights: {e}")
            # Fallback: return shared insights sorted by likes from memory
            shared_insights = [insights for insights in insights_storage.values() 
                             if insights.is_shared and getattr(insights, 'likes', 0) > 0]
            shared_insights.sort(key=lambda x: getattr(x, 'likes', 0), reverse=True)
            return shared_insights[:limit]

    def update_sharing_status(self, insight_id: str, is_shared: bool, user_id: str) -> bool:
        """Update the sharing status of an insight"""
        try:
            if self.use_firestore and self.db:
                doc_ref = self.db.collection(FIRESTORE_COLLECTION).document(insight_id)
                
                doc = doc_ref.get()
                if doc.exists:
                    data = doc.to_dict()
                    if data.get('author_id') != user_id:
                        logger.warning(f"User {user_id} attempted to modify insight {insight_id} they don't own")
                        return False
                    
                    doc_ref.update({
                        'is_shared': is_shared,
                        'updated_at': firestore.SERVER_TIMESTAMP
                    })
                    
                    if insight_id in insights_storage:
                        insights_storage[insight_id].is_shared = is_shared
                    
                    return True
            
            else:
                if insight_id in insights_storage:
                    insight = insights_storage[insight_id]
                    if insight.author_id == user_id:
                        insight.is_shared = is_shared
                        return True
                return False
                
        except Exception as e:
            logger.error(f"Error updating sharing status for insight {insight_id}: {e}")
            return False
