#!/usr/bin/env python3
"""
Simple Admin Setup Script

Run this script after Firebase is properly configured to set up jsong@koreatous.com as admin.

Usage:
    python setup_admin.py
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_admin():
    """Set up the initial admin user"""
    try:
        from auth.firestore_manager import UserFirestoreManager
        
        # Initialize Firestore manager
        firestore_manager = UserFirestoreManager()
        
        if not firestore_manager.use_firestore:
            logger.error("❌ Firestore is not available. Please check your Firebase configuration.")
            logger.info("Make sure you have:")
            logger.info("1. Valid Firebase credentials")
            logger.info("2. GOOGLE_APPLICATION_CREDENTIALS environment variable set")
            logger.info("3. Or service account configured in Secret Manager")
            return False
        
        admin_email = "jsong@koreatous.com"
        
        # Check if user already exists and is admin
        user_data = firestore_manager.get_user_data(admin_email)
        if user_data and user_data.get('is_admin'):
            logger.info(f"✅ {admin_email} is already an admin user")
            return True
        
        # Set up admin user
        if not user_data:
            # Create new user
            new_user_data = {
                'email': admin_email,
                'display_name': 'jsong',
                'is_admin': True,
                'admin_granted_by': 'system-init',
                'usage': {
                    'insights_generated': 0,
                    'insights_remaining': 100  # Give admin more insights
                }
            }
            
            success = firestore_manager.create_user(admin_email, new_user_data)
            if success:
                logger.info(f"✅ Created admin user: {admin_email}")
                return True
            else:
                logger.error(f"❌ Failed to create admin user: {admin_email}")
                return False
        else:
            # Grant admin privileges to existing user
            success = firestore_manager.set_admin_status(admin_email, True, 'system-init')
            if success:
                logger.info(f"✅ Granted admin privileges to: {admin_email}")
                return True
            else:
                logger.error(f"❌ Failed to grant admin privileges to: {admin_email}")
                return False
                
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Make sure you're running this from the project root directory")
        return False
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False

def main():
    logger.info("🚀 Setting up admin user...")
    
    success = setup_admin()
    
    if success:
        logger.info("✅ Admin setup completed successfully!")
        logger.info("📋 Admin privileges for jsong@koreatous.com:")
        logger.info("   - Can pin/unpin any insight")
        logger.info("   - Can delete any insight (shared or private)")
        logger.info("   - Has enhanced insight generation limits")
    else:
        logger.error("❌ Admin setup failed")
        sys.exit(1)

if __name__ == '__main__':
    main() 