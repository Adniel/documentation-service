/**
 * Markdown Conversion Utilities
 *
 * Handles conversion between TipTap JSON and Markdown formats.
 */

import type { EditorDocument, BlockNode, TextNode, Mark } from '../types/editor';

// Simple markdown to HTML (for import)
export function markdownToHtml(markdown: string): string {
  let html = markdown;

  // Code blocks (must be first to protect content)
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    return `<pre><code class="language-${lang || 'plaintext'}">${escapeHtml(code.trim())}</code></pre>`;
  });

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Headers
  html = html.replace(/^######\s+(.+)$/gm, '<h6>$1</h6>');
  html = html.replace(/^#####\s+(.+)$/gm, '<h5>$1</h5>');
  html = html.replace(/^####\s+(.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^###\s+(.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^##\s+(.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^#\s+(.+)$/gm, '<h1>$1</h1>');

  // Blockquotes
  html = html.replace(/^>\s+(.+)$/gm, '<blockquote><p>$1</p></blockquote>');

  // Horizontal rules
  html = html.replace(/^[-*_]{3,}$/gm, '<hr>');

  // Unordered lists
  html = html.replace(/^[-*+]\s+(.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');

  // Ordered lists
  html = html.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');

  // Task lists
  html = html.replace(
    /^[-*]\s+\[([ x])\]\s+(.+)$/gm,
    (_, checked, text) =>
      `<li data-type="taskItem" data-checked="${checked === 'x'}">${text}</li>`
  );

  // Bold
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__([^_]+)__/g, '<strong>$1</strong>');

  // Italic
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  html = html.replace(/_([^_]+)_/g, '<em>$1</em>');

  // Strikethrough
  html = html.replace(/~~([^~]+)~~/g, '<s>$1</s>');

  // Images (must be before links to prevent links from matching image syntax)
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">');

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

  // Paragraphs (lines that aren't already wrapped)
  html = html
    .split('\n\n')
    .map((block) => {
      if (
        block.startsWith('<') ||
        block.trim() === ''
      ) {
        return block;
      }
      return `<p>${block}</p>`;
    })
    .join('\n');

  return html;
}

// Convert TipTap JSON to Markdown
export function jsonToMarkdown(doc: EditorDocument): string {
  if (!doc.content) return '';
  return doc.content.map((node) => blockToMarkdown(node)).join('\n\n');
}

function blockToMarkdown(node: BlockNode, depth = 0): string {
  switch (node.type) {
    case 'paragraph':
      return inlineToMarkdown(node.content || []);

    case 'heading': {
      const level = (node.attrs as { level: number })?.level || 1;
      const prefix = '#'.repeat(level);
      return `${prefix} ${inlineToMarkdown(node.content || [])}`;
    }

    case 'bulletList':
      return (node.content || [])
        .map((item) => `- ${blockToMarkdown(item as BlockNode, depth + 1)}`)
        .join('\n');

    case 'orderedList':
      return (node.content || [])
        .map((item, i) => `${i + 1}. ${blockToMarkdown(item as BlockNode, depth + 1)}`)
        .join('\n');

    case 'listItem':
      return (node.content || [])
        .map((child) => blockToMarkdown(child as BlockNode, depth))
        .join('\n');

    case 'taskList':
      return (node.content || [])
        .map((item) => {
          const checked = (item as BlockNode).attrs?.checked ? 'x' : ' ';
          const content = ((item as BlockNode).content || [])
            .map((child) => blockToMarkdown(child as BlockNode, depth + 1))
            .join('');
          return `- [${checked}] ${content}`;
        })
        .join('\n');

    case 'taskItem': {
      const checked = node.attrs?.checked ? 'x' : ' ';
      const content = (node.content || [])
        .map((child) => blockToMarkdown(child as BlockNode, depth + 1))
        .join('');
      return `- [${checked}] ${content}`;
    }

    case 'codeBlock': {
      const lang = (node.attrs as { language?: string })?.language || '';
      const code = (node.content || [])
        .map((n) => (n as TextNode).text || '')
        .join('');
      return `\`\`\`${lang}\n${code}\n\`\`\``;
    }

    case 'blockquote':
      return (node.content || [])
        .map((child) => `> ${blockToMarkdown(child as BlockNode, depth + 1)}`)
        .join('\n');

    case 'horizontalRule':
      return '---';

    case 'table':
      return tableToMarkdown(node);

    case 'image': {
      const attrs = node.attrs as { src: string; alt?: string; title?: string };
      const alt = attrs.alt || '';
      const title = attrs.title ? ` "${attrs.title}"` : '';
      return `![${alt}](${attrs.src}${title})`;
    }

    default:
      return inlineToMarkdown(node.content || []);
  }
}

function tableToMarkdown(node: BlockNode): string {
  const rows = (node.content || []) as BlockNode[];
  if (rows.length === 0) return '';

  const lines: string[] = [];

  rows.forEach((row, rowIndex) => {
    const cells = (row.content || []) as BlockNode[];
    const cellTexts = cells.map((cell) =>
      (cell.content || [])
        .map((child) => blockToMarkdown(child as BlockNode))
        .join('')
        .trim()
    );

    lines.push(`| ${cellTexts.join(' | ')} |`);

    // Add header separator after first row
    if (rowIndex === 0) {
      lines.push(`| ${cellTexts.map(() => '---').join(' | ')} |`);
    }
  });

  return lines.join('\n');
}

function inlineToMarkdown(content: (BlockNode | TextNode)[]): string {
  return content
    .map((node) => {
      if (node.type === 'text') {
        const textNode = node as TextNode;
        let text = textNode.text;

        if (textNode.marks) {
          textNode.marks.forEach((mark) => {
            text = applyMark(text, mark);
          });
        }

        return text;
      }

      // Handle nested blocks
      if ('content' in node) {
        return blockToMarkdown(node as BlockNode);
      }

      return '';
    })
    .join('');
}

function applyMark(text: string, mark: Mark): string {
  switch (mark.type) {
    case 'bold':
      return `**${text}**`;
    case 'italic':
      return `*${text}*`;
    case 'strike':
      return `~~${text}~~`;
    case 'code':
      return `\`${text}\``;
    case 'link': {
      const href = (mark.attrs as { href?: string })?.href || '';
      return `[${text}](${href})`;
    }
    default:
      return text;
  }
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Export markdown content
export function exportToMarkdown(doc: EditorDocument, options?: {
  includeMetadata?: boolean;
  title?: string;
}): string {
  let markdown = '';

  if (options?.includeMetadata && options?.title) {
    markdown += `---\ntitle: ${options.title}\n---\n\n`;
  }

  markdown += jsonToMarkdown(doc);

  return markdown;
}

// Import markdown content to TipTap HTML (for setContent)
export function importFromMarkdown(markdown: string): string {
  return markdownToHtml(markdown);
}
