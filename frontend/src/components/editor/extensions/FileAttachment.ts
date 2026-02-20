/**
 * FileAttachment Extension for TipTap
 *
 * Sprint F: Attachments & Media Support
 *
 * Renders as a card with filename, size, icon, and download link.
 */

import { Node, mergeAttributes } from '@tiptap/core';

export interface FileAttachmentOptions {
  HTMLAttributes: Record<string, unknown>;
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    fileAttachment: {
      setFileAttachment: (attributes: {
        attachmentId: string;
        filename: string;
        mimeType: string;
        fileSize: number;
        description?: string;
      }) => ReturnType;
    };
  }
}

export const FileAttachment = Node.create<FileAttachmentOptions>({
  name: 'fileAttachment',

  addOptions() {
    return {
      HTMLAttributes: {},
    };
  },

  group: 'block',

  atom: true,

  addAttributes() {
    return {
      attachmentId: {
        default: null,
        parseHTML: (element) => element.getAttribute('data-attachment-id'),
        renderHTML: (attributes) => ({
          'data-attachment-id': attributes.attachmentId,
        }),
      },
      filename: {
        default: '',
        parseHTML: (element) => element.getAttribute('data-filename'),
        renderHTML: (attributes) => ({
          'data-filename': attributes.filename,
        }),
      },
      mimeType: {
        default: '',
        parseHTML: (element) => element.getAttribute('data-mime-type'),
        renderHTML: (attributes) => ({
          'data-mime-type': attributes.mimeType,
        }),
      },
      fileSize: {
        default: 0,
        parseHTML: (element) => parseInt(element.getAttribute('data-file-size') || '0', 10),
        renderHTML: (attributes) => ({
          'data-file-size': attributes.fileSize,
        }),
      },
      description: {
        default: null,
        parseHTML: (element) => element.getAttribute('data-description'),
        renderHTML: (attributes) => {
          if (!attributes.description) return {};
          return { 'data-description': attributes.description };
        },
      },
    };
  },

  parseHTML() {
    return [
      {
        tag: 'div[data-type="file-attachment"]',
      },
    ];
  },

  renderHTML({ HTMLAttributes }) {
    const filename = HTMLAttributes['data-filename'] || 'Unknown file';
    const fileSize = HTMLAttributes['data-file-size'] || 0;
    const sizeStr = formatFileSize(fileSize);

    return [
      'div',
      mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
        'data-type': 'file-attachment',
        class: 'file-attachment-card',
      }),
      [
        'div',
        { class: 'file-attachment-info' },
        ['span', { class: 'file-attachment-icon' }, getFileIcon(HTMLAttributes['data-mime-type'])],
        [
          'div',
          { class: 'file-attachment-details' },
          ['span', { class: 'file-attachment-name' }, filename],
          ['span', { class: 'file-attachment-size' }, sizeStr],
        ],
      ],
    ];
  },

  addCommands() {
    return {
      setFileAttachment:
        (attributes) =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
            attrs: attributes,
          });
        },
    };
  },
});

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

function getFileIcon(mimeType: string): string {
  if (!mimeType) return '📄';
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

export default FileAttachment;
