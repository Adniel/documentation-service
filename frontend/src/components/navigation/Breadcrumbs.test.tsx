/**
 * Tests for Breadcrumbs component (Sprint 3)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { render, testData } from '../../test/utils';
import { Breadcrumbs } from './Breadcrumbs';

// Mock the API
vi.mock('../../lib/api', () => ({
  navigationApi: {
    getPageBreadcrumbs: vi.fn(),
    getSpaceBreadcrumbs: vi.fn(),
  },
}));

import { navigationApi } from '../../lib/api';

describe('Breadcrumbs', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render nothing when no pageId or spaceId provided', () => {
    const { container } = render(<Breadcrumbs />);
    expect(container.firstChild).toBeNull();
  });

  it('should show loading state initially', () => {
    vi.mocked(navigationApi.getPageBreadcrumbs).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<Breadcrumbs pageId="page-123" />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('should render breadcrumbs for a page', async () => {
    vi.mocked(navigationApi.getPageBreadcrumbs).mockResolvedValue(testData.breadcrumbs);

    render(<Breadcrumbs pageId="page-123" />);

    await waitFor(() => {
      expect(screen.getByText('Test Org')).toBeInTheDocument();
    });

    expect(screen.getByText('Test Workspace')).toBeInTheDocument();
    expect(screen.getByText('Test Space')).toBeInTheDocument();
    expect(screen.getByText('Test Page')).toBeInTheDocument();
  });

  it('should render breadcrumbs for a space', async () => {
    const spaceBreadcrumbs = testData.breadcrumbs.slice(0, 3);
    vi.mocked(navigationApi.getSpaceBreadcrumbs).mockResolvedValue(spaceBreadcrumbs);

    render(<Breadcrumbs spaceId="space-123" />);

    await waitFor(() => {
      expect(screen.getByText('Test Space')).toBeInTheDocument();
    });
  });

  it('should render navigation links for non-last items', async () => {
    vi.mocked(navigationApi.getPageBreadcrumbs).mockResolvedValue(testData.breadcrumbs);

    render(<Breadcrumbs pageId="page-123" />);

    await waitFor(() => {
      expect(screen.getByText('Test Org')).toBeInTheDocument();
    });

    // Non-last items should be links
    const orgLink = screen.getByText('Test Org').closest('a');
    expect(orgLink).toHaveAttribute('href', '/org/org-123');

    const wsLink = screen.getByText('Test Workspace').closest('a');
    expect(wsLink).toHaveAttribute('href', '/workspace/ws-123');
  });

  it('should show last item as text (not link)', async () => {
    vi.mocked(navigationApi.getPageBreadcrumbs).mockResolvedValue(testData.breadcrumbs);

    render(<Breadcrumbs pageId="page-123" />);

    await waitFor(() => {
      expect(screen.getByText('Test Page')).toBeInTheDocument();
    });

    // Last item should not be a link
    const pageElement = screen.getByText('Test Page');
    expect(pageElement.closest('a')).toBeNull();
  });

  it('should render separators between items', async () => {
    vi.mocked(navigationApi.getPageBreadcrumbs).mockResolvedValue(testData.breadcrumbs);

    render(<Breadcrumbs pageId="page-123" />);

    await waitFor(() => {
      expect(screen.getByText('Test Org')).toBeInTheDocument();
    });

    // Should have separators
    const separators = screen.getAllByText('/');
    expect(separators.length).toBe(3); // 4 items = 3 separators
  });

  it('should render nothing for empty breadcrumbs', async () => {
    vi.mocked(navigationApi.getPageBreadcrumbs).mockResolvedValue([]);

    const { container } = render(<Breadcrumbs pageId="page-123" />);

    await waitFor(() => {
      expect(container.querySelector('nav')).toBeNull();
    });
  });

  it('should use correct icons for different types', async () => {
    vi.mocked(navigationApi.getPageBreadcrumbs).mockResolvedValue(testData.breadcrumbs);

    render(<Breadcrumbs pageId="page-123" />);

    await waitFor(() => {
      expect(screen.getByText('Test Org')).toBeInTheDocument();
    });

    // Check for type icons (these are emoji in the actual component)
    const nav = screen.getByRole('navigation');
    expect(nav.textContent).toContain('🏢'); // organization
    expect(nav.textContent).toContain('📂'); // workspace
    expect(nav.textContent).toContain('📁'); // space
    expect(nav.textContent).toContain('📄'); // page
  });
});
