/**
 * QuestionBank - Question management with drag-drop reordering.
 *
 * Features:
 * - Drag-and-drop reordering
 * - Bulk delete
 * - Question preview
 * - Search/filter
 *
 * Sprint 9.5: Admin UI
 */

import { useState, useCallback } from 'react';
import type { AssessmentQuestion, QuestionType } from '../../lib/api';

interface QuestionBankProps {
  questions: AssessmentQuestion[];
  onReorder: (questionIds: string[]) => Promise<void>;
  onEdit: (question: AssessmentQuestion) => void;
  onDelete: (questionId: string) => Promise<void>;
  onBulkDelete?: (questionIds: string[]) => Promise<void>;
  isLoading?: boolean;
}

const QUESTION_TYPE_LABELS: Record<QuestionType, string> = {
  multiple_choice: 'Multiple Choice',
  true_false: 'True/False',
  fill_blank: 'Fill in Blank',
};

const QUESTION_TYPE_ICONS: Record<QuestionType, string> = {
  multiple_choice: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2',
  true_false: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  fill_blank: 'M4 6h16M4 12h16m-7 6h7',
};

export function QuestionBank({
  questions,
  onReorder,
  onEdit,
  onDelete,
  onBulkDelete,
  isLoading = false,
}: QuestionBankProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [draggedId, setDraggedId] = useState<string | null>(null);
  const [dragOverId, setDragOverId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<QuestionType | 'all'>('all');
  const [reordering, setReordering] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Filter questions
  const filteredQuestions = questions.filter((q) => {
    const matchesSearch = q.question_text.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'all' || q.question_type === filterType;
    return matchesSearch && matchesType;
  });

  // Drag handlers
  const handleDragStart = useCallback((e: React.DragEvent, id: string) => {
    setDraggedId(id);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', id);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent, id: string) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    if (id !== draggedId) {
      setDragOverId(id);
    }
  }, [draggedId]);

  const handleDragLeave = useCallback(() => {
    setDragOverId(null);
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent, targetId: string) => {
    e.preventDefault();
    setDragOverId(null);

    if (!draggedId || draggedId === targetId) {
      setDraggedId(null);
      return;
    }

    // Calculate new order
    const currentOrder = questions.map((q) => q.id);
    const draggedIndex = currentOrder.indexOf(draggedId);
    const targetIndex = currentOrder.indexOf(targetId);

    if (draggedIndex === -1 || targetIndex === -1) {
      setDraggedId(null);
      return;
    }

    // Remove dragged item and insert at new position
    const newOrder = [...currentOrder];
    newOrder.splice(draggedIndex, 1);
    newOrder.splice(targetIndex, 0, draggedId);

    setDraggedId(null);
    setReordering(true);

    try {
      await onReorder(newOrder);
    } finally {
      setReordering(false);
    }
  }, [draggedId, questions, onReorder]);

  const handleDragEnd = useCallback(() => {
    setDraggedId(null);
    setDragOverId(null);
  }, []);

  // Selection handlers
  const toggleSelect = useCallback((id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const selectAll = useCallback(() => {
    if (selectedIds.size === filteredQuestions.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredQuestions.map((q) => q.id)));
    }
  }, [filteredQuestions, selectedIds.size]);

  const handleBulkDelete = useCallback(async () => {
    if (selectedIds.size === 0 || !onBulkDelete) return;

    const confirmed = window.confirm(
      `Are you sure you want to delete ${selectedIds.size} question(s)? This cannot be undone.`
    );
    if (!confirmed) return;

    setDeleting(true);
    try {
      await onBulkDelete(Array.from(selectedIds));
      setSelectedIds(new Set());
    } finally {
      setDeleting(false);
    }
  }, [selectedIds, onBulkDelete]);

  const handleSingleDelete = useCallback(async (id: string) => {
    const confirmed = window.confirm('Are you sure you want to delete this question?');
    if (!confirmed) return;

    setDeleting(true);
    try {
      await onDelete(id);
      setSelectedIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    } finally {
      setDeleting(false);
    }
  }, [onDelete]);

  if (questions.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="text-sm">No questions yet. Add your first question to get started.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3 bg-gray-50 p-3 rounded-lg">
        {/* Search */}
        <div className="flex-1 min-w-48">
          <input
            type="text"
            placeholder="Search questions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
          />
        </div>

        {/* Filter by type */}
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value as QuestionType | 'all')}
          className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
        >
          <option value="all">All Types</option>
          <option value="multiple_choice">Multiple Choice</option>
          <option value="true_false">True/False</option>
          <option value="fill_blank">Fill in Blank</option>
        </select>

        {/* Bulk actions */}
        {selectedIds.size > 0 && onBulkDelete && (
          <button
            onClick={handleBulkDelete}
            disabled={deleting}
            className="px-3 py-1.5 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md hover:bg-red-100 disabled:opacity-50"
          >
            {deleting ? 'Deleting...' : `Delete (${selectedIds.size})`}
          </button>
        )}

        {/* Reorder indicator */}
        {reordering && (
          <span className="text-sm text-blue-600 flex items-center gap-1">
            <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Saving order...
          </span>
        )}
      </div>

      {/* Select all */}
      {filteredQuestions.length > 0 && (
        <div className="flex items-center gap-2 px-2">
          <input
            type="checkbox"
            checked={selectedIds.size === filteredQuestions.length && filteredQuestions.length > 0}
            onChange={selectAll}
            className="w-4 h-4 text-blue-600 rounded"
          />
          <span className="text-sm text-gray-600">
            {selectedIds.size > 0
              ? `${selectedIds.size} selected`
              : `${filteredQuestions.length} questions`}
          </span>
        </div>
      )}

      {/* Question list */}
      <div className="space-y-2">
        {filteredQuestions.map((question, index) => (
          <div
            key={question.id}
            draggable={!isLoading && !reordering}
            onDragStart={(e) => handleDragStart(e, question.id)}
            onDragOver={(e) => handleDragOver(e, question.id)}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, question.id)}
            onDragEnd={handleDragEnd}
            className={`
              border rounded-lg transition-all
              ${draggedId === question.id ? 'opacity-50 border-blue-400 bg-blue-50' : 'bg-white'}
              ${dragOverId === question.id ? 'border-blue-500 border-2' : 'border-gray-200'}
              ${selectedIds.has(question.id) ? 'ring-2 ring-blue-500 ring-offset-1' : ''}
            `}
          >
            <div className="flex items-start gap-3 p-3">
              {/* Drag handle */}
              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  checked={selectedIds.has(question.id)}
                  onChange={() => toggleSelect(question.id)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <div className="cursor-grab text-gray-400 hover:text-gray-600">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8h16M4 16h16" />
                  </svg>
                </div>
              </div>

              {/* Question info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium text-gray-500">#{index + 1}</span>
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full ${
                    question.question_type === 'multiple_choice' ? 'bg-blue-100 text-blue-700' :
                    question.question_type === 'true_false' ? 'bg-green-100 text-green-700' :
                    'bg-purple-100 text-purple-700'
                  }`}>
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={QUESTION_TYPE_ICONS[question.question_type]} />
                    </svg>
                    {QUESTION_TYPE_LABELS[question.question_type]}
                  </span>
                  <span className="text-xs text-gray-500">{question.points} pts</span>
                </div>

                <p className="text-sm text-gray-900 line-clamp-2">{question.question_text}</p>

                {/* Expanded preview */}
                {expandedId === question.id && (
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    {question.question_type === 'multiple_choice' && question.options && (
                      <div className="space-y-1">
                        {question.options.map((opt) => (
                          <div key={opt.id} className={`flex items-center gap-2 text-sm ${opt.is_correct ? 'text-green-700 font-medium' : 'text-gray-600'}`}>
                            <span className={`w-5 h-5 flex items-center justify-center rounded-full text-xs ${opt.is_correct ? 'bg-green-100' : 'bg-gray-100'}`}>
                              {opt.id.toUpperCase()}
                            </span>
                            {opt.text}
                            {opt.is_correct && <span className="text-green-600 text-xs">(correct)</span>}
                          </div>
                        ))}
                      </div>
                    )}
                    {question.question_type === 'true_false' && (
                      <p className="text-sm text-green-700">Correct answer: {question.correct_answer}</p>
                    )}
                    {question.question_type === 'fill_blank' && (
                      <p className="text-sm text-green-700">Correct answer: {question.correct_answer}</p>
                    )}
                    {question.explanation && (
                      <p className="mt-2 text-xs text-gray-500 italic">Explanation: {question.explanation}</p>
                    )}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setExpandedId(expandedId === question.id ? null : question.id)}
                  className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                  title={expandedId === question.id ? 'Collapse' : 'Preview'}
                >
                  <svg className={`w-4 h-4 transition-transform ${expandedId === question.id ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                <button
                  onClick={() => onEdit(question)}
                  className="p-1.5 text-blue-600 hover:bg-blue-50 rounded"
                  title="Edit"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button
                  onClick={() => handleSingleDelete(question.id)}
                  disabled={deleting}
                  className="p-1.5 text-red-600 hover:bg-red-50 rounded disabled:opacity-50"
                  title="Delete"
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

      {/* Empty filter result */}
      {filteredQuestions.length === 0 && questions.length > 0 && (
        <div className="text-center py-6 text-gray-500">
          <p className="text-sm">No questions match your search or filter.</p>
          <button
            onClick={() => {
              setSearchQuery('');
              setFilterType('all');
            }}
            className="mt-2 text-sm text-blue-600 hover:text-blue-700"
          >
            Clear filters
          </button>
        </div>
      )}
    </div>
  );
}

export default QuestionBank;
