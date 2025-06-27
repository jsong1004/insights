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

    def toggle_like(self, insight_id: str, user_id: str) -> bool:
        """Toggle like for an insight by a user"""
        try:
            if self.use_firestore and self.db:
                doc_ref = self.db.collection(FIRESTORE_COLLECTION).document(insight_id)
                
                @firestore.transactional
                def update_likes(transaction):
                    doc = doc_ref.get(transaction=transaction)
                    if doc.exists:
                        data = doc.to_dict()
                        liked_by = data.get('liked_by', [])
                        likes = data.get('likes', 0)
                        
                        if user_id in liked_by:
                            liked_by.remove(user_id)
                            likes = max(0, likes - 1)
                        else:
                            liked_by.append(user_id)
                            likes += 1
                        
                        transaction.update(doc_ref, {
                            'liked_by': liked_by,
                            'likes': likes,
                            'updated_at': firestore.SERVER_TIMESTAMP
                        })
                        
                        if insight_id in insights_storage:
                            insights_storage[insight_id].liked_by = liked_by
                            insights_storage[insight_id].likes = likes
                        
                        return True
                    return False
                
                transaction = self.db.transaction()
                return update_likes(transaction)
            
            else:
                if insight_id in insights_storage:
                    insight = insights_storage[insight_id]
                    if user_id in insight.liked_by:
                        insight.liked_by.remove(user_id)
                        insight.likes = max(0, insight.likes - 1)
                    else:
                        insight.liked_by.append(user_id)
                        insight.likes += 1
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error toggling like for insight {insight_id}: {e}")
            return False

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
