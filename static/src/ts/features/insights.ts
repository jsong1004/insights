/**
 * Insights Page Feature Module
 * Handles insights display page functionality
 */

import { copyToClipboard, showFlashMessage, scrollToElement } from '../core/utils';

export function initializeInsights(): void {
  console.log('[Insights] Initializing insights page...');

  // Initialize read more/less toggles
  initializeReadMore();

  // Initialize copy to clipboard
  initializeCopyToClipboard();

  // Initialize smooth scrolling
  initializeSmoothScrolling();

  // Initialize print styles
  initializePrintStyles();

  console.log('[Insights] Insights page initialized');
}

/**
 * Initialize read more/less functionality
 */
function initializeReadMore(): void {
  const readMoreButtons = document.querySelectorAll('.read-more-btn');

  readMoreButtons.forEach((button) => {
    button.addEventListener('click', function (this: HTMLElement) {
      const targetId = this.dataset.target;
      if (!targetId) return;

      const content = document.getElementById(targetId);
      if (!content) return;

      const isCollapsed = content.classList.contains('collapsed');

      if (isCollapsed) {
        content.classList.remove('collapsed');
        content.classList.add('expanded');
        this.textContent = 'Read Less';
      } else {
        content.classList.remove('expanded');
        content.classList.add('collapsed');
        this.textContent = 'Read More';
      }
    });
  });
}

/**
 * Initialize copy to clipboard for sources
 */
function initializeCopyToClipboard(): void {
  const sourceLinks = document.querySelectorAll('.source-link');

  sourceLinks.forEach((link) => {
    const anchorLink = link as HTMLAnchorElement;
    anchorLink.addEventListener('click', async (e: MouseEvent) => {
      // Ctrl+Click to copy
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();

        const url = anchorLink.href;
        const success = await copyToClipboard(url);

        if (success) {
          showFlashMessage('URL copied to clipboard!', 'success', 2000);
        } else {
          showFlashMessage('Failed to copy URL', 'error', 2000);
        }
      }
    });
  });
}

/**
 * Initialize smooth scrolling for anchor links
 */
function initializeSmoothScrolling(): void {
  const anchorLinks = document.querySelectorAll('a[href^="#"]');

  anchorLinks.forEach((link) => {
    link.addEventListener('click', function (this: HTMLAnchorElement, e) {
      e.preventDefault();

      const targetId = this.getAttribute('href');
      if (targetId && targetId !== '#') {
        scrollToElement(targetId, -80); // 80px offset for header
      }
    });
  });
}

/**
 * Initialize print styles
 */
function initializePrintStyles(): void {
  // Inject print styles dynamically
  const printStyles = `
    @media print {
      .no-print {
        display: none !important;
      }

      .insight-card {
        page-break-inside: avoid;
      }

      .source-item {
        page-break-inside: avoid;
      }

      a[href]:after {
        content: " (" attr(href) ")";
        font-size: 0.8em;
        color: #666;
      }
    }
  `;

  const styleElement = document.createElement('style');
  styleElement.textContent = printStyles;
  document.head.appendChild(styleElement);
}
