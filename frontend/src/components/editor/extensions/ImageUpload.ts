/**
 * ImageUpload Extension for TipTap
 *
 * Sprint F: Attachments & Media Support
 *
 * Extends the built-in Image node with attachment support:
 * - Adds attachmentId attribute for linking to stored attachments
 * - Supports drag-and-drop image upload
 * - Supports clipboard paste image upload
 */

import { Node, mergeAttributes } from '@tiptap/core';
import { Plugin, PluginKey } from '@tiptap/pm/state';

export interface ImageUploadOptions {
  HTMLAttributes: Record<string, unknown>;
  onUpload?: (file: File) => Promise<{ src: string; attachmentId: string }>;
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    imageUpload: {
      setImageUpload: (attributes: {
        src: string;
        alt?: string;
        title?: string;
        width?: number;
        height?: number;
        attachmentId?: string;
      }) => ReturnType;
    };
  }
}

export const ImageUpload = Node.create<ImageUploadOptions>({
  name: 'image',

  addOptions() {
    return {
      HTMLAttributes: {},
      onUpload: undefined,
    };
  },

  inline: false,

  group: 'block',

  draggable: true,

  addAttributes() {
    return {
      src: {
        default: null,
      },
      alt: {
        default: null,
      },
      title: {
        default: null,
      },
      width: {
        default: null,
      },
      height: {
        default: null,
      },
      attachmentId: {
        default: null,
        parseHTML: (element) => element.getAttribute('data-attachment-id'),
        renderHTML: (attributes) => {
          if (!attributes.attachmentId) return {};
          return { 'data-attachment-id': attributes.attachmentId };
        },
      },
    };
  },

  parseHTML() {
    return [
      {
        tag: 'img[src]',
      },
    ];
  },

  renderHTML({ HTMLAttributes }) {
    return ['img', mergeAttributes(this.options.HTMLAttributes, HTMLAttributes)];
  },

  addCommands() {
    return {
      setImageUpload:
        (attributes) =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
            attrs: attributes,
          });
        },
    };
  },

  addProseMirrorPlugins() {
    const onUpload = this.options.onUpload;

    if (!onUpload) {
      return [];
    }

    return [
      new Plugin({
        key: new PluginKey('imageUpload'),
        props: {
          handleDrop: (view, event) => {
            const files = event.dataTransfer?.files;
            if (!files || files.length === 0) return false;

            const imageFiles = Array.from(files).filter((file) =>
              file.type.startsWith('image/')
            );

            if (imageFiles.length === 0) return false;

            event.preventDefault();

            const coordinates = view.posAtCoords({
              left: event.clientX,
              top: event.clientY,
            });

            imageFiles.forEach(async (file) => {
              try {
                const result = await onUpload(file);
                const node = view.state.schema.nodes.image.create({
                  src: result.src,
                  attachmentId: result.attachmentId,
                  alt: file.name,
                });

                const pos = coordinates?.pos ?? view.state.selection.anchor;
                const transaction = view.state.tr.insert(pos, node);
                view.dispatch(transaction);
              } catch (error) {
                console.error('Image upload failed:', error);
              }
            });

            return true;
          },

          handlePaste: (view, event) => {
            const items = event.clipboardData?.items;
            if (!items) return false;

            const imageItems = Array.from(items).filter((item) =>
              item.type.startsWith('image/')
            );

            if (imageItems.length === 0) return false;

            event.preventDefault();

            imageItems.forEach(async (item) => {
              const file = item.getAsFile();
              if (!file) return;

              try {
                const result = await onUpload(file);
                const node = view.state.schema.nodes.image.create({
                  src: result.src,
                  attachmentId: result.attachmentId,
                  alt: file.name,
                });

                const transaction = view.state.tr.replaceSelectionWith(node);
                view.dispatch(transaction);
              } catch (error) {
                console.error('Image paste upload failed:', error);
              }
            });

            return true;
          },
        },
      }),
    ];
  },
});

export default ImageUpload;
