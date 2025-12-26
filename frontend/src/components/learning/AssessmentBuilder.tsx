/**
 * AssessmentBuilder - Main assessment configuration panel.
 *
 * Allows admins to create and edit assessments with settings and questions.
 *
 * Sprint 9.5: Admin UI
 */

import { useState, useEffect, useCallback } from 'react';
import {
  learningApi,
  type Assessment,
  type AssessmentQuestion,
  type QuestionType,
} from '../../lib/api';
import { QuestionEditor, type QuestionFormData } from './QuestionEditor';

interface AssessmentBuilderProps {
  assessmentId?: string;
  pageId?: string;
  pageTitle?: string;
  onSave?: (assessment: Assessment) => void;
  onCancel?: () => void;
}

interface AssessmentFormData {
  title: string;
  description: string;
  passing_score: number;
  max_attempts: number | null;
  time_limit_minutes: number | null;
  is_active: boolean;
}

export function AssessmentBuilder({
  assessmentId,
  pageId,
  pageTitle,
  onSave,
  onCancel,
}: AssessmentBuilderProps) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);

  const [formData, setFormData] = useState<AssessmentFormData>({
    title: '',
    description: '',
    passing_score: 80,
    max_attempts: null,
    time_limit_minutes: null,
    is_active: true,
  });

  const [editingQuestion, setEditingQuestion] = useState<AssessmentQuestion | null>(null);
  const [isAddingQuestion, setIsAddingQuestion] = useState(false);
  const [activeTab, setActiveTab] = useState<'settings' | 'questions'>('settings');

  const loadAssessment = useCallback(async () => {
    if (!assessmentId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await learningApi.getAssessment(assessmentId);
      setAssessment(data);
      setQuestions(data.questions || []);
      setFormData({
        title: data.title,
        description: data.description || '',
        passing_score: data.passing_score,
        max_attempts: data.max_attempts || null,
        time_limit_minutes: data.time_limit_minutes || null,
        is_active: data.is_active,
      });
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to load assessment');
    } finally {
      setLoading(false);
    }
  }, [assessmentId]);

  useEffect(() => {
    loadAssessment();
  }, [loadAssessment]);

  const handleSaveSettings = async () => {
    if (!formData.title.trim()) {
      setError('Title is required');
      return;
    }

    setSaving(true);
    setError(null);

    try {
      let savedAssessment: Assessment;

      if (assessment) {
        // Update existing
        savedAssessment = await learningApi.updateAssessment(assessment.id, {
          title: formData.title,
          description: formData.description || undefined,
          passing_score: formData.passing_score,
          max_attempts: formData.max_attempts || undefined,
          time_limit_minutes: formData.time_limit_minutes || undefined,
          is_active: formData.is_active,
        });
      } else if (pageId) {
        // Create new
        savedAssessment = await learningApi.createAssessment({
          page_id: pageId,
          title: formData.title,
          description: formData.description || undefined,
          passing_score: formData.passing_score,
          max_attempts: formData.max_attempts || undefined,
          time_limit_minutes: formData.time_limit_minutes || undefined,
        });
        setAssessment(savedAssessment);
      } else {
        throw new Error('No page ID provided');
      }

      onSave?.(savedAssessment);
      setActiveTab('questions');
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to save assessment');
    } finally {
      setSaving(false);
    }
  };

  const handleAddQuestion = async (data: QuestionFormData) => {
    if (!assessment) return;

    try {
      const question = await learningApi.addQuestion(assessment.id, {
        question_type: data.question_type,
        question_text: data.question_text,
        options: data.options,
        correct_answer: data.correct_answer,
        points: data.points,
        explanation: data.explanation,
      });
      setQuestions([...questions, question]);
      setIsAddingQuestion(false);
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to add question');
    }
  };

  const handleUpdateQuestion = async (data: QuestionFormData) => {
    if (!editingQuestion) return;

    try {
      const updated = await learningApi.updateQuestion(editingQuestion.id, {
        question_type: data.question_type,
        question_text: data.question_text,
        options: data.options,
        correct_answer: data.correct_answer,
        points: data.points,
        explanation: data.explanation,
      });
      setQuestions(questions.map((q) => (q.id === updated.id ? updated : q)));
      setEditingQuestion(null);
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to update question');
    }
  };

  const handleDeleteQuestion = async (questionId: string) => {
    if (!confirm('Are you sure you want to delete this question?')) return;

    try {
      await learningApi.deleteQuestion(questionId);
      setQuestions(questions.filter((q) => q.id !== questionId));
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to delete question');
    }
  };

  const moveQuestion = async (questionId: string, direction: 'up' | 'down') => {
    const index = questions.findIndex((q) => q.id === questionId);
    if (index === -1) return;

    const newIndex = direction === 'up' ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= questions.length) return;

    const newQuestions = [...questions];
    [newQuestions[index], newQuestions[newIndex]] = [newQuestions[newIndex], newQuestions[index]];

    setQuestions(newQuestions);

    // Save new order to backend
    if (assessment) {
      try {
        await learningApi.reorderQuestions(
          assessment.id,
          newQuestions.map((q) => q.id)
        );
      } catch (err) {
        // Revert on error
        setQuestions(questions);
        const error = err as { response?: { data?: { detail?: string } } };
        setError(error.response?.data?.detail || 'Failed to reorder questions');
      }
    }
  };

  const getQuestionTypeLabel = (type: QuestionType): string => {
    switch (type) {
      case 'multiple_choice':
        return 'Multiple Choice';
      case 'true_false':
        return 'True/False';
      case 'fill_blank':
        return 'Fill in Blank';
      default:
        return type;
    }
  };

  const totalPoints = questions.reduce((sum, q) => sum + q.points, 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        <span className="ml-3 text-gray-600">Loading assessment...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            {assessment ? 'Edit Assessment' : 'Create Assessment'}
          </h2>
          {pageTitle && (
            <p className="text-sm text-gray-500 mt-1">For document: {pageTitle}</p>
          )}
        </div>
        {onCancel && (
          <button
            onClick={onCancel}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <svg className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <div className="flex-1">
            <p className="text-red-700">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-600">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-8">
          <button
            onClick={() => setActiveTab('settings')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'settings'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Settings
          </button>
          <button
            onClick={() => setActiveTab('questions')}
            disabled={!assessment}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'questions'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            } ${!assessment ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            Questions ({questions.length})
          </button>
        </nav>
      </div>

      {/* Settings Tab */}
      {activeTab === 'settings' && (
        <div className="bg-white p-6 rounded-lg border border-gray-200 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Assessment Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., SOP-001 Training Quiz"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Brief description of what this assessment covers..."
            />
          </div>

          <div className="grid grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Passing Score (%)
              </label>
              <input
                type="number"
                min={0}
                max={100}
                value={formData.passing_score}
                onChange={(e) =>
                  setFormData({ ...formData, passing_score: parseInt(e.target.value) || 0 })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="mt-1 text-xs text-gray-500">Default: 80%</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Attempts
              </label>
              <input
                type="number"
                min={1}
                value={formData.max_attempts || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    max_attempts: e.target.value ? parseInt(e.target.value) : null,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Unlimited"
              />
              <p className="mt-1 text-xs text-gray-500">Leave empty for unlimited</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Time Limit (minutes)
              </label>
              <input
                type="number"
                min={1}
                value={formData.time_limit_minutes || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    time_limit_minutes: e.target.value ? parseInt(e.target.value) : null,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="No limit"
              />
              <p className="mt-1 text-xs text-gray-500">Leave empty for no time limit</p>
            </div>
          </div>

          {assessment && (
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
                Assessment is active (users can take it)
              </label>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            {onCancel && (
              <button
                onClick={onCancel}
                disabled={saving}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
            )}
            <button
              onClick={handleSaveSettings}
              disabled={saving || !formData.title.trim()}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              {saving && (
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              )}
              {assessment ? 'Save Settings' : 'Create Assessment'}
            </button>
          </div>
        </div>
      )}

      {/* Questions Tab */}
      {activeTab === 'questions' && assessment && (
        <div className="space-y-4">
          {/* Summary */}
          <div className="bg-gray-50 p-4 rounded-lg flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div>
                <span className="text-2xl font-bold text-gray-900">{questions.length}</span>
                <span className="text-sm text-gray-500 ml-1">questions</span>
              </div>
              <div>
                <span className="text-2xl font-bold text-gray-900">{totalPoints}</span>
                <span className="text-sm text-gray-500 ml-1">total points</span>
              </div>
              <div>
                <span className="text-2xl font-bold text-gray-900">{formData.passing_score}%</span>
                <span className="text-sm text-gray-500 ml-1">to pass</span>
              </div>
            </div>
            <button
              onClick={() => setIsAddingQuestion(true)}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add Question
            </button>
          </div>

          {/* Add/Edit Question Form */}
          {(isAddingQuestion || editingQuestion) && (
            <QuestionEditor
              question={editingQuestion || undefined}
              onSave={editingQuestion ? handleUpdateQuestion : handleAddQuestion}
              onCancel={() => {
                setIsAddingQuestion(false);
                setEditingQuestion(null);
              }}
            />
          )}

          {/* Questions List */}
          {questions.length === 0 && !isAddingQuestion ? (
            <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="mt-4 text-lg font-medium text-gray-900">No questions yet</h3>
              <p className="mt-2 text-sm text-gray-500">Get started by adding your first question.</p>
              <button
                onClick={() => setIsAddingQuestion(true)}
                className="mt-4 px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-md"
              >
                Add your first question
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {questions.map((question, index) => (
                <div
                  key={question.id}
                  className="bg-white p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
                >
                  <div className="flex items-start gap-4">
                    {/* Order Controls */}
                    <div className="flex flex-col gap-1">
                      <button
                        onClick={() => moveQuestion(question.id, 'up')}
                        disabled={index === 0}
                        className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                        </svg>
                      </button>
                      <span className="text-sm font-medium text-gray-500 text-center">{index + 1}</span>
                      <button
                        onClick={() => moveQuestion(question.id, 'down')}
                        disabled={index === questions.length - 1}
                        className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                    </div>

                    {/* Question Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-600 rounded">
                          {getQuestionTypeLabel(question.question_type)}
                        </span>
                        <span className="text-xs text-gray-500">{question.points} pts</span>
                      </div>
                      <p className="text-gray-900 line-clamp-2">{question.question_text}</p>
                      {question.question_type === 'multiple_choice' && question.options && (
                        <div className="mt-2 flex flex-wrap gap-2">
                          {question.options.map((opt) => (
                            <span
                              key={opt.id}
                              className={`text-xs px-2 py-1 rounded ${
                                opt.is_correct
                                  ? 'bg-green-100 text-green-700'
                                  : 'bg-gray-100 text-gray-600'
                              }`}
                            >
                              {opt.id.toUpperCase()}: {opt.text.substring(0, 30)}
                              {opt.text.length > 30 ? '...' : ''}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setEditingQuestion(question)}
                        className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => handleDeleteQuestion(question.id)}
                        className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default AssessmentBuilder;
