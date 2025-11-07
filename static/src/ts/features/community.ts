/**
 * Community Page Feature Module
 * Handles community page functionality including toggles, sorting, keyboard shortcuts,
 * search, statistics, and admin features
 */

import { InsightsAPI } from '../core/api';
import { isAdmin } from '../core/auth';

export function initializeCommunity(): void {
  console.log('[Community] Initializing community page...');

  // Initialize toggle details functionality
  initializeToggleDetails();

  // Initialize keyboard shortcuts
  initializeKeyboardShortcuts();

  // Initialize table row interactions
  initializeTableRows();

  // Initialize search functionality
  initializeSearch();

  // Initialize community stats
  initializeCommunityStats();

  // Initialize admin features (if admin)
  if (isAdmin()) {
    initializeAdminFeatures();
  }

  console.log('[Community] Community page initialized');
}

/**
 * Initialize toggle details buttons
 */
function initializeToggleDetails(): void {
  const toggleButtons = document.querySelectorAll('.toggle-details');

  toggleButtons.forEach((button) => {
    button.addEventListener('click', function (this: HTMLElement) {
      const targetId = this.dataset.target;
      if (!targetId) return;

      const targetElement = document.getElementById(targetId);
      if (!targetElement) return;

      const isHidden = targetElement.classList.contains('d-none');

      if (isHidden) {
        targetElement.classList.remove('d-none');
        this.textContent = 'Hide Details';
        this.setAttribute('aria-expanded', 'true');
      } else {
        targetElement.classList.add('d-none');
        this.textContent = 'View Details';
        this.setAttribute('aria-expanded', 'false');
      }
    });
  });
}

/**
 * Initialize keyboard shortcuts
 */
function initializeKeyboardShortcuts(): void {
  document.addEventListener('keydown', (e) => {
    // Refresh on 'r' key
    if (e.key === 'r' && !e.ctrlKey && !e.metaKey && !e.altKey) {
      // Make sure we're not in an input field
      const target = e.target as HTMLElement;
      if (
        target.tagName !== 'INPUT' &&
        target.tagName !== 'TEXTAREA' &&
        !target.isContentEditable
      ) {
        e.preventDefault();
        window.location.reload();
      }
    }
  });
}

/**
 * Initialize table row interactions
 */
function initializeTableRows(): void {
  const tableRows = document.querySelectorAll('.community-table tbody tr');

  tableRows.forEach((row) => {
    const tr = row as HTMLTableRowElement;

    // Add hover effect
    tr.addEventListener('mouseenter', function (this: HTMLTableRowElement) {
      this.style.backgroundColor = 'rgba(0, 0, 0, 0.02)';
    });

    tr.addEventListener('mouseleave', function (this: HTMLTableRowElement) {
      this.style.backgroundColor = '';
    });

    // Make row clickable (expand details)
    tr.addEventListener('click', function (this: HTMLTableRowElement, e) {
      // Don't trigger if clicking on buttons or links
      const target = e.target as HTMLElement;
      if (
        target.tagName === 'BUTTON' ||
        target.tagName === 'A' ||
        target.closest('button') ||
        target.closest('a')
      ) {
        return;
      }

      // Find and click the toggle button
      const toggleButton = this.querySelector('.toggle-details') as HTMLElement;
      if (toggleButton) {
        toggleButton.click();
      }
    });
  });
}

/**
 * Initialize search functionality
 */
function initializeSearch(): void {
  const searchInput = document.querySelector(
    '.community-search-input'
  ) as HTMLInputElement;
  const searchButton = document.querySelector('.community-search-button');
  const clearButton = document.querySelector('.community-search-clear');

  if (!searchInput) return;

  // Search on button click
  if (searchButton) {
    searchButton.addEventListener('click', () => {
      performSearch(searchInput.value);
    });
  }

  // Search on Enter key
  searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      performSearch(searchInput.value);
    }
  });

  // Clear search
  if (clearButton) {
    clearButton.addEventListener('click', () => {
      searchInput.value = '';
      performSearch('');
    });
  }
}

/**
 * Perform search and update URL
 */
function performSearch(query: string): void {
  const url = new URL(window.location.href);
  const currentSort = url.searchParams.get('sort') || 'recent';

  if (query.trim()) {
    url.searchParams.set('q', query.trim());
  } else {
    url.searchParams.delete('q');
  }

  url.searchParams.set('sort', currentSort);
  url.searchParams.delete('page'); // Reset to page 1

  window.location.href = url.toString();
}

/**
 * Initialize community statistics display
 */
async function initializeCommunityStats(): Promise<void> {
  const statsContainer = document.querySelector('.community-stats-container');

  if (!statsContainer) return;

  try {
    const stats = await InsightsAPI.getCommunityStats();

    // Update stats display if elements exist
    updateStatElement('.stat-total-insights', stats.total_insights);
    updateStatElement('.stat-total-likes', stats.total_likes);
    updateStatElement('.stat-total-authors', stats.total_authors);

    // Update trending topics if container exists
    const trendingContainer = document.querySelector('.trending-topics-list');
    if (trendingContainer && stats.trending_topics) {
      displayTrendingTopics(trendingContainer, stats.trending_topics);
    }
  } catch (error) {
    console.error('[Community] Failed to load community stats:', error);
  }
}

/**
 * Update a stat element with formatted number
 */
function updateStatElement(selector: string, value: number): void {
  const element = document.querySelector(selector);
  if (element) {
    element.textContent = value.toLocaleString();
  }
}

/**
 * Display trending topics list
 */
function displayTrendingTopics(container: Element, topics: any[]): void {
  if (!topics || topics.length === 0) {
    container.innerHTML = '<p class="text-muted">No trending topics yet</p>';
    return;
  }

  const html = topics
    .slice(0, 5)
    .map(
      (topic, index) => `
    <div class="trending-topic-item">
      <span class="trending-rank">${index + 1}</span>
      <a href="?q=${encodeURIComponent(topic.topic)}" class="trending-topic-link">
        ${topic.topic}
      </a>
      <span class="trending-count badge bg-secondary">${topic.count}</span>
    </div>
  `
    )
    .join('');

  container.innerHTML = html;
}

/**
 * Initialize admin features (pin buttons, etc.)
 */
function initializeAdminFeatures(): void {
  console.log('[Community] Initializing admin features...');

  // Pin buttons are handled by SocialInteractions component
  // Add any additional admin-specific functionality here

  // Show admin controls
  const adminControls = document.querySelectorAll('.admin-only');
  adminControls.forEach((control) => {
    (control as HTMLElement).style.display = 'block';
  });
}
