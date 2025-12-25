/**
 * Tests for Markdown conversion utilities (Sprint 2)
 */

import { describe, it, expect } from 'vitest';
import {
  markdownToHtml,
  jsonToMarkdown,
  exportToMarkdown,
  importFromMarkdown,
} from './markdown';
import type { EditorDocument } from '../types/editor';

describe('markdownToHtml', () => {
  describe('headings', () => {
    it('should convert h1 heading', () => {
      const result = markdownToHtml('# Heading 1');
      expect(result).toContain('<h1>Heading 1</h1>');
    });

    it('should convert h2 heading', () => {
      const result = markdownToHtml('## Heading 2');
      expect(result).toContain('<h2>Heading 2</h2>');
    });

    it('should convert all heading levels', () => {
      const markdown = `# H1
## H2
### H3
#### H4
##### H5
###### H6`;
      const result = markdownToHtml(markdown);

      expect(result).toContain('<h1>H1</h1>');
      expect(result).toContain('<h2>H2</h2>');
      expect(result).toContain('<h3>H3</h3>');
      expect(result).toContain('<h4>H4</h4>');
      expect(result).toContain('<h5>H5</h5>');
      expect(result).toContain('<h6>H6</h6>');
    });
  });

  describe('inline formatting', () => {
    it('should convert bold text with **', () => {
      const result = markdownToHtml('This is **bold** text');
      expect(result).toContain('<strong>bold</strong>');
    });

    it('should convert bold text with __', () => {
      const result = markdownToHtml('This is __bold__ text');
      expect(result).toContain('<strong>bold</strong>');
    });

    it('should convert italic text with *', () => {
      const result = markdownToHtml('This is *italic* text');
      expect(result).toContain('<em>italic</em>');
    });

    it('should convert italic text with _', () => {
      const result = markdownToHtml('This is _italic_ text');
      expect(result).toContain('<em>italic</em>');
    });

    it('should convert strikethrough', () => {
      const result = markdownToHtml('This is ~~deleted~~ text');
      expect(result).toContain('<s>deleted</s>');
    });

    it('should convert inline code', () => {
      const result = markdownToHtml('Use the `const` keyword');
      expect(result).toContain('<code>const</code>');
    });
  });

  describe('links and images', () => {
    it('should convert links', () => {
      const result = markdownToHtml('[Click here](https://example.com)');
      expect(result).toContain('<a href="https://example.com">Click here</a>');
    });

    it('should convert images', () => {
      const result = markdownToHtml('![Alt text](image.png)');
      expect(result).toContain('<img src="image.png" alt="Alt text">');
    });
  });

  describe('code blocks', () => {
    it('should convert fenced code block', () => {
      const markdown = '```javascript\nconst x = 1;\n```';
      const result = markdownToHtml(markdown);

      expect(result).toContain('<pre>');
      expect(result).toContain('<code');
      expect(result).toContain('language-javascript');
    });

    it('should escape HTML in code blocks', () => {
      const markdown = '```html\n<div>test</div>\n```';
      const result = markdownToHtml(markdown);

      expect(result).toContain('&lt;div&gt;');
    });
  });

  describe('lists', () => {
    it('should convert unordered list', () => {
      const markdown = '- Item 1\n- Item 2';
      const result = markdownToHtml(markdown);

      expect(result).toContain('<li>Item 1</li>');
      expect(result).toContain('<li>Item 2</li>');
    });

    it('should convert ordered list', () => {
      const markdown = '1. First\n2. Second';
      const result = markdownToHtml(markdown);

      expect(result).toContain('<li>First</li>');
      expect(result).toContain('<li>Second</li>');
    });
  });

  describe('blockquotes', () => {
    it('should convert blockquote', () => {
      const result = markdownToHtml('> This is a quote');
      expect(result).toContain('<blockquote>');
      expect(result).toContain('This is a quote');
    });
  });

  describe('horizontal rules', () => {
    it('should convert horizontal rule with ---', () => {
      const result = markdownToHtml('---');
      expect(result).toContain('<hr>');
    });

    it('should convert horizontal rule with ***', () => {
      const result = markdownToHtml('***');
      expect(result).toContain('<hr>');
    });
  });
});

