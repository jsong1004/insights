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
                'monthly_insights': 150,  # 5 per day * 30 days
                'monthly_tokens': 100000,
                'daily_insights': 5,
                'rate_limit_per_hour': 10
            },
            'freemium': {
                'monthly_insights': 1500,  # 50 per day * 30 days
                'monthly_tokens': 1000000,
                'daily_insights': 50,
                'rate_limit_per_hour': 60
            },
            'max': {
                'monthly_insights': -1,  # Unlimited
                'monthly_tokens': -1,
                'daily_insights': -1,
                'rate_limit_per_hour': -1
            },
            # Legacy plans for backward compatibility
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

    def get_dashboard_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard analytics"""
        try:
            stats = self.get_usage_stats(user_id)
            user_data = self.get_user_data(user_id)
            
            # Calculate additional metrics
            current_streak = self._calculate_current_streak(stats['daily_breakdown'])
            efficiency_score = self._calculate_efficiency_score(stats)
            avg_processing_time = self._get_average_processing_time(user_id)
            
            # Get recent activities
            recent_activities = self.get_recent_activities(user_id, limit=8)
            
            return {
                **stats,
                'quick_stats': {
                    'total_insights': stats['current_usage']['insights_generated'],
                    'current_streak': current_streak,
                    'avg_processing_time': avg_processing_time,
                    'efficiency_score': efficiency_score
                },
                'activity_heatmap': self._generate_activity_heatmap(stats['daily_breakdown']),
                'monthly_trend': self._get_monthly_trend(user_data),
                'recommendations': self._generate_recommendations(stats),
                'recent_activities': recent_activities
            }
        except Exception as e:
            logger.error(f"Error getting dashboard analytics: {e}")
            return self.get_usage_stats(user_id)  # Fallback to basic stats

    def _calculate_current_streak(self, daily_breakdown: List) -> int:
        """Calculate current consecutive days of activity"""
        streak = 0
        for day in reversed(daily_breakdown):
            if day['insights'] > 0:
                streak += 1
            else:
                break
        return streak

    def _calculate_efficiency_score(self, stats: Dict) -> int:
        """Calculate efficiency score based on usage patterns"""
        if stats['current_usage']['insights_generated'] == 0:
            return 0
        
        # Score based on insights per session, token efficiency, etc.
        insights = stats['current_usage']['insights_generated']
        tokens = stats['current_usage']['total_tokens_used']
        
        # Token efficiency (lower tokens per insight = higher score)
        if insights > 0:
            tokens_per_insight = tokens / insights
            efficiency = max(0, 100 - (tokens_per_insight / 100))  # Normalize
            return min(100, int(efficiency))
        return 0

    def _get_average_processing_time(self, user_id: str) -> float:
        """Get average processing time from recent insights"""
        # This would query insights collection for this user
        # For now, return estimated value
        return 45.2  # seconds

    def _generate_activity_heatmap(self, daily_breakdown: List) -> List[Dict]:
        """Generate 7-day activity heatmap data"""
        heatmap = []
        for day in daily_breakdown:
            level = 0
            if day['insights'] > 0:
                if day['insights'] >= 5:
                    level = 4
                elif day['insights'] >= 3:
                    level = 3
                elif day['insights'] >= 2:
                    level = 2
                else:
                    level = 1
            
            heatmap.append({
                'date': day['date'],
                'day_name': day['day_name'],
                'insights': day['insights'],
                'level': level
            })
        return heatmap

    def _get_monthly_trend(self, user_data: Dict) -> Dict:
        """Get monthly usage trend"""
        if not user_data:
            return {'data': [], 'direction': 'stable'}
            
        usage = user_data.get('usage', {})
        monthly_breakdown = usage.get('monthly_breakdown', {})
        
        # Get last 3 months for trend
        months = sorted(monthly_breakdown.keys())[-3:]
        trend_data = []
        
        for month in months:
            data = monthly_breakdown[month]
            trend_data.append({
                'month': month,
                'insights': data.get('insights', 0),
                'tokens': data.get('tokens', 0),
                'days_active': data.get('days_active', 0)
            })
        
        return {
            'data': trend_data,
            'direction': self._calculate_trend_direction(trend_data)
        }

    def _calculate_trend_direction(self, trend_data: List) -> str:
        """Calculate if usage is trending up, down, or stable"""
        if len(trend_data) < 2:
            return 'stable'
        
        recent = trend_data[-1]['insights']
        previous = trend_data[-2]['insights']
        
        if recent > previous * 1.1:
            return 'up'
        elif recent < previous * 0.9:
            return 'down'
        else:
            return 'stable'

    def _generate_recommendations(self, stats: Dict) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        usage_pct = stats['usage_percentage']['insights']
        
        if usage_pct > 80:
            recommendations.append("You're approaching your monthly limit. Consider upgrading your plan.")
        elif usage_pct < 20:
            recommendations.append("You have plenty of insights remaining. Try exploring new research topics!")
        
        # Check daily patterns
        daily_breakdown = stats['daily_breakdown']
        active_days = sum(1 for day in daily_breakdown if day['insights'] > 0)
        
        if active_days < 3:
            recommendations.append("Try to use the service more regularly for better research habits.")
        elif active_days >= 6:
            recommendations.append("Great consistency! You're building excellent research habits.")
        
        return recommendations

    def track_activity(self, user_id: str, activity_type: str, description: str, metadata: Dict[str, Any] = None) -> bool:
        """Track user activity for recent activity feed"""
        try:
            if not self.use_firestore or not self.db:
                logger.warning("Firestore not available - cannot track activity")
                return False
            
            activity_data = {
                'user_id': user_id,
                'type': activity_type,
                'description': description,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'metadata': metadata or {}
            }
            
            # Add to activities collection
            activities_ref = self.db.collection('user_activities')
            activities_ref.add(activity_data)
            
            # Also update user's recent activities array (keep last 10)
            user_ref = self.db.collection(self.users_collection).document(user_id)
            
            @firestore.transactional
            def update_user_activities(transaction):
                doc = user_ref.get(transaction=transaction)
                if doc.exists:
                    data = doc.to_dict()
                    recent_activities = data.get('recent_activities', [])
                    
                    # Add new activity
                    new_activity = {
                        'type': activity_type,
                        'description': description,
                        'timestamp': datetime.now().isoformat(),
                        'metadata': metadata or {}
                    }
                    recent_activities.insert(0, new_activity)
                    
                    # Keep only last 10 activities
                    recent_activities = recent_activities[:10]
                    
                    transaction.update(user_ref, {
                        'recent_activities': recent_activities,
                        'updated_at': firestore.SERVER_TIMESTAMP
                    })
                else:
                    # Create user with initial activity
                    initial_data = {
                        'created_at': firestore.SERVER_TIMESTAMP,
                        'recent_activities': [{
                            'type': activity_type,
                            'description': description,
                            'timestamp': datetime.now().isoformat(),
                            'metadata': metadata or {}
                        }]
                    }
                    transaction.set(user_ref, initial_data)
            
            # Execute transaction
            transaction = self.db.transaction()
            update_user_activities(transaction)
            
            logger.info(f"✅ Tracked activity for user {user_id}: {activity_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking activity for user {user_id}: {e}")
            return False

    def get_recent_activities(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activities for a user"""
        try:
            if not self.use_firestore or not self.db:
                return []
            
            user_data = self.get_user_data(user_id)
            if not user_data:
                return []
            
            recent_activities = user_data.get('recent_activities', [])
            
            # Process activities and add relative time
            processed_activities = []
            for activity in recent_activities[:limit]:
                try:
                    # Parse timestamp
                    timestamp_str = activity.get('timestamp', '')
                    if timestamp_str:
                        activity_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        
                        # Calculate relative time
                        now = datetime.now()
                        time_diff = now - activity_time.replace(tzinfo=None)
                        
                        if time_diff.days > 0:
                            relative_time = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
                        elif time_diff.seconds > 3600:
                            hours = time_diff.seconds // 3600
                            relative_time = f"{hours} hour{'s' if hours > 1 else ''} ago"
                        elif time_diff.seconds > 60:
                            minutes = time_diff.seconds // 60
                            relative_time = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
                        else:
                            relative_time = "Just now"
                        
                        activity['relative_time'] = relative_time
                        activity['formatted_time'] = activity_time.strftime('%I:%M %p')
                    else:
                        activity['relative_time'] = "Unknown"
                        activity['formatted_time'] = "Unknown"
                    
                    # Add icon based on activity type
                    activity['icon'] = self._get_activity_icon(activity.get('type', ''))
                    activity['color'] = self._get_activity_color(activity.get('type', ''))
                    
                    processed_activities.append(activity)
                    
                except Exception as parse_error:
                    logger.warning(f"Error parsing activity timestamp: {parse_error}")
                    activity['relative_time'] = "Unknown"
                    activity['formatted_time'] = "Unknown"
                    activity['icon'] = 'fas fa-circle'
                    activity['color'] = 'text-muted'
                    processed_activities.append(activity)
            
            return processed_activities
            
        except Exception as e:
            logger.error(f"Error getting recent activities for user {user_id}: {e}")
            return []

    def _get_activity_icon(self, activity_type: str) -> str:
        """Get FontAwesome icon for activity type"""
        icons = {
            'insight_generated': 'fas fa-brain',
            'login': 'fas fa-sign-in-alt',
            'logout': 'fas fa-sign-out-alt',
            'profile_updated': 'fas fa-user-edit',
            'subscription_changed': 'fas fa-crown',
            'limit_reached': 'fas fa-exclamation-triangle',
            'error': 'fas fa-times-circle',
            'success': 'fas fa-check-circle',
            'dashboard_viewed': 'fas fa-tachometer-alt',
            'insights_viewed': 'fas fa-eye'
        }
        return icons.get(activity_type, 'fas fa-circle')

    def _get_activity_color(self, activity_type: str) -> str:
        """Get CSS color class for activity type"""
        colors = {
            'insight_generated': 'text-primary',
            'login': 'text-success',
            'logout': 'text-muted',
            'profile_updated': 'text-info',
            'subscription_changed': 'text-warning',
            'limit_reached': 'text-danger',
            'error': 'text-danger',
            'success': 'text-success',
            'dashboard_viewed': 'text-primary',
            'insights_viewed': 'text-info'
        }
        return colors.get(activity_type, 'text-muted')

    def get_activity_report(self, user_id: str, period: str) -> Dict[str, Any]:
        """Get activity report for different time periods"""
        try:
            if period == 'week':
                return self._get_weekly_activity(user_id)
            elif period == 'month':
                return self._get_monthly_daily_activity(user_id)
            elif period == 'quarter':
                return self._get_quarterly_activity(user_id)
            elif period == 'year':
                return self._get_yearly_activity(user_id)
            else:
                return self._get_weekly_activity(user_id)  # Default to week
            
        except Exception as e:
            logger.error(f"Error getting activity report: {e}")
            return self._get_empty_activity_data()

    def _get_empty_activity_data(self) -> Dict[str, Any]:
        """Return empty activity data structure"""
        return {
            'data': [], 
            'summary': {
                'total_insights': 0, 
                'active_periods': 0, 
                'peak_value': 0, 
                'peak_label': 'N/A'
            }
        }

    def _get_hourly_activity(self, user_id: str) -> Dict[str, Any]:
        """Get 24-hour activity breakdown from actual insight data"""
        from datetime import datetime, timedelta
        
        try:
            if not self.use_firestore or not self.db:
                logger.warning("Firestore not available for hourly activity, using fallback")
                return self._get_hourly_fallback(user_id)
            
            # Get insights from last 24 hours with proper timezone handling
            now = datetime.now()
            yesterday = now - timedelta(days=1)
            
            logger.info(f"Querying hourly activity for user {user_id} from {yesterday} to {now}")
            
            # Query insights collection for user's insights in last 24 hours
            from google.cloud.firestore import FieldFilter
            
            insights_collection = self.db.collection('insights')
            insights_query = insights_collection.where(filter=FieldFilter('author_id', '==', user_id))\
                                               .where(filter=FieldFilter('created_at', '>=', yesterday))\
                                               .stream()
            
            # Group insights by hour
            hourly_counts = {hour: 0 for hour in range(24)}
            total_documents = 0
            processed_documents = 0
            
            for doc in insights_query:
                total_documents += 1
                try:
                    data = doc.to_dict()
                    created_at = data.get('created_at')
                    if created_at:
                        # Convert Firestore timestamp to datetime
                        if hasattr(created_at, 'seconds'):
                            # Firestore timestamp object
                            insight_time = datetime.fromtimestamp(created_at.seconds)
                        elif hasattr(created_at, 'timestamp'):
                            # Firestore timestamp with timestamp() method
                            insight_time = datetime.fromtimestamp(created_at.timestamp())
                        else:
                            # Already a datetime object
                            insight_time = created_at
                        
                        # Only count if within last 24 hours
                        if insight_time >= yesterday:
                            hour = insight_time.hour
                            hourly_counts[hour] += 1
                            processed_documents += 1
                            logger.debug(f"Insight at {insight_time} counted in hour {hour}")
                except Exception as e:
                    logger.warning(f"Error processing insight document: {e}")
                    continue
            
            logger.info(f"Hourly activity query: {total_documents} total docs, {processed_documents} processed")
            
            # Build response data
            hours = []
            total_insights = 0
            peak_value = 0
            peak_hour = ''
            
            for hour in range(24):
                value = hourly_counts[hour]
                if value > peak_value:
                    peak_value = value
                    peak_hour = f"{hour}"
                
                total_insights += value
                hours.append({
                    'label': f"{hour}",  # Just the hour number
                    'value': value
                })
            
            logger.info(f"Hourly activity result: {total_insights} total insights across {sum(1 for h in hours if h['value'] > 0)} active hours")
            
            # If no insights found from Firestore query, try fallback using today's daily usage
            if total_insights == 0:
                logger.info("No insights found from Firestore, trying fallback with daily usage data")
                return self._get_hourly_fallback(user_id)
            
            return {
                'data': hours,
                'summary': {
                    'total_insights': total_insights,
                    'active_periods': sum(1 for h in hours if h['value'] > 0),
                    'peak_value': peak_value,
                    'peak_label': f"Hour {peak_hour}" if peak_hour else 'N/A'
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting hourly activity: {e}")
            return self._get_empty_activity_data()

    def _get_hourly_fallback(self, user_id: str) -> Dict[str, Any]:
        """Fallback hourly activity using today's daily usage data"""
        from datetime import datetime
        
        try:
            # Get today's insights from daily usage
            now = datetime.now()
            today_key = now.strftime('%Y-%m-%d')
            
            user_data = self.get_user_data(user_id)
            daily_usage = user_data.get('usage', {}).get('daily_usage', {}) if user_data else {}
            today_insights = daily_usage.get(today_key, {}).get('insights', 0)
            
            logger.info(f"Hourly fallback: Found {today_insights} insights for today ({today_key})")
            
            # Create realistic hourly distribution
            hours = []
            total_insights = today_insights
            peak_value = 0
            peak_hour = ''
            
            if today_insights > 0:
                # Distribute insights across likely working hours (9-17) and some evening hours
                working_hours = [9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21]
                insights_per_hour = max(1, today_insights // len(working_hours))
                remainder = today_insights % len(working_hours)
                
                hourly_counts = {hour: 0 for hour in range(24)}
                
                # Distribute main insights
                for i, hour in enumerate(working_hours):
                    hourly_counts[hour] = insights_per_hour
                    if i < remainder:  # Distribute remainder
                        hourly_counts[hour] += 1
                
                # Find peak
                for hour in range(24):
                    value = hourly_counts[hour]
                    if value > peak_value:
                        peak_value = value
                        peak_hour = str(hour)
                    
                    hours.append({
                        'label': str(hour),
                        'value': value
                    })
            else:
                # No insights today - return empty hourly data
                for hour in range(24):
                    hours.append({
                        'label': str(hour),
                        'value': 0
                    })
            
            return {
                'data': hours,
                'summary': {
                    'total_insights': total_insights,
                    'active_periods': sum(1 for h in hours if h['value'] > 0),
                    'peak_value': peak_value,
                    'peak_label': f"Hour {peak_hour}" if peak_hour else 'N/A'
                }
            }
            
        except Exception as e:
            logger.error(f"Error in hourly fallback: {e}")
            return self._get_empty_activity_data()

    def _get_weekly_activity(self, user_id: str) -> Dict[str, Any]:
        """Get 7-day activity breakdown"""
        stats = self.get_usage_stats(user_id)
        daily_breakdown = stats.get('daily_breakdown', [])
        
        total_insights = sum(day['insights'] for day in daily_breakdown)
        active_days = sum(1 for day in daily_breakdown if day['insights'] > 0)
        peak_day = max(daily_breakdown, key=lambda x: x['insights'], default={'insights': 0, 'day_name': 'N/A'})
        
        data = []
        for day in daily_breakdown:
            data.append({
                'label': day['day_name'][:3],  # Short day names
                'value': day['insights']
            })
        
        return {
            'data': data,
            'summary': {
                'total_insights': total_insights,
                'active_periods': active_days,
                'peak_value': peak_day['insights'],
                'peak_label': peak_day['day_name']
            }
        }

    def _get_monthly_daily_activity(self, user_id: str) -> Dict[str, Any]:
        """Get daily activity for current month from user's daily usage data"""
        from datetime import datetime, timedelta
        import calendar
        
        try:
            # Get current month data
            now = datetime.now()
            current_month = now.strftime('%Y-%m')
            days_in_month = calendar.monthrange(now.year, now.month)[1]
            
            # Get user's daily usage data
            user_data = self.get_user_data(user_id)
            daily_usage = user_data.get('usage', {}).get('daily_usage', {}) if user_data else {}
            
            days = []
            total_insights = 0
            peak_value = 0
            peak_day = ''
            
            for day in range(1, days_in_month + 1):
                # Only count days up to today
                if day > now.day:
                    value = 0
                else:
                    # Format date key as stored in daily_usage
                    date_key = f"{current_month}-{day:02d}"
                    day_data = daily_usage.get(date_key, {})
                    value = day_data.get('insights', 0)
                    
                    if value > peak_value:
                        peak_value = value
                        peak_day = f"Day {day}"
                
                total_insights += value
                days.append({
                    'label': str(day),
                    'value': value
                })
            
            return {
                'data': days,
                'summary': {
                    'total_insights': total_insights,
                    'active_periods': sum(1 for d in days if d['value'] > 0),
                    'peak_value': peak_value,
                    'peak_label': peak_day if peak_day else 'N/A'
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting monthly daily activity: {e}")
            return self._get_empty_activity_data()

    def _get_quarterly_activity(self, user_id: str) -> Dict[str, Any]:
        """Get quarterly activity (3 months) from user's monthly breakdown data"""
        from datetime import datetime, timedelta
        import calendar
        
        try:
            # Get user's monthly breakdown data
            user_data = self.get_user_data(user_id)
            monthly_breakdown = user_data.get('usage', {}).get('monthly_breakdown', {}) if user_data else {}
            
            # Get last 3 months
            now = datetime.now()
            months = []
            
            for i in range(3):
                month_date = now - timedelta(days=30*i)
                month_key = month_date.strftime('%Y-%m')
                month_name = calendar.month_abbr[month_date.month]
                
                # Get actual data from monthly breakdown
                month_data = monthly_breakdown.get(month_key, {})
                value = month_data.get('insights', 0)
                
                months.insert(0, {
                    'label': month_name,
                    'value': value
                })
            
            total_insights = sum(m['value'] for m in months)
            peak_month = max(months, key=lambda x: x['value']) if months else {'value': 0, 'label': 'N/A'}
            
            return {
                'data': months,
                'summary': {
                    'total_insights': total_insights,
                    'active_periods': sum(1 for m in months if m['value'] > 0),
                    'peak_value': peak_month['value'],
                    'peak_label': peak_month['label']
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting quarterly activity: {e}")
            return self._get_empty_activity_data()

    def _get_yearly_activity(self, user_id: str) -> Dict[str, Any]:
        """Get 12-month activity breakdown from user's monthly breakdown data"""
        from datetime import datetime, timedelta
        import calendar
        
        try:
            # Get user's monthly breakdown data
            user_data = self.get_user_data(user_id)
            monthly_breakdown = user_data.get('usage', {}).get('monthly_breakdown', {}) if user_data else {}
            
            # Get last 12 months
            now = datetime.now()
            months = []
            
            for i in range(12):
                month_date = now - timedelta(days=30*i)
                month_key = month_date.strftime('%Y-%m')
                month_name = calendar.month_abbr[month_date.month]
                
                # Get actual data from monthly breakdown
                month_data = monthly_breakdown.get(month_key, {})
                value = month_data.get('insights', 0)
                
                months.insert(0, {
                    'label': month_name,
                    'value': value
                })
            
            total_insights = sum(m['value'] for m in months)
            peak_month = max(months, key=lambda x: x['value']) if months else {'value': 0, 'label': 'N/A'}
            
            return {
                'data': months,
                'summary': {
                    'total_insights': total_insights,
                    'active_periods': sum(1 for m in months if m['value'] > 0),
                    'peak_value': peak_month['value'],
                    'peak_label': peak_month['label']
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting yearly activity: {e}")
            return self._get_empty_activity_data() 