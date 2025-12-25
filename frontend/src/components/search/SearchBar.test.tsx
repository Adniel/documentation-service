/**
 * Tests for SearchBar component (Sprint 3)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '../../test/utils';
import { SearchBar } from './SearchBar';

// Mock the API
vi.mock('../../lib/api', () => ({
  searchApi: {
    getSuggestions: vi.fn(),
  },
}));

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

import { searchApi } from '../../lib/api';

describe('SearchBar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(searchApi.getSuggestions).mockResolvedValue([]);
  });

  it('should render with default placeholder', () => {
    render(<SearchBar />);

    expect(screen.getByPlaceholderText('Search documentation...')).toBeInTheDocument();
  });

  it('should render with custom placeholder', () => {
    render(<SearchBar placeholder="Find pages..." />);

    expect(screen.getByPlaceholderText('Find pages...')).toBeInTheDocument();
  });

  it('should show clear button when input has value', async () => {
    const user = userEvent.setup();
    render(<SearchBar />);

    const input = screen.getByPlaceholderText('Search documentation...');
    await user.type(input, 'test');

    expect(screen.getByText('✕')).toBeInTheDocument();
  });

  it('should clear input when clear button clicked', async () => {
    const user = userEvent.setup();
    render(<SearchBar />);

    const input = screen.getByPlaceholderText('Search documentation...');
    await user.type(input, 'test query');

    const clearButton = screen.getByText('✕');
    await user.click(clearButton);

    expect(input).toHaveValue('');
  });

  it('should not show suggestions for short queries', async () => {
    const user = userEvent.setup();
    render(<SearchBar />);

    const input = screen.getByPlaceholderText('Search documentation...');
    await user.type(input, 'a');

    expect(searchApi.getSuggestions).not.toHaveBeenCalled();
  });

  it('should fetch suggestions for queries >= 2 chars', async () => {
    const user = userEvent.setup();
    vi.mocked(searchApi.getSuggestions).mockResolvedValue([
      { type: 'page', id: 'p1', title: 'Test Page', description: 'A page' },
    ]);

    render(<SearchBar />);

    const input = screen.getByPlaceholderText('Search documentation...');
    await user.type(input, 'te');

    await waitFor(() => {
      expect(searchApi.getSuggestions).toHaveBeenCalledWith('te', 5);
    });
  });

  it('should display suggestions dropdown', async () => {
    const user = userEvent.setup();
    vi.mocked(searchApi.getSuggestions).mockResolvedValue([
      { type: 'page', id: 'p1', title: 'Getting Started', description: 'Start here' },
      { type: 'space', id: 's1', title: 'Tutorials', description: 'Learn more' },
    ]);

    render(<SearchBar />);

    const input = screen.getByPlaceholderText('Search documentation...');
    await user.type(input, 'test');

    await waitFor(() => {
      expect(screen.getByText('Getting Started')).toBeInTheDocument();
      expect(screen.getByText('Tutorials')).toBeInTheDocument();
    });
  });

  it('should show page icon for page suggestions', async () => {
    const user = userEvent.setup();
    vi.mocked(searchApi.getSuggestions).mockResolvedValue([
      { type: 'page', id: 'p1', title: 'Test Page' },
    ]);

    render(<SearchBar />);

    const input = screen.getByPlaceholderText('Search documentation...');
    await user.type(input, 'test');

    await waitFor(() => {
      expect(screen.getByText('📄')).toBeInTheDocument();
    });
  });

  it('should show space icon for space suggestions', async () => {
    const user = userEvent.setup();
    vi.mocked(searchApi.getSuggestions).mockResolvedValue([
      { type: 'space', id: 's1', title: 'Test Space' },
    ]);

    render(<SearchBar />);

    const input = screen.getByPlaceholderText('Search documentation...');
    await user.type(input, 'test');

    await waitFor(() => {
      expect(screen.getByText('📁')).toBeInTheDocument();
    });
  });

  it('should navigate to page on suggestion click', async () => {
    const user = userEvent.setup();
    vi.mocked(searchApi.getSuggestions).mockResolvedValue([
      { type: 'page', id: 'page-123', title: 'Test Page' },
    ]);

    render(<SearchBar />);

    const input = screen.getByPlaceholderText('Search documentation...');
    await user.type(input, 'test');

    await waitFor(() => {
      expect(screen.getByText('Test Page')).toBeInTheDocument();
    });

    await user.click(screen.getByText('Test Page'));

    expect(mockNavigate).toHaveBeenCalledWith('/editor/page-123');
  });

  it('should navigate to space on suggestion click', async () => {
    const user = userEvent.setup();
    vi.mocked(searchApi.getSuggestions).mockResolvedValue([
      { type: 'space', id: 'space-123', title: 'Test Space' },
    ]);

    render(<SearchBar />);

    const input = screen.getByPlaceholderText('Search documentation...');
    await user.type(input, 'test');

    await waitFor(() => {
      expect(screen.getByText('Test Space')).toBeInTheDocument();
    });

    await user.click(screen.getByText('Test Space'));

    expect(mockNavigate).toHaveBeenCalledWith('/space/space-123');
  });

  it('should navigate to search results on Enter', async () => {
    const user = userEvent.setup();
    render(<SearchBar workspaceId="ws-123" />);

    const input = screen.getByPlaceholderText('Search documentation...');
    await user.type(input, 'my query{enter}');

    expect(mockNavigate).toHaveBeenCalledWith('/search?q=my%20query&workspace=ws-123');
  });

  it('should call onSearch callback if provided', async () => {
    const user = userEvent.setup();
    const onSearch = vi.fn();

    render(<SearchBar onSearch={onSearch} />);

    const input = screen.getByPlaceholderText('Search documentation...');
    await user.type(input, 'test query{enter}');

    expect(onSearch).toHaveBeenCalledWith('test query');
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('should close dropdown on Escape', async () => {
    const user = userEvent.setup();
    vi.mocked(searchApi.getSuggestions).mockResolvedValue([
      { type: 'page', id: 'p1', title: 'Test Page' },
    ]);

    render(<SearchBar />);

    const input = screen.getByPlaceholderText('Search documentation...');
    await user.type(input, 'test');

    await waitFor(() => {
      expect(screen.getByText('Test Page')).toBeInTheDocument();
    });

    await user.keyboard('{Escape}');

    await waitFor(() => {
      expect(screen.queryByText('Test Page')).not.toBeInTheDocument();
    });
  });

  it('should support keyboard navigation in suggestions', async () => {
    const user = userEvent.setup();
    vi.mocked(searchApi.getSuggestions).mockResolvedValue([
      { type: 'page', id: 'p1', title: 'First Page' },
      { type: 'page', id: 'p2', title: 'Second Page' },
    ]);

    render(<SearchBar />);

    const input = screen.getByPlaceholderText('Search documentation...');
    await user.type(input, 'test');

    await waitFor(() => {
      expect(screen.getByText('First Page')).toBeInTheDocument();
    });

    // Press down arrow to select first item
    await user.keyboard('{ArrowDown}');

    // Press Enter to navigate
    await user.keyboard('{Enter}');

    expect(mockNavigate).toHaveBeenCalledWith('/editor/p1');
  });

  it('should show no results message', async () => {
    const user = userEvent.setup();
    vi.mocked(searchApi.getSuggestions).mockResolvedValue([]);

    render(<SearchBar />);

    const input = screen.getByPlaceholderText('Search documentation...');
    await user.type(input, 'nonexistent');

    await waitFor(() => {
      expect(screen.getByText(/No results found/)).toBeInTheDocument();
    });
  });
});
