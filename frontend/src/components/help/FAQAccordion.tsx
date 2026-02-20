/**
 * FAQAccordion - Collapsible FAQ sections with smooth animation.
 *
 * Renders a list of question/answer pairs. Supports single-open
 * (default) or multi-open mode via the allowMultiple prop.
 */

import React, { useState, useRef, useCallback } from 'react';
import { ChevronDown } from 'lucide-react';

export interface FAQItem {
  question: string;
  answer: React.ReactNode;
}

interface FAQAccordionProps {
  items: FAQItem[];
  allowMultiple?: boolean;
}

interface AccordionItemProps {
  item: FAQItem;
  isExpanded: boolean;
  onToggle: () => void;
  isFirst: boolean;
  isLast: boolean;
}

function AccordionItem({ item, isExpanded, onToggle, isFirst, isLast }: AccordionItemProps) {
  const contentRef = useRef<HTMLDivElement>(null);

  return (
    <div
      className={`border-b border-gray-200 last:border-b-0 ${
        isFirst ? 'rounded-t-lg' : ''
      } ${isLast ? 'rounded-b-lg' : ''}`}
    >
      <button
        onClick={onToggle}
        aria-expanded={isExpanded}
        className={`w-full flex items-center justify-between px-5 py-4 text-left text-sm font-medium text-gray-900 hover:bg-gray-50 transition-colors ${
          isFirst ? 'rounded-t-lg' : ''
        } ${isLast && !isExpanded ? 'rounded-b-lg' : ''}`}
      >
        <span>{item.question}</span>
        <ChevronDown
          className={`w-4 h-4 text-gray-500 flex-shrink-0 ml-4 transition-transform duration-200 ${
            isExpanded ? 'rotate-180' : ''
          }`}
        />
      </button>

      <div
        className="overflow-hidden transition-[max-height] duration-200 ease-in-out"
        style={{
          maxHeight: isExpanded
            ? `${contentRef.current?.scrollHeight ?? 1000}px`
            : '0px',
        }}
      >
        <div ref={contentRef} className="px-5 pb-4 text-sm text-gray-600">
          {item.answer}
        </div>
      </div>
    </div>
  );
}

export function FAQAccordion({ items, allowMultiple = false }: FAQAccordionProps) {
  const [expandedIndices, setExpandedIndices] = useState<Set<number>>(new Set());

  const toggleItem = useCallback(
    (index: number) => {
      setExpandedIndices((prev) => {
        const next = new Set(prev);

        if (next.has(index)) {
          next.delete(index);
        } else {
          if (!allowMultiple) {
            next.clear();
          }
          next.add(index);
        }

        return next;
      });
    },
    [allowMultiple]
  );

  if (items.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      {items.map((item, index) => (
        <AccordionItem
          key={index}
          item={item}
          isExpanded={expandedIndices.has(index)}
          onToggle={() => toggleItem(index)}
          isFirst={index === 0}
          isLast={index === items.length - 1}
        />
      ))}
    </div>
  );
}
