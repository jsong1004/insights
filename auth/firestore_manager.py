import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
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

    def get_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive usage statistics for a user"""
        try:
            user_data = self.get_user_data(user_id)
            if not user_data:
                return self._get_default_usage_stats()
            
            # Current month
            current_month = datetime.now().strftime('%Y-%m')
            current_day = datetime.now().strftime('%Y-%m-%d')
            
            # Get or initialize usage data
            usage = user_data.get('usage', {})
            limits = user_data.get('limits', self._get_default_limits(user_data.get('subscription', {}).get('plan', 'free')))
            
            # Calculate remaining allowances
            monthly_insights_used = usage.get('monthly_breakdown', {}).get(current_month, {}).get('insights', 0)
            monthly_tokens_used = usage.get('monthly_breakdown', {}).get(current_month, {}).get('tokens', 0)
            daily_insights_used = usage.get('daily_usage', {}).get(current_day, {}).get('insights', 0)
            
            stats = {
                'current_usage': {
                    'insights_generated': usage.get('insights_generated', 0),
                    'total_tokens_used': usage.get('total_tokens_used', 0),
                    'monthly_insights': monthly_insights_used,
                    'monthly_tokens': monthly_tokens_used,
                    'daily_insights': daily_insights_used
                },
                'limits': limits,
                'remaining': {
                    'monthly_insights': max(0, limits['monthly_insights'] - monthly_insights_used),
                    'monthly_tokens': max(0, limits['monthly_tokens'] - monthly_tokens_used),
                    'daily_insights': max(0, limits['daily_insights'] - daily_insights_used),
                    'insights_remaining': usage.get('insights_remaining', limits['monthly_insights'])
                },
                'usage_percentage': {
                    'insights': (monthly_insights_used / limits['monthly_insights'] * 100) if limits['monthly_insights'] > 0 else 0,
                    'tokens': (monthly_tokens_used / limits['monthly_tokens'] * 100) if limits['monthly_tokens'] > 0 else 0
                },
                'daily_breakdown': self._get_last_7_days_usage(usage.get('daily_usage', {})),
                'subscription': user_data.get('subscription', {'plan': 'free', 'status': 'active'})
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting usage stats for user {user_id}: {e}")
            return self._get_default_usage_stats()

    def track_insight_generation(self, user_id: str, tokens_used: int, search_requests: int = 1) -> bool:
        """Track when an insight is generated with detailed metrics"""
        try:
            if not self.use_firestore or not self.db:
                logger.warning("Firestore not available - cannot track insight generation")
                return False
                
            current_month = datetime.now().strftime('%Y-%m')
            current_day = datetime.now().strftime('%Y-%m-%d')
            
            doc_ref = self.db.collection(self.users_collection).document(user_id)
            
            @firestore.transactional
            def update_usage(transaction):
                doc = doc_ref.get(transaction=transaction)
                
                if doc.exists:
                    data = doc.to_dict()
                    usage = data.get('usage', {})
                    
                    # Update totals
                    usage['insights_generated'] = usage.get('insights_generated', 0) + 1
                    usage['total_tokens_used'] = usage.get('total_tokens_used', 0) + tokens_used
                    usage['current_month'] = current_month
                    
                    # Update monthly breakdown
                    monthly = usage.get('monthly_breakdown', {})
                    if current_month not in monthly:
                        monthly[current_month] = {'insights': 0, 'tokens': 0, 'search_requests': 0, 'days_active': 0}
                    
                    monthly[current_month]['insights'] += 1
                    monthly[current_month]['tokens'] += tokens_used
                    monthly[current_month]['search_requests'] += search_requests
                    
                    # Update daily usage
                    daily = usage.get('daily_usage', {})
                    if current_day not in daily:
                        daily[current_day] = {'insights': 0, 'tokens': 0, 'search_requests': 0}
                        # Increment days active for the month
                        monthly[current_month]['days_active'] = monthly[current_month].get('days_active', 0) + 1
                    
                    daily[current_day]['insights'] += 1
                    daily[current_day]['tokens'] += tokens_used
                    daily[current_day]['search_requests'] += search_requests
                    
                    # Keep only last 30 days of daily data
                    daily = self._cleanup_old_daily_data(daily)
                    
                    # Update insights remaining
                    limits = data.get('limits', self._get_default_limits(data.get('subscription', {}).get('plan', 'free')))
                    monthly_insights = monthly[current_month]['insights']
                    usage['insights_remaining'] = max(0, limits['monthly_insights'] - monthly_insights)
                    
                    # Update the document
                    transaction.update(doc_ref, {
                        'usage': usage,
                        'updated_at': firestore.SERVER_TIMESTAMP
                    })
                else:
                    # Create new user with usage data
                    self._create_user_with_usage(transaction, doc_ref, user_id, tokens_used)
            
            # Execute transaction
            transaction = self.db.transaction()
            update_usage(transaction)
            
            logger.info(f"✅ Tracked insight generation for user {user_id}: {tokens_used} tokens")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking insight generation for user {user_id}: {e}")
            return False

    def check_usage_limits(self, user_id: str) -> Dict[str, bool]:
        """Check if user has exceeded any usage limits"""
        try:
            stats = self.get_usage_stats(user_id)
            
            return {
                'can_generate': stats['remaining']['monthly_insights'] > 0 and stats['remaining']['daily_insights'] > 0,
                'has_monthly_insights': stats['remaining']['monthly_insights'] > 0,
                'has_daily_insights': stats['remaining']['daily_insights'] > 0,
                'has_tokens': stats['remaining']['monthly_tokens'] > 0,
                'monthly_insights_exceeded': stats['remaining']['monthly_insights'] <= 0,
                'daily_insights_exceeded': stats['remaining']['daily_insights'] <= 0,
                'tokens_exceeded': stats['remaining']['monthly_tokens'] <= 0
            }
            
        except Exception as e:
            logger.error(f"Error checking usage limits for user {user_id}: {e}")
            return {'can_generate': True}  # Allow generation on error

    def _get_default_limits(self, plan: str) -> Dict[str, int]:
        """Get default limits based on subscription plan"""
        limits = {
            'free': {
                'monthly_insights': 20,
                'monthly_tokens': 100000,
                'daily_insights': 5,
                'rate_limit_per_hour': 10
            },
            'basic': {
                'monthly_insights': 100,
                'monthly_tokens': 500000,
                'daily_insights': 20,
                'rate_limit_per_hour': 30
            },
            'pro': {
                'monthly_insights': 500,
                'monthly_tokens': 2000000,
                'daily_insights': 50,
                'rate_limit_per_hour': 60
            },
            'enterprise': {
                'monthly_insights': -1,  # Unlimited
                'monthly_tokens': -1,
                'daily_insights': -1,
                'rate_limit_per_hour': -1
            }
        }
        
        return limits.get(plan, limits['free'])

    def _get_last_7_days_usage(self, daily_usage: Dict) -> List[Dict]:
        """Get usage data for the last 7 days"""
        from datetime import datetime, timedelta
        
        days = []
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i))
            date_str = date.strftime('%Y-%m-%d')
            day_data = daily_usage.get(date_str, {'insights': 0, 'tokens': 0, 'search_requests': 0})
            
            days.append({
                'date': date_str,
                'day': date.day,
                'day_name': date.strftime('%a'),
                'insights': day_data.get('insights', 0),
                'tokens': day_data.get('tokens', 0),
                'search_requests': day_data.get('search_requests', 0)
            })
        
        return days

    def _cleanup_old_daily_data(self, daily_usage: Dict) -> Dict:
        """Keep only the last 30 days of daily usage data"""
        from datetime import datetime, timedelta
        
        cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        return {
            date: data 
            for date, data in daily_usage.items() 
            if date >= cutoff_date
        }

    def _create_user_with_usage(self, transaction, doc_ref, user_id: str, tokens_used: int):
        """Create a new user document with initial usage data"""
        current_month = datetime.now().strftime('%Y-%m')
        current_day = datetime.now().strftime('%Y-%m-%d')
        
        limits = self._get_default_limits('free')
        
        new_user_data = {
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP,
            'usage': {
                'insights_generated': 1,
                'total_tokens_used': tokens_used,
                'current_month': current_month,
                'insights_remaining': max(0, limits['monthly_insights'] - 1),
                'monthly_breakdown': {
                    current_month: {
                        'insights': 1,
                        'tokens': tokens_used,
                        'search_requests': 1,
                        'days_active': 1
                    }
                },
                'daily_usage': {
                    current_day: {
                        'insights': 1,
                        'tokens': tokens_used,
                        'search_requests': 1
                    }
                }
            },
            'limits': limits,
            'subscription': {
                'plan': 'free',
                'status': 'active'
            }
        }
        
        transaction.set(doc_ref, new_user_data)
        logger.info(f"✅ Created new user with usage tracking: {user_id}")

    def _get_default_usage_stats(self) -> Dict[str, Any]:
        """Return default usage stats for new or unfound users"""
        limits = self._get_default_limits('free')
        return {
            'current_usage': {
                'insights_generated': 0,
                'total_tokens_used': 0,
                'monthly_insights': 0,
                'monthly_tokens': 0,
                'daily_insights': 0
            },
            'limits': limits,
            'remaining': {
                'monthly_insights': limits['monthly_insights'],
                'monthly_tokens': limits['monthly_tokens'],
                'daily_insights': limits['daily_insights'],
                'insights_remaining': limits['monthly_insights']
            },
            'usage_percentage': {
                'insights': 0,
                'tokens': 0
            },
            'daily_breakdown': self._get_last_7_days_usage({}),
            'subscription': {'plan': 'free', 'status': 'active'}
        } 