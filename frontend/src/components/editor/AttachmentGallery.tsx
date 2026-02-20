/**
 * AttachmentGallery Component
 *
 * Sprint F: Attachments & Media Support
 *
 * Displays a list of attachments for a page in list, grid, or table layout.
 * Used both as a standalone panel and as the renderer for attachmentList blocks.
 */

import React, { useEffect, useState } from 'react';
import { attachmentApi } from '../../lib/api';
import type { AttachmentResponse } from '../../lib/api';
import FileAttachmentCard from './FileAttachmentCard';

interface AttachmentGalleryProps {
  pageId?: string;
  attachmentIds?: string[];
  layout?: 'list' | 'grid' | 'table';
  onReplace?: (attachment: AttachmentResponse) => void;
  onDelete?: (attachment: AttachmentResponse) => void;
  readOnly?: boolean;
}

export const AttachmentGallery: React.FC<AttachmentGalleryProps> = ({
  pageId,
  attachmentIds,
  layout = 'list',
  onReplace,
  onDelete,
  readOnly = false,
}) => {
  const [attachments, setAttachments] = useState<AttachmentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadAttachments = async () => {
      setLoading(true);
      setError(null);

      try {
        if (attachmentIds && attachmentIds.length > 0) {
          // Load specific attachments by ID
          const results = await Promise.all(
            attachmentIds.map((id) => attachmentApi.get(id).catch(() => null))
          );
          setAttachments(
            results.filter((a): a is AttachmentResponse => a !== null)
          );
        } else if (pageId) {
          // Load all attachments for a page
          const result = await attachmentApi.listForPage(pageId);
          setAttachments(result.attachments);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load attachments');
      } finally {
        setLoading(false);
      }
    };

    loadAttachments();
  }, [pageId, attachmentIds]);

  if (loading) {
    return (
      <div className="p-4 text-center text-slate-400 text-sm">
        Loading attachments...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-center text-red-400 text-sm">
        {error}
      </div>
    );
  }

  if (attachments.length === 0) {
    return (
      <div className="p-4 text-center text-slate-500 text-sm">
        No attachments
      </div>
    );
  }

  if (layout === 'grid') {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        {attachments.map((att) => (
          <div key={att.id} className="flex flex-col items-center p-3 border border-slate-600 rounded-lg bg-slate-800">
            {att.mime_type.startsWith('image/') ? (
              <img
                src={attachmentApi.getThumbnailUrl(att.id)}
                alt={att.alt_text || att.filename}
                className="w-full h-24 object-cover rounded mb-2"
              />
            ) : (
              <div className="w-full h-24 flex items-center justify-center text-4xl mb-2">
                📄
              </div>
            )}
            <span className="text-xs text-slate-300 truncate w-full text-center">
              {att.filename}
            </span>
          </div>
        ))}
      </div>
    );
  }

  if (layout === 'table') {
    return (
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-700 text-slate-400">
            <th className="text-left py-2 px-3">File</th>
            <th className="text-left py-2 px-3">Type</th>
            <th className="text-right py-2 px-3">Size</th>
            <th className="text-right py-2 px-3">Version</th>
          </tr>
        </thead>
        <tbody>
          {attachments.map((att) => (
            <tr key={att.id} className="border-b border-slate-800 hover:bg-slate-800/50">
              <td className="py-2 px-3">
                <a
                  href={attachmentApi.getContentUrl(att.id)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300"
                >
                  {att.filename}
                </a>
              </td>
              <td className="py-2 px-3 text-slate-400">{att.mime_type}</td>
              <td className="py-2 px-3 text-right text-slate-400">
                {formatFileSize(att.file_size)}
              </td>
              <td className="py-2 px-3 text-right text-slate-400">
                v{att.version}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  }

  // Default: list layout
  return (
    <div className="space-y-2">
      {attachments.map((att) => (
        <FileAttachmentCard
          key={att.id}
          attachment={att}
          onReplace={readOnly ? undefined : onReplace}
          onDelete={readOnly ? undefined : onDelete}
          readOnly={readOnly}
        />
      ))}
    </div>
  );
};

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

export default AttachmentGallery;
