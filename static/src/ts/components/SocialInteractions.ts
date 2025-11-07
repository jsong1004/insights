/**
 * Social Interactions Component
 * Handles likes, sharing toggles, and other social features
 */

import { API, APIException, InsightsAPI } from '../core/api';
import { showFlashMessage } from '../core/utils';
import { isAdmin } from '../core/auth';

export class SocialInteractions {
  constructor() {
    this.initializeLikeButtons();
    this.initializeShareToggles();
    this.initializePinButtons();

    console.log('[SocialInteractions] Component initialized');
  }

  /**
   * Initialize like buttons
   */
  private initializeLikeButtons(): void {
    const likeButtons = document.querySelectorAll('.like-button');

    likeButtons.forEach((button) => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();

        const btn = button as HTMLElement;
        const insightId = btn.dataset.insightId;

        if (insightId) {
          this.toggleLike(btn, insightId);
        }
      });
    });
  }

  /**
   * Initialize share toggles
   */
  private initializeShareToggles(): void {
    const shareToggles = document.querySelectorAll('.share-toggle');

    shareToggles.forEach((toggle) => {
      toggle.addEventListener('change', (e) => {
        const checkbox = e.target as HTMLInputElement;
        const insightId = checkbox.dataset.insightId;

        if (insightId) {
          this.toggleShare(checkbox, insightId);
        }
      });
    });
  }

  /**
   * Toggle like for an insight
   */
  private async toggleLike(button: HTMLElement, insightId: string): Promise<void> {
    // Prevent double-clicking
    if (button.classList.contains('processing')) return;

    button.classList.add('processing');

    try {
      const response = await API.post<{
        liked: boolean;
        likes_count: number;
      }>(`/api/insights/${insightId}/like`, {});

      // Update button state
      const icon = button.querySelector('.fa-heart');
      const countElement = button.querySelector('.likes-count');

      if (icon) {
        if (response.liked) {
          icon.classList.remove('fa-regular');
          icon.classList.add('fa-solid', 'text-danger');
        } else {
          icon.classList.remove('fa-solid', 'text-danger');
          icon.classList.add('fa-regular');
        }
      }

      if (countElement) {
        countElement.textContent = response.likes_count.toString();
      }

      // Update aria-label for accessibility
      button.setAttribute(
        'aria-label',
        response.liked ? 'Unlike this insight' : 'Like this insight'
      );
    } catch (error) {
      if (error instanceof APIException) {
        showFlashMessage(error.message, 'error');
      } else {
        showFlashMessage('Failed to update like. Please try again.', 'error');
      }
      console.error('[SocialInteractions] Like error:', error);
    } finally {
      button.classList.remove('processing');
    }
  }

  /**
   * Toggle share status for an insight
   */
  private async toggleShare(
    checkbox: HTMLInputElement,
    insightId: string
  ): Promise<void> {
    const originalValue = checkbox.checked;

    try {
      const response = await API.post<{
        is_shared: boolean;
      }>(`/api/insights/${insightId}/share`, {
        is_shared: checkbox.checked,
      });

      checkbox.checked = response.is_shared;

      showFlashMessage(
        response.is_shared
          ? 'Insight is now shared publicly'
          : 'Insight is now private',
        'success'
      );
    } catch (error) {
      // Revert checkbox state on error
      checkbox.checked = originalValue;

      if (error instanceof APIException) {
        showFlashMessage(error.message, 'error');
      } else {
        showFlashMessage('Failed to update sharing. Please try again.', 'error');
      }
      console.error('[SocialInteractions] Share error:', error);
    }
  }

  /**
   * Initialize pin buttons (admin only)
   */
  private initializePinButtons(): void {
    // Only initialize if user is admin
    if (!isAdmin()) return;

    const pinButtons = document.querySelectorAll('.pin-button');

    pinButtons.forEach((button) => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();

        const btn = button as HTMLElement;
        const insightId = btn.dataset.insightId;
        const isPinned = btn.dataset.isPinned === 'true';

        if (insightId) {
          this.togglePin(btn, insightId, isPinned);
        }
      });
    });
  }

  /**
   * Toggle pin status for an insight (admin only)
   */
  private async togglePin(
    button: HTMLElement,
    insightId: string,
    currentlyPinned: boolean
  ): Promise<void> {
    // Prevent double-clicking
    if (button.classList.contains('processing')) return;

    button.classList.add('processing');
    (button as HTMLButtonElement).disabled = true;

    try {
      const response = await InsightsAPI.pinInsight(insightId, !currentlyPinned);

      // Update button state
      const icon = button.querySelector('i');
      const textElement = button.querySelector('.pin-text');

      if (icon) {
        if (response.is_pinned) {
          icon.classList.remove('fa-regular');
          icon.classList.add('fa-solid');
          button.classList.remove('btn-outline-warning');
          button.classList.add('btn-warning');
        } else {
          icon.classList.remove('fa-solid');
          icon.classList.add('fa-regular');
          button.classList.remove('btn-warning');
          button.classList.add('btn-outline-warning');
        }
      }

      if (textElement) {
        textElement.textContent = response.is_pinned ? 'Unpin' : 'Pin';
      }

      // Update data attribute
      button.dataset.isPinned = response.is_pinned.toString();

      // Update aria-label for accessibility
      button.setAttribute(
        'aria-label',
        response.is_pinned ? 'Unpin this insight' : 'Pin this insight'
      );

      showFlashMessage(
        response.is_pinned
          ? 'Insight pinned successfully'
          : 'Insight unpinned successfully',
        'success'
      );
    } catch (error) {
      if (error instanceof APIException) {
        showFlashMessage(error.message, 'error');
      } else {
        showFlashMessage('Failed to update pin status. Please try again.', 'error');
      }
      console.error('[SocialInteractions] Pin error:', error);
    } finally {
      button.classList.remove('processing');
      (button as HTMLButtonElement).disabled = false;
    }
  }

  /**
   * Refresh like buttons (useful after dynamic content updates)
   */
  public refresh(): void {
    this.initializeLikeButtons();
    this.initializeShareToggles();
    this.initializePinButtons();
  }
}
