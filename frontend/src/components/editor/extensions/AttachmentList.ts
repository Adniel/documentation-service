/**
 * AttachmentList Extension for TipTap
 *
 * Sprint F: Attachments & Media Support
 *
 * Displays multiple attachments in a list, grid, or table layout.
 */

import { Node, mergeAttributes } from '@tiptap/core';

export type AttachmentListLayout = 'list' | 'grid' | 'table';

export interface AttachmentListOptions {
  HTMLAttributes: Record<string, unknown>;
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    attachmentList: {
      setAttachmentList: (attributes: {
        layout?: AttachmentListLayout;
        attachmentIds: string[];
      }) => ReturnType;
    };
  }
}

export const AttachmentList = Node.create<AttachmentListOptions>({
  name: 'attachmentList',

  addOptions() {
    return {
      HTMLAttributes: {},
    };
  },

  group: 'block',

  atom: true,

  addAttributes() {
    return {
      layout: {
        default: 'list',
        parseHTML: (element) => element.getAttribute('data-layout') || 'list',
        renderHTML: (attributes) => ({
          'data-layout': attributes.layout,
        }),
      },
      attachmentIds: {
        default: [],
        parseHTML: (element) => {
          const raw = element.getAttribute('data-attachment-ids');
          if (!raw) return [];
          try {
            return JSON.parse(raw);
          } catch {
            return [];
          }
        },
        renderHTML: (attributes) => ({
          'data-attachment-ids': JSON.stringify(attributes.attachmentIds || []),
        }),
      },
    };
  },

  parseHTML() {
    return [
      {
        tag: 'div[data-type="attachment-list"]',
      },
    ];
  },

  renderHTML({ HTMLAttributes }) {
    const count = (() => {
      try {
        const ids = JSON.parse(HTMLAttributes['data-attachment-ids'] || '[]');
        return Array.isArray(ids) ? ids.length : 0;
      } catch {
        return 0;
      }
    })();

    return [
      'div',
      mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
        'data-type': 'attachment-list',
        class: `attachment-list attachment-list-${HTMLAttributes['data-layout'] || 'list'}`,
      }),
      ['div', { class: 'attachment-list-placeholder' }, `${count} attachment(s)`],
    ];
  },

  addCommands() {
    return {
      setAttachmentList:
        (attributes) =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
            attrs: {
              layout: attributes.layout || 'list',
              attachmentIds: attributes.attachmentIds,
            },
          });
        },
    };
  },
});

export default AttachmentList;
