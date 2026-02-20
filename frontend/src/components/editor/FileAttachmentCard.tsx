/**
 * FileAttachmentCard Component
 *
 * Sprint F: Attachments & Media Support
 *
 * Renders an attachment as a card with icon, filename, size, and actions.
 */

import React from 'react';
import type { AttachmentResponse } from '../../lib/api';
import { attachmentApi } from '../../lib/api';

interface FileAttachmentCardProps {
  attachment: AttachmentResponse;
  onReplace?: (attachment: AttachmentResponse) => void;
  onDelete?: (attachment: AttachmentResponse) => void;
  readOnly?: boolean;
}

function getFileIcon(mimeType: string): string {
  if (mimeType.startsWith('image/')) return '🖼';
  if (mimeType.startsWith('video/')) return '🎬';
  if (mimeType.startsWith('audio/')) return '🎵';
  if (mimeType === 'application/pdf') return '📕';
  if (mimeType.includes('spreadsheet') || mimeType.includes('excel')) return '📊';
  if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) return '📽';
  if (mimeType.includes('word') || mimeType.includes('document')) return '📝';
  if (mimeType.includes('zip') || mimeType.includes('gzip')) return '📦';
  return '📄';
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  for (const unit of units) {
    if (size < 1024) {
      return unit === 'B' ? `${size} ${unit}` : `${size.toFixed(1)} ${unit}`;
    }
    size /= 1024;
  }
  return `${size.toFixed(1)} TB`;
}

export const FileAttachmentCard: React.FC<FileAttachmentCardProps> = ({
  attachment,
  onReplace,
  onDelete,
  readOnly = false,
}) => {
  const downloadUrl = attachmentApi.getContentUrl(attachment.id);
  const icon = getFileIcon(attachment.mime_type);
  const sizeStr = formatFileSize(attachment.file_size);

  return (
    <div className="flex items-center gap-3 p-3 border border-slate-600 rounded-lg bg-slate-800 hover:bg-slate-750 transition-colors group">
      <span className="text-2xl flex-shrink-0" role="img" aria-label="file type">
        {icon}
      </span>

      <div className="flex-1 min-w-0">
        <a
          href={downloadUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm font-medium text-blue-400 hover:text-blue-300 truncate block"
        >
          {attachment.filename}
        </a>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span>{sizeStr}</span>
          {attachment.version > 1 && (
            <span className="bg-slate-700 px-1.5 py-0.5 rounded">
              v{attachment.version}
            </span>
          )}
          {attachment.description && (
            <span className="truncate">{attachment.description}</span>
          )}
        </div>
      </div>

      {!readOnly && (
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {onReplace && (
            <button
              onClick={() => onReplace(attachment)}
              className="p-1.5 text-slate-400 hover:text-white rounded hover:bg-slate-700"
              title="Replace with new version"
            >
              ↻
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(attachment)}
              className="p-1.5 text-slate-400 hover:text-red-400 rounded hover:bg-slate-700"
              title="Delete attachment"
            >
              ✕
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default FileAttachmentCard;
