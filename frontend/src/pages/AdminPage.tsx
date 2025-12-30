/**
 * AdminPage - Administrative dashboard for platform management.
 *
 * Provides access to assessment management, document control, training reports,
 * and Git remote configuration.
 *
 * Sprint 9.5: Admin UI
 * Sprint 13: Git Remote Support
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { AssessmentAdminList, AssessmentBuilder, CompletionReport } from '../components/learning';
import {
  DocumentControlDashboard,
  PendingApprovalsPanel,
  ApprovalMatrixEditor,
} from '../components/document-control';
import { RemoteConfigPanel, SyncStatusBadge, SyncHistoryList } from '../components/git';
import { SiteConfigPanel, ThemeEditor } from '../components/publishing';
import { UserManagementPanel, OrganizationSettingsPanel, AuditLogPanel } from '../components/admin';
import { organizationApi, publishingApi, type Assessment } from '../lib/api';

type AdminTab = 'users' | 'organization' | 'audit' | 'assessments' | 'document-control' | 'approvals' | 'training-reports' | 'git-remote' | 'publishing';

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<AdminTab>('users');
  const [editingAssessment, setEditingAssessment] = useState<Assessment | null>(null);
  const [creatingAssessment, setCreatingAssessment] = useState(false);
  const [showMatrixEditor, setShowMatrixEditor] = useState(false);
  const [selectedOrgId, setSelectedOrgId] = useState<string>('');
  const [showThemeEditor, setShowThemeEditor] = useState(false);
  const [editingThemeId, setEditingThemeId] = useState<string | undefined>(undefined);

  // Fetch organizations for Git Remote tab
  const { data: organizations = [] } = useQuery({
    queryKey: ['organizations'],
    queryFn: organizationApi.list,
  });

  // Set first organization as default
  useEffect(() => {
    if (!selectedOrgId && organizations.length > 0) {
      setSelectedOrgId(organizations[0].id);
    }
  }, [selectedOrgId, organizations]);

  const tabs: { id: AdminTab; label: string; icon: React.ReactNode }[] = [
    {
      id: 'users',
      label: 'Users',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      ),
    },
    {
      id: 'organization',
      label: 'Organization',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      ),
    },
    {
      id: 'audit',
      label: 'Audit Trail',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
      ),
    },
    {
      id: 'assessments',
      label: 'Assessments',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
        </svg>
      ),
    },
    {
      id: 'document-control',
      label: 'Document Control',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
    },
    {
      id: 'approvals',
      label: 'Approvals',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    {
      id: 'training-reports',
      label: 'Training Reports',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
    },
    {
      id: 'git-remote',
      label: 'Git Remote',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      ),
    },
    {
      id: 'publishing',
      label: 'Publishing',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
        </svg>
      ),
    },
  ];

  const handleEditAssessment = (assessment: Assessment) => {
    setEditingAssessment(assessment);
    setCreatingAssessment(false);
  };

  const handleCreateAssessment = () => {
    setCreatingAssessment(true);
    setEditingAssessment(null);
  };

  const handleCloseBuilder = () => {
    setEditingAssessment(null);
    setCreatingAssessment(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link to="/" className="text-gray-500 hover:text-gray-700">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </Link>
              <h1 className="text-xl font-semibold text-gray-900">Administration</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="flex gap-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  handleCloseBuilder();
                }}
                className={`flex items-center gap-2 pb-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'assessments' && (
          <div>
            {editingAssessment ? (
              <AssessmentBuilder
                assessmentId={editingAssessment.id}
                onCancel={handleCloseBuilder}
                onSave={handleCloseBuilder}
              />
            ) : creatingAssessment ? (
              <div className="space-y-4">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-sm text-yellow-800">
                    To create an assessment, first navigate to a document and create an assessment for it.
                    Assessments are linked to specific documents.
                  </p>
                </div>
                <button
                  onClick={handleCloseBuilder}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Back to List
                </button>
              </div>
            ) : (
              <AssessmentAdminList
                onEdit={handleEditAssessment}
                onCreate={handleCreateAssessment}
              />
            )}
          </div>
        )}

        {activeTab === 'document-control' && <DocumentControlDashboard />}

        {activeTab === 'approvals' && (
          <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">Approval Workflows</h2>
              <button
                onClick={() => setShowMatrixEditor(true)}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition"
              >
                Create Approval Matrix
              </button>
            </div>

            {/* Pending Approvals */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-md font-medium text-gray-900 mb-4">My Pending Approvals</h3>
              <PendingApprovalsPanel />
            </div>

            {/* Approval Matrix Editor Modal */}
            {showMatrixEditor && (
              <ApprovalMatrixEditor
                onClose={() => setShowMatrixEditor(false)}
                onSaved={() => setShowMatrixEditor(false)}
              />
            )}
          </div>
        )}

        {activeTab === 'training-reports' && <CompletionReport />}

        {activeTab === 'users' && (
          <div className="space-y-6">
            {/* Organization Selector */}
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center gap-4">
                <label className="text-sm font-medium text-gray-700">
                  Organization:
                </label>
                <select
                  value={selectedOrgId}
                  onChange={(e) => setSelectedOrgId(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                >
                  {organizations.map((org) => (
                    <option key={org.id} value={org.id}>
                      {org.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {selectedOrgId ? (
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-lg font-medium text-gray-900">Members</h2>
                  <p className="mt-1 text-sm text-gray-500">
                    Manage users and their roles within your organization
                  </p>
                </div>
                <div className="p-6">
                  <UserManagementPanel organizationId={selectedOrgId} />
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
                <p>No organizations available. Please create an organization first.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'organization' && (
          <div className="space-y-6">
            {/* Organization Selector */}
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center gap-4">
                <label className="text-sm font-medium text-gray-700">
                  Organization:
                </label>
                <select
                  value={selectedOrgId}
                  onChange={(e) => setSelectedOrgId(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                >
                  {organizations.map((org) => (
                    <option key={org.id} value={org.id}>
                      {org.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {selectedOrgId ? (
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-lg font-medium text-gray-900">Organization Settings</h2>
                  <p className="mt-1 text-sm text-gray-500">
                    Configure your organization&apos;s preferences and defaults
                  </p>
                </div>
                <div className="p-6">
                  <OrganizationSettingsPanel organizationId={selectedOrgId} />
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
                <p>No organizations available. Please create an organization first.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'audit' && (
          <div className="space-y-6">
            {/* Organization Selector */}
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center gap-4">
                <label className="text-sm font-medium text-gray-700">
                  Organization:
                </label>
                <select
                  value={selectedOrgId}
                  onChange={(e) => setSelectedOrgId(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                >
                  {organizations.map((org) => (
                    <option key={org.id} value={org.id}>
                      {org.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {selectedOrgId ? (
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-lg font-medium text-gray-900">Audit Trail</h2>
                  <p className="mt-1 text-sm text-gray-500">
                    View and export audit events for compliance reporting
                  </p>
                </div>
                <div className="p-6">
                  <AuditLogPanel organizationId={selectedOrgId} />
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
                <p>No organizations available. Please create an organization first.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'git-remote' && (
          <div className="space-y-6">
            {/* Organization Selector */}
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center gap-4">
                <label className="text-sm font-medium text-gray-700">
                  Organization:
                </label>
                <select
                  value={selectedOrgId}
                  onChange={(e) => setSelectedOrgId(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                >
                  {organizations.map((org) => (
                    <option key={org.id} value={org.id}>
                      {org.name}
                    </option>
                  ))}
                </select>
                {selectedOrgId && (
                  <SyncStatusBadge organizationId={selectedOrgId} showSyncButton />
                )}
              </div>
            </div>

            {selectedOrgId ? (
              <>
                {/* Remote Configuration */}
                <div className="bg-white rounded-lg shadow">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-lg font-medium text-gray-900">Remote Configuration</h2>
                    <p className="mt-1 text-sm text-gray-500">
                      Configure Git remote sync for backup or collaboration
                    </p>
                  </div>
                  <div className="p-6">
                    <RemoteConfigPanel organizationId={selectedOrgId} />
                  </div>
                </div>

                {/* Sync History */}
                <div className="bg-white rounded-lg shadow">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-lg font-medium text-gray-900">Sync History</h2>
                    <p className="mt-1 text-sm text-gray-500">
                      Recent sync operations and their status
                    </p>
                  </div>
                  <div className="p-6">
                    <SyncHistoryList organizationId={selectedOrgId} limit={20} />
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
                <p>No organizations available. Please create an organization first.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'publishing' && (
          <div className="space-y-6">
            {/* Organization Selector */}
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center gap-4">
                <label className="text-sm font-medium text-gray-700">
                  Organization:
                </label>
                <select
                  value={selectedOrgId}
                  onChange={(e) => setSelectedOrgId(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                >
                  {organizations.map((org) => (
                    <option key={org.id} value={org.id}>
                      {org.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {selectedOrgId ? (
              <>
                {/* Sites Configuration */}
                <div className="bg-white rounded-lg shadow">
                  <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-medium text-gray-900">Published Sites</h2>
                      <p className="mt-1 text-sm text-gray-500">
                        Create and manage documentation sites for your spaces
                      </p>
                    </div>
                  </div>
                  <div className="p-6">
                    <SiteConfigPanel organizationId={selectedOrgId} />
                  </div>
                </div>

                {/* Themes */}
                <div className="bg-white rounded-lg shadow">
                  <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-medium text-gray-900">Themes</h2>
                      <p className="mt-1 text-sm text-gray-500">
                        Customize the look and feel of your documentation sites
                      </p>
                    </div>
                    <button
                      onClick={() => {
                        setEditingThemeId(undefined);
                        setShowThemeEditor(true);
                      }}
                      className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition"
                    >
                      Create Theme
                    </button>
                  </div>
                  <div className="p-6">
                    <ThemeList
                      organizationId={selectedOrgId}
                      onEdit={(themeId) => {
                        setEditingThemeId(themeId);
                        setShowThemeEditor(true);
                      }}
                    />
                  </div>
                </div>

                {/* Theme Editor Modal */}
                {showThemeEditor && (
                  <ThemeEditor
                    organizationId={selectedOrgId}
                    themeId={editingThemeId}
                    onClose={() => {
                      setShowThemeEditor(false);
                      setEditingThemeId(undefined);
                    }}
                  />
                )}
              </>
            ) : (
              <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
                <p>No organizations available. Please create an organization first.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// Theme list component
function ThemeList({ organizationId, onEdit }: { organizationId: string; onEdit: (themeId: string) => void }) {
  const { data: themes = [], isLoading } = useQuery({
    queryKey: ['themes', organizationId],
    queryFn: () => publishingApi.listThemes({ organization_id: organizationId, include_system: true }),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (themes.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No themes available. Create a theme to get started.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {themes.map((theme) => (
        <div
          key={theme.id}
          className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
        >
          <div className="flex items-start justify-between">
            <div>
              <h4 className="font-medium text-gray-900">{theme.name}</h4>
              {theme.description && (
                <p className="text-sm text-gray-500 mt-1">{theme.description}</p>
              )}
              <div className="flex items-center gap-2 mt-2">
                {theme.is_default && (
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">
                    Default
                  </span>
                )}
                {!theme.organization_id && (
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                    System
                  </span>
                )}
              </div>
            </div>
            {theme.organization_id && (
              <button
                onClick={() => onEdit(theme.id)}
                className="p-1 text-gray-400 hover:text-gray-600"
                title="Edit theme"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
            )}
          </div>
          {/* Color preview */}
          <div className="flex gap-1 mt-3">
            <div
              className="w-6 h-6 rounded-full border border-gray-200"
              style={{ backgroundColor: theme.primary_color }}
              title="Primary"
            />
            <div
              className="w-6 h-6 rounded-full border border-gray-200"
              style={{ backgroundColor: theme.secondary_color }}
              title="Secondary"
            />
            <div
              className="w-6 h-6 rounded-full border border-gray-200"
              style={{ backgroundColor: theme.accent_color }}
              title="Accent"
            />
            <div
              className="w-6 h-6 rounded-full border border-gray-200"
              style={{ backgroundColor: theme.background_color }}
              title="Background"
            />
          </div>
        </div>
      ))}
    </div>
  );
}
