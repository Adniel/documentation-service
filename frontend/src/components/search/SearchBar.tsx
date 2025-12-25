/**
 * SearchBar Component with Autocomplete
 *
 * Provides full-text search with type-ahead suggestions.
 */

import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { searchApi, type SearchSuggestion } from '../../lib/api';
import { clsx } from 'clsx';

interface SearchBarProps {
  workspaceId?: string;
  placeholder?: string;
  onSearch?: (query: string) => void;
  className?: string;
}

export function SearchBar({
  workspaceId,
  placeholder = 'Search documentation...',
  onSearch,
  className,
}: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const { data: suggestions } = useQuery({
    queryKey: ['search-suggestions', query],
    queryFn: () => searchApi.getSuggestions(query, 5),
    enabled: query.length >= 2,
    staleTime: 1000,
  });

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Reset selection when suggestions change
  useEffect(() => {
    setSelectedIndex(-1);
  }, [suggestions]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        if (suggestions && suggestions.length > 0) {
          e.preventDefault();
          setSelectedIndex((prev) =>
            prev < suggestions.length - 1 ? prev + 1 : prev
          );
        }
        break;
      case 'ArrowUp':
        if (suggestions && suggestions.length > 0) {
          e.preventDefault();
          setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        }
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && suggestions && suggestions[selectedIndex]) {
          handleSuggestionClick(suggestions[selectedIndex]);
        } else if (query.trim()) {
          handleSearch();
        }
        break;
      case 'Escape':
        setIsOpen(false);
        inputRef.current?.blur();
        break;
    }
  };

  const handleSearch = () => {
    if (query.trim()) {
      setIsOpen(false);
      if (onSearch) {
        onSearch(query);
      } else {
        navigate(`/search?q=${encodeURIComponent(query)}&workspace=${workspaceId || ''}`);
      }
    }
  };

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    setIsOpen(false);
    setQuery('');

    if (suggestion.type === 'page') {
      navigate(`/editor/${suggestion.id}`);
    } else if (suggestion.type === 'space') {
      navigate(`/space/${suggestion.id}`);
    }
  };

  return (
    <div ref={containerRef} className={clsx('relative', className)}>
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(e.target.value.length >= 2);
          }}
          onFocus={() => setIsOpen(query.length >= 2)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="w-full px-4 py-2 pl-10 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
        />
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
          🔍
        </span>
        {query && (
          <button
            onClick={() => {
              setQuery('');
              setIsOpen(false);
              inputRef.current?.focus();
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
          >
            ✕
          </button>
        )}
      </div>

      {/* Suggestions dropdown */}
      {isOpen && suggestions && suggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-slate-800 border border-slate-600 rounded-lg shadow-lg overflow-hidden">
          <ul className="py-1">
            {suggestions.map((suggestion, index) => (
              <li key={`${suggestion.type}-${suggestion.id}`}>
                <button
                  onClick={() => handleSuggestionClick(suggestion)}
                  className={clsx(
                    'w-full px-4 py-2 text-left flex items-center gap-3 transition-colors',
                    index === selectedIndex
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-300 hover:bg-slate-700'
                  )}
                >
                  <span className="text-sm">
                    {suggestion.type === 'page' ? '📄' : '📁'}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="truncate font-medium">{suggestion.title}</div>
                    {suggestion.description && (
                      <div className="text-xs text-slate-400 truncate">
                        {suggestion.description}
                      </div>
                    )}
                  </div>
                  <span className="text-xs text-slate-500 uppercase">
                    {suggestion.type}
                  </span>
                </button>
              </li>
            ))}
          </ul>
          <div className="px-4 py-2 border-t border-slate-700 text-xs text-slate-400">
            Press Enter to search for "{query}"
          </div>
        </div>
      )}

      {/* No results message */}
      {isOpen && query.length >= 2 && suggestions && suggestions.length === 0 && (
        <div className="absolute z-50 w-full mt-1 bg-slate-800 border border-slate-600 rounded-lg shadow-lg p-4 text-center text-slate-400">
          No results found for "{query}"
        </div>
      )}
    </div>
  );
}

export default SearchBar;
