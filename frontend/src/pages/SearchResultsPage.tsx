/**
 * SearchResults Page
 *
 * Full-page search results with filtering and pagination.
 */

import { Link, useParams, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { searchApi, type SearchResult } from '../lib/api';
import { clsx } from 'clsx';

type DiátaxisType = 'tutorial' | 'how_to' | 'reference' | 'explanation' | '';

const DIATAXIS_FILTERS: Array<{ value: DiátaxisType; label: string }> = [
  { value: '', label: 'All Types' },
  { value: 'tutorial', label: 'Tutorials' },
  { value: 'how_to', label: 'How-to Guides' },
  { value: 'reference', label: 'Reference' },
  { value: 'explanation', label: 'Explanation' },
];

const STATUS_FILTERS = [
  { value: '', label: 'All Status' },
  { value: 'draft', label: 'Draft' },
  { value: 'in_review', label: 'In Review' },
  { value: 'approved', label: 'Approved' },
  { value: 'effective', label: 'Effective' },
];

const SORT_OPTIONS = [
  { value: 'relevance', label: 'Relevance' },
  { value: 'updated_at:desc', label: 'Recently Updated' },
  { value: 'title:asc', label: 'Title A-Z' },
  { value: 'title:desc', label: 'Title Z-A' },
];

const PAGE_SIZE = 20;

export default function SearchResultsPage() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const [searchParams, setSearchParams] = useSearchParams();

  const query = searchParams.get('q') || '';
  const diataxisType = searchParams.get('type') || '';
  const status = searchParams.get('status') || '';
  const sort = searchParams.get('sort') || 'relevance';
  const page = parseInt(searchParams.get('page') || '1', 10);

  const offset = (page - 1) * PAGE_SIZE;

  const { data: results, isLoading, error } = useQuery<SearchResult>({
    queryKey: ['search', query, workspaceId, diataxisType, status, sort, page],
    queryFn: () =>
      searchApi.searchPages({
        q: query,
        workspace_id: workspaceId,
        diataxis_type: diataxisType || undefined,
        status: status || undefined,
        sort: sort === 'relevance' ? undefined : sort,
        limit: PAGE_SIZE,
        offset,
      }),
    enabled: query.length > 0,
  });

  const updateFilter = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams);
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    params.set('page', '1'); // Reset to first page on filter change
    setSearchParams(params);
  };

  const totalPages = results ? Math.ceil(results.total / PAGE_SIZE) : 0;

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-slate-800/50 border-b border-slate-700 px-6 py-4">
        <h1 className="text-xl font-semibold text-white mb-4">
          Search Results
          {query && (
            <span className="text-slate-400 font-normal ml-2">for "{query}"</span>
          )}
        </h1>

        {/* Filters */}
        <div className="flex flex-wrap gap-4">
          <select
            value={diataxisType}
            onChange={(e) => updateFilter('type', e.target.value)}
            className="px-3 py-1.5 bg-slate-700 border border-slate-600 rounded text-sm text-white focus:outline-none focus:border-blue-500"
          >
            {DIATAXIS_FILTERS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>

          <select
            value={status}
            onChange={(e) => updateFilter('status', e.target.value)}
            className="px-3 py-1.5 bg-slate-700 border border-slate-600 rounded text-sm text-white focus:outline-none focus:border-blue-500"
          >
            {STATUS_FILTERS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>

          <select
            value={sort}
            onChange={(e) => updateFilter('sort', e.target.value)}
            className="px-3 py-1.5 bg-slate-700 border border-slate-600 rounded text-sm text-white focus:outline-none focus:border-blue-500"
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto p-6">
        {!query ? (
          <div className="text-center py-12 text-slate-400">
            Enter a search query to find documents
          </div>
        ) : isLoading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className="h-24 bg-slate-800 rounded-lg animate-pulse border border-slate-700"
              />
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-12 text-red-400">
            Failed to load search results
          </div>
        ) : results && results.hits.length > 0 ? (
          <div className="space-y-4">
            {/* Results count */}
            <div className="text-sm text-slate-400">
              Found {results.total} result{results.total !== 1 ? 's' : ''} in{' '}
              {results.processing_time_ms}ms
            </div>

            {/* Results list */}
            <div className="space-y-3">
              {results.hits.map((hit) => (
                <SearchResultItem key={hit.id} hit={hit} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <Pagination
                currentPage={page}
                totalPages={totalPages}
                onPageChange={(newPage) => updateFilter('page', newPage.toString())}
              />
            )}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-lg font-medium text-white mb-2">No results found</h3>
            <p className="text-slate-400">
              Try different keywords or adjust your filters
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

interface SearchResultItemProps {
  hit: SearchResult['hits'][0];
}

function SearchResultItem({ hit }: SearchResultItemProps) {
  const statusColors: Record<string, string> = {
    draft: 'bg-yellow-500/20 text-yellow-400',
    in_review: 'bg-blue-500/20 text-blue-400',
    approved: 'bg-green-500/20 text-green-400',
    effective: 'bg-emerald-500/20 text-emerald-400',
    obsolete: 'bg-slate-500/20 text-slate-400',
  };

  const diataxisIcons: Record<string, string> = {
    tutorial: '📚',
    how_to: '🔧',
    reference: '📖',
    explanation: '💡',
  };

  return (
    <Link
      to={`/editor/${hit.id}`}
      className="block p-4 bg-slate-800 rounded-lg border border-slate-700 hover:border-slate-600 hover:bg-slate-750 transition-all group"
    >
      <div className="flex items-start gap-4">
        <span className="text-2xl">
          {hit.diataxis_type ? diataxisIcons[hit.diataxis_type] || '📄' : '📄'}
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3
              className="font-medium text-white group-hover:text-blue-400 transition-colors"
              dangerouslySetInnerHTML={{
                __html: hit._formatted?.title || hit.title,
              }}
            />
            {hit.document_number && (
              <span className="text-xs text-slate-500 font-mono">
                {hit.document_number}
              </span>
            )}
          </div>

          {(hit._formatted?.summary || hit.summary) && (
            <p
              className="text-sm text-slate-400 line-clamp-2 mb-2"
              dangerouslySetInnerHTML={{
                __html: hit._formatted?.summary || hit.summary || '',
              }}
            />
          )}

          {hit._formatted?.content_text && (
            <p
              className="text-sm text-slate-500 line-clamp-2"
              dangerouslySetInnerHTML={{ __html: hit._formatted.content_text }}
            />
          )}

          <div className="flex items-center gap-3 mt-2">
            <span className={clsx('text-xs px-2 py-0.5 rounded', statusColors[hit.status] || statusColors.draft)}>
              {hit.status.replace('_', ' ')}
            </span>
            <span className="text-xs text-slate-500">v{hit.version}</span>
            <span className="text-xs text-slate-500">
              Updated {new Date(hit.updated_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  const pages: (number | string)[] = [];

  // Build page numbers array with ellipsis
  if (totalPages <= 7) {
    for (let i = 1; i <= totalPages; i++) {
      pages.push(i);
    }
  } else {
    pages.push(1);
    if (currentPage > 3) pages.push('...');

    for (
      let i = Math.max(2, currentPage - 1);
      i <= Math.min(totalPages - 1, currentPage + 1);
      i++
    ) {
      pages.push(i);
    }

    if (currentPage < totalPages - 2) pages.push('...');
    pages.push(totalPages);
  }

  return (
    <div className="flex items-center justify-center gap-1 mt-6">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="px-3 py-1.5 text-sm bg-slate-700 text-slate-300 rounded hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Previous
      </button>

      {pages.map((page, idx) =>
        typeof page === 'number' ? (
          <button
            key={idx}
            onClick={() => onPageChange(page)}
            className={clsx(
              'px-3 py-1.5 text-sm rounded',
              page === currentPage
                ? 'bg-blue-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            )}
          >
            {page}
          </button>
        ) : (
          <span key={idx} className="px-2 text-slate-500">
            {page}
          </span>
        )
      )}

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="px-3 py-1.5 text-sm bg-slate-700 text-slate-300 rounded hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Next
      </button>
    </div>
  );
}
