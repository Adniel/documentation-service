/**
 * Test utilities for rendering components with providers.
 */

import { ReactElement, ReactNode } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Create a new QueryClient for each test
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

interface AllProvidersProps {
  children: ReactNode;
}

function AllProviders({ children }: AllProvidersProps) {
  const queryClient = createTestQueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  );
}

function customRender(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return render(ui, { wrapper: AllProviders, ...options });
}

// Re-export everything
export * from '@testing-library/react';
export { customRender as render };

// Helper to create mock API responses
export function mockApiResponse<T>(data: T, delay = 0): Promise<T> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(data), delay);
  });
}

// Helper to create mock error response
export function mockApiError(message: string, status = 500): Promise<never> {
  return Promise.reject({
    response: {
      status,
      data: { detail: message },
    },
  });
}

// Sample test data
export const testData = {
  user: {
    id: 'user-123',
    email: 'test@example.com',
    full_name: 'Test User',
    title: 'Developer',
    is_active: true,
    email_verified: true,
    clearance_level: 2,
    avatar_url: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-15T00:00:00Z',
  },

  organization: {
    id: 'org-123',
    name: 'Test Organization',
    slug: 'test-org',
    description: 'A test organization',
    is_active: true,
    logo_url: null,
    owner_id: 'user-123',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-15T00:00:00Z',
  },

  workspace: {
    id: 'ws-123',
    name: 'Test Workspace',
    slug: 'test-workspace',
    description: 'A test workspace',
    organization_id: 'org-123',
    is_active: true,
    is_public: false,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-15T00:00:00Z',
  },

  space: {
    id: 'space-123',
    name: 'Test Space',
    slug: 'test-space',
    description: 'A test space',
    workspace_id: 'ws-123',
    parent_id: null,
    diataxis_type: 'tutorial' as const,
    classification: 0,
    sort_order: 0,
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-15T00:00:00Z',
  },

  page: {
    id: 'page-123',
    title: 'Test Page',
    slug: 'test-page',
    space_id: 'space-123',
    author_id: 'user-123',
    parent_id: null,
    document_number: 'DOC-001',
    version: '1.0',
    status: 'draft' as const,
    classification: 0,
    content: {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'Hello, world!' }],
        },
      ],
    },
    summary: 'A test page',
    git_path: null,
    git_commit_sha: null,
    is_active: true,
    is_template: false,
    sort_order: 0,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-15T00:00:00Z',
  },

  breadcrumbs: [
    { type: 'organization' as const, id: 'org-123', name: 'Test Org', slug: 'test-org' },
    { type: 'workspace' as const, id: 'ws-123', name: 'Test Workspace', slug: 'test-ws' },
    { type: 'space' as const, id: 'space-123', name: 'Test Space', slug: 'test-space' },
    { type: 'page' as const, id: 'page-123', name: 'Test Page', slug: 'test-page' },
  ],
};
