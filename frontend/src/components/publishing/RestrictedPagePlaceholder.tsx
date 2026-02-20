/**
 * Restricted Page Placeholder Component
 *
 * Sprint D: Integrated Access Control
 *
 * Displays when a visitor tries to access a restricted page:
 * - Lock icon and title
 * - Customizable message
 * - Optional login prompt
 */

import React from 'react';
import { Lock, LogIn, Shield, ArrowLeft } from 'lucide-react';

interface RestrictedPagePlaceholderProps {
  pageTitle: string;
  message?: string;
  showLoginPrompt?: boolean;
  onLogin?: () => void;
  onBack?: () => void;
}

export function RestrictedPagePlaceholder({
  pageTitle,
  message = 'You do not have access to view this content.',
  showLoginPrompt = false,
  onLogin,
  onBack,
}: RestrictedPagePlaceholderProps) {
  return (
    <div className="min-h-[400px] flex items-center justify-center p-8">
      <div className="text-center max-w-md">
        {/* Icon */}
        <div className="w-16 h-16 mx-auto mb-6 bg-amber-100 rounded-full flex items-center justify-center">
          <Lock className="w-8 h-8 text-amber-600" />
        </div>

        {/* Title */}
        <h1 className="text-2xl font-bold text-gray-900 mb-2">{pageTitle}</h1>

        {/* Badge */}
        <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-sm mb-4">
          <Shield className="w-4 h-4" />
          Access Restricted
        </div>

        {/* Message */}
        <p className="text-gray-600 mb-6">{message}</p>

        {/* Actions */}
        <div className="flex items-center justify-center gap-3">
          {onBack && (
            <button
              onClick={onBack}
              className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-md flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Go Back
            </button>
          )}

          {showLoginPrompt && onLogin && (
            <button
              onClick={onLogin}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
            >
              <LogIn className="w-4 h-4" />
              Sign In for Access
            </button>
          )}
        </div>

        {/* Info text */}
        {showLoginPrompt && (
          <p className="mt-6 text-sm text-gray-500">
            Sign in with your credentials to access this content
          </p>
        )}
      </div>
    </div>
  );
}

/**
 * Inline restricted content indicator for navigation items
 */
interface RestrictedNavItemProps {
  title: string;
  onClick?: () => void;
}

export function RestrictedNavItem({ title, onClick }: RestrictedNavItemProps) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-2 px-3 py-2 text-gray-400 hover:bg-gray-50 rounded-md group"
    >
      <Lock className="w-4 h-4 text-amber-400 group-hover:text-amber-500" />
      <span className="truncate">{title}</span>
      <span className="text-xs text-gray-400 ml-auto">Restricted</span>
    </button>
  );
}

/**
 * Inline restricted content indicator for search results
 */
interface RestrictedSearchResultProps {
  title: string;
  onClick?: () => void;
}

export function RestrictedSearchResult({
  title,
  onClick,
}: RestrictedSearchResultProps) {
  return (
    <button
      onClick={onClick}
      className="w-full text-left p-3 hover:bg-gray-50 border-b border-gray-100 last:border-0"
    >
      <div className="flex items-center gap-2">
        <Lock className="w-4 h-4 text-amber-400 flex-shrink-0" />
        <span className="font-medium text-gray-700 truncate">{title}</span>
        <span className="text-xs bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded">
          Restricted
        </span>
      </div>
      <p className="text-sm text-gray-400 mt-1 ml-6">
        This content requires additional access
      </p>
    </button>
  );
}

/**
 * Inline restricted link indicator for transformed content
 */
interface RestrictedLinkProps {
  text: string;
  href?: string;
  onClick?: (e: React.MouseEvent) => void;
}

export function RestrictedLink({ text, href, onClick }: RestrictedLinkProps) {
  return (
    <a
      href={href}
      onClick={onClick}
      className="inline-flex items-center gap-1 text-amber-600 hover:text-amber-700"
      title="This link requires additional access"
    >
      <Lock className="w-3 h-3" />
      <span className="underline">{text}</span>
    </a>
  );
}

export default RestrictedPagePlaceholder;
