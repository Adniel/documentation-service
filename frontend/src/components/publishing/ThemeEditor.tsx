/**
 * ThemeEditor - Theme customization editor for published sites.
 *
 * Allows editing colors, typography, and layout settings for themes.
 *
 * Sprint A: Publishing
 */

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  publishingApi,
  type Theme,
  type ThemeCreate,
  type ThemeUpdate,
  type SidebarPosition,
  type ContentWidth,
} from '../../lib/api';

interface ThemeEditorProps {
  organizationId: string;
  themeId?: string;
  onClose: () => void;
  onSaved?: (theme: Theme) => void;
}

const defaultTheme: ThemeCreate = {
  name: '',
  description: '',
  primary_color: '#2563eb',
  secondary_color: '#4f46e5',
  accent_color: '#06b6d4',
  background_color: '#ffffff',
  surface_color: '#f9fafb',
  text_color: '#111827',
  text_muted_color: '#6b7280',
  heading_font: 'Inter, sans-serif',
  body_font: 'Inter, sans-serif',
  code_font: 'JetBrains Mono, monospace',
  base_font_size: '16px',
  sidebar_position: 'left',
  content_width: 'medium',
  toc_enabled: true,
  header_height: '64px',
};

export function ThemeEditor({ organizationId, themeId, onClose, onSaved }: ThemeEditorProps) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<ThemeCreate>(defaultTheme);
  const [activeTab, setActiveTab] = useState<'colors' | 'typography' | 'layout' | 'custom'>('colors');

  // Fetch existing theme if editing
  const { data: existingTheme, isLoading } = useQuery({
    queryKey: ['theme', themeId],
    queryFn: () => publishingApi.getTheme(themeId!),
    enabled: !!themeId,
  });

  // Populate form with existing theme data
  useEffect(() => {
    if (existingTheme) {
      setFormData({
        name: existingTheme.name,
        description: existingTheme.description || '',
        primary_color: existingTheme.primary_color,
        secondary_color: existingTheme.secondary_color,
        accent_color: existingTheme.accent_color,
        background_color: existingTheme.background_color,
        surface_color: existingTheme.surface_color,
        text_color: existingTheme.text_color,
        text_muted_color: existingTheme.text_muted_color,
        heading_font: existingTheme.heading_font,
        body_font: existingTheme.body_font,
        code_font: existingTheme.code_font,
        base_font_size: existingTheme.base_font_size,
        sidebar_position: existingTheme.sidebar_position,
        content_width: existingTheme.content_width,
        toc_enabled: existingTheme.toc_enabled,
        header_height: existingTheme.header_height,
        logo_url: existingTheme.logo_url || '',
        favicon_url: existingTheme.favicon_url || '',
        custom_css: existingTheme.custom_css || '',
        custom_head_html: existingTheme.custom_head_html || '',
      });
    }
  }, [existingTheme]);

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: ThemeCreate) => publishingApi.createTheme(organizationId, data),
    onSuccess: (theme) => {
      queryClient.invalidateQueries({ queryKey: ['themes'] });
      onSaved?.(theme);
      onClose();
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data: ThemeUpdate) => publishingApi.updateTheme(themeId!, data),
    onSuccess: (theme) => {
      queryClient.invalidateQueries({ queryKey: ['themes'] });
      onSaved?.(theme);
      onClose();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (themeId) {
      updateMutation.mutate(formData);
    } else {
      createMutation.mutate(formData);
    }
  };

  const updateField = <K extends keyof ThemeCreate>(field: K, value: ThemeCreate[K]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-medium text-gray-900">
            {themeId ? 'Edit Theme' : 'Create Theme'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="flex h-[calc(90vh-140px)]">
            {/* Sidebar with tabs */}
            <div className="w-48 border-r border-gray-200 bg-gray-50 p-4">
              <nav className="space-y-1">
                {(['colors', 'typography', 'layout', 'custom'] as const).map((tab) => (
                  <button
                    key={tab}
                    type="button"
                    onClick={() => setActiveTab(tab)}
                    className={`w-full text-left px-3 py-2 text-sm font-medium rounded-md transition ${
                      activeTab === tab
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </button>
                ))}
              </nav>
            </div>

            {/* Main content */}
            <div className="flex-1 overflow-y-auto p-6">
              {/* Basic Info (always shown) */}
              <div className="mb-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Theme Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => updateField('name', e.target.value)}
                    placeholder="My Custom Theme"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <input
                    type="text"
                    value={formData.description}
                    onChange={(e) => updateField('description', e.target.value)}
                    placeholder="A brief description of this theme"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
                  />
                </div>
              </div>

              {/* Colors Tab */}
              {activeTab === 'colors' && (
                <div className="space-y-4">
                  <h3 className="text-sm font-medium text-gray-900">Color Palette</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <ColorInput
                      label="Primary Color"
                      value={formData.primary_color || ''}
                      onChange={(v) => updateField('primary_color', v)}
                    />
                    <ColorInput
                      label="Secondary Color"
                      value={formData.secondary_color || ''}
                      onChange={(v) => updateField('secondary_color', v)}
                    />
                    <ColorInput
                      label="Accent Color"
                      value={formData.accent_color || ''}
                      onChange={(v) => updateField('accent_color', v)}
                    />
                    <ColorInput
                      label="Background Color"
                      value={formData.background_color || ''}
                      onChange={(v) => updateField('background_color', v)}
                    />
                    <ColorInput
                      label="Surface Color"
                      value={formData.surface_color || ''}
                      onChange={(v) => updateField('surface_color', v)}
                    />
                    <ColorInput
                      label="Text Color"
                      value={formData.text_color || ''}
                      onChange={(v) => updateField('text_color', v)}
                    />
                    <ColorInput
                      label="Muted Text Color"
                      value={formData.text_muted_color || ''}
                      onChange={(v) => updateField('text_muted_color', v)}
                    />
                  </div>

                  {/* Preview */}
                  <div className="mt-6 p-4 rounded-lg border border-gray-200">
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Preview</h4>
                    <div
                      className="p-4 rounded-lg"
                      style={{ backgroundColor: formData.background_color }}
                    >
                      <div
                        className="p-4 rounded"
                        style={{ backgroundColor: formData.surface_color }}
                      >
                        <h5
                          className="text-lg font-semibold mb-2"
                          style={{ color: formData.text_color }}
                        >
                          Sample Heading
                        </h5>
                        <p style={{ color: formData.text_muted_color }}>
                          This is some sample muted text.
                        </p>
                        <button
                          type="button"
                          className="mt-3 px-4 py-2 rounded-md text-white text-sm"
                          style={{ backgroundColor: formData.primary_color }}
                        >
                          Primary Button
                        </button>
                        <button
                          type="button"
                          className="mt-3 ml-2 px-4 py-2 rounded-md text-white text-sm"
                          style={{ backgroundColor: formData.accent_color }}
                        >
                          Accent Button
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Typography Tab */}
              {activeTab === 'typography' && (
                <div className="space-y-4">
                  <h3 className="text-sm font-medium text-gray-900">Typography</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Heading Font
                      </label>
                      <select
                        value={formData.heading_font}
                        onChange={(e) => updateField('heading_font', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900"
                      >
                        <option value="Inter, sans-serif">Inter</option>
                        <option value="system-ui, sans-serif">System UI</option>
                        <option value="Georgia, serif">Georgia</option>
                        <option value="'Playfair Display', serif">Playfair Display</option>
                        <option value="'Roboto', sans-serif">Roboto</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Body Font
                      </label>
                      <select
                        value={formData.body_font}
                        onChange={(e) => updateField('body_font', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900"
                      >
                        <option value="Inter, sans-serif">Inter</option>
                        <option value="system-ui, sans-serif">System UI</option>
                        <option value="Georgia, serif">Georgia</option>
                        <option value="'Lora', serif">Lora</option>
                        <option value="'Roboto', sans-serif">Roboto</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Code Font
                      </label>
                      <select
                        value={formData.code_font}
                        onChange={(e) => updateField('code_font', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900"
                      >
                        <option value="'JetBrains Mono', monospace">JetBrains Mono</option>
                        <option value="'Fira Code', monospace">Fira Code</option>
                        <option value="'Source Code Pro', monospace">Source Code Pro</option>
                        <option value="Menlo, monospace">Menlo</option>
                        <option value="monospace">System Monospace</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Base Font Size
                      </label>
                      <select
                        value={formData.base_font_size}
                        onChange={(e) => updateField('base_font_size', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900"
                      >
                        <option value="14px">14px (Small)</option>
                        <option value="16px">16px (Normal)</option>
                        <option value="18px">18px (Large)</option>
                        <option value="20px">20px (Extra Large)</option>
                      </select>
                    </div>
                  </div>

                  {/* Typography Preview */}
                  <div className="mt-6 p-4 rounded-lg border border-gray-200">
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Preview</h4>
                    <div style={{ fontSize: formData.base_font_size }}>
                      <h1 style={{ fontFamily: formData.heading_font }} className="text-2xl font-bold mb-2">
                        Heading Text
                      </h1>
                      <p style={{ fontFamily: formData.body_font }} className="mb-2">
                        This is body text. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                      </p>
                      <code
                        style={{ fontFamily: formData.code_font }}
                        className="bg-gray-100 px-2 py-1 rounded text-sm"
                      >
                        const code = "example";
                      </code>
                    </div>
                  </div>
                </div>
              )}

              {/* Layout Tab */}
              {activeTab === 'layout' && (
                <div className="space-y-4">
                  <h3 className="text-sm font-medium text-gray-900">Layout</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Sidebar Position
                      </label>
                      <select
                        value={formData.sidebar_position}
                        onChange={(e) => updateField('sidebar_position', e.target.value as SidebarPosition)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900"
                      >
                        <option value="left">Left</option>
                        <option value="right">Right</option>
                        <option value="none">None (Full Width)</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Content Width
                      </label>
                      <select
                        value={formData.content_width}
                        onChange={(e) => updateField('content_width', e.target.value as ContentWidth)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900"
                      >
                        <option value="narrow">Narrow (640px)</option>
                        <option value="medium">Medium (768px)</option>
                        <option value="wide">Wide (1024px)</option>
                        <option value="full">Full Width</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Header Height
                      </label>
                      <select
                        value={formData.header_height}
                        onChange={(e) => updateField('header_height', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900"
                      >
                        <option value="48px">Compact (48px)</option>
                        <option value="64px">Normal (64px)</option>
                        <option value="80px">Tall (80px)</option>
                      </select>
                    </div>
                    <div className="flex items-center">
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={formData.toc_enabled}
                          onChange={(e) => updateField('toc_enabled', e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-700">Show Table of Contents</span>
                      </label>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Logo URL
                      </label>
                      <input
                        type="url"
                        value={formData.logo_url || ''}
                        onChange={(e) => updateField('logo_url', e.target.value)}
                        placeholder="https://example.com/logo.png"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Favicon URL
                      </label>
                      <input
                        type="url"
                        value={formData.favicon_url || ''}
                        onChange={(e) => updateField('favicon_url', e.target.value)}
                        placeholder="https://example.com/favicon.ico"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Custom Tab */}
              {activeTab === 'custom' && (
                <div className="space-y-4">
                  <h3 className="text-sm font-medium text-gray-900">Custom Styles</h3>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Custom CSS
                    </label>
                    <textarea
                      value={formData.custom_css || ''}
                      onChange={(e) => updateField('custom_css', e.target.value)}
                      rows={10}
                      placeholder="/* Add custom CSS here */"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md font-mono text-sm bg-white text-gray-900"
                    />
                    <p className="mt-1 text-xs text-gray-500">
                      CSS will be injected into the published site. Use with caution.
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Custom Head HTML
                    </label>
                    <textarea
                      value={formData.custom_head_html || ''}
                      onChange={(e) => updateField('custom_head_html', e.target.value)}
                      rows={5}
                      placeholder="<!-- Add custom head elements here -->"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md font-mono text-sm bg-white text-gray-900"
                    />
                    <p className="mt-1 text-xs text-gray-500">
                      HTML will be added to the &lt;head&gt; section. Use for external fonts, scripts, etc.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!formData.name || isSubmitting}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {isSubmitting ? 'Saving...' : themeId ? 'Update Theme' : 'Create Theme'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Color input component with preview
interface ColorInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
}

function ColorInput({ label, value, onChange }: ColorInputProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <div className="flex gap-2">
        <input
          type="color"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="h-10 w-12 rounded border border-gray-300 cursor-pointer"
        />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="#000000"
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm bg-white text-gray-900"
        />
      </div>
    </div>
  );
}

export default ThemeEditor;
