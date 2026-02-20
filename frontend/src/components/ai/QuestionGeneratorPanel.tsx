/**
 * QuestionGeneratorPanel — AI-powered question generation for assessments.
 *
 * Sprint K: AI Features
 */

import { useState } from 'react';
import {
  aiApi,
  type GeneratedQuestion,
  type GenerateQuestionsRequest,
} from '../../lib/api';

interface QuestionGeneratorPanelProps {
  pageId: string;
  onQuestionsGenerated: (questions: GeneratedQuestion[]) => void;
  onClose: () => void;
}

const QUESTION_TYPES = [
  { value: 'multiple_choice', label: 'Multiple Choice' },
  { value: 'true_false', label: 'True/False' },
  { value: 'fill_blank', label: 'Fill in Blank' },
];

const DIFFICULTIES = [
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
];

export function QuestionGeneratorPanel({
  pageId,
  onQuestionsGenerated,
  onClose,
}: QuestionGeneratorPanelProps) {
  const [count, setCount] = useState(5);
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
  const [questionTypes, setQuestionTypes] = useState<string[]>(['multiple_choice', 'true_false']);
  const [focusTopics, setFocusTopics] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [questions, setQuestions] = useState<GeneratedQuestion[]>([]);
  const [selected, setSelected] = useState<Set<number>>(new Set());

  const toggleType = (type: string) => {
    setQuestionTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const toggleSelect = (index: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  };

  const selectAll = () => {
    setSelected(new Set(questions.map((_, i) => i)));
  };

  const handleGenerate = async () => {
    if (questionTypes.length === 0) {
      setError('Select at least one question type');
      return;
    }
    setLoading(true);
    setError(null);
    setQuestions([]);
    setSelected(new Set());

    try {
      const request: GenerateQuestionsRequest = {
        page_id: pageId,
        count,
        difficulty,
        question_types: questionTypes,
        focus_topics: focusTopics.trim()
          ? focusTopics.split(',').map((t) => t.trim())
          : [],
      };
      const response = await aiApi.generateQuestions(request);
      setQuestions(response.questions);
      setSelected(new Set(response.questions.map((_, i) => i)));
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to generate questions');
    } finally {
      setLoading(false);
    }
  };

  const handleAddSelected = () => {
    const selectedQuestions = questions.filter((_, i) => selected.has(i));
    onQuestionsGenerated(selectedQuestions);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Generate Questions with AI</h3>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Configuration */}
      {questions.length === 0 && (
        <div className="space-y-4">
          {/* Count slider */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Number of questions: {count}
            </label>
            <input
              type="range"
              min={1}
              max={20}
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-400">
              <span>1</span>
              <span>20</span>
            </div>
          </div>

          {/* Difficulty */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Difficulty</label>
            <div className="flex gap-2">
              {DIFFICULTIES.map((d) => (
                <button
                  key={d.value}
                  onClick={() => setDifficulty(d.value as 'easy' | 'medium' | 'hard')}
                  className={`px-3 py-1.5 text-sm rounded-md border ${
                    difficulty === d.value
                      ? 'bg-blue-50 border-blue-300 text-blue-700'
                      : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </div>

          {/* Question Types */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Question Types</label>
            <div className="flex gap-2 flex-wrap">
              {QUESTION_TYPES.map((t) => (
                <label key={t.value} className="flex items-center gap-1.5 text-sm text-gray-600">
                  <input
                    type="checkbox"
                    checked={questionTypes.includes(t.value)}
                    onChange={() => toggleType(t.value)}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                  />
                  {t.label}
                </label>
              ))}
            </div>
          </div>

          {/* Focus Topics */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Focus Topics (optional, comma-separated)
            </label>
            <input
              type="text"
              value={focusTopics}
              onChange={(e) => setFocusTopics(e.target.value)}
              placeholder="e.g., safety procedures, installation steps"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm bg-white text-gray-900"
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 text-sm font-medium flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Generating...
              </>
            ) : (
              'Generate Questions'
            )}
          </button>
        </div>
      )}

      {/* Results */}
      {questions.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">
              {selected.size} of {questions.length} selected
            </span>
            <button onClick={selectAll} className="text-sm text-blue-600 hover:text-blue-800">
              Select all
            </button>
          </div>

          <div className="max-h-80 overflow-y-auto space-y-2">
            {questions.map((q, i) => (
              <div
                key={i}
                className={`p-3 rounded border cursor-pointer transition-colors ${
                  selected.has(i)
                    ? 'border-blue-300 bg-blue-50'
                    : 'border-gray-200 bg-white hover:bg-gray-50'
                }`}
                onClick={() => toggleSelect(i)}
              >
                <div className="flex items-start gap-2">
                  <input
                    type="checkbox"
                    checked={selected.has(i)}
                    onChange={() => toggleSelect(i)}
                    className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-1.5 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
                        {q.question_type.replace('_', ' ')}
                      </span>
                      <span className="text-xs text-gray-400">{q.difficulty}</span>
                      <span className="text-xs text-gray-400">{q.points} pt</span>
                    </div>
                    <p className="text-sm text-gray-900">{q.question_text}</p>
                    {q.options.length > 0 && (
                      <div className="mt-1 flex flex-wrap gap-1">
                        {q.options.map((opt) => (
                          <span
                            key={opt.id}
                            className={`text-xs px-1.5 py-0.5 rounded ${
                              opt.is_correct
                                ? 'bg-green-100 text-green-700'
                                : 'bg-gray-100 text-gray-500'
                            }`}
                          >
                            {opt.id.toUpperCase()}: {opt.text.substring(0, 40)}
                            {opt.text.length > 40 ? '...' : ''}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="flex gap-2 pt-2 border-t border-gray-200">
            <button
              onClick={() => {
                setQuestions([]);
                setSelected(new Set());
              }}
              className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Regenerate
            </button>
            <button
              onClick={handleAddSelected}
              disabled={selected.size === 0}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 text-sm font-medium"
            >
              Add {selected.size} Selected Question{selected.size !== 1 ? 's' : ''}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default QuestionGeneratorPanel;