describe('jsonToMarkdown', () => {
  it('should handle empty document', () => {
    const doc: EditorDocument = { type: 'doc', content: [] };
    const result = jsonToMarkdown(doc);
    expect(result).toBe('');
  });

  it('should convert paragraph', () => {
    const doc: EditorDocument = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'Hello, world!' }],
        },
      ],
    };

    const result = jsonToMarkdown(doc);
    expect(result).toBe('Hello, world!');
  });

  it('should convert heading', () => {
    const doc: EditorDocument = {
      type: 'doc',
      content: [
        {
          type: 'heading',
          attrs: { level: 2 },
          content: [{ type: 'text', text: 'My Heading' }],
        },
      ],
    };

    const result = jsonToMarkdown(doc);
    expect(result).toBe('## My Heading');
  });

  it('should convert bold text', () => {
    const doc: EditorDocument = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'This is ' },
            { type: 'text', text: 'bold', marks: [{ type: 'bold' }] },
            { type: 'text', text: ' text' },
          ],
        },
      ],
    };

    const result = jsonToMarkdown(doc);
    expect(result).toBe('This is **bold** text');
  });

  it('should convert italic text', () => {
    const doc: EditorDocument = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'emphasized', marks: [{ type: 'italic' }] },
          ],
        },
      ],
    };

    const result = jsonToMarkdown(doc);
    expect(result).toBe('*emphasized*');
  });

  it('should convert code block', () => {
    const doc: EditorDocument = {
      type: 'doc',
      content: [
        {
          type: 'codeBlock',
          attrs: { language: 'typescript' },
          content: [{ type: 'text', text: 'const x = 1;' }],
        },
      ],
    };

    const result = jsonToMarkdown(doc);
    expect(result).toBe('```typescript\nconst x = 1;\n```');
  });

  it('should convert bullet list', () => {
    const doc: EditorDocument = {
      type: 'doc',
      content: [
        {
          type: 'bulletList',
          content: [
            {
              type: 'listItem',
              content: [
                {
                  type: 'paragraph',
                  content: [{ type: 'text', text: 'Item 1' }],
                },
              ],
            },
            {
              type: 'listItem',
              content: [
                {
                  type: 'paragraph',
                  content: [{ type: 'text', text: 'Item 2' }],
                },
              ],
            },
          ],
        },
      ],
    };

    const result = jsonToMarkdown(doc);
    expect(result).toContain('- Item 1');
    expect(result).toContain('- Item 2');
  });

  it('should convert link', () => {
    const doc: EditorDocument = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            {
              type: 'text',
              text: 'Click me',
              marks: [{ type: 'link', attrs: { href: 'https://example.com' } }],
            },
          ],
        },
      ],
    };

    const result = jsonToMarkdown(doc);
    expect(result).toBe('[Click me](https://example.com)');
  });

  it('should convert horizontal rule', () => {
    const doc: EditorDocument = {
      type: 'doc',
      content: [{ type: 'horizontalRule' }],
    };

    const result = jsonToMarkdown(doc);
    expect(result).toBe('---');
  });

  it('should convert blockquote', () => {
    const doc: EditorDocument = {
      type: 'doc',
      content: [
        {
          type: 'blockquote',
          content: [
            {
              type: 'paragraph',
              content: [{ type: 'text', text: 'A quote' }],
            },
          ],
        },
      ],
    };

    const result = jsonToMarkdown(doc);
    expect(result).toContain('> A quote');
  });
});

describe('exportToMarkdown', () => {
  it('should export without metadata by default', () => {
    const doc: EditorDocument = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'Content' }],
        },
      ],
    };

    const result = exportToMarkdown(doc);
    expect(result).not.toContain('---');
    expect(result).toBe('Content');
  });

  it('should include frontmatter when requested', () => {
    const doc: EditorDocument = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'Content' }],
        },
      ],
    };

    const result = exportToMarkdown(doc, {
      includeMetadata: true,
      title: 'My Document',
    });

    expect(result).toContain('---');
    expect(result).toContain('title: My Document');
    expect(result).toContain('Content');
  });
});

describe('importFromMarkdown', () => {
  it('should return HTML from markdown', () => {
    const markdown = '# Hello\n\nThis is a **test**.';
    const result = importFromMarkdown(markdown);

    expect(result).toContain('<h1>Hello</h1>');
    expect(result).toContain('<strong>test</strong>');
  });
});
