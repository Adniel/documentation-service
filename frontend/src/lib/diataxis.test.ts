/**
 * Tests for Diátaxis utility functions (Sprint 2/3)
 */

import { describe, it, expect } from 'vitest';
import {
  DIATAXIS_INFO,
  getDiataxisInfo,
  getDiataxisTypes,
  templateToEditorContent,
} from './diataxis';

describe('DIATAXIS_INFO', () => {
  it('should have all four main documentation types', () => {
    expect(DIATAXIS_INFO).toHaveProperty('tutorial');
    expect(DIATAXIS_INFO).toHaveProperty('how_to');
    expect(DIATAXIS_INFO).toHaveProperty('reference');
    expect(DIATAXIS_INFO).toHaveProperty('explanation');
  });

  it('should have mixed type for organizational containers', () => {
    expect(DIATAXIS_INFO).toHaveProperty('mixed');
  });

  it('each type should have required properties', () => {
    const requiredProps = [
      'type',
      'label',
      'icon',
      'color',
      'bgColor',
      'borderColor',
      'description',
      'purpose',
      'characteristics',
      'template',
    ];

    for (const type of Object.values(DIATAXIS_INFO)) {
      for (const prop of requiredProps) {
        expect(type).toHaveProperty(prop);
      }
    }
  });

  it('tutorial should be learning-oriented', () => {
    const tutorial = DIATAXIS_INFO.tutorial;
    expect(tutorial.purpose.toLowerCase()).toContain('learn');
    expect(tutorial.icon).toBe('📚');
  });

  it('how_to should be task-oriented', () => {
    const howTo = DIATAXIS_INFO.how_to;
    expect(howTo.purpose.toLowerCase()).toContain('accomplish');
    expect(howTo.icon).toBe('🔧');
  });

  it('reference should be information-oriented', () => {
    const reference = DIATAXIS_INFO.reference;
    expect(reference.purpose.toLowerCase()).toContain('accurate');
    expect(reference.icon).toBe('📖');
  });

  it('explanation should be understanding-oriented', () => {
    const explanation = DIATAXIS_INFO.explanation;
    expect(explanation.purpose.toLowerCase()).toContain('understand');
    expect(explanation.icon).toBe('💡');
  });
});

describe('getDiataxisInfo', () => {
  it('should return correct info for each type', () => {
    expect(getDiataxisInfo('tutorial').type).toBe('tutorial');
    expect(getDiataxisInfo('how_to').type).toBe('how_to');
    expect(getDiataxisInfo('reference').type).toBe('reference');
    expect(getDiataxisInfo('explanation').type).toBe('explanation');
  });

  it('should return mixed for undefined type', () => {
    expect(getDiataxisInfo(undefined).type).toBe('mixed');
  });

  it('should return mixed type info', () => {
    const mixed = getDiataxisInfo('mixed');
    expect(mixed.type).toBe('mixed');
    expect(mixed.label).toBe('Mixed');
  });
});

describe('getDiataxisTypes', () => {
  it('should return array of four main types', () => {
    const types = getDiataxisTypes();
    expect(types).toHaveLength(4);
  });

  it('should not include mixed type', () => {
    const types = getDiataxisTypes();
    const typeNames = types.map((t) => t.type);
    expect(typeNames).not.toContain('mixed');
  });

  it('should include all main types', () => {
    const types = getDiataxisTypes();
    const typeNames = types.map((t) => t.type);
    expect(typeNames).toContain('tutorial');
    expect(typeNames).toContain('how_to');
    expect(typeNames).toContain('reference');
    expect(typeNames).toContain('explanation');
  });
});

describe('templateToEditorContent', () => {
  it('should convert template to TipTap doc format', () => {
    const template = {
      title: 'Test',
      blocks: [
        { type: 'paragraph', content: 'Hello, world!' },
      ],
    };

    const result = templateToEditorContent(template);

    expect(result.type).toBe('doc');
    expect(result.content).toBeInstanceOf(Array);
  });

  it('should convert heading blocks correctly', () => {
    const template = {
      title: 'Test',
      blocks: [
        { type: 'heading', content: 'Title', attrs: { level: 2 } },
      ],
    };

    const result = templateToEditorContent(template);
    const heading = result.content[0] as any;

    expect(heading.type).toBe('heading');
    expect(heading.attrs.level).toBe(2);
    expect(heading.content[0].text).toBe('Title');
  });

  it('should convert paragraph blocks correctly', () => {
    const template = {
      title: 'Test',
      blocks: [
        { type: 'paragraph', content: 'Some text content' },
      ],
    };

    const result = templateToEditorContent(template);
    const paragraph = result.content[0] as any;

    expect(paragraph.type).toBe('paragraph');
    expect(paragraph.content[0].text).toBe('Some text content');
  });

  it('should convert code blocks correctly', () => {
    const template = {
      title: 'Test',
      blocks: [
        { type: 'codeBlock', content: 'const x = 1;', attrs: { language: 'typescript' } },
      ],
    };

    const result = templateToEditorContent(template);
    const codeBlock = result.content[0] as any;

    expect(codeBlock.type).toBe('codeBlock');
    expect(codeBlock.attrs.language).toBe('typescript');
    expect(codeBlock.content[0].text).toBe('const x = 1;');
  });

  it('should convert bullet lists correctly', () => {
    const template = {
      title: 'Test',
      blocks: [
        { type: 'bulletList', content: '- Item 1\n- Item 2' },
      ],
    };

    const result = templateToEditorContent(template);
    const list = result.content[0] as any;

    expect(list.type).toBe('bulletList');
    expect(list.content).toHaveLength(2);
    expect(list.content[0].type).toBe('listItem');
  });

  it('should convert callout blocks correctly', () => {
    const template = {
      title: 'Test',
      blocks: [
        { type: 'callout', content: 'Important note', attrs: { type: 'warning' } },
      ],
    };

    const result = templateToEditorContent(template);
    const callout = result.content[0] as any;

    expect(callout.type).toBe('callout');
    expect(callout.attrs.type).toBe('warning');
  });

  it('should handle tutorial template', () => {
    const tutorialTemplate = DIATAXIS_INFO.tutorial.template;
    const result = templateToEditorContent(tutorialTemplate);

    expect(result.type).toBe('doc');
    expect(result.content.length).toBeGreaterThan(0);
  });

  it('should handle how-to template', () => {
    const howToTemplate = DIATAXIS_INFO.how_to.template;
    const result = templateToEditorContent(howToTemplate);

    expect(result.type).toBe('doc');
    expect(result.content.length).toBeGreaterThan(0);
  });

  it('should handle reference template', () => {
    const refTemplate = DIATAXIS_INFO.reference.template;
    const result = templateToEditorContent(refTemplate);

    expect(result.type).toBe('doc');
    expect(result.content.length).toBeGreaterThan(0);
  });

  it('should handle explanation template', () => {
    const explTemplate = DIATAXIS_INFO.explanation.template;
    const result = templateToEditorContent(explTemplate);

    expect(result.type).toBe('doc');
    expect(result.content.length).toBeGreaterThan(0);
  });
});
