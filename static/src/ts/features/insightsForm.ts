/**
 * Insights Form Feature Module
 * Handles insights generation form functionality
 */

import { API } from '../core/api';
import { FormValidation } from '../components/FormValidation';
import { showFlashMessage, showLoading, hideLoading } from '../core/utils';
import type { UsageStats } from '../core/types';

export function initializeInsightsForm(): void {
  console.log('[InsightsForm] Initializing insights form...');

  // Initialize form validation
  const formValidation = new FormValidation('#insights-form');

  // Initialize usage limit checking
  initializeUsageLimitCheck();

  // Initialize form submission
  initializeFormSubmission(formValidation);

  console.log('[InsightsForm] Insights form initialized');
}

/**
 * Initialize usage limit checking
 */
async function initializeUsageLimitCheck(): Promise<void> {
  try {
    const stats = await API.get<UsageStats>('/api/usage-stats');

    // Check if user has reached limit
    const limits = stats.plan_limits;
    const monthlyUsage = stats.monthly.insights_generated;

    if (limits.monthly_insights && monthlyUsage >= limits.monthly_insights) {
      showFlashMessage(
        'You have reached your monthly insights limit. Please upgrade your plan.',
        'warning'
      );

      // Disable form
      const submitButton = document.querySelector('#insights-form button[type="submit"]');
      if (submitButton) {
        (submitButton as HTMLButtonElement).disabled = true;
      }
    }
  } catch (error) {
    console.error('[InsightsForm] Failed to check usage limits:', error);
  }
}

/**
 * Initialize form submission
 */
function initializeFormSubmission(formValidation: FormValidation): void {
  const form = document.querySelector('#insights-form') as HTMLFormElement;
  if (!form) return;

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    // Validate form
    if (!formValidation.validate()) {
      return;
    }

    const submitButton = form.querySelector('button[type="submit"]') as HTMLButtonElement;
    if (!submitButton) return;

    // Show loading state
    showLoading(submitButton, 'Generating Insights...');
    formValidation.disableSubmission();

    try {
      const formData = new FormData(form);
      const data = Object.fromEntries(formData.entries());

      // Submit to backend
      await API.post('/api/insights/generate', data);

      // Success - redirect to insights page
      showFlashMessage('Insights generated successfully!', 'success');
      setTimeout(() => {
        window.location.href = '/insights';
      }, 1000);
    } catch (error) {
      hideLoading(submitButton);
      formValidation.enableSubmission();

      showFlashMessage(
        'Failed to generate insights. Please try again.',
        'error'
      );
      console.error('[InsightsForm] Form submission error:', error);
    }
  });
}
