#!/usr/bin/env python3
"""
Admin Management Script for AI Insights Generator

This script allows you to manage admin privileges for users.

Usage:
    python scripts/manage_admins.py --grant user@example.com
    python scripts/manage_admins.py --revoke user@example.com  
    python scripts/manage_admins.py --list
    python scripts/manage_admins.py --init-admin jsong@koreatous.com
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.firestore_manager import UserFirestoreManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdminManager:
    def __init__(self):
        self.firestore_manager = UserFirestoreManager()
        
        if not self.firestore_manager.use_firestore:
            logger.error("❌ Firestore is not available. Cannot manage admin users.")
            sys.exit(1)
        
        logger.info("✅ Connected to Firestore for admin management")
    
    def grant_admin(self, email: str, granted_by: str = "system"):
        """Grant admin privileges to a user"""
        try:
            # First, we need to find the user ID by email
            # For Firebase Auth, the user ID is typically the email or a generated UID
            # We'll use email as the user ID for this implementation
            user_id = email
            
            # Check if user exists, if not create them
            user_data = self.firestore_manager.get_user_data(user_id)
            if not user_data:
                # Create user record
                new_user_data = {
                    'email': email,
                    'display_name': email.split('@')[0],
                    'is_admin': True,
                    'admin_granted_by': granted_by,
                    'usage': {
                        'insights_generated': 0,
                        'insights_remaining': 5
                    }
                }
                
                success = self.firestore_manager.create_user(user_id, new_user_data)
                if success:
                    logger.info(f"✅ Created new user and granted admin privileges to: {email}")
                    return True
                else:
                    logger.error(f"❌ Failed to create user: {email}")
                    return False
            else:
                # User exists, just grant admin privileges
                success = self.firestore_manager.set_admin_status(user_id, True, granted_by)
                if success:
                    logger.info(f"✅ Granted admin privileges to: {email}")
                    return True
                else:
                    logger.error(f"❌ Failed to grant admin privileges to: {email}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error granting admin privileges to {email}: {e}")
            return False
    
    def revoke_admin(self, email: str):
        """Revoke admin privileges from a user"""
        try:
            user_id = email
            
            success = self.firestore_manager.set_admin_status(user_id, False)
            if success:
                logger.info(f"✅ Revoked admin privileges from: {email}")
                return True
            else:
                logger.error(f"❌ Failed to revoke admin privileges from: {email}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error revoking admin privileges from {email}: {e}")
            return False
    
    def list_admins(self):
        """List all admin users"""
        try:
            admin_users = self.firestore_manager.get_admin_users()
            
            if not admin_users:
                logger.info("📝 No admin users found")
                return
            
            logger.info(f"📝 Found {len(admin_users)} admin user(s):")
            print("\n" + "="*80)
            print(f"{'Email':<30} {'Display Name':<20} {'Granted By':<20} {'Granted At':<20}")
            print("="*80)
            
            for admin in admin_users:
                email = admin.get('email', 'N/A')
                display_name = admin.get('display_name', 'N/A')
                granted_by = admin.get('admin_granted_by', 'N/A')
                granted_at = admin.get('admin_granted_at')
                
                if granted_at:
                    # Format timestamp if it exists
                    try:
                        if hasattr(granted_at, 'strftime'):
                            granted_at_str = granted_at.strftime('%Y-%m-%d %H:%M')
                        else:
                            granted_at_str = str(granted_at)[:16]
                    except:
                        granted_at_str = 'N/A'
                else:
                    granted_at_str = 'N/A'
                
                print(f"{email:<30} {display_name:<20} {granted_by:<20} {granted_at_str:<20}")
            
            print("="*80 + "\n")
            
        except Exception as e:
            logger.error(f"❌ Error listing admin users: {e}")
    
    def init_default_admin(self, email: str):
        """Initialize the first admin user"""
        logger.info(f"🚀 Initializing default admin user: {email}")
        return self.grant_admin(email, "system-init")

def main():
    parser = argparse.ArgumentParser(description='Manage admin privileges for AI Insights Generator')
    parser.add_argument('--grant', type=str, help='Grant admin privileges to user email')
    parser.add_argument('--revoke', type=str, help='Revoke admin privileges from user email')
    parser.add_argument('--list', action='store_true', help='List all admin users')
    parser.add_argument('--init-admin', type=str, help='Initialize default admin user')
    parser.add_argument('--granted-by', type=str, default='manual', help='Who is granting the admin privilege')
    
    args = parser.parse_args()
    
    if not any([args.grant, args.revoke, args.list, args.init_admin]):
        parser.print_help()
        return
    
    admin_manager = AdminManager()
    
    if args.grant:
        admin_manager.grant_admin(args.grant, args.granted_by)
    
    if args.revoke:
        admin_manager.revoke_admin(args.revoke)
    
    if args.list:
        admin_manager.list_admins()
    
    if args.init_admin:
        admin_manager.init_default_admin(args.init_admin)

if __name__ == '__main__':
    main() 