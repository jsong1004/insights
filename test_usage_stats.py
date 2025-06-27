from auth.firestore_manager import UserFirestoreManager
import logging
import firebase_admin

logging.basicConfig(level=logging.INFO)

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    firebase_admin.initialize_app()

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
