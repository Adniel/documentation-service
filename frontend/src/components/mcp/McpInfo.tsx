/**
 * MCP Server Info Component
 *
 * Sprint C: MCP Integration
 *
 * Displays information about the MCP server for integration.
 */

import { useState, useEffect } from 'react';
import { mcpApi, type McpServerInfo } from '../../lib/api';

interface McpInfoProps {
  className?: string;
}

export function McpInfo({ className = '' }: McpInfoProps) {
  const [info, setInfo] = useState<McpServerInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedField, setCopiedField] = useState<string | null>(null);

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        setLoading(true);
        const response = await mcpApi.getInfo();
        setInfo(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load MCP info');
      } finally {
        setLoading(false);
      }
    };

    fetchInfo();
  }, []);

  const copyToClipboard = async (text: string, field: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(field);
      setTimeout(() => setCopiedField(null), 2000);
    } catch {
      // Clipboard API might not be available
    }
  };

  const getEndpointUrl = () => {
    const baseUrl = window.location.origin;
    return `${baseUrl}/api/v1${info?.endpoint || '/mcp'}`;
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-6 ${className}`}>
        <p className="text-red-700">{error}</p>
      </div>
    );
  }

  if (!info) return null;

  return (
    <div className={`bg-white rounded-lg border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900">{info.name}</h3>
            <p className="text-sm text-gray-500">{info.description}</p>
          </div>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            v{info.version}
          </span>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Connection Details */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Connection Details</h4>
          <div className="space-y-3">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Endpoint URL</label>
              <div className="flex items-center gap-2">
                <code className="flex-1 block bg-gray-100 px-3 py-2 rounded-md text-sm font-mono text-gray-800 overflow-x-auto">
                  {getEndpointUrl()}
                </code>
                <button
                  onClick={() => copyToClipboard(getEndpointUrl(), 'endpoint')}
                  className="p-2 text-gray-400 hover:text-gray-600"
                  title="Copy to clipboard"
                >
                  {copiedField === 'endpoint' ? (
                    <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs text-gray-500 mb-1">Protocol Version</label>
              <code className="block bg-gray-100 px-3 py-2 rounded-md text-sm font-mono text-gray-800">
                {info.protocol_version}
              </code>
            </div>

            <div>
              <label className="block text-xs text-gray-500 mb-1">Authentication</label>
              <code className="block bg-gray-100 px-3 py-2 rounded-md text-sm font-mono text-gray-800">
                {info.authentication.header}: {info.authentication.format}
              </code>
            </div>
          </div>
        </div>

        {/* Available Tools */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Available Tools</h4>
          <div className="flex flex-wrap gap-2">
            {info.tools.map((tool) => (
              <span
                key={tool}
                className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-blue-100 text-blue-800"
              >
                {tool}
              </span>
            ))}
          </div>
        </div>

        {/* Example Request */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Example Request</h4>
          <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
            <pre className="text-sm text-gray-100 font-mono">
{`curl -X POST ${getEndpointUrl()} \\
  -H "Authorization: Bearer dsk_your_api_key" \\
  -H "Content-Type: application/json" \\
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'`}
            </pre>
          </div>
          <button
            onClick={() => copyToClipboard(
              `curl -X POST ${getEndpointUrl()} \\\n  -H "Authorization: Bearer dsk_your_api_key" \\\n  -H "Content-Type: application/json" \\\n  -d '{\n    "jsonrpc": "2.0",\n    "id": 1,\n    "method": "tools/list"\n  }'`,
              'example'
            )}
            className="mt-2 text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            {copiedField === 'example' ? (
              <>
                <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Copied!
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy example
              </>
            )}
          </button>
        </div>

        {/* Claude Code Configuration */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Claude Code MCP Configuration</h4>
          <p className="text-sm text-gray-500 mb-2">
            Add this to your Claude Code MCP settings to connect:
          </p>
          <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
            <pre className="text-sm text-gray-100 font-mono">
{`{
  "mcpServers": {
    "docservice": {
      "url": "${getEndpointUrl()}",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer dsk_your_api_key"
      }
    }
  }
}`}
            </pre>
          </div>
          <button
            onClick={() => copyToClipboard(
              JSON.stringify({
                mcpServers: {
                  docservice: {
                    url: getEndpointUrl(),
                    transport: "http",
                    headers: {
                      Authorization: "Bearer dsk_your_api_key"
                    }
                  }
                }
              }, null, 2),
              'config'
            )}
            className="mt-2 text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            {copiedField === 'config' ? (
              <>
                <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Copied!
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy configuration
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
