#!/usr/bin/env python3
"""
Database Migration Script for Social Features

This script adds the necessary fields for social features to existing insights
and sets up admin users.

Usage:
    python scripts/migrate_social_features.py
"""

import sys
import os
import logging
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.insights_manager import FirestoreManager
from auth.firestore_manager import UserFirestoreManager
import firebase_admin
from firebase_admin import firestore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_insights_social_features():
    """Add social features fields to existing insights"""
    try:
        insights_manager = FirestoreManager()
        
        if not insights_manager.use_firestore or not insights_manager.db:
            logger.error("Firestore not available for migration")
            return False
        
        # Get all insights
        docs = insights_manager.db.collection('insights').stream()
        
        updated_count = 0
        error_count = 0
        
        for doc in docs:
            try:
                data = doc.to_dict()
                
                # Check if social features already exist
                if 'is_pinned' in data and 'view_count' in data:
                    logger.info(f"Insight {doc.id} already has social features")
                    continue
                
                # Add missing social feature fields
                update_data = {}
                
                # Social features
                if 'is_pinned' not in data:
                    update_data['is_pinned'] = False
                if 'pinned_by' not in data:
                    update_data['pinned_by'] = None
                if 'pinned_at' not in data:
                    update_data['pinned_at'] = None
                
                # Engagement metrics
                if 'view_count' not in data:
                    update_data['view_count'] = 0
                if 'featured' not in data:
                    update_data['featured'] = False
                if 'category' not in data:
                    update_data['category'] = None
                if 'language' not in data:
                    update_data['language'] = 'en'
                
                # Quality metrics
                if 'quality_score' not in data:
                    update_data['quality_score'] = None
                if 'engagement_score' not in data:
                    update_data['engagement_score'] = None
                
                # Ensure likes fields exist
                if 'likes' not in data:
                    update_data['likes'] = 0
                if 'liked_by' not in data:
                    update_data['liked_by'] = []
                
                # Update the document
                if update_data:
                    doc.reference.update(update_data)
                    updated_count += 1
                    logger.info(f"✅ Updated insight {doc.id} with social features")
                
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Error updating insight {doc.id}: {e}")
                continue
        
        logger.info(f"Migration completed: {updated_count} insights updated, {error_count} errors")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

def setup_initial_admin(admin_email: str):
    """Set up initial admin user"""
    try:
        from firebase_admin import auth as firebase_auth
        
        user_manager = UserFirestoreManager()
        
        # Get user by email
        try:
            user = firebase_auth.get_user_by_email(admin_email)
            user_id = user.uid
            
            # Grant admin status
            success = user_manager.set_admin_status(user_id, True, "migration_script")
            
            if success:
                logger.info(f"✅ Successfully granted admin privileges to {admin_email}")
                return True
            else:
                logger.error(f"❌ Failed to grant admin privileges to {admin_email}")
                return False
                
        except Exception as e:
            logger.error(f"User not found with email {admin_email}: {e}")
            logger.info("Please make sure the user has signed up before running this migration")
            return False
            
    except Exception as e:
        logger.error(f"Error setting up admin user: {e}")
        return False

def add_firestore_indexes():
    """Print instructions for adding required Firestore indexes"""
    logger.info("=" * 80)
    logger.info("FIRESTORE INDEXES REQUIRED")
    logger.info("=" * 80)
    logger.info("Please add the following indexes to your Firestore database:")
    logger.info("")
    logger.info("1. For community insights sorting by likes:")
    logger.info("   Collection: insights")
    logger.info("   Fields: is_shared (Ascending), likes (Descending)")
    logger.info("")
    logger.info("2. For community insights sorting with pinned:")
    logger.info("   Collection: insights")
    logger.info("   Fields: is_shared (Ascending), is_pinned (Descending), created_at (Descending)")
    logger.info("")
    logger.info("3. For trending topics by date:")
    logger.info("   Collection: insights")
    logger.info("   Fields: is_shared (Ascending), created_at (Ascending)")
    logger.info("")
    logger.info("You can add these indexes in the Firebase Console:")
    logger.info("https://console.firebase.google.com/project/your-project/firestore/indexes")
    logger.info("")
    logger.info("Or use the Firebase CLI:")
    logger.info("firebase deploy --only firestore:indexes")
    logger.info("=" * 80)

def verify_migration():
    """Verify that the migration was successful"""
    try:
        insights_manager = FirestoreManager()
        user_manager = UserFirestoreManager()
        
        # Check insights
        insights_count = insights_manager.get_community_insights_count()
        logger.info(f"Community insights available: {insights_count}")
        
        # Check admin users
        admin_users = user_manager.get_admin_users()
        logger.info(f"Admin users configured: {len(admin_users)}")
        
        for admin in admin_users:
            logger.info(f"  - {admin['email']} ({admin['user_id']})")
        
        # Test community stats
        stats = insights_manager.get_community_stats()
        logger.info(f"Community stats: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False

def main():
    """Main migration function"""
    logger.info("Starting social features migration...")
    
    try:
        # Step 1: Migrate insights
        logger.info("Step 1: Migrating insights with social features...")
        if not migrate_insights_social_features():
            logger.error("Insights migration failed")
            return False
        
        # Step 2: Set up admin user (optional)
        admin_email = input("Enter admin email address (or press Enter to skip): ").strip()
        if admin_email:
            logger.info(f"Step 2: Setting up admin user {admin_email}...")
            setup_initial_admin(admin_email)
        else:
            logger.info("Step 2: Skipping admin setup")
        
        # Step 3: Show index requirements
        logger.info("Step 3: Database indexes...")
        add_firestore_indexes()
        
        # Step 4: Verify migration
        logger.info("Step 4: Verifying migration...")
        verify_migration()
        
        logger.info("✅ Migration completed successfully!")
        logger.info("Remember to add the required Firestore indexes shown above.")
        
        return True
        
    except KeyboardInterrupt:
        logger.info("Migration cancelled by user")
        return False
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)