/**
 * SignatureBadge - Visual indicator for electronic signatures.
 *
 * Displays signature status with meaning icon and verification state.
 */

import type { ElectronicSignature, SignatureMeaning } from '../../lib/api';

interface SignatureBadgeProps {
  signature: ElectronicSignature;
  size?: 'sm' | 'md' | 'lg';
  showDetails?: boolean;
  onClick?: () => void;
}

const MEANING_CONFIG: Record<
  SignatureMeaning,
  { label: string; icon: string; color: string }
> = {
  authored: {
    label: 'Authored',
    icon: 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z',
    color: 'blue',
  },
  reviewed: {
    label: 'Reviewed',
    icon: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z',
    color: 'purple',
  },
  approved: {
    label: 'Approved',
    icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    color: 'green',
  },
  witnessed: {
    label: 'Witnessed',
    icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    color: 'yellow',
  },
  acknowledged: {
    label: 'Acknowledged',
    icon: 'M5 13l4 4L19 7',
    color: 'teal',
  },
};

const COLOR_CLASSES: Record<string, { bg: string; text: string; border: string }> = {
  blue: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-200' },
  purple: { bg: 'bg-purple-100', text: 'text-purple-700', border: 'border-purple-200' },
  green: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-200' },
  yellow: { bg: 'bg-yellow-100', text: 'text-yellow-700', border: 'border-yellow-200' },
  teal: { bg: 'bg-teal-100', text: 'text-teal-700', border: 'border-teal-200' },
  red: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-200' },
  gray: { bg: 'bg-gray-100', text: 'text-gray-500', border: 'border-gray-200' },
};

const SIZE_CLASSES = {
  sm: {
    badge: 'px-2 py-0.5 text-xs',
    icon: 'w-3 h-3',
    text: 'text-xs',
  },
  md: {
    badge: 'px-2.5 py-1 text-sm',
    icon: 'w-4 h-4',
    text: 'text-sm',
  },
  lg: {
    badge: 'px-3 py-1.5 text-base',
    icon: 'w-5 h-5',
    text: 'text-base',
  },
};

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function SignatureBadge({
  signature,
  size = 'md',
  showDetails = false,
  onClick,
}: SignatureBadgeProps) {
  const config = MEANING_CONFIG[signature.meaning];
  const colorClass = signature.is_valid
    ? COLOR_CLASSES[config.color]
    : COLOR_CLASSES.gray;
  const sizeClass = SIZE_CLASSES[size];

  const badge = (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-medium ${
        colorClass.bg
      } ${colorClass.text} ${colorClass.border} ${sizeClass.badge} ${
        onClick ? 'cursor-pointer hover:opacity-80' : ''
      } ${!signature.is_valid ? 'line-through opacity-75' : ''}`}
      onClick={onClick}
      title={signature.meaning_description}
    >
      <svg
        className={sizeClass.icon}
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        strokeWidth={2}
      >
        <path strokeLinecap="round" strokeLinejoin="round" d={config.icon} />
      </svg>
      <span>{config.label}</span>
      {!signature.is_valid && (
        <svg className={sizeClass.icon} fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
            clipRule="evenodd"
          />
        </svg>
      )}
    </span>
  );

  if (!showDetails) {
    return badge;
  }

  return (
    <div className="flex items-start gap-3">
      <div className="flex-shrink-0 pt-0.5">{badge}</div>
      <div className="flex-1 min-w-0">
        <div className={`font-medium text-gray-900 ${sizeClass.text}`}>
          {signature.signer_name}
        </div>
        <div className={`text-gray-500 ${sizeClass.text}`}>
          {signature.signer_title && (
            <span className="block">{signature.signer_title}</span>
          )}
          <span className="block">
            {formatDate(signature.signed_at)} at {formatTime(signature.signed_at)}
          </span>
        </div>
        {signature.reason && (
          <p className={`mt-1 text-gray-600 ${sizeClass.text}`}>
            &ldquo;{signature.reason}&rdquo;
          </p>
        )}
        {!signature.is_valid && signature.invalidation_reason && (
          <p className="mt-1 text-red-600 text-xs">
            Invalidated: {signature.invalidation_reason}
          </p>
        )}
      </div>
    </div>
  );
}

export default SignatureBadge;
