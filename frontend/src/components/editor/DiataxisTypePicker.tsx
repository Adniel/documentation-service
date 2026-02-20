/**
 * DiataxisTypePicker Component
 *
 * Sprint E: Diataxis Revision
 *
 * Multi-select type picker for per-page Diataxis categorization.
 * Shows the 4 core types as toggleable badges with colors from diataxis.ts.
 */

import React from 'react';
import type { DiataxisType } from '../../types';
import { getDiataxisTypes } from '../../lib/diataxis';

interface DiataxisTypePickerProps {
  selected: DiataxisType[];
  onChange: (types: DiataxisType[]) => void;
  disabled?: boolean;
  compact?: boolean;
}

export const DiataxisTypePicker: React.FC<DiataxisTypePickerProps> = ({
  selected,
  onChange,
  disabled = false,
  compact = false,
}) => {
  const types = getDiataxisTypes();

  const toggleType = (type: DiataxisType) => {
    if (disabled) return;

    if (selected.includes(type)) {
      onChange(selected.filter((t) => t !== type));
    } else {
      onChange([...selected, type]);
    }
  };

  return (
    <div className="space-y-1">
      {!compact && (
        <label className="block text-xs font-medium text-slate-400 mb-1.5">
          Content Type
        </label>
      )}
      <div className="flex flex-wrap gap-1.5">
        {types.map((info) => {
          const isSelected = selected.includes(info.type);
          return (
            <button
              key={info.type}
              type="button"
              onClick={() => toggleType(info.type)}
              disabled={disabled}
              className={`
                inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium
                border transition-all
                ${isSelected
                  ? `${info.bgColor} ${info.color} ${info.borderColor}`
                  : 'bg-slate-800 text-slate-500 border-slate-700 hover:border-slate-600'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
              title={info.description}
            >
              <span>{info.icon}</span>
              <span>{info.label}</span>
            </button>
          );
        })}
      </div>
      {!compact && selected.length === 0 && (
        <p className="text-xs text-slate-500 mt-1">
          No type assigned. Click to categorize this page.
        </p>
      )}
    </div>
  );
};

export default DiataxisTypePicker;
