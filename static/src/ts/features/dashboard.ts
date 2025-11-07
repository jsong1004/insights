/**
 * Dashboard Page Feature Module
 * Handles dashboard functionality including usage stats, charts, and insights table
 */

import { API } from '../core/api';
import type { UsageStats, TableSortState } from '../core/types';

export function initializeDashboard(): void {
  console.log('[Dashboard] Initializing dashboard page...');

  // Initialize usage statistics display
  initializeUsageStats();

  // Initialize insights table
  initializeInsightsTable();

  // Initialize table sorting
  initializeTableSorting();

  console.log('[Dashboard] Dashboard page initialized');
}

/**
 * Initialize usage statistics display
 */
async function initializeUsageStats(): Promise<void> {
  try {
    const stats = await API.get<UsageStats>('/api/usage-stats');

    // Update UI with stats (implementation to be completed)
    console.log('[Dashboard] Usage stats loaded:', stats);

    // TODO: Update progress bars, charts, etc.
  } catch (error) {
    console.error('[Dashboard] Failed to load usage stats:', error);
  }
}

/**
 * Initialize insights table
 */
function initializeInsightsTable(): void {
  // TODO: Implement insights table initialization
  console.log('[Dashboard] Insights table initialized');
}

/**
 * Initialize table sorting
 */
function initializeTableSorting(): void {
  const sortableHeaders = document.querySelectorAll('th[data-sortable]');
  let sortState: TableSortState = { column: 'date', direction: 'desc' };

  sortableHeaders.forEach((header) => {
    header.addEventListener('click', function (this: HTMLTableCellElement) {
      const column = this.dataset.column;
      if (!column) return;

      // Toggle sort direction
      if (sortState.column === column) {
        sortState.direction = sortState.direction === 'asc' ? 'desc' : 'asc';
      } else {
        sortState = { column, direction: 'asc' };
      }

      // TODO: Sort table rows
      console.log('[Dashboard] Sorting by:', sortState);
    });
  });
}
