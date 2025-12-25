/**
 * Breadcrumbs Navigation Component
 *
 * Shows the current location in the content hierarchy.
 */

import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { navigationApi, type Breadcrumb } from '../../lib/api';

interface BreadcrumbsProps {
  pageId?: string;
  spaceId?: string;
}

const TYPE_ROUTES: Record<string, (id: string) => string> = {
  organization: (id) => `/org/${id}`,
  workspace: (id) => `/workspace/${id}`,
  space: (id) => `/space/${id}`,
  page: (id) => `/editor/${id}`,
};

const TYPE_ICONS: Record<string, string> = {
  organization: '🏢',
  workspace: '📂',
  space: '📁',
  page: '📄',
};

export function Breadcrumbs({ pageId, spaceId }: BreadcrumbsProps) {
  const { data: breadcrumbs, isLoading } = useQuery({
    queryKey: ['breadcrumbs', pageId || spaceId],
    queryFn: () => {
      if (pageId) {
        return navigationApi.getPageBreadcrumbs(pageId);
      }
      if (spaceId) {
        return navigationApi.getSpaceBreadcrumbs(spaceId);
      }
      return Promise.resolve([]);
    },
    enabled: !!(pageId || spaceId),
  });

  if (isLoading) {
    return (
      <nav className="flex items-center gap-2 text-sm text-slate-400">
        <span className="animate-pulse">Loading...</span>
      </nav>
    );
  }

  if (!breadcrumbs || breadcrumbs.length === 0) {
    return null;
  }

  return (
    <nav className="flex items-center gap-1 text-sm overflow-x-auto">
      {breadcrumbs.map((crumb, index) => (
        <BreadcrumbItem
          key={crumb.id}
          crumb={crumb}
          isLast={index === breadcrumbs.length - 1}
        />
      ))}
    </nav>
  );
}

interface BreadcrumbItemProps {
  crumb: Breadcrumb;
  isLast: boolean;
}

function BreadcrumbItem({ crumb, isLast }: BreadcrumbItemProps) {
  const route = TYPE_ROUTES[crumb.type]?.(crumb.id) || '#';
  const icon = TYPE_ICONS[crumb.type] || '📄';

  if (isLast) {
    return (
      <span className="flex items-center gap-1 text-white font-medium truncate max-w-[200px]">
        <span className="text-xs">{icon}</span>
        <span className="truncate">{crumb.name}</span>
      </span>
    );
  }

  return (
    <>
      <Link
        to={route}
        className="flex items-center gap-1 text-slate-400 hover:text-white transition-colors truncate max-w-[150px]"
      >
        <span className="text-xs">{icon}</span>
        <span className="truncate">{crumb.name}</span>
      </Link>
      <span className="text-slate-600">/</span>
    </>
  );
}

export default Breadcrumbs;
