/**
 * Main entry point for the AI Insights Frontend Application
 *
 * This file initializes all components and features based on the current page.
 * Page detection is done via data-page attribute on the body tag.
 */

// Import core utilities
import { initializeAuth } from './core/auth';
import { initializeAPI } from './core/api';
import { showFlashMessage } from './core/utils';

// Import components
import { FlashMessages } from './components/FlashMessages';
import { LoadingStates } from './components/LoadingStates';

// Import features
import { initializeCommunity } from './features/community';
import { initializeInsights } from './features/insights';
import { initializeDashboard } from './features/dashboard';
import { initializeInsightsForm } from './features/insightsForm';

/**
 * Initialize the application
 */
function initializeApp() {
  console.log('[AI Insights] Initializing application...');

  // Initialize core systems
  initializeAuth();
  initializeAPI();

  // Initialize components
  const flashMessages = new FlashMessages();
  const loadingStates = new LoadingStates();

  // Detect current page
  const page = document.body.dataset.page || 'unknown';
  console.log(`[AI Insights] Current page: ${page}`);

  // Initialize page-specific features
  switch (page) {
    case 'community':
      initializeCommunity();
      break;
    case 'insights':
      initializeInsights();
      break;
    case 'dashboard':
      initializeDashboard();
      break;
    case 'insights-form':
      initializeInsightsForm();
      break;
    case 'home':
      console.log('[AI Insights] Home page loaded');
      break;
    default:
      console.log(`[AI Insights] Unknown page: ${page}`);
  }

  // Expose utilities globally for inline scripts (temporary during transition)
  (window as any).AIInsights = {
    showFlashMessage,
    flashMessages,
    loadingStates,
  };

  console.log('[AI Insights] Application initialized successfully');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeApp);
} else {
  initializeApp();
}
