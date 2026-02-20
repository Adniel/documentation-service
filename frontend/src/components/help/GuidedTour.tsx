/**
 * GuidedTour - Step-by-step tour overlay with spotlight.
 *
 * Highlights target elements on the page with a semi-transparent overlay
 * and positions an instructional tooltip near each target. Supports
 * next/previous/skip navigation and keyboard shortcuts.
 */

import { useState, useEffect, useCallback } from 'react';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';

export interface TourStep {
  target: string;
  title: string;
  description: string;
  placement?: 'top' | 'bottom' | 'left' | 'right';
}

interface GuidedTourProps {
  steps: TourStep[];
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

interface TooltipPosition {
  top: number;
  left: number;
}

interface SpotlightRect {
  top: number;
  left: number;
  width: number;
  height: number;
}

const PADDING = 8;
const TOOLTIP_OFFSET = 16;

function getSpotlightRect(el: Element): SpotlightRect {
  const rect = el.getBoundingClientRect();
  return {
    top: rect.top - PADDING + window.scrollY,
    left: rect.left - PADDING + window.scrollX,
    width: rect.width + PADDING * 2,
    height: rect.height + PADDING * 2,
  };
}

function getTooltipPosition(
  el: Element,
  placement: 'top' | 'bottom' | 'left' | 'right'
): TooltipPosition {
  const rect = el.getBoundingClientRect();
  const scrollY = window.scrollY;
  const scrollX = window.scrollX;

  switch (placement) {
    case 'top':
      return {
        top: rect.top + scrollY - TOOLTIP_OFFSET,
        left: rect.left + scrollX + rect.width / 2,
      };
    case 'bottom':
      return {
        top: rect.bottom + scrollY + TOOLTIP_OFFSET,
        left: rect.left + scrollX + rect.width / 2,
      };
    case 'left':
      return {
        top: rect.top + scrollY + rect.height / 2,
        left: rect.left + scrollX - TOOLTIP_OFFSET,
      };
    case 'right':
      return {
        top: rect.top + scrollY + rect.height / 2,
        left: rect.right + scrollX + TOOLTIP_OFFSET,
      };
  }
}

function getTransformClasses(placement: 'top' | 'bottom' | 'left' | 'right'): string {
  switch (placement) {
    case 'top':
      return '-translate-x-1/2 -translate-y-full';
    case 'bottom':
      return '-translate-x-1/2';
    case 'left':
      return '-translate-x-full -translate-y-1/2';
    case 'right':
      return '-translate-y-1/2';
  }
}

export function GuidedTour({ steps, isOpen, onClose, onComplete }: GuidedTourProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [spotlight, setSpotlight] = useState<SpotlightRect | null>(null);
  const [tooltipPos, setTooltipPos] = useState<TooltipPosition | null>(null);

  const step = steps[currentStep];
  const placement = step?.placement ?? 'bottom';
  const isLastStep = currentStep === steps.length - 1;

  const updatePositions = useCallback(() => {
    if (!step) return;

    const el = document.querySelector(step.target);
    if (!el) {
      setSpotlight(null);
      setTooltipPos(null);
      return;
    }

    setSpotlight(getSpotlightRect(el));
    setTooltipPos(getTooltipPosition(el, placement));
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, [step, placement]);

  // Reposition on step change or window resize
  useEffect(() => {
    if (!isOpen) return;

    updatePositions();

    window.addEventListener('resize', updatePositions);
    window.addEventListener('scroll', updatePositions);
    return () => {
      window.removeEventListener('resize', updatePositions);
      window.removeEventListener('scroll', updatePositions);
    };
  }, [isOpen, updatePositions]);

  // Reset step when tour opens
  useEffect(() => {
    if (isOpen) {
      setCurrentStep(0);
    }
  }, [isOpen]);

  // Escape key to close
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const goToNext = useCallback(() => {
    if (isLastStep) {
      onComplete();
      return;
    }

    // Find next step with a valid target (skip missing ones)
    let next = currentStep + 1;
    while (next < steps.length) {
      const el = document.querySelector(steps[next].target);
      if (el) {
        setCurrentStep(next);
        return;
      }
      next++;
    }

    // All remaining targets missing, complete the tour
    onComplete();
  }, [currentStep, steps, isLastStep, onComplete]);

  const goToPrevious = useCallback(() => {
    if (currentStep <= 0) return;

    let prev = currentStep - 1;
    while (prev >= 0) {
      const el = document.querySelector(steps[prev].target);
      if (el) {
        setCurrentStep(prev);
        return;
      }
      prev--;
    }
  }, [currentStep, steps]);

  if (!isOpen || !step) return null;

  // Build the overlay box-shadow to create the spotlight cutout
  const overlayStyle = spotlight
    ? {
        position: 'absolute' as const,
        top: spotlight.top,
        left: spotlight.left,
        width: spotlight.width,
        height: spotlight.height,
        boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.5)',
        borderRadius: '8px',
        pointerEvents: 'none' as const,
        zIndex: 40,
      }
    : undefined;

  return (
    <div className="fixed inset-0 z-50">
      {/* Overlay background (fallback if no spotlight) */}
      {!spotlight && (
        <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      )}

      {/* Spotlight cutout */}
      {spotlight && overlayStyle && <div style={overlayStyle} />}

      {/* Click-away layer behind tooltip but above overlay */}
      {spotlight && (
        <div className="fixed inset-0 z-40" onClick={onClose} />
      )}

      {/* Tooltip card */}
      {tooltipPos && (
        <div
          className={`absolute z-50 w-80 ${getTransformClasses(placement)}`}
          style={{ top: tooltipPos.top, left: tooltipPos.left }}
        >
          <div className="bg-white rounded-lg shadow-xl border border-gray-200 p-5">
            {/* Header */}
            <div className="flex items-start justify-between mb-2">
              <h3 className="text-sm font-semibold text-gray-900">{step.title}</h3>
              <button
                onClick={onClose}
                className="p-0.5 text-gray-400 hover:text-gray-600 rounded"
                aria-label="Close tour"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Description */}
            <p className="text-sm text-gray-600 mb-4">{step.description}</p>

            {/* Footer */}
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">
                Step {currentStep + 1} of {steps.length}
              </span>

              <div className="flex items-center gap-2">
                <button
                  onClick={onClose}
                  className="px-3 py-1.5 text-xs text-gray-500 hover:text-gray-700"
                >
                  Skip
                </button>

                {currentStep > 0 && (
                  <button
                    onClick={goToPrevious}
                    className="px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-100 rounded-md flex items-center gap-1"
                  >
                    <ChevronLeft className="w-3 h-3" />
                    Back
                  </button>
                )}

                <button
                  onClick={goToNext}
                  className="px-3 py-1.5 text-xs bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-1"
                >
                  {isLastStep ? 'Finish' : 'Next'}
                  {!isLastStep && <ChevronRight className="w-3 h-3" />}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Fallback: centered card when target element is missing */}
      {!tooltipPos && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="bg-white rounded-lg shadow-xl border border-gray-200 p-5 w-80">
            <div className="flex items-start justify-between mb-2">
              <h3 className="text-sm font-semibold text-gray-900">{step.title}</h3>
              <button
                onClick={onClose}
                className="p-0.5 text-gray-400 hover:text-gray-600 rounded"
                aria-label="Close tour"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-sm text-gray-600 mb-4">{step.description}</p>

            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">
                Step {currentStep + 1} of {steps.length}
              </span>

              <div className="flex items-center gap-2">
                <button
                  onClick={onClose}
                  className="px-3 py-1.5 text-xs text-gray-500 hover:text-gray-700"
                >
                  Skip
                </button>

                {currentStep > 0 && (
                  <button
                    onClick={goToPrevious}
                    className="px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-100 rounded-md flex items-center gap-1"
                  >
                    <ChevronLeft className="w-3 h-3" />
                    Back
                  </button>
                )}

                <button
                  onClick={goToNext}
                  className="px-3 py-1.5 text-xs bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-1"
                >
                  {isLastStep ? 'Finish' : 'Next'}
                  {!isLastStep && <ChevronRight className="w-3 h-3" />}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
