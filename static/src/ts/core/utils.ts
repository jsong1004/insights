/**
 * Utility Functions Module
 * Shared utility functions used across the application
 */

import type { FlashMessage } from './types';

/**
 * Show a flash message to the user
 */
export function showFlashMessage(
  message: string,
  type: FlashMessage['type'] = 'info',
  duration: number = 5000
): void {
  // Try to use Bootstrap toast if available
  const toastContainer = document.querySelector('.toast-container');

  if (toastContainer) {
    const toastId = `toast-${Date.now()}`;
    const toastHTML = `
      <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            ${escapeHTML(message)}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
      </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);

    const toastElement = document.getElementById(toastId);
    if (toastElement && (window as any).bootstrap) {
      const toast = new (window as any).bootstrap.Toast(toastElement, {
        autohide: true,
        delay: duration,
      });
      toast.show();

      // Remove toast element after it's hidden
      toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
      });
    }
  } else {
    // Fallback to alert if Bootstrap toast is not available
    alert(message);
  }
}

/**
 * Escape HTML to prevent XSS
 */
export function escapeHTML(str: string): string {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/**
 * Show loading state on an element
 */
export function showLoading(
  element: HTMLElement,
  message: string = 'Loading...'
): void {
  element.classList.add('loading');
  element.setAttribute('disabled', 'disabled');

  // If it's a button, save original text and show spinner
  if (element.tagName === 'BUTTON') {
    const originalText = element.textContent || '';
    element.setAttribute('data-original-text', originalText);
    element.innerHTML = `
      <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
      ${escapeHTML(message)}
    `;
  }
}

/**
 * Hide loading state on an element
 */
export function hideLoading(element: HTMLElement): void {
  element.classList.remove('loading');
  element.removeAttribute('disabled');

  // If it's a button, restore original text
  if (element.tagName === 'BUTTON') {
    const originalText = element.getAttribute('data-original-text');
    if (originalText) {
      element.textContent = originalText;
      element.removeAttribute('data-original-text');
    }
  }
}

/**
 * Debounce a function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;

  return function (...args: Parameters<T>): void {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * Throttle a function
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false;

  return function (...args: Parameters<T>): void {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Format a date string
 */
export function formatDate(
  dateString: string,
  options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }
): string {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, options);
  } catch {
    return dateString;
  }
}

/**
 * Format a number with commas
 */
export function formatNumber(num: number): string {
  return num.toLocaleString();
}

/**
 * Copy text to clipboard
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
        return true;
      } catch {
        return false;
      } finally {
        document.body.removeChild(textArea);
      }
    }
  } catch {
    return false;
  }
}

/**
 * Smooth scroll to element
 */
export function scrollToElement(
  selector: string,
  offset: number = 0
): void {
  const element = document.querySelector(selector);
  if (element) {
    const top = element.getBoundingClientRect().top + window.pageYOffset + offset;
    window.scrollTo({ top, behavior: 'smooth' });
  }
}

/**
 * Get query parameter from URL
 */
export function getQueryParam(param: string): string | null {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}

/**
 * Set query parameter in URL
 */
export function setQueryParam(param: string, value: string): void {
  const url = new URL(window.location.href);
  url.searchParams.set(param, value);
  window.history.pushState({}, '', url.toString());
}

/**
 * Remove query parameter from URL
 */
export function removeQueryParam(param: string): void {
  const url = new URL(window.location.href);
  url.searchParams.delete(param);
  window.history.pushState({}, '', url.toString());
}

/**
 * Check if element is in viewport
 */
export function isInViewport(element: HTMLElement): boolean {
  const rect = element.getBoundingClientRect();
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  );
}

/**
 * Wait for a specified time
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Generate a random ID
 */
export function generateId(prefix: string = 'id'): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Export utilities for global access (backward compatibility)
 */
if (typeof window !== 'undefined') {
  (window as any).showFlashMessage = showFlashMessage;
  (window as any).showLoading = showLoading;
  (window as any).hideLoading = hideLoading;
  (window as any).copyToClipboard = copyToClipboard;
  (window as any).formatDate = formatDate;
  (window as any).formatNumber = formatNumber;
}
