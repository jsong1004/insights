# AI Insights Generator - Usage Stats Implementation Guide (Flask/Python)

## Overview
This implementation guide provides a practical approach to add usage statistics to your AI Insights Generator Flask application using your existing Firestore integration and Firebase authentication.

## 1. Current Architecture Analysis

Your application already has:
- ✅ **Firebase Authentication** with `FirebaseAuthManager`
- ✅ **User Firestore Manager** with methods like `update_user_login()`, `increment_usage()`
- ✅ **Session Management** with user tracking
- ✅ **Firestore Database** named `ai-biz`

## 2. Enhanced Firestore Schema for Usage Stats

### Update User Collection Structure

Since you already have `UserFirestoreManager` in `auth/firestore_manager.py`, we'll enhance it:

```python
# Enhanced user document structure in Firestore
# Collection: users/{userId}
{
    "email": "user@example.com",
    "created_at": timestamp,
    "last_login": timestamp,
    "subscription": {
        "plan": "free",  # free, basic, pro, enterprise
        "status": "active",
        "started_at": timestamp,
        "ends_at": timestamp
    },
    "usage": {
        "insights_generated": 15,
        "insights_remaining": 5,
        "total_tokens_used": 45000,
        "last_reset": timestamp,
        "current_month": "2025-01",
        
        # New detailed tracking
        "monthly_breakdown": {
            "2025-01": {
                "insights": 15,
                "tokens": 45000,
                "search_requests": 45,
                "days_active": 8
            }
        },
        "daily_usage": {
            "2025-01-26": {
                "insights": 3,
                "tokens": 8500,
                "search_requests": 9
            }
        }
    },
    "limits": {
        "monthly_insights": 20,  # Based on plan
        "monthly_tokens": 100000,
        "daily_insights": 5,
        "rate_limit_per_hour": 10
    }
}
```

## 3. Enhance UserFirestoreManager

Update your existing `auth/firestore_manager.py`:

```python
# Add these methods to your existing UserFirestoreManager class

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
```

## 4. Update Main Routes for Usage Tracking

In your `routes/main.py`, update the generate_insights route:

```python
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
        
        # Generate insights
        insights = crew_system.generate_insights(topic, instructions, source, time_range)
        
        # Track usage with actual token count
        tokens_used = insights.total_tokens
        search_requests = len(insights.insights) if insights.insights else 1
        
        firestore_manager.track_insight_generation(
            user_id, 
            tokens_used, 
            search_requests
        )
        
        # Save insights
        saved = insights_firestore_manager.save_insights(insights)
        
        # ... rest of your existing code ...
        
    except Exception as e:
        logger.error(f"❌ Error generating insights: {e}")
        flash(f'Error generating insights: {str(e)}', 'error')
        return redirect(url_for('main.index'))
```

## 5. Add Usage Stats API Endpoint

Add to your `routes/api.py`:

```python
@api_bp.route('/usage-stats')
@login_required
def get_usage_stats():
    """Get current user's usage statistics"""
    try:
        user_id = session.get('user_id')
        firestore_manager = current_app.extensions.get('firestore_manager')
        
        stats = firestore_manager.get_usage_stats(user_id)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve usage statistics'
        }), 500
```

## 6. Update Dashboard Template

Update your `templates/auth/dashboard.html` to display enhanced usage stats:

