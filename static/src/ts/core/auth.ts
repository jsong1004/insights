/**
 * Authentication Module
 * Handles user authentication, logout, and session management
 */

import { showFlashMessage } from './utils';

/**
 * Logout the current user
 */
export async function logout(): Promise<void> {
  try {
    // Sign out from Firebase (client-side)
    if (typeof window !== 'undefined' && (window as any).firebase) {
      const auth = (window as any).firebase.auth();
      await auth.signOut();
    }

    // Clear server-side session
    const response = await fetch('/auth/logout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      showFlashMessage('Successfully logged out', 'success');
      // Redirect to home page after a short delay
      setTimeout(() => {
        window.location.href = '/';
      }, 500);
    } else {
      throw new Error('Logout failed');
    }
  } catch (error) {
    console.error('[Auth] Logout error:', error);
    showFlashMessage('Error logging out. Please try again.', 'error');
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;

  // Check for Firebase user
  if ((window as any).firebase) {
    const auth = (window as any).firebase.auth();
    return auth.currentUser !== null;
  }

  return false;
}

/**
 * Get current user
 */
export function getCurrentUser(): any | null {
  if (typeof window === 'undefined') return null;

  if ((window as any).firebase) {
    const auth = (window as any).firebase.auth();
    return auth.currentUser;
  }

  return null;
}

/**
 * Check if current user is an admin
 * This checks the server-side session via DOM
 */
export function isAdmin(): boolean {
  if (typeof window === 'undefined') return false;

  // Check if admin badge exists in navigation
  const adminBadge = document.querySelector('.navbar .badge.bg-warning');
  return adminBadge !== null;
}

/**
 * Initialize authentication module
 */
export function initializeAuth(): void {
  console.log('[Auth] Authentication module initialized');

  // Set up Firebase auth state listener if Firebase is available
  if (typeof window !== 'undefined' && (window as any).firebase) {
    try {
      // Check if Firebase app is initialized
      const firebaseApp = (window as any).firebase.apps.length > 0
        ? (window as any).firebase.app()
        : null;

      if (firebaseApp) {
        const auth = (window as any).firebase.auth();
        auth.onAuthStateChanged((user: any) => {
          if (user) {
            console.log('[Auth] User is signed in:', user.email);
          } else {
            console.log('[Auth] User is signed out');
          }
        });
      } else {
        console.log('[Auth] Firebase not initialized yet - auth state listener skipped');
      }
    } catch (error) {
      console.warn('[Auth] Firebase auth initialization skipped:', error);
    }
  }

  // Attach logout event handler to logout links
  document.addEventListener('click', (event) => {
    const target = event.target as HTMLElement;
    const logoutLink = target.closest('[data-action="logout"]');

    if (logoutLink) {
      event.preventDefault();

      if (confirm('Are you sure you want to logout?')) {
        logout();
      }
    }
  });
}

/**
 * Export for global access (backward compatibility)
 */
if (typeof window !== 'undefined') {
  (window as any).logout = logout;
  (window as any).isAuthenticated = isAuthenticated;
  (window as any).getCurrentUser = getCurrentUser;
  (window as any).isAdmin = isAdmin;
}
