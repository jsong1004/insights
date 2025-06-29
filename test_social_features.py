#!/usr/bin/env python3
"""
Test script for social features implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.insights_manager import FirestoreManager
from core.crew_ai import GeneratedInsights, InsightItem
import uuid
from datetime import datetime

def test_social_features():
    """Test the new social features"""
    print("🧪 Testing Social Features Implementation")
    print("=" * 50)
    
    # Initialize manager
    manager = FirestoreManager()
    
    # Create test insights
    test_insight = GeneratedInsights(
        id=str(uuid.uuid4()),
        topic="Test AI Social Features",
        instructions="Testing like/dislike functionality",
        timestamp=datetime.now().isoformat(),
        insights=[
            InsightItem(
                title="Test Insight",
                summary="This is a test insight for social features",
                key_points=["Test point 1", "Test point 2"],
                detailed_report="Detailed test report content",
                significance="Testing significance",
                sources=["https://example.com"],
                confidence_score=0.9,
                research_quality="High"
            )
        ],
        total_insights=1,
        processing_time=1.0,
        agent_notes="Test notes",
        author_id="test_user_1",
        author_name="Test User",
        is_shared=True,
        likes=0,
        liked_by=[],
        dislikes=0,
        disliked_by=[]
    )
    
    print("1. Testing insight creation...")
    success = manager.save_insights(test_insight)
    print(f"   ✅ Insight saved: {success}")
    
    print("2. Testing like functionality...")
    like_success = manager.toggle_like(test_insight.id, "test_user_2")
    print(f"   ✅ Like toggle: {like_success}")
    
    # Retrieve and check
    retrieved = manager.get_insights(test_insight.id)
    if retrieved:
        print(f"   ✅ Likes count: {retrieved.likes}")
        print(f"   ✅ Liked by: {retrieved.liked_by}")
    
    print("3. Testing dislike functionality...")
    dislike_success = manager.toggle_dislike(test_insight.id, "test_user_3")
    print(f"   ✅ Dislike toggle: {dislike_success}")
    
    # Retrieve and check
    retrieved = manager.get_insights(test_insight.id)
    if retrieved:
        print(f"   ✅ Dislikes count: {retrieved.dislikes}")
        print(f"   ✅ Disliked by: {retrieved.disliked_by}")
    
    print("4. Testing shared insights retrieval...")
    shared_insights = manager.get_shared_insights()
    print(f"   ✅ Shared insights count: {len(shared_insights)}")
    
    print("5. Testing trending insights...")
    trending = manager.get_trending_insights(limit=5)
    print(f"   ✅ Trending insights count: {len(trending)}")
    
    print("6. Testing most liked insights...")
    most_liked = manager.get_most_liked_insights(limit=5)
    print(f"   ✅ Most liked insights count: {len(most_liked)}")
    
    print("7. Testing featured insights...")
    featured = manager.get_featured_insights(limit=5)
    print(f"   ✅ Featured insights count: {len(featured)}")
    
    # Cleanup
    print("8. Cleaning up test data...")
    cleanup_success = manager.delete_insights(test_insight.id)
    print(f"   ✅ Cleanup: {cleanup_success}")
    
    print("\n🎉 Social features test completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_social_features() 