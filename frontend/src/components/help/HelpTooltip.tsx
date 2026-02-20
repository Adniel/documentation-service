/**
 * HelpTooltip - Contextual help popover triggered by a help icon.
 *
 * Renders a small HelpCircle icon that opens a popover with a title
 * and content on click. Closes on click-outside or Escape key.
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { HelpCircle } from 'lucide-react';

interface HelpTooltipProps {
  content: React.ReactNode;
  title?: string;
  placement?: 'top' | 'bottom' | 'left' | 'right';
}

function getPopoverPositionClasses(placement: 'top' | 'bottom' | 'left' | 'right'): string {
  switch (placement) {
    case 'top':
      return 'bottom-full left-1/2 -translate-x-1/2 mb-2';
    case 'bottom':
      return 'top-full left-1/2 -translate-x-1/2 mt-2';
    case 'left':
      return 'right-full top-1/2 -translate-y-1/2 mr-2';
    case 'right':
      return 'left-full top-1/2 -translate-y-1/2 ml-2';
  }
}

function getArrowClasses(placement: 'top' | 'bottom' | 'left' | 'right'): string {
  const base = 'absolute w-2 h-2 bg-white border rotate-45';
  switch (placement) {
    case 'top':
      return `${base} -bottom-1 left-1/2 -translate-x-1/2 border-t-0 border-l-0 border-gray-200`;
    case 'bottom':
      return `${base} -top-1 left-1/2 -translate-x-1/2 border-b-0 border-r-0 border-gray-200`;
    case 'left':
      return `${base} -right-1 top-1/2 -translate-y-1/2 border-b-0 border-l-0 border-gray-200`;
    case 'right':
      return `${base} -left-1 top-1/2 -translate-y-1/2 border-t-0 border-r-0 border-gray-200`;
  }
}

export function HelpTooltip({
  content,
  title,
  placement = 'top',
}: HelpTooltipProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const close = useCallback(() => setIsOpen(false), []);

  // Close on click-outside
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        close();
      }
    };

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        close();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, close]);

  return (
    <div ref={containerRef} className="relative inline-flex items-center">
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
        aria-label="Show help"
        aria-expanded={isOpen}
        type="button"
      >
        <HelpCircle className="w-4 h-4" />
      </button>

      {isOpen && (
        <div
          className={`absolute z-50 w-64 ${getPopoverPositionClasses(placement)}`}
          role="tooltip"
        >
          <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-3">
            {/* Arrow */}
            <div className={getArrowClasses(placement)} />

            {/* Title */}
            {title && (
              <p className="text-sm font-semibold text-gray-900 mb-1">{title}</p>
            )}

            {/* Content */}
            <div className="text-sm text-gray-600">{content}</div>
          </div>
        </div>
      )}
    </div>
  );
}
