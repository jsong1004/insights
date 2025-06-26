import os
import logging
from datetime import datetime
from typing import Dict, Optional, Any
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials

logger = logging.getLogger(__name__)

class UserFirestoreManager:
    """Manages Firestore operations for user authentication data"""
    
    def __init__(self, database="ai-biz"):
        self.db = None
        self.database = database
        self.users_collection = "users"
        self.use_firestore = False
        
        try:
            # Use existing Firebase Admin app if available
            if firebase_admin._apps:
                self.db = firestore.Client(database=self.database)
                self.use_firestore = True
                logger.info(f"✅ User Firestore Manager connected to database: {self.database}")
            else:
                logger.warning("Firebase Admin not initialized - user data will not persist")
        except Exception as e:
            logger.error(f"Failed to initialize User Firestore Manager: {e}")
    
    def create_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Create a new user record"""
        try:
            if not self.use_firestore or not self.db:
                logger.warning("Firestore not available - cannot create user")
                return False
            
            # Add metadata
            user_data.update({
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            # Create user document
            doc_ref = self.db.collection(self.users_collection).document(user_id)
            doc_ref.set(user_data)
            
            logger.info(f"✅ Created user record: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {e}")
            return False
    
    def get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data by ID"""
        try:
            if not self.use_firestore or not self.db:
                return None
            
            doc_ref = self.db.collection(self.users_collection).document(user_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                logger.info(f"User not found: {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user data {user_id}: {e}")
            return None
    
    def update_user_data(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            if not self.use_firestore or not self.db:
                logger.warning("Firestore not available - cannot update user")
                return False
            
            # Create a copy of update_data with timestamp (don't modify original)
            firestore_data = update_data.copy()
            firestore_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref = self.db.collection(self.users_collection).document(user_id)
            doc_ref.update(firestore_data)
            
            logger.info(f"✅ Updated user data: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False
    
    def update_user_login(self, user_id: str, login_data: Dict[str, Any] = None) -> bool:
        """Update user last login time and optional login data"""
        try:
            if not self.use_firestore or not self.db:
                return False
            
            update_data = {
                'last_login': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            # Add any additional login data
            if login_data:
                update_data.update(login_data)
            
            doc_ref = self.db.collection(self.users_collection).document(user_id)
            doc_ref.update(update_data)
            
            logger.info(f"✅ Updated login for user: {user_id}")
            return True
            
        except Exception as e:
            # Try to create user if they don't exist
            try:
                user_data = {
                    'last_login': firestore.SERVER_TIMESTAMP,
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'usage': {
                        'insights_generated': 0,
                        'insights_remaining': 5
                    }
                }
                
                if login_data:
                    user_data.update(login_data)
                
                return self.create_user(user_id, user_data)
                
            except Exception as create_error:
                logger.error(f"Error updating/creating user login {user_id}: {create_error}")
                return False
    
    def increment_usage(self, user_id: str, metric: str, amount: int = 1) -> bool:
        """Increment a usage metric for a user"""
        try:
            if not self.use_firestore or not self.db:
                return False
            
            doc_ref = self.db.collection(self.users_collection).document(user_id)
            
            # Use Firestore transaction to safely increment
            @firestore.transactional
            def update_in_transaction(transaction):
                doc = doc_ref.get(transaction=transaction)
                
                if doc.exists:
                    current_data = doc.to_dict()
                    usage = current_data.get('usage', {})
                    
                    # Increment the specified metric
                    current_value = usage.get(metric, 0)
                    usage[metric] = current_value + amount
                    
                    # If incrementing insights_generated, decrement insights_remaining
                    if metric == 'insights_generated':
                        current_remaining = usage.get('insights_remaining', 0)
                        if current_remaining > 0:
                            usage['insights_remaining'] = max(0, current_remaining - amount)
                    
                    # Update the document
                    transaction.update(doc_ref, {
                        'usage': usage,
                        'updated_at': firestore.SERVER_TIMESTAMP
                    })
                else:
                    # Create new user with initial usage
                    new_usage = {metric: amount}
                    if metric == 'insights_generated':
                        new_usage['insights_remaining'] = max(0, 5 - amount)  # Start with 5 free
                    
                    transaction.set(doc_ref, {
                        'usage': new_usage,
                        'created_at': firestore.SERVER_TIMESTAMP,
                        'updated_at': firestore.SERVER_TIMESTAMP
                    })
            
            # Execute the transaction
            transaction = self.db.transaction()
            update_in_transaction(transaction)
            
            logger.info(f"✅ Incremented {metric} by {amount} for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing usage {metric} for user {user_id}: {e}")
            return False
    
    def update_user_subscription(self, user_id: str, subscription_data: Dict[str, Any]) -> bool:
        """Update user subscription information"""
        try:
            if not self.use_firestore or not self.db:
                return False
            
            update_data = {
                'subscription': subscription_data,
                'subscription_updated_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            doc_ref = self.db.collection(self.users_collection).document(user_id)
            doc_ref.update(update_data)
            
            logger.info(f"✅ Updated subscription for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating subscription for user {user_id}: {e}")
            return False 