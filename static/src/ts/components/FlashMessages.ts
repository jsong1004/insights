/**
 * Flash Messages Component
 * Manages toast notifications and flash messages
 */

import { showFlashMessage } from '../core/utils';
import type { FlashMessage } from '../core/types';

export class FlashMessages {
  private container: HTMLElement | null;

  constructor(containerId: string = 'flash-messages') {
    // Find or create toast container
    this.container = document.getElementById(containerId);

    if (!this.container) {
      this.container = this.createContainer(containerId);
    }

    // Initialize any server-rendered flash messages
    this.initializeServerMessages();

    console.log('[FlashMessages] Component initialized');
  }

  /**
   * Create toast container if it doesn't exist
   */
  private createContainer(id: string): HTMLElement {
    const container = document.createElement('div');
    container.id = id;
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
  }

  /**
   * Initialize server-rendered flash messages
   */
  private initializeServerMessages(): void {
    const flashContainer = document.querySelector('.flash-messages');
    if (!flashContainer) return;

    const messages = flashContainer.querySelectorAll('.alert');
    messages.forEach((alert) => {
      const message = alert.textContent?.trim() || '';
      const type = this.extractTypeFromClass(alert.className);

      if (message) {
        this.show(message, type);
      }

      // Remove the server-rendered message
      alert.remove();
    });

    // Remove the container if empty
    if (flashContainer.children.length === 0) {
      flashContainer.remove();
    }
  }

  /**
   * Extract message type from Bootstrap alert class
   */
  private extractTypeFromClass(className: string): FlashMessage['type'] {
    if (className.includes('alert-success')) return 'success';
    if (className.includes('alert-danger') || className.includes('alert-error'))
      return 'error';
    if (className.includes('alert-warning')) return 'warning';
    return 'info';
  }

  /**
   * Show a flash message
   */
  public show(
    message: string,
    type: FlashMessage['type'] = 'info',
    duration: number = 5000
  ): void {
    showFlashMessage(message, type, duration);
  }

  /**
   * Show success message
   */
  public success(message: string, duration?: number): void {
    this.show(message, 'success', duration);
  }

  /**
   * Show error message
   */
  public error(message: string, duration?: number): void {
    this.show(message, 'error', duration);
  }

  /**
   * Show warning message
   */
  public warning(message: string, duration?: number): void {
    this.show(message, 'warning', duration);
  }

  /**
   * Show info message
   */
  public info(message: string, duration?: number): void {
    this.show(message, 'info', duration);
  }
}
