#!/usr/bin/env python3
"""
Database Migration Script for Social Features

This script migrates existing insights to include the new social features:
- is_pinned, pinned_by, pinned_at
- views, view_count
- Enhanced social metadata

Usage:
    python scripts/migrate_social_features.py
"""

import sys
import os
import logging
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.insights_manager import FirestoreManager, FIRESTORE_COLLECTION
from google.cloud import firestore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SocialFeaturesMigration:
    def __init__(self):
        self.firestore_manager = FirestoreManager()
        
        if not self.firestore_manager.use_firestore:
            logger.error("❌ Firestore is not available. Cannot run migration.")
            sys.exit(1)
        
        self.db = self.firestore_manager.db
        logger.info("✅ Connected to Firestore for migration")
    
    def migrate_insights(self):
        """Migrate all existing insights to include social features"""
        try:
            logger.info("🚀 Starting social features migration...")
            
            # Get all insights
            docs = self.db.collection(FIRESTORE_COLLECTION).stream()
            
            updated_count = 0
            skipped_count = 0
            error_count = 0
            
            for doc in docs:
                try:
                    data = doc.to_dict()
                    doc_id = doc.id
                    
                    # Check if migration is needed
                    needs_migration = False
                    updates = {}
                    
                    # Add missing social fields
                    if 'is_pinned' not in data:
                        updates['is_pinned'] = False
                        needs_migration = True
                    
                    if 'pinned_by' not in data:
                        updates['pinned_by'] = None
                        needs_migration = True
                    
                    if 'pinned_at' not in data:
                        updates['pinned_at'] = None
                        needs_migration = True
                    
                    if 'views' not in data:
                        updates['views'] = 0
                        needs_migration = True
                    
                    if 'view_count' not in data:
                        updates['view_count'] = 0
                        needs_migration = True
                    
                    # Ensure existing social fields have default values
                    if 'likes' not in data:
                        updates['likes'] = 0
                        needs_migration = True
                    
                    if 'liked_by' not in data:
                        updates['liked_by'] = []
                        needs_migration = True
                    
                    if 'is_shared' not in data:
                        # Default to True for existing insights (they were public before)
                        updates['is_shared'] = True
                        needs_migration = True
                    
                    # Ensure author fields are present
                    if 'author_name' not in data:
                        # Try to derive from author_email or set to Anonymous
                        author_email = data.get('author_email', '')
                        if author_email:
                            updates['author_name'] = author_email.split('@')[0]
                        else:
                            updates['author_name'] = 'Anonymous'
                        needs_migration = True
                    
                    if needs_migration:
                        # Add migration timestamp
                        updates['migrated_at'] = firestore.SERVER_TIMESTAMP
                        updates['updated_at'] = firestore.SERVER_TIMESTAMP
                        
                        # Update the document
                        doc_ref = self.db.collection(FIRESTORE_COLLECTION).document(doc_id)
                        doc_ref.update(updates)
                        
                        updated_count += 1
                        logger.info(f"✅ Migrated insight: {doc_id} (Topic: {data.get('topic', 'Unknown')[:50]})")
                    else:
                        skipped_count += 1
                        logger.debug(f"⏭️ Skipped insight: {doc_id} (already migrated)")
                
                except Exception as e:
                    error_count += 1
                    logger.error(f"❌ Error migrating insight {doc.id}: {e}")
                    continue
            
            logger.info(f"""
🎉 Migration completed!
   ✅ Updated: {updated_count} insights
   ⏭️ Skipped: {skipped_count} insights (already migrated)
   ❌ Errors: {error_count} insights
   📊 Total processed: {updated_count + skipped_count + error_count} insights
            """)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
    
    def verify_migration(self):
        """Verify that the migration was successful"""
        try:
            logger.info("🔍 Verifying migration...")
            
            # Check a sample of documents
            docs = self.db.collection(FIRESTORE_COLLECTION).limit(10).stream()
            
            verified_count = 0
            missing_fields = set()
            
            required_fields = [
                'is_pinned', 'pinned_by', 'pinned_at', 'views', 'view_count',
                'likes', 'liked_by', 'is_shared', 'author_name'
            ]
            
            for doc in docs:
                data = doc.to_dict()
                doc_verified = True
                
                for field in required_fields:
                    if field not in data:
                        missing_fields.add(field)
                        doc_verified = False
                
                if doc_verified:
                    verified_count += 1
            
            if missing_fields:
                logger.warning(f"⚠️ Some documents are missing fields: {missing_fields}")
                logger.warning("You may need to run the migration again.")
            else:
                logger.info(f"✅ Verification successful! Checked {verified_count} documents.")
            
            return len(missing_fields) == 0
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False
    
    def create_indexes(self):
        """Print instructions for creating required Firestore indexes"""
        logger.info("""
📋 IMPORTANT: Create these Firestore indexes for optimal performance:

1. In the Firebase Console, go to Firestore > Indexes
2. Create these composite indexes:

Index 1 - Community Insights (Likes sorting):
Collection: insights
Fields:
  - is_shared (Ascending)
  - likes (Descending)

Index 2 - Community Insights (Pinned sorting):
Collection: insights  
Fields:
  - is_shared (Ascending)
  - is_pinned (Descending)
  - created_at (Descending)

Index 3 - Community Insights (Recent sorting):
Collection: insights
Fields:
  - is_shared (Ascending)
  - created_at (Descending)

Or use the Firebase CLI with this command:
firebase deploy --only firestore:indexes

Make sure your firestore.indexes.json includes these indexes.
        """)

def main():
    migration = SocialFeaturesMigration()
    
    logger.info("🔄 Starting Social Features Migration")
    logger.info("This will add social features to existing insights...")
    
    # Run the migration
    success = migration.migrate_insights()
    
    if success:
        # Verify the migration
        migration.verify_migration()
        
        # Show index creation instructions
        migration.create_indexes()
        
        logger.info("✅ Migration process completed successfully!")
    else:
        logger.error("❌ Migration failed. Please check the logs and try again.")
        sys.exit(1)

if __name__ == '__main__':
    main() 