```html
<!-- Update the Usage Stats Card -->
<div class="col-md-6 col-lg-4 mb-4">
    <div class="card h-100 shadow-sm">
        <div class="card-body">
            <h5 class="card-title">
                <i class="fas fa-chart-bar text-success me-2"></i>
                Usage Stats
            </h5>
            
            <div class="usage-stats" id="usage-stats-container">
                <div class="text-center py-3">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Add this JavaScript at the bottom -->
<script>
async function loadUsageStats() {
    try {
        const response = await fetch('/api/usage-stats');
        const data = await response.json();
        
        if (data.success) {
            const stats = data.stats;
            const container = document.getElementById('usage-stats-container');
            
            container.innerHTML = `
                <!-- Monthly Insights -->
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="fw-semibold">Monthly Insights</span>
                        <span class="text-muted">${stats.current_usage.monthly_insights}/${stats.limits.monthly_insights}</span>
                    </div>
                    <div class="progress" style="height: 10px;">
                        <div class="progress-bar ${stats.usage_percentage.insights > 80 ? 'bg-danger' : stats.usage_percentage.insights > 60 ? 'bg-warning' : 'bg-success'}" 
                             role="progressbar" 
                             style="width: ${stats.usage_percentage.insights}%"
                             aria-valuenow="${stats.usage_percentage.insights}" 
                             aria-valuemin="0" 
                             aria-valuemax="100">
                        </div>
                    </div>
                    <small class="text-muted">${stats.remaining.monthly_insights} remaining</small>
                </div>
                
                <!-- Token Usage -->
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="fw-semibold">Token Usage</span>
                        <span class="text-muted">${(stats.current_usage.monthly_tokens / 1000).toFixed(1)}k/${(stats.limits.monthly_tokens / 1000).toFixed(0)}k</span>
                    </div>
                    <div class="progress" style="height: 10px;">
                        <div class="progress-bar ${stats.usage_percentage.tokens > 80 ? 'bg-danger' : stats.usage_percentage.tokens > 60 ? 'bg-warning' : 'bg-info'}" 
                             role="progressbar" 
                             style="width: ${stats.usage_percentage.tokens}%"
                             aria-valuenow="${stats.usage_percentage.tokens}" 
                             aria-valuemin="0" 
                             aria-valuemax="100">
                        </div>
                    </div>
                    <small class="text-muted">${((stats.limits.monthly_tokens - stats.current_usage.monthly_tokens) / 1000).toFixed(0)}k tokens remaining</small>
                </div>
                
                <!-- Daily Insights -->
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="fw-semibold">Today's Insights</span>
                        <span class="text-muted">${stats.current_usage.daily_insights}/${stats.limits.daily_insights}</span>
                    </div>
                    <div class="progress" style="height: 6px;">
                        <div class="progress-bar bg-primary" 
                             role="progressbar" 
                             style="width: ${(stats.current_usage.daily_insights / stats.limits.daily_insights * 100)}%">
                        </div>
                    </div>
                </div>
                
                <!-- 7-Day Activity Chart -->
                <div class="mt-4">
                    <h6 class="text-muted mb-2">Last 7 Days Activity</h6>
                    <div class="d-flex align-items-end" style="height: 60px;">
                        ${stats.daily_breakdown.map(day => {
                            const maxInsights = Math.max(...stats.daily_breakdown.map(d => d.insights), 1);
                            const height = (day.insights / maxInsights * 100) || 0;
                            return `
                                <div class="flex-fill text-center position-relative" title="${day.date}: ${day.insights} insights">
                                    <div class="bg-primary bg-opacity-75" 
                                         style="height: ${height}%; min-height: ${day.insights > 0 ? '4px' : '0'}; 
                                                margin: 0 2px; border-radius: 2px 2px 0 0;">
                                    </div>
                                    <small class="text-muted" style="font-size: 10px;">${day.day}</small>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
                
                ${stats.usage_percentage.insights > 80 || stats.usage_percentage.tokens > 80 ? `
                    <div class="alert alert-warning alert-sm mt-3 mb-0 py-2 px-3">
                        <small>
                            <i class="fas fa-exclamation-triangle me-1"></i>
                            You're approaching your limits. 
                            <a href="/billing/plans" class="alert-link">Upgrade plan</a>
                        </small>
                    </div>
                ` : ''}
            `;
        }
    } catch (error) {
        console.error('Failed to load usage stats:', error);
        document.getElementById('usage-stats-container').innerHTML = `
            <p class="text-muted">Failed to load usage data</p>
            <button class="btn btn-sm btn-outline-primary" onclick="loadUsageStats()">
                <i class="fas fa-sync-alt me-1"></i>Retry
            </button>
        `;
    }
}

// Load usage stats on page load
document.addEventListener('DOMContentLoaded', function() {
    loadUsageStats();
    
    // Refresh stats every 30 seconds
    setInterval(loadUsageStats, 30000);
});
</script>
```

## 7. Add Monthly Reset Cloud Function

Create `functions/reset_monthly_usage.py`:

```python
from firebase_functions import scheduler_fn
from firebase_admin import firestore
import logging

logger = logging.getLogger(__name__)

@scheduler_fn.on_schedule(
    schedule="0 0 1 * *",  # First day of month at midnight
    timezone="UTC",
    memory=256,
    timeout_sec=540
)
def reset_monthly_usage(req: scheduler_fn.ScheduledEvent) -> None:
    """Reset monthly usage statistics for all users"""
    try:
        db = firestore.client()
        batch_size = 500
        total_updated = 0
        
        # Get all users in batches
        users_ref = db.collection('users')
        
        while True:
            # Get batch of users
            if total_updated == 0:
                batch = users_ref.limit(batch_size).stream()
            else:
                batch = users_ref.start_after(last_doc).limit(batch_size).stream()
            
            batch_list = list(batch)
            if not batch_list:
                break
                
            # Update users in this batch
            batch_update = db.batch()
            
            for user_doc in batch_list:
                user_data = user_doc.to_dict()
                subscription_plan = user_data.get('subscription', {}).get('plan', 'free')
                
                # Get limits for the user's plan
                limits = _get_plan_limits(subscription_plan)
                
                # Reset usage while preserving history
                usage = user_data.get('usage', {})
                usage['insights_remaining'] = limits['monthly_insights']
                usage['last_reset'] = firestore.SERVER_TIMESTAMP
                
                batch_update.update(user_doc.reference, {
                    'usage.insights_remaining': limits['monthly_insights'],
                    'usage.last_reset': firestore.SERVER_TIMESTAMP,
                    'limits': limits
                })
                
            batch_update.commit()
            total_updated += len(batch_list)
            
            # Set last document for pagination
            if batch_list:
                last_doc = batch_list[-1]
            
            logger.info(f"Updated {len(batch_list)} users, total: {total_updated}")
        
        logger.info(f"✅ Monthly reset completed. Updated {total_updated} users.")
        
    except Exception as e:
        logger.error(f"❌ Monthly reset failed: {e}")
        raise

