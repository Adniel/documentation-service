/**
 * TemplateSelector Component
 *
 * Allows users to select a Diátaxis template when creating new pages.
 */

import { useState } from 'react';
import { getDiataxisTypes, getDiataxisInfo, templateToEditorContent, type DiataxisInfo } from '../../lib/diataxis';
import { clsx } from 'clsx';
import type { DiataxisType } from '../../types';

interface TemplateSelectorProps {
  onSelect: (content: Record<string, unknown>, title: string, type: DiataxisType) => void;
  onCancel: () => void;
}

export function TemplateSelector({ onSelect, onCancel }: TemplateSelectorProps) {
  const [selectedType, setSelectedType] = useState<DiataxisType | null>(null);
  const types = getDiataxisTypes();

  const handleSelect = () => {
    if (!selectedType) return;

    const info = getDiataxisInfo(selectedType);
    const content = templateToEditorContent(info.template);
    onSelect(content, info.template.title, selectedType);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-xl border border-slate-700 max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-slate-700">
          <h2 className="text-xl font-semibold text-white">Choose a Template</h2>
          <p className="text-slate-400 mt-1">
            Select a documentation type to start with a pre-structured template
          </p>
        </div>

        {/* Template options */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {types.map((type) => (
              <TemplateCard
                key={type.type}
                info={type}
                selected={selectedType === type.type}
                onSelect={() => setSelectedType(type.type)}
              />
            ))}
          </div>

          {/* Blank option */}
          <div className="mt-4">
            <button
              onClick={() => onSelect({ type: 'doc', content: [{ type: 'paragraph' }] }, 'Untitled', 'mixed')}
              className="w-full p-4 text-left bg-slate-700/50 rounded-lg border border-slate-600 hover:border-slate-500 transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">📄</span>
                <div>
                  <h3 className="font-medium text-white">Blank Page</h3>
                  <p className="text-sm text-slate-400">Start with an empty document</p>
                </div>
              </div>
            </button>
          </div>
        </div>

        {/* Selected template details */}
        {selectedType && (
          <div className="p-4 bg-slate-850 border-t border-slate-700">
            <TemplatePreview type={selectedType} />
          </div>
        )}

        {/* Footer */}
        <div className="p-4 border-t border-slate-700 flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-slate-300 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSelect}
            disabled={!selectedType}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Use Template
          </button>
        </div>
      </div>
    </div>
  );
}

interface TemplateCardProps {
  info: DiataxisInfo;
  selected: boolean;
  onSelect: () => void;
}

function TemplateCard({ info, selected, onSelect }: TemplateCardProps) {
  return (
    <button
      onClick={onSelect}
      className={clsx(
        'p-4 text-left rounded-lg border-2 transition-all',
        selected
          ? `${info.bgColor} ${info.borderColor} border-opacity-100`
          : 'bg-slate-700/50 border-slate-600 hover:border-slate-500'
      )}
    >
      <div className="flex items-start gap-3">
        <span className={clsx('text-2xl', info.color)}>{info.icon}</span>
        <div className="flex-1 min-w-0">
          <h3 className={clsx('font-medium', selected ? info.color : 'text-white')}>
            {info.label}
          </h3>
          <p className="text-sm text-slate-400 mt-1">{info.description}</p>
          <div className="mt-2">
            <span className="text-xs text-slate-500">{info.purpose}</span>
          </div>
        </div>
        {selected && (
          <span className={clsx('text-lg', info.color)}>✓</span>
        )}
      </div>
    </button>
  );
}

interface TemplatePreviewProps {
  type: DiataxisType;
}

function TemplatePreview({ type }: TemplatePreviewProps) {
  const info = getDiataxisInfo(type);

  return (
    <div className="space-y-3">
      <h4 className={clsx('font-medium', info.color)}>
        {info.icon} {info.label} Characteristics
      </h4>
      <ul className="space-y-1">
        {info.characteristics.map((char, i) => (
          <li key={i} className="text-sm text-slate-400 flex items-start gap-2">
            <span className="text-slate-500">•</span>
            <span>{char}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TemplateSelector;
