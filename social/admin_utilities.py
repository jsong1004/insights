# Add these admin utility functions to your auth/firestore_manager.py

def set_admin_status(self, user_id: str, is_admin: bool, admin_email: str = None) -> bool:
    """Set admin status for a user"""
    try:
        if not self.use_firestore or not self.db:
            logger.warning("Firestore not available - cannot set admin status")
            return False
        
        doc_ref = self.db.collection(self.users_collection).document(user_id)
        doc = doc_ref.get()
        
        if doc.exists:
            doc_ref.update({
                'is_admin': is_admin,
                'admin_granted_by': admin_email if is_admin else None,
                'admin_granted_at': firestore.SERVER_TIMESTAMP if is_admin else None,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"✅ {'Granted' if is_admin else 'Revoked'} admin status for user: {user_id}")
            return True
        else:
            logger.warning(f"User not found: {user_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error setting admin status for user {user_id}: {e}")
        return False

def is_user_admin(self, user_id: str) -> bool:
    """Check if user has admin privileges"""
    try:
        user_data = self.get_user_data(user_id)
        return user_data.get('is_admin', False) if user_data else False
        
    except Exception as e:
        logger.error(f"Error checking admin status for user {user_id}: {e}")
        return False

def get_admin_users(self) -> List[Dict[str, Any]]:
    """Get list of all admin users"""
    try:
        if not self.use_firestore or not self.db:
            return []
        
        docs = self.db.collection(self.users_collection)\
                      .where('is_admin', '==', True)\
                      .stream()
        
        admin_users = []
        for doc in docs:
            try:
                data = doc.to_dict()
                admin_users.append({
                    'user_id': doc.id,
                    'email': data.get('email'),
                    'display_name': data.get('display_name'),
                    'admin_granted_at': data.get('admin_granted_at'),
                    'admin_granted_by': data.get('admin_granted_by')
                })
            except Exception as e:
                logger.warning(f"Error parsing admin user document {doc.id}: {e}")
                continue
        
        return admin_users
        
    except Exception as e:
        logger.error(f"Error getting admin users: {e}")
        return []

# Admin management script - create a separate file: scripts/