def _get_plan_limits(plan: str) -> dict:
    """Get limits based on subscription plan"""
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
            'monthly_insights': -1,
            'monthly_tokens': -1,
            'daily_insights': -1,
            'rate_limit_per_hour': -1
        }
    }
    
    return limits.get(plan, limits['free'])
```

## 8. Add Usage Warning on Homepage

Update `templates/index.html` to show usage warnings:

```html
{% if session.user_id %}
<!-- Add this after the authentication notice -->
<div id="usage-warning-container"></div>

<script>
// Check usage limits on page load
async function checkUsageLimits() {
    try {
        const response = await fetch('/api/usage-stats');
        const data = await response.json();
        
        if (data.success) {
            const stats = data.stats;
            const container = document.getElementById('usage-warning-container');
            
            // Show warnings if approaching limits
            if (stats.remaining.daily_insights === 0) {
                container.innerHTML = `
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        <i class="fas fa-exclamation-circle me-2"></i>
                        <strong>Daily limit reached!</strong> You've used all ${stats.limits.daily_insights} daily insights. 
                        Come back tomorrow or <a href="/billing/plans" class="alert-link">upgrade your plan</a>.
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `;
            } else if (stats.remaining.monthly_insights === 0) {
                container.innerHTML = `
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        <i class="fas fa-exclamation-circle me-2"></i>
                        <strong>Monthly limit reached!</strong> You've used all ${stats.limits.monthly_insights} monthly insights. 
                        <a href="/billing/plans" class="alert-link">Upgrade your plan</a> to continue.
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `;
            } else if (stats.usage_percentage.insights > 80) {
                container.innerHTML = `
                    <div class="alert alert-warning alert-dismissible fade show" role="alert">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        You've used ${stats.current_usage.monthly_insights} of ${stats.limits.monthly_insights} monthly insights (${Math.round(stats.usage_percentage.insights)}%). 
                        <a href="/auth/dashboard" class="alert-link">View usage details</a>
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Failed to check usage limits:', error);
    }
}

// Check on page load if user is logged in
if (document.getElementById('usage-warning-container')) {
    checkUsageLimits();
}
</script>
{% endif %}
```

## 9. Deploy Cloud Function

```bash
# Deploy the monthly reset function
cd functions
firebase deploy --only functions:reset_monthly_usage
```

## 10. Testing the Implementation

Create a test script `test_usage_stats.py`:

```python
from auth.firestore_manager import UserFirestoreManager
import logging

logging.basicConfig(level=logging.INFO)

# Test user ID (use a real user ID from your system)
test_user_id = "test-user-123"

# Initialize manager
manager = UserFirestoreManager()

# Test tracking
print("Testing insight generation tracking...")
success = manager.track_insight_generation(test_user_id, tokens_used=2500, search_requests=3)
print(f"Tracking success: {success}")

# Test getting stats
print("\nGetting usage statistics...")
stats = manager.get_usage_stats(test_user_id)
print(f"Current usage: {stats['current_usage']}")
print(f"Remaining: {stats['remaining']}")
print(f"Usage percentage: {stats['usage_percentage']}")

# Test limits check
print("\nChecking usage limits...")
limits = manager.check_usage_limits(test_user_id)
print(f"Can generate: {limits['can_generate']}")
print(f"Limit status: {limits}")
```

## Summary

This implementation provides:

1. **Comprehensive Usage Tracking**: Tracks insights, tokens, and search requests
2. **Multi-level Limits**: Monthly, daily, and rate limits based on subscription plans
3. **Real-time Dashboard**: Visual progress bars and 7-day activity charts
4. **Automatic Warnings**: Alerts users when approaching limits
5. **Plan-based Scaling**: Different limits for free, basic, pro, and enterprise users
6. **Historical Data**: Maintains monthly breakdowns and 30-day rolling history
7. **Cloud Function Reset**: Automatic monthly usage reset

The implementation leverages your existing Flask architecture with Firebase authentication and Firestore database, requiring minimal changes to your current codebase while adding powerful usage tracking capabilities.