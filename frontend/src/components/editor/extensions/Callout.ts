/**
 * Callout/Admonition Extension for TipTap
 *
 * Provides info, warning, danger, success, and note callout blocks.
 */

import { Node, mergeAttributes } from '@tiptap/core';

export type CalloutType = 'info' | 'warning' | 'danger' | 'success' | 'note';

export interface CalloutOptions {
  HTMLAttributes: Record<string, unknown>;
  types: CalloutType[];
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    callout: {
      setCallout: (attributes: { type: CalloutType; title?: string }) => ReturnType;
      toggleCallout: (attributes: { type: CalloutType; title?: string }) => ReturnType;
      unsetCallout: () => ReturnType;
    };
  }
}

export const Callout = Node.create<CalloutOptions>({
  name: 'callout',

  addOptions() {
    return {
      HTMLAttributes: {},
      types: ['info', 'warning', 'danger', 'success', 'note'],
    };
  },

  content: 'block+',

  group: 'block',

  defining: true,

  addAttributes() {
    return {
      type: {
        default: 'info',
        parseHTML: (element) => element.getAttribute('data-callout-type'),
        renderHTML: (attributes) => ({
          'data-callout-type': attributes.type,
        }),
      },
      title: {
        default: null,
        parseHTML: (element) => element.getAttribute('data-callout-title'),
        renderHTML: (attributes) => {
          if (!attributes.title) {
            return {};
          }
          return {
            'data-callout-title': attributes.title,
          };
        },
      },
    };
  },

  parseHTML() {
    return [
      {
        tag: 'div[data-callout-type]',
      },
    ];
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'div',
      mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
        class: `callout callout-${HTMLAttributes['data-callout-type']}`,
      }),
      0,
    ];
  },

  addCommands() {
    return {
      setCallout:
        (attributes) =>
        ({ commands }) => {
          return commands.wrapIn(this.name, attributes);
        },
      toggleCallout:
        (attributes) =>
        ({ commands }) => {
          return commands.toggleWrap(this.name, attributes);
        },
      unsetCallout:
        () =>
        ({ commands }) => {
          return commands.lift(this.name);
        },
    };
  },

  addKeyboardShortcuts() {
    return {
      // Mod+Shift+I for info callout
      'Mod-Shift-i': () =>
        this.editor.commands.toggleCallout({ type: 'info' }),
      // Mod+Shift+W for warning callout
      'Mod-Shift-w': () =>
        this.editor.commands.toggleCallout({ type: 'warning' }),
    };
  },
});

export default Callout;
