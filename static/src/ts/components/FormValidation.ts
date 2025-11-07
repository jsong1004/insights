/**
 * Form Validation Component
 * Handles form validation, character counters, and submission protection
 */

import { debounce } from '../core/utils';

export class FormValidation {
  private form: HTMLFormElement;
  private isSubmitting: boolean = false;
  private characterCounters: Map<HTMLElement, HTMLElement> = new Map();

  constructor(formSelector: string) {
    const form = document.querySelector(formSelector) as HTMLFormElement;
    if (!form) {
      throw new Error(`Form not found: ${formSelector}`);
    }

    this.form = form;
    this.initialize();

    console.log('[FormValidation] Component initialized for:', formSelector);
  }

  /**
   * Initialize form validation
   */
  private initialize(): void {
    // Set up character counters
    this.setupCharacterCounters();

    // Set up auto-resize textareas
    this.setupAutoResize();

    // Prevent double submission
    this.form.addEventListener('submit', (e) => {
      if (this.isSubmitting) {
        e.preventDefault();
        return;
      }

      // Validate form before submission
      if (!this.validate()) {
        e.preventDefault();
        return;
      }

      this.isSubmitting = true;
    });
  }

  /**
   * Set up character counters for inputs and textareas
   */
  private setupCharacterCounters(): void {
    const elements = this.form.querySelectorAll('[data-max-length]');

    elements.forEach((element) => {
      const input = element as HTMLInputElement | HTMLTextAreaElement;
      const maxLength = parseInt(input.dataset.maxLength || '0', 10);

      if (maxLength > 0) {
        // Create counter element
        const counter = this.createCounter(input);
        this.characterCounters.set(input, counter);

        // Update counter on input
        input.addEventListener('input', debounce(() => {
          this.updateCounter(input, counter, maxLength);
        }, 100));

        // Initial update
        this.updateCounter(input, counter, maxLength);
      }
    });
  }

  /**
   * Create a character counter element
   */
  private createCounter(
    input: HTMLInputElement | HTMLTextAreaElement
  ): HTMLElement {
    const counter = document.createElement('div');
    counter.className = 'character-counter text-muted small mt-1';
    counter.setAttribute('aria-live', 'polite');

    // Insert after the input
    input.parentElement?.insertBefore(counter, input.nextSibling);

    return counter;
  }

  /**
   * Update character counter
   */
  private updateCounter(
    input: HTMLInputElement | HTMLTextAreaElement,
    counter: HTMLElement,
    maxLength: number
  ): void {
    const length = input.value.length;
    const remaining = maxLength - length;

    counter.textContent = `${length} / ${maxLength} characters`;

    // Warn when approaching limit
    if (remaining <= 20) {
      counter.classList.add('text-warning');
      counter.classList.remove('text-muted');
    } else if (remaining <= 0) {
      counter.classList.add('text-danger');
      counter.classList.remove('text-warning', 'text-muted');
    } else {
      counter.classList.add('text-muted');
      counter.classList.remove('text-warning', 'text-danger');
    }
  }

  /**
   * Set up auto-resize for textareas
   */
  private setupAutoResize(): void {
    const textareas = this.form.querySelectorAll('textarea[data-auto-resize]');

    textareas.forEach((textarea) => {
      const element = textarea as HTMLTextAreaElement;

      const resize = () => {
        element.style.height = 'auto';
        element.style.height = `${element.scrollHeight}px`;
      };

      element.addEventListener('input', debounce(resize, 100));

      // Initial resize
      resize();
    });
  }

  /**
   * Validate form
   */
  public validate(): boolean {
    // Check HTML5 validation
    if (!this.form.checkValidity()) {
      this.form.reportValidity();
      return false;
    }

    let isValid = true;

    // Check custom validations
    const elements = this.form.querySelectorAll('[data-max-length]');
    elements.forEach((element) => {
      const input = element as HTMLInputElement | HTMLTextAreaElement;
      const maxLength = parseInt(input.dataset.maxLength || '0', 10);

      if (input.value.length > maxLength) {
        isValid = false;
        input.setCustomValidity(`Maximum length is ${maxLength} characters`);
        input.reportValidity();
      } else {
        input.setCustomValidity('');
      }
    });

    return isValid;
  }

  /**
   * Reset form and submission state
   */
  public reset(): void {
    this.form.reset();
    this.isSubmitting = false;

    // Update all counters
    this.characterCounters.forEach((counter, input) => {
      const maxLength = parseInt(input.dataset.maxLength || '0', 10);
      this.updateCounter(input as HTMLInputElement | HTMLTextAreaElement, counter, maxLength);
    });
  }

  /**
   * Enable form submission
   */
  public enableSubmission(): void {
    this.isSubmitting = false;
  }

  /**
   * Disable form submission
   */
  public disableSubmission(): void {
    this.isSubmitting = true;
  }
}
