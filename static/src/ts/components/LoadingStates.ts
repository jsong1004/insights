/**
 * Loading States Component
 * Manages loading states for buttons and elements
 */

import { showLoading, hideLoading } from '../core/utils';

export class LoadingStates {
  private loadingElements: Map<HTMLElement, string>;

  constructor() {
    this.loadingElements = new Map();
    console.log('[LoadingStates] Component initialized');
  }

  /**
   * Show loading state on an element
   */
  public show(
    element: HTMLElement | string,
    message: string = 'Loading...'
  ): void {
    const el = typeof element === 'string'
      ? document.querySelector(element) as HTMLElement
      : element;

    if (!el) {
      console.warn('[LoadingStates] Element not found:', element);
      return;
    }

    // Store original state
    if (!this.loadingElements.has(el)) {
      this.loadingElements.set(el, el.innerHTML);
    }

    showLoading(el, message);
  }

  /**
   * Hide loading state on an element
   */
  public hide(element: HTMLElement | string): void {
    const el = typeof element === 'string'
      ? document.querySelector(element) as HTMLElement
      : element;

    if (!el) {
      console.warn('[LoadingStates] Element not found:', element);
      return;
    }

    hideLoading(el);

    // Clean up stored state
    this.loadingElements.delete(el);
  }

  /**
   * Toggle loading state
   */
  public toggle(element: HTMLElement | string, message?: string): void {
    const el = typeof element === 'string'
      ? document.querySelector(element) as HTMLElement
      : element;

    if (!el) {
      console.warn('[LoadingStates] Element not found:', element);
      return;
    }

    if (this.loadingElements.has(el)) {
      this.hide(el);
    } else {
      this.show(el, message);
    }
  }

  /**
   * Check if element is in loading state
   */
  public isLoading(element: HTMLElement | string): boolean {
    const el = typeof element === 'string'
      ? document.querySelector(element) as HTMLElement
      : element;

    return el ? this.loadingElements.has(el) : false;
  }

  /**
   * Hide all loading states
   */
  public hideAll(): void {
    this.loadingElements.forEach((_, element) => {
      this.hide(element);
    });
  }
}
