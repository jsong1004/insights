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