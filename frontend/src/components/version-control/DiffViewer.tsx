/**
 * DiffViewer - Visual diff display for comparing document versions.
 *
 * Renders unified diff output in a side-by-side or unified view
 * with syntax highlighting for additions and deletions.
 */

import { useState, useMemo } from 'react';
import type { DiffResult, DiffHunk } from '../../types';

interface DiffViewerProps {
  diff: DiffResult;
  title?: string;
  viewMode?: 'unified' | 'split';
  onViewModeChange?: (mode: 'unified' | 'split') => void;
}

interface ParsedLine {
  type: 'context' | 'addition' | 'deletion' | 'info';
  content: string;
  oldLineNumber?: number;
  newLineNumber?: number;
}

function parseHunkContent(hunk: DiffHunk): ParsedLine[] {
  const lines: ParsedLine[] = [];
  const contentLines = hunk.content.split('\n').filter((line) => line !== '');

  let oldLine = hunk.old_start;
  let newLine = hunk.new_start;

  for (const line of contentLines) {
    if (line.startsWith('+')) {
      lines.push({
        type: 'addition',
        content: line.substring(1),
        newLineNumber: newLine++,
      });
    } else if (line.startsWith('-')) {
      lines.push({
        type: 'deletion',
        content: line.substring(1),
        oldLineNumber: oldLine++,
      });
    } else if (line.startsWith(' ')) {
      lines.push({
        type: 'context',
        content: line.substring(1),
        oldLineNumber: oldLine++,
        newLineNumber: newLine++,
      });
    }
  }

  return lines;
}

function shortenSha(sha: string): string {
  return sha.substring(0, 7);
}

