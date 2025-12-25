/**
 * DraftStatusBadge - Visual status indicator for change requests.
 *
 * Includes tooltips explaining what each status means for better UX.
 */

import type { ChangeRequestStatus } from '../../types';

interface DraftStatusBadgeProps {
  status: ChangeRequestStatus;
  size?: 'sm' | 'md';
  showTooltip?: boolean;
}

const statusConfig: Record<
  ChangeRequestStatus,
  { label: string; description: string; className: string; icon: string }
> = {
  draft: {
    label: 'Draft',
    description: 'Your proposed changes are saved but not yet submitted for review.',
    className: 'bg-gray-100 text-gray-700 border-gray-200',
    icon: 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z',
  },
  submitted: {
    label: 'Submitted',
    description: 'Your changes have been submitted and are waiting for a reviewer.',
    className: 'bg-blue-100 text-blue-700 border-blue-200',
    icon: 'M12 19l9 2-9-18-9 18 9-2zm0 0v-8',
  },
  in_review: {
    label: 'In Review',
    description: 'A reviewer is currently examining your proposed changes.',
    className: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    icon: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z',
  },
  changes_requested: {
    label: 'Changes Requested',
    description: 'The reviewer has requested modifications before approval.',
    className: 'bg-orange-100 text-orange-700 border-orange-200',
    icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
  },
  approved: {
    label: 'Approved',
    description: 'Your changes are approved and ready to be published.',
    className: 'bg-green-100 text-green-700 border-green-200',
    icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  published: {
    label: 'Published',
    description: 'Your changes are now part of the official document.',
    className: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    icon: 'M5 13l4 4L19 7',
  },
  rejected: {
    label: 'Rejected',
    description: 'The reviewer declined these changes.',
    className: 'bg-red-100 text-red-700 border-red-200',
    icon: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  cancelled: {
    label: 'Cancelled',
    description: 'This change request was cancelled and will not be published.',
    className: 'bg-gray-100 text-gray-500 border-gray-200',
    icon: 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636',
  },
};

export function DraftStatusBadge({ status, size = 'sm', showTooltip = true }: DraftStatusBadgeProps) {
  const config = statusConfig[status];
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-sm';

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border font-medium cursor-help ${config.className} ${sizeClasses}`}
      title={showTooltip ? config.description : undefined}
    >
      <svg
        className={size === 'sm' ? 'w-3 h-3' : 'w-4 h-4'}
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        strokeWidth={2}
      >
        <path strokeLinecap="round" strokeLinejoin="round" d={config.icon} />
      </svg>
      {config.label}
    </span>
  );
}

export default DraftStatusBadge;
