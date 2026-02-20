/**
 * AI integration context menu items — copy content formatted for AI tools.
 *
 * Sprint I: Context Menu
 */

import { useState } from 'react';

interface AiIntegrationMenuProps {
  selectedText: string;
  pageTitle: string;
  fullMarkdown?: string;
}

export function useAiIntegrationActions({ selectedText, pageTitle, fullMarkdown }: AiIntegrationMenuProps) {
  const [toast, setToast] = useState('');

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(''), 2000);
  };

  const copyForChatGPT = async () => {
    const text = selectedText || fullMarkdown || '';
    const formatted = `# ${pageTitle}\n\n${text}\n\n---\nPlease analyze the above document.`;
    await navigator.clipboard.writeText(formatted);
    showToast('Copied for ChatGPT');
  };

  const copyForClaude = async () => {
    const text = selectedText || fullMarkdown || '';
    const formatted = `<document title="${pageTitle}">\n${text}\n</document>\n\nPlease analyze the above document.`;
    await navigator.clipboard.writeText(formatted);
    showToast('Copied for Claude');
  };

  const copyForMCP = async () => {
    const text = selectedText || fullMarkdown || '';
    const formatted = JSON.stringify({
      type: 'document',
      title: pageTitle,
      content: text,
    }, null, 2);
    await navigator.clipboard.writeText(formatted);
    showToast('Copied for MCP');
  };

  return { copyForChatGPT, copyForClaude, copyForMCP, toast };
}