function UnifiedView({ hunks }: { hunks: DiffHunk[] }) {
  return (
    <div className="font-mono text-sm">
      {hunks.map((hunk, hunkIndex) => {
        const lines = parseHunkContent(hunk);

        return (
          <div key={hunkIndex} className="border-b border-slate-600 last:border-b-0">
            {/* Hunk header */}
            <div className="bg-blue-600/20 text-blue-300 px-4 py-1 text-xs">
              @@ -{hunk.old_start},{hunk.old_lines} +{hunk.new_start},{hunk.new_lines} @@
            </div>

            {/* Lines */}
            {lines.map((line, lineIndex) => (
              <div
                key={lineIndex}
                className={`flex ${
                  line.type === 'addition'
                    ? 'bg-green-600/10'
                    : line.type === 'deletion'
                    ? 'bg-red-600/10'
                    : ''
                }`}
              >
                {/* Line numbers */}
                <div className="w-12 flex-shrink-0 text-right pr-2 text-slate-500 select-none border-r border-slate-600 bg-slate-800/50">
                  {line.oldLineNumber || ''}
                </div>
                <div className="w-12 flex-shrink-0 text-right pr-2 text-slate-500 select-none border-r border-slate-600 bg-slate-800/50">
                  {line.newLineNumber || ''}
                </div>

                {/* Indicator */}
                <div className="w-6 flex-shrink-0 text-center select-none">
                  {line.type === 'addition' && (
                    <span className="text-green-400">+</span>
                  )}
                  {line.type === 'deletion' && (
                    <span className="text-red-400">-</span>
                  )}
                </div>

                {/* Content */}
                <pre className="flex-1 px-2 overflow-x-auto whitespace-pre">
                  <code
                    className={
                      line.type === 'addition'
                        ? 'text-green-300'
                        : line.type === 'deletion'
                        ? 'text-red-300'
                        : 'text-slate-300'
                    }
                  >
                    {line.content || ' '}
                  </code>
                </pre>
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
}

function SplitView({ hunks }: { hunks: DiffHunk[] }) {
  const splitData = useMemo(() => {
    const left: (ParsedLine | null)[] = [];
    const right: (ParsedLine | null)[] = [];

    for (const hunk of hunks) {
      const lines = parseHunkContent(hunk);

      // Add hunk separator
      left.push({ type: 'info', content: `@@ -${hunk.old_start},${hunk.old_lines}` });
      right.push({ type: 'info', content: `+${hunk.new_start},${hunk.new_lines} @@` });

      let i = 0;
      while (i < lines.length) {
        const line = lines[i];

        if (line.type === 'context') {
          left.push(line);
          right.push(line);
          i++;
        } else if (line.type === 'deletion') {
          // Look ahead for matching addition
          const nextAdd = lines[i + 1];
          if (nextAdd && nextAdd.type === 'addition') {
            left.push(line);
            right.push(nextAdd);
            i += 2;
          } else {
            left.push(line);
            right.push(null);
            i++;
          }
        } else if (line.type === 'addition') {
          left.push(null);
          right.push(line);
          i++;
        } else {
          i++;
        }
      }
    }

    return { left, right };
  }, [hunks]);

  return (
    <div className="font-mono text-sm flex">
      {/* Left side (old) */}
      <div className="flex-1 border-r border-slate-600">
        {splitData.left.map((line, index) => (
          <div
            key={index}
            className={`flex ${
              line?.type === 'deletion'
                ? 'bg-red-600/10'
                : line?.type === 'info'
                ? 'bg-blue-600/20'
                : !line
                ? 'bg-slate-800/50'
                : ''
            }`}
          >
            <div className="w-12 flex-shrink-0 text-right pr-2 text-slate-500 select-none border-r border-slate-600 bg-slate-800/50">
              {line?.oldLineNumber || ''}
            </div>
            <pre className="flex-1 px-2 overflow-x-auto whitespace-pre min-h-[1.5rem]">
              <code
                className={
                  line?.type === 'deletion'
                    ? 'text-red-300'
                    : line?.type === 'info'
                    ? 'text-blue-300 text-xs'
                    : 'text-slate-300'
                }
              >
                {line?.content || ''}
              </code>
            </pre>
          </div>
        ))}
      </div>

      {/* Right side (new) */}
      <div className="flex-1">
        {splitData.right.map((line, index) => (
          <div
            key={index}
            className={`flex ${
              line?.type === 'addition'
                ? 'bg-green-600/10'
                : line?.type === 'info'
                ? 'bg-blue-600/20'
                : !line
                ? 'bg-slate-800/50'
                : ''
            }`}
          >
            <div className="w-12 flex-shrink-0 text-right pr-2 text-slate-500 select-none border-r border-slate-600 bg-slate-800/50">
              {line?.newLineNumber || ''}
            </div>
            <pre className="flex-1 px-2 overflow-x-auto whitespace-pre min-h-[1.5rem]">
              <code
                className={
                  line?.type === 'addition'
                    ? 'text-green-300'
                    : line?.type === 'info'
                    ? 'text-blue-300 text-xs'
                    : 'text-slate-300'
                }
              >
                {line?.content || ''}
              </code>
            </pre>
          </div>
        ))}
      </div>
    </div>
  );
}

export function DiffViewer({
  diff,
  title,
  viewMode: initialViewMode = 'unified',
  onViewModeChange,
}: DiffViewerProps) {
  const [viewMode, setViewMode] = useState(initialViewMode);

  const handleViewModeChange = (mode: 'unified' | 'split') => {
    setViewMode(mode);
    onViewModeChange?.(mode);
  };

  if (diff.is_binary) {
    return (
      <div className="border border-slate-600 rounded-lg overflow-hidden bg-slate-800">
        {title && (
          <div className="bg-slate-700 px-4 py-2 border-b border-slate-600">
            <h3 className="text-sm font-medium text-slate-200">{title}</h3>
          </div>
        )}
        <div className="p-4 text-center text-slate-400">
          Binary file - diff not available
        </div>
      </div>
    );
  }

  return (
    <div className="border border-slate-600 rounded-lg overflow-hidden bg-slate-800" data-testid="diff-viewer">
      {/* Header */}
      <div className="bg-slate-700 px-4 py-2 border-b border-slate-600 flex items-center justify-between">
        <div className="flex items-center gap-4">
          {title && (
            <h3 className="text-sm font-medium text-slate-200">{title}</h3>
          )}
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <code className="px-1.5 py-0.5 bg-red-600/30 text-red-300 rounded font-mono">
              {shortenSha(diff.from_sha)}
            </code>
            <span className="text-slate-500">&rarr;</span>
            <code className="px-1.5 py-0.5 bg-green-600/30 text-green-300 rounded font-mono">
              {shortenSha(diff.to_sha)}
            </code>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Stats */}
          <div className="flex items-center gap-2 text-xs" data-testid="diff-stats">
            <span className="text-green-400">+{diff.additions}</span>
            <span className="text-red-400">-{diff.deletions}</span>
          </div>

          {/* View mode toggle */}
          <div className="flex border border-slate-500 rounded overflow-hidden">
            <button
              onClick={() => handleViewModeChange('unified')}
              className={`px-2 py-1 text-xs ${
                viewMode === 'unified'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Unified
            </button>
            <button
              onClick={() => handleViewModeChange('split')}
              className={`px-2 py-1 text-xs ${
                viewMode === 'split'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Split
            </button>
          </div>
        </div>
      </div>

      {/* Diff content */}
      <div className="overflow-x-auto max-h-[600px] overflow-y-auto bg-slate-900">
        {diff.hunks.length === 0 ? (
          <div className="p-4 text-center text-slate-500">No changes</div>
        ) : viewMode === 'unified' ? (
          <UnifiedView hunks={diff.hunks} />
        ) : (
          <SplitView hunks={diff.hunks} />
        )}
      </div>
    </div>
  );
}

export default DiffViewer;
