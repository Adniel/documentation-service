/**
 * Diátaxis Framework Types and Templates
 *
 * Diátaxis organizes documentation into four types:
 * - Tutorials: Learning-oriented (practical steps)
 * - How-to Guides: Task-oriented (problem-solving)
 * - Reference: Information-oriented (technical description)
 * - Explanation: Understanding-oriented (conceptual discussion)
 */

import type { DiataxisType } from '../types';

export interface DiataxisInfo {
  type: DiataxisType;
  label: string;
  icon: string;
  color: string;
  bgColor: string;
  borderColor: string;
  description: string;
  purpose: string;
  characteristics: string[];
  template: DiataxisTemplate;
}

export interface DiataxisTemplate {
  title: string;
  blocks: Array<{
    type: string;
    content: string;
    attrs?: Record<string, unknown>;
  }>;
}

export const DIATAXIS_INFO: Record<DiataxisType, DiataxisInfo> = {
  tutorial: {
    type: 'tutorial',
    label: 'Tutorial',
    icon: '📚',
    color: 'text-green-400',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    description: 'Learning-oriented guides that take the reader through a series of steps.',
    purpose: 'To help the reader LEARN by doing',
    characteristics: [
      'Practical, step-by-step instructions',
      'Builds skills through practice',
      'Focuses on what the reader will DO',
      'Provides a sense of accomplishment',
    ],
    template: {
      title: 'Tutorial: [Topic Name]',
      blocks: [
        {
          type: 'heading',
          content: 'Overview',
          attrs: { level: 2 },
        },
        {
          type: 'paragraph',
          content: 'In this tutorial, you will learn to [describe what the reader will accomplish].',
        },
        {
          type: 'callout',
          content: '**Prerequisites:** Before starting, make sure you have [list prerequisites].',
          attrs: { type: 'info' },
        },
        {
          type: 'heading',
          content: 'What you will build',
          attrs: { level: 2 },
        },
        {
          type: 'paragraph',
          content: 'By the end of this tutorial, you will have [describe the outcome].',
        },
        {
          type: 'heading',
          content: 'Step 1: [First Step]',
          attrs: { level: 2 },
        },
        {
          type: 'paragraph',
          content: 'Start by [describe the first action].',
        },
        {
          type: 'codeBlock',
          content: '# Example code here',
          attrs: { language: 'bash' },
        },
        {
          type: 'heading',
          content: 'Step 2: [Second Step]',
          attrs: { level: 2 },
        },
        {
          type: 'paragraph',
          content: 'Next, [describe the second action].',
        },
        {
          type: 'heading',
          content: 'Summary',
          attrs: { level: 2 },
        },
        {
          type: 'paragraph',
          content: 'In this tutorial, you learned how to [summarize key learnings].',
        },
        {
          type: 'heading',
          content: 'Next Steps',
          attrs: { level: 2 },
        },
        {
          type: 'bulletList',
          content: '- [Related tutorial 1]\n- [Related tutorial 2]\n- [Relevant how-to guide]',
        },
      ],
    },
  },

  how_to: {
    type: 'how_to',
    label: 'How-to Guide',
    icon: '🔧',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    description: 'Task-oriented guides that show how to solve a specific problem.',
    purpose: 'To help the reader ACCOMPLISH a specific task',
    characteristics: [
      'Focused on a specific problem',
      'Assumes existing knowledge',
      'Provides working solutions',
      'Can be followed out of sequence',
    ],
    template: {
      title: 'How to [Task Name]',
      blocks: [
        {
          type: 'paragraph',
          content: 'This guide shows you how to [describe the task] when you need to [describe the situation].',
        },
        {
          type: 'callout',
          content: '**Requirements:** You will need [list requirements].',
          attrs: { type: 'info' },
        },
        {
          type: 'heading',
          content: 'Procedure',
          attrs: { level: 2 },
        },
        {
          type: 'orderedList',
          content: '1. [First step]\n2. [Second step]\n3. [Third step]',
        },
        {
          type: 'heading',
          content: 'Example',
          attrs: { level: 2 },
        },
        {
          type: 'codeBlock',
          content: '# Example implementation',
          attrs: { language: 'bash' },
        },
        {
          type: 'heading',
          content: 'Troubleshooting',
          attrs: { level: 2 },
        },
        {
          type: 'paragraph',
          content: 'If you encounter [common issue], try [solution].',
        },
        {
          type: 'heading',
          content: 'Related',
          attrs: { level: 2 },
        },
        {
          type: 'bulletList',
          content: '- [Related how-to 1]\n- [Reference documentation]\n- [Explanation of concept]',
        },
      ],
    },
  },

  reference: {
    type: 'reference',
    label: 'Reference',
    icon: '📖',
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/30',
    description: 'Technical descriptions of the system and how to use it.',
    purpose: 'To provide ACCURATE technical information',
    characteristics: [
      'Structured for quick lookup',
      'Comprehensive and accurate',
      'Austere and to the point',
      'Consistent format',
    ],
    template: {
      title: '[Component/API Name] Reference',
      blocks: [
        {
          type: 'paragraph',
          content: '[Brief description of what this component/API does].',
        },
        {
          type: 'heading',
          content: 'Syntax',
          attrs: { level: 2 },
        },
        {
          type: 'codeBlock',
          content: '// Syntax example',
          attrs: { language: 'typescript' },
        },
        {
          type: 'heading',
          content: 'Parameters',
          attrs: { level: 2 },
        },
        {
          type: 'table',
          content: '| Parameter | Type | Required | Description |\n|-----------|------|----------|-------------|\n| param1 | string | Yes | Description |\n| param2 | number | No | Description |',
        },
        {
          type: 'heading',
          content: 'Return Value',
          attrs: { level: 2 },
        },
        {
          type: 'paragraph',
          content: 'Returns [type] containing [description].',
        },
        {
          type: 'heading',
          content: 'Examples',
          attrs: { level: 2 },
        },
        {
          type: 'codeBlock',
          content: '// Basic usage example',
          attrs: { language: 'typescript' },
        },
        {
          type: 'heading',
          content: 'Notes',
          attrs: { level: 2 },
        },
        {
          type: 'bulletList',
          content: '- [Important note 1]\n- [Important note 2]',
        },
        {
          type: 'heading',
          content: 'See Also',
          attrs: { level: 2 },
        },
        {
          type: 'bulletList',
          content: '- [Related reference 1]\n- [How-to guide]\n- [Explanation]',
        },
      ],
    },
  },

  explanation: {
    type: 'explanation',
    label: 'Explanation',
    icon: '💡',
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/30',
    description: 'Discussion that clarifies and illuminates a topic.',
    purpose: 'To help the reader UNDERSTAND concepts',
    characteristics: [
      'Provides context and background',
      'Explores alternatives and opinions',
      'Makes connections to other concepts',
      'Answers "why" questions',
    ],
    template: {
      title: 'Understanding [Concept Name]',
      blocks: [
        {
          type: 'paragraph',
          content: '[Opening paragraph that introduces the concept and why it matters].',
        },
        {
          type: 'heading',
          content: 'Background',
          attrs: { level: 2 },
        },
        {
          type: 'paragraph',
          content: '[Historical context or foundational knowledge].',
        },
        {
          type: 'heading',
          content: 'Key Concepts',
          attrs: { level: 2 },
        },
        {
          type: 'paragraph',
          content: '[Explanation of the main ideas].',
        },
        {
          type: 'heading',
          content: 'How It Works',
          attrs: { level: 2 },
        },
        {
          type: 'paragraph',
          content: '[Detailed explanation of the mechanics or processes].',
        },
        {
          type: 'heading',
          content: 'Considerations',
          attrs: { level: 2 },
        },
        {
          type: 'paragraph',
          content: '[Discussion of trade-offs, alternatives, or design decisions].',
        },
        {
          type: 'heading',
          content: 'Common Misconceptions',
          attrs: { level: 2 },
        },
        {
          type: 'paragraph',
          content: '[Address common misunderstandings].',
        },
        {
          type: 'heading',
          content: 'Summary',
          attrs: { level: 2 },
        },
        {
          type: 'paragraph',
          content: '[Brief summary of the key points].',
        },
        {
          type: 'heading',
          content: 'Further Reading',
          attrs: { level: 2 },
        },
        {
          type: 'bulletList',
          content: '- [Related explanation]\n- [External resource]\n- [Reference documentation]',
        },
      ],
    },
  },

  mixed: {
    type: 'mixed',
    label: 'Mixed',
    icon: '📁',
    color: 'text-slate-400',
    bgColor: 'bg-slate-500/10',
    borderColor: 'border-slate-500/30',
    description: 'Content that spans multiple documentation types.',
    purpose: 'To organize diverse content',
    characteristics: [
      'May contain multiple documentation types',
      'Used for organizational containers',
      'No specific structure required',
    ],
    template: {
      title: '[Document Title]',
      blocks: [
        {
          type: 'paragraph',
          content: '[Introduction to the content].',
        },
        {
          type: 'heading',
          content: 'Section 1',
          attrs: { level: 2 },
        },
        {
          type: 'paragraph',
          content: '[Content for section 1].',
        },
        {
          type: 'heading',
          content: 'Section 2',
          attrs: { level: 2 },
        },
        {
          type: 'paragraph',
          content: '[Content for section 2].',
        },
      ],
    },
  },
};

