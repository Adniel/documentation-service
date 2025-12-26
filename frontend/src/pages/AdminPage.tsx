/**
 * AdminPage - Administrative dashboard for platform management.
 *
 * Provides access to assessment management, document control, and training reports.
 *
 * Sprint 9.5: Admin UI
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { AssessmentAdminList, AssessmentBuilder, CompletionReport } from '../components/learning';
import { DocumentControlDashboard } from '../components/document-control';
import type { Assessment } from '../lib/api';

type AdminTab = 'assessments' | 'document-control' | 'training-reports';

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<AdminTab>('assessments');
  const [editingAssessment, setEditingAssessment] = useState<Assessment | null>(null);
  const [creatingAssessment, setCreatingAssessment] = useState(false);

  const tabs: { id: AdminTab; label: string; icon: React.ReactNode }[] = [
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
      id: 'training-reports',
      label: 'Training Reports',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
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

        {activeTab === 'training-reports' && <CompletionReport />}
      </div>
    </div>
  );
}
