/**
 * QuestionEditor - Create and edit assessment questions.
 *
 * Supports multiple choice, true/false, and fill-in-blank question types.
 *
 * Sprint 9.5: Admin UI
 */

import { useState, useEffect } from 'react';
import type { QuestionType, QuestionOption, AssessmentQuestion } from '../../lib/api';

interface QuestionEditorProps {
  question?: AssessmentQuestion;
  onSave: (question: QuestionFormData) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export interface QuestionFormData {
  question_type: QuestionType;
  question_text: string;
  options?: QuestionOption[];
  correct_answer?: string;
  points: number;
  explanation?: string;
}

const DEFAULT_OPTIONS: QuestionOption[] = [
  { id: 'a', text: '', is_correct: false },
  { id: 'b', text: '', is_correct: false },
  { id: 'c', text: '', is_correct: false },
  { id: 'd', text: '', is_correct: false },
];

export function QuestionEditor({
  question,
  onSave,
  onCancel,
  isLoading = false,
}: QuestionEditorProps) {
  const [formData, setFormData] = useState<QuestionFormData>({
    question_type: 'multiple_choice',
    question_text: '',
    options: DEFAULT_OPTIONS,
    correct_answer: '',
    points: 1,
    explanation: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (question) {
      setFormData({
        question_type: question.question_type,
        question_text: question.question_text,
        options: question.options || DEFAULT_OPTIONS,
        correct_answer: question.correct_answer || '',
        points: question.points,
        explanation: question.explanation || '',
      });
    }
  }, [question]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.question_text.trim()) {
      newErrors.question_text = 'Question text is required';
    }

    if (formData.question_type === 'multiple_choice') {
      const filledOptions = formData.options?.filter((o) => o.text.trim()) || [];
      if (filledOptions.length < 2) {
        newErrors.options = 'At least 2 options are required';
      }
      const hasCorrect = formData.options?.some((o) => o.is_correct);
      if (!hasCorrect) {
        newErrors.correct = 'Select the correct answer';
      }
    }

    if (formData.question_type === 'true_false') {
      if (!formData.correct_answer) {
        newErrors.correct_answer = 'Select True or False';
      }
    }

    if (formData.question_type === 'fill_blank') {
      if (!formData.correct_answer?.trim()) {
        newErrors.correct_answer = 'Correct answer is required';
      }
    }

    if (formData.points < 1) {
      newErrors.points = 'Points must be at least 1';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setSaving(true);
    try {
      await onSave(formData);
    } finally {
      setSaving(false);
    }
  };

  const updateOption = (index: number, field: keyof QuestionOption, value: string | boolean) => {
    const newOptions = [...(formData.options || [])];
    newOptions[index] = { ...newOptions[index], [field]: value };

    // If setting this option as correct, unset others
    if (field === 'is_correct' && value === true) {
      newOptions.forEach((opt, i) => {
        if (i !== index) opt.is_correct = false;
      });
    }

    setFormData({ ...formData, options: newOptions });
  };

  const addOption = () => {
    const nextId = String.fromCharCode(97 + (formData.options?.length || 0)); // a, b, c, d...
    setFormData({
      ...formData,
      options: [...(formData.options || []), { id: nextId, text: '', is_correct: false }],
    });
  };

  const removeOption = (index: number) => {
    const newOptions = formData.options?.filter((_, i) => i !== index) || [];
    // Re-assign IDs
    newOptions.forEach((opt, i) => {
      opt.id = String.fromCharCode(97 + i);
    });
    setFormData({ ...formData, options: newOptions });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg border border-gray-200">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          {question ? 'Edit Question' : 'Add Question'}
        </h3>
        <button
          type="button"
          onClick={onCancel}
          className="text-gray-400 hover:text-gray-600"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Question Type */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Question Type</label>
        <div className="flex gap-4">
          {[
            { value: 'multiple_choice', label: 'Multiple Choice' },
            { value: 'true_false', label: 'True/False' },
            { value: 'fill_blank', label: 'Fill in Blank' },
          ].map((type) => (
            <label key={type.value} className="flex items-center">
              <input
                type="radio"
                name="question_type"
                value={type.value}
                checked={formData.question_type === type.value}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    question_type: e.target.value as QuestionType,
                    options: e.target.value === 'multiple_choice' ? DEFAULT_OPTIONS : undefined,
                    correct_answer: '',
                  })
                }
                className="mr-2"
              />
              <span className="text-sm text-gray-700">{type.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Question Text */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Question Text <span className="text-red-500">*</span>
        </label>
        <textarea
          value={formData.question_text}
          onChange={(e) => setFormData({ ...formData, question_text: e.target.value })}
          rows={3}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.question_text ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Enter your question here..."
        />
        {errors.question_text && (
          <p className="mt-1 text-sm text-red-500">{errors.question_text}</p>
        )}
      </div>

      {/* Multiple Choice Options */}
      {formData.question_type === 'multiple_choice' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Options <span className="text-red-500">*</span>
          </label>
          <div className="space-y-2">
            {formData.options?.map((option, index) => (
              <div key={option.id} className="flex items-center gap-2">
                <input
                  type="radio"
                  name="correct_option"
                  checked={option.is_correct}
                  onChange={() => updateOption(index, 'is_correct', true)}
                  title="Mark as correct answer"
                  className="h-4 w-4 text-green-600 focus:ring-green-500"
                />
                <span className="w-6 h-6 flex items-center justify-center bg-gray-100 rounded text-sm font-medium text-gray-600">
                  {option.id.toUpperCase()}
                </span>
                <input
                  type="text"
                  value={option.text}
                  onChange={(e) => updateOption(index, 'text', e.target.value)}
                  placeholder={`Option ${option.id.toUpperCase()}`}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                />
                {(formData.options?.length || 0) > 2 && (
                  <button
                    type="button"
                    onClick={() => removeOption(index)}
                    className="p-1 text-red-500 hover:bg-red-50 rounded"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                )}
                {option.is_correct && (
                  <span className="text-green-600 text-sm font-medium">Correct</span>
                )}
              </div>
            ))}
          </div>
          {(formData.options?.length || 0) < 6 && (
            <button
              type="button"
              onClick={addOption}
              className="mt-2 text-sm text-blue-600 hover:text-blue-700"
            >
              + Add Option
            </button>
          )}
          {errors.options && <p className="mt-1 text-sm text-red-500">{errors.options}</p>}
          {errors.correct && <p className="mt-1 text-sm text-red-500">{errors.correct}</p>}
        </div>
      )}

      {/* True/False Options */}
      {formData.question_type === 'true_false' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Correct Answer <span className="text-red-500">*</span>
          </label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="true_false_answer"
                value="true"
                checked={formData.correct_answer === 'true'}
                onChange={() => setFormData({ ...formData, correct_answer: 'true' })}
                className="mr-2 h-4 w-4 text-green-600"
              />
              <span className="text-sm">True</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="true_false_answer"
                value="false"
                checked={formData.correct_answer === 'false'}
                onChange={() => setFormData({ ...formData, correct_answer: 'false' })}
                className="mr-2 h-4 w-4 text-green-600"
              />
              <span className="text-sm">False</span>
            </label>
          </div>
          {errors.correct_answer && (
            <p className="mt-1 text-sm text-red-500">{errors.correct_answer}</p>
          )}
        </div>
      )}

      {/* Fill in Blank Answer */}
      {formData.question_type === 'fill_blank' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Correct Answer <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.correct_answer || ''}
            onChange={(e) => setFormData({ ...formData, correct_answer: e.target.value })}
            placeholder="Enter the correct answer"
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.correct_answer ? 'border-red-500' : 'border-gray-300'
            }`}
          />
          <p className="mt-1 text-xs text-gray-500">
            The answer will be compared case-insensitively.
          </p>
          {errors.correct_answer && (
            <p className="mt-1 text-sm text-red-500">{errors.correct_answer}</p>
          )}
        </div>
      )}

      {/* Points */}
      <div className="flex gap-4">
        <div className="w-32">
          <label className="block text-sm font-medium text-gray-700 mb-1">Points</label>
          <input
            type="number"
            min={1}
            max={100}
            value={formData.points}
            onChange={(e) => setFormData({ ...formData, points: parseInt(e.target.value) || 1 })}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.points ? 'border-red-500' : 'border-gray-300'
            }`}
          />
          {errors.points && <p className="mt-1 text-sm text-red-500">{errors.points}</p>}
        </div>
      </div>

      {/* Explanation */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Explanation (shown after answering)
        </label>
        <textarea
          value={formData.explanation || ''}
          onChange={(e) => setFormData({ ...formData, explanation: e.target.value })}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
          placeholder="Optional explanation to show after the user answers..."
        />
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
        <button
          type="button"
          onClick={onCancel}
          disabled={saving || isLoading}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={saving || isLoading}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
        >
          {(saving || isLoading) && (
            <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          )}
          {question ? 'Save Changes' : 'Add Question'}
        </button>
      </div>
    </form>
  );
}

export default QuestionEditor;