/**
 * Get Diátaxis info for a specific type
 */
export function getDiataxisInfo(type: DiataxisType | undefined): DiataxisInfo {
  return DIATAXIS_INFO[type || 'mixed'];
}

/**
 * Get all Diátaxis types as an array (excluding 'mixed')
 */
export function getDiataxisTypes(): DiataxisInfo[] {
  return ['tutorial', 'how_to', 'reference', 'explanation'].map(
    (type) => DIATAXIS_INFO[type as DiataxisType]
  );
}

/**
 * Convert Diátaxis template to TipTap editor content
 */
export function templateToEditorContent(template: DiataxisTemplate): Record<string, unknown> {
  return {
    type: 'doc',
    content: template.blocks.map((block) => {
      switch (block.type) {
        case 'heading':
          return {
            type: 'heading',
            attrs: block.attrs,
            content: [{ type: 'text', text: block.content }],
          };
        case 'paragraph':
          return {
            type: 'paragraph',
            content: [{ type: 'text', text: block.content }],
          };
        case 'codeBlock':
          return {
            type: 'codeBlock',
            attrs: block.attrs,
            content: [{ type: 'text', text: block.content }],
          };
        case 'callout':
          return {
            type: 'callout',
            attrs: block.attrs,
            content: [
              {
                type: 'paragraph',
                content: [{ type: 'text', text: block.content }],
              },
            ],
          };
        case 'bulletList':
          return {
            type: 'bulletList',
            content: block.content.split('\n').map((item) => ({
              type: 'listItem',
              content: [
                {
                  type: 'paragraph',
                  content: [{ type: 'text', text: item.replace(/^[-*]\s*/, '') }],
                },
              ],
            })),
          };
        case 'orderedList':
          return {
            type: 'orderedList',
            content: block.content.split('\n').map((item) => ({
              type: 'listItem',
              content: [
                {
                  type: 'paragraph',
                  content: [{ type: 'text', text: item.replace(/^\d+\.\s*/, '') }],
                },
              ],
            })),
          };
        case 'table':
          // Parse markdown table to TipTap table format
          const rows = block.content.split('\n').filter((row) => !row.includes('---'));
          return {
            type: 'table',
            content: rows.map((row, index) => ({
              type: 'tableRow',
              content: row
                .split('|')
                .filter((cell) => cell.trim())
                .map((cell) => ({
                  type: index === 0 ? 'tableHeader' : 'tableCell',
                  content: [
                    {
                      type: 'paragraph',
                      content: [{ type: 'text', text: cell.trim() }],
                    },
                  ],
                })),
            })),
          };
        default:
          return {
            type: 'paragraph',
            content: [{ type: 'text', text: block.content }],
          };
      }
    }),
  };
}
