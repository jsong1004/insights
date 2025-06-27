#!/usr/bin/env python3
"""
Test script to populate sample recent activities for demonstration
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Add the current directory to path so we can import our modules
sys.path.append('.')

def create_sample_activities():
    """Create sample activities for testing the recent activity feature"""
    try:
        from auth.firestore_manager import UserFirestoreManager
        
        firestore_manager = UserFirestoreManager()
        
        # Sample user ID (replace with a real one from your system)
        user_id = "test-user-123"
        
        # Sample activities with different types and timestamps
        sample_activities = [
            {
                'type': 'login',
                'description': 'User logged in',
                'metadata': {'email': 'test@example.com'},
                'hours_ago': 0.5
            },
            {
                'type': 'insight_generated',
                'description': 'Generated insights for "AI Market Trends"',
                'metadata': {
                    'topic': 'AI Market Trends',
                    'tokens': 2500,
                    'processing_time': 45.2,
                    'source': 'web',
                    'insights_count': 5,
                    'status': 'success'
                },
                'hours_ago': 2
            },
            {
                'type': 'insights_viewed',
                'description': 'Viewed insights: "Climate Change Solutions"',
                'metadata': {
                    'insight_id': 'insight-456',
                    'topic': 'Climate Change Solutions',
                    'insights_count': 7
                },
                'hours_ago': 3
            },
            {
                'type': 'dashboard_viewed',
                'description': 'Viewed dashboard',
                'metadata': {},
                'hours_ago': 4
            },
            {
                'type': 'insight_generated',
                'description': 'Generated insights for "Cryptocurrency Future"',
                'metadata': {
                    'topic': 'Cryptocurrency Future',
                    'tokens': 1800,
                    'processing_time': 32.1,
                    'source': 'general',
                    'insights_count': 4,
                    'status': 'success'
                },
                'hours_ago': 6
            },
            {
                'type': 'profile_updated',
                'description': 'Updated profile information',
                'metadata': {'fields_updated': ['bio', 'preferences']},
                'hours_ago': 12
            },
            {
                'type': 'insights_viewed',
                'description': 'Viewed insights: "Renewable Energy"',
                'metadata': {
                    'insight_id': 'insight-789',
                    'topic': 'Renewable Energy',
                    'insights_count': 6
                },
                'hours_ago': 18
            },
            {
                'type': 'login',
                'description': 'User logged in',
                'metadata': {'email': 'test@example.com'},
                'hours_ago': 24
            }
        ]
        
        print("🔄 Creating sample activities...")
        
        for activity in sample_activities:
            # Calculate timestamp
            timestamp = datetime.now() - timedelta(hours=activity['hours_ago'])
            
            # Create activity manually to set custom timestamp
            user_ref = firestore_manager.db.collection('users').document(user_id)
            
            # Get current user data
            doc = user_ref.get()
            if doc.exists:
                data = doc.to_dict()
                recent_activities = data.get('recent_activities', [])
            else:
                recent_activities = []
                # Create user document if it doesn't exist
                user_ref.set({
                    'created_at': timestamp,
                    'recent_activities': []
                })
            
            # Add new activity with custom timestamp
            new_activity = {
                'type': activity['type'],
                'description': activity['description'],
                'timestamp': timestamp.isoformat(),
                'metadata': activity['metadata']
            }
            recent_activities.insert(0, new_activity)
            
            # Keep only last 10 activities
            recent_activities = recent_activities[:10]
            
            # Update user document
            user_ref.update({
                'recent_activities': recent_activities,
                'updated_at': firestore_manager.db.SERVER_TIMESTAMP
            })
            
            print(f"✅ Added activity: {activity['description']}")
        
        print(f"\n🎉 Successfully created {len(sample_activities)} sample activities!")
        print(f"📝 Activities are associated with user ID: {user_id}")
        print("\n💡 To test:")
        print("1. Update the user_id in your session or create a user with this ID")
        print("2. Visit the dashboard to see the recent activities")
        print("3. The activities will show up in chronological order with proper icons and metadata")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample activities: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Recent Activity Test Script")
    print("=" * 50)
    
    # Check if Firebase credentials are available
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS') and not os.path.exists('service-account-key.json'):
        print("⚠️  Warning: Firebase credentials not found.")
        print("Please ensure GOOGLE_APPLICATION_CREDENTIALS is set or service-account-key.json exists.")
    
    success = create_sample_activities()
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1) 