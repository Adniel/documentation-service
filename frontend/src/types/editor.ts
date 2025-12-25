/**
 * Block Editor Type Definitions
 *
 * Defines the structure of content blocks used in the editor.
 * Compatible with TipTap/ProseMirror JSON format.
 */

// Block types supported by the editor
export type BlockType =
  | 'paragraph'
  | 'heading'
  | 'bulletList'
  | 'orderedList'
  | 'listItem'
  | 'codeBlock'
  | 'blockquote'
  | 'horizontalRule'
  | 'table'
  | 'tableRow'
  | 'tableCell'
  | 'tableHeader'
  | 'taskList'
  | 'taskItem'
  | 'image'
  | 'callout';

// Mark types for inline formatting
export type MarkType =
  | 'bold'
  | 'italic'
  | 'strike'
  | 'code'
  | 'link'
  | 'highlight'
  | 'subscript'
  | 'superscript';

// Base mark definition
export interface Mark {
  type: MarkType;
  attrs?: Record<string, unknown>;
}

// Text node with optional marks
export interface TextNode {
  type: 'text';
  text: string;
  marks?: Mark[];
}

// Base block node
export interface BlockNode {
  type: BlockType;
  attrs?: Record<string, unknown>;
  content?: (BlockNode | TextNode)[];
}

// Heading block with level
export interface HeadingBlock extends BlockNode {
  type: 'heading';
  attrs: {
    level: 1 | 2 | 3 | 4 | 5 | 6;
  };
}

// Code block with language
export interface CodeBlock extends BlockNode {
  type: 'codeBlock';
  attrs?: {
    language?: string;
  };
}

// Callout/admonition block
export interface CalloutBlock extends BlockNode {
  type: 'callout';
  attrs: {
    type: 'info' | 'warning' | 'danger' | 'success' | 'note';
    title?: string;
  };
}

// Image block
export interface ImageBlock extends BlockNode {
  type: 'image';
  attrs: {
    src: string;
    alt?: string;
    title?: string;
    width?: number;
    height?: number;
  };
}

// Task item with checked state
export interface TaskItemBlock extends BlockNode {
  type: 'taskItem';
  attrs: {
    checked: boolean;
  };
}

// Document structure
export interface EditorDocument {
  type: 'doc';
  content: BlockNode[];
}

// Editor state for persistence
export interface EditorState {
  document: EditorDocument;
  selection?: {
    anchor: number;
    head: number;
  };
  metadata?: {
    lastModified: string;
    wordCount: number;
    characterCount: number;
  };
}

// Block menu item definition
export interface BlockMenuItem {
  id: string;
  label: string;
  description: string;
  icon: string;
  shortcut?: string;
  keywords: string[];
  action: () => void;
}

// Editor toolbar button
export interface ToolbarButton {
  id: string;
  label: string;
  icon: string;
  shortcut?: string;
  isActive?: () => boolean;
  action: () => void;
}

// Markdown conversion options
export interface MarkdownOptions {
  gfm?: boolean; // GitHub Flavored Markdown
  breaks?: boolean; // Convert line breaks
  tables?: boolean; // Support tables
  taskLists?: boolean; // Support task lists
}

// Save status for auto-save indicator
export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

// Editor configuration
export interface EditorConfig {
  placeholder?: string;
  autofocus?: boolean;
  editable?: boolean;
  autoSave?: {
    enabled: boolean;
    debounceMs: number;
  };
  collaboration?: {
    enabled: boolean;
    documentId: string;
    wsUrl: string;
  };
}
