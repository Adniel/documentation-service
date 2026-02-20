/**
 * Discovery Settings Component
 *
 * Sprint D: Integrated Access Control
 *
 * Configures how restricted content appears:
 * - Site-level default behavior
 * - Page-level overrides
 * - Placeholder message customization
 */

import React, { useState, useEffect } from 'react';
import {
  Eye,
  EyeOff,
  Lock,
  Settings,
  AlertCircle,
  Info,
  Save,
  RefreshCw,
  FileText,
} from 'lucide-react';

interface DiscoverySettingsProps {
  siteId: string;
  currentSettings: {
    show_restricted_as_placeholder: boolean;
    restricted_placeholder_message: string | null;
  };
  onSave: (settings: {
    show_restricted_as_placeholder: boolean;
    restricted_placeholder_message: string | null;
  }) => Promise<void>;
}

interface PageOverride {
  page_id: string;
  page_title: string;
  show_when_restricted: boolean | null;
}

export function DiscoverySettings({
  siteId,
  currentSettings,
  onSave,
}: DiscoverySettingsProps) {
  const [showPlaceholder, setShowPlaceholder] = useState(
    currentSettings.show_restricted_as_placeholder
  );
  const [placeholderMessage, setPlaceholderMessage] = useState(
    currentSettings.restricted_placeholder_message || ''
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Page overrides would be loaded from the API
  const [pageOverrides, setPageOverrides] = useState<PageOverride[]>([]);

  useEffect(() => {
    // Reset success state when settings change
    setSuccess(false);
  }, [showPlaceholder, placeholderMessage]);

  async function handleSave() {
    setSaving(true);
    setError(null);
    setSuccess(false);

    try {
      await onSave({
        show_restricted_as_placeholder: showPlaceholder,
        restricted_placeholder_message: placeholderMessage || null,
      });
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Site-level settings */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
          <h3 className="font-medium text-gray-900 flex items-center gap-2">
            <Settings className="w-4 h-4" />
            Site Discovery Behavior
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            Control how restricted content appears to visitors without access
          </p>
        </div>

        <div className="p-4 space-y-4">
          {/* Show placeholder option */}
          <div className="space-y-3">
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="radio"
                name="discovery"
                checked={!showPlaceholder}
                onChange={() => setShowPlaceholder(false)}
                className="mt-1"
              />
              <div>
                <div className="flex items-center gap-2">
                  <EyeOff className="w-4 h-4 text-gray-400" />
                  <span className="font-medium text-gray-900">
                    Hidden (Default)
                  </span>
                </div>
                <p className="text-sm text-gray-500 mt-0.5">
                  Restricted pages are completely hidden from visitors without
                  access. They won't appear in navigation or search results.
                </p>
              </div>
            </label>

            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="radio"
                name="discovery"
                checked={showPlaceholder}
                onChange={() => setShowPlaceholder(true)}
                className="mt-1"
              />
              <div>
                <div className="flex items-center gap-2">
                  <Eye className="w-4 h-4 text-gray-400" />
                  <span className="font-medium text-gray-900">
                    Show as Placeholder
                  </span>
                </div>
                <p className="text-sm text-gray-500 mt-0.5">
                  Restricted pages appear in navigation with a lock icon and
                  "Access Restricted" message. Visitors know the content exists.
                </p>
              </div>
            </label>
          </div>

          {/* Placeholder message */}
          {showPlaceholder && (
            <div className="pl-7 pt-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Placeholder Message
              </label>
              <textarea
                value={placeholderMessage}
                onChange={(e) => setPlaceholderMessage(e.target.value)}
                placeholder="You do not have access to view this content."
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                This message appears when a visitor views a restricted page
              </p>
            </div>
          )}

          {/* Preview */}
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
              Preview
            </p>
            {showPlaceholder ? (
              <div className="flex items-center gap-3 text-gray-700">
                <Lock className="w-5 h-5 text-amber-500" />
                <div>
                  <p className="font-medium">Confidential Document</p>
                  <p className="text-sm text-gray-500">
                    {placeholderMessage || 'You do not have access to view this content.'}
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3 text-gray-400 italic">
                <FileText className="w-5 h-5" />
                <span>Page will not be visible</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Info about page-level overrides */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex gap-3">
          <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-blue-800">
              Page-Level Overrides
            </p>
            <p className="text-sm text-blue-700 mt-1">
              Individual pages can override this setting. Use the page settings
              to show or hide specific pages regardless of the site default.
            </p>
          </div>
        </div>
      </div>

      {/* Error/Success messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2 text-red-700">
          <AlertCircle className="w-4 h-4" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-3 flex items-center gap-2 text-green-700">
          <Save className="w-4 h-4" />
          <span className="text-sm">Settings saved successfully</span>
        </div>
      )}

      {/* Save button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
        >
          {saving ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Save className="w-4 h-4" />
          )}
          Save Settings
        </button>
      </div>
    </div>
  );
}

/**
 * Page Discovery Override Component
 *
 * Used in page settings to override site-level discovery behavior
 */
interface PageDiscoveryOverrideProps {
  pageId: string;
  currentValue: boolean | null;
  siteDefault: boolean;
  onChange: (value: boolean | null) => void;
}

export function PageDiscoveryOverride({
  pageId,
  currentValue,
  siteDefault,
  onChange,
}: PageDiscoveryOverrideProps) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Restricted Visibility
      </label>

      <div className="space-y-2">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="radio"
            name={`page-discovery-${pageId}`}
            checked={currentValue === null}
            onChange={() => onChange(null)}
          />
          <span className="text-sm text-gray-700">
            Use site default ({siteDefault ? 'Show placeholder' : 'Hidden'})
          </span>
        </label>

        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="radio"
            name={`page-discovery-${pageId}`}
            checked={currentValue === true}
            onChange={() => onChange(true)}
          />
          <span className="text-sm text-gray-700 flex items-center gap-1">
            <Eye className="w-4 h-4 text-gray-400" />
            Always show as placeholder
          </span>
        </label>

        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="radio"
            name={`page-discovery-${pageId}`}
            checked={currentValue === false}
            onChange={() => onChange(false)}
          />
          <span className="text-sm text-gray-700 flex items-center gap-1">
            <EyeOff className="w-4 h-4 text-gray-400" />
            Always hide
          </span>
        </label>
      </div>

      <p className="text-xs text-gray-500">
        Controls how this page appears to visitors who lack access
      </p>
    </div>
  );
}

export default DiscoverySettings;
