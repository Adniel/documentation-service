/**
 * QuestionCard - Renders a single quiz question.
 *
 * Supports multiple choice, true/false, and fill-in-the-blank question types.
 * Auto-saves answers on change.
 *
 * Sprint 9: Learning Module Basics
 */

import { useCallback } from 'react';
import type { QuestionPublic, QuestionType } from '../../lib/api';

interface QuestionCardProps {
  question: QuestionPublic;
  questionNumber: number;
  totalQuestions: number;
  selectedAnswer?: string;
  onAnswerChange: (questionId: string, answer: string) => void;
  disabled?: boolean;
  showResult?: boolean;
  isCorrect?: boolean;
  correctAnswer?: string;
  explanation?: string;
}

export function QuestionCard({
  question,
  questionNumber,
  totalQuestions,
  selectedAnswer,
  onAnswerChange,
  disabled = false,
  showResult = false,
  isCorrect,
  correctAnswer,
  explanation,
}: QuestionCardProps) {
  const handleChange = useCallback(
    (answer: string) => {
      if (!disabled) {
        onAnswerChange(question.id, answer);
      }
    },
    [question.id, onAnswerChange, disabled]
  );

  const renderQuestionInput = () => {
    switch (question.question_type as QuestionType) {
      case 'multiple_choice':
        return (
          <div className="space-y-2">
            {question.options?.map((option) => {
              const isSelected = selectedAnswer === option.id;
              const isCorrectOption = showResult && correctAnswer === option.id;
              const isWrongSelection = showResult && isSelected && !isCorrect;

              return (
                <label
                  key={option.id}
                  className={`flex items-start gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                    disabled ? 'cursor-default' : 'hover:border-gray-300'
                  } ${
                    isSelected && !showResult
                      ? 'border-blue-500 bg-blue-50'
                      : isCorrectOption
                      ? 'border-green-500 bg-green-50'
                      : isWrongSelection
                      ? 'border-red-500 bg-red-50'
                      : 'border-gray-200'
                  }`}
                >
                  <input
                    type="radio"
                    name={`question-${question.id}`}
                    value={option.id}
                    checked={isSelected}
                    onChange={() => handleChange(option.id)}
                    disabled={disabled}
                    className="mt-0.5"
                  />
                  <span className="text-gray-900">{option.text}</span>
                  {showResult && isCorrectOption && (
                    <svg
                      className="w-5 h-5 text-green-600 ml-auto flex-shrink-0"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                  {showResult && isWrongSelection && (
                    <svg
                      className="w-5 h-5 text-red-600 ml-auto flex-shrink-0"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </label>
              );
            })}
          </div>
        );

      case 'true_false':
        return (
          <div className="flex gap-4">
            {['true', 'false'].map((value) => {
              const isSelected = selectedAnswer === value;
              const isCorrectOption = showResult && correctAnswer === value;
              const isWrongSelection = showResult && isSelected && !isCorrect;

              return (
                <label
                  key={value}
                  className={`flex-1 flex items-center justify-center gap-2 p-4 border rounded-lg cursor-pointer transition-colors ${
                    disabled ? 'cursor-default' : 'hover:border-gray-300'
                  } ${
                    isSelected && !showResult
                      ? 'border-blue-500 bg-blue-50'
                      : isCorrectOption
                      ? 'border-green-500 bg-green-50'
                      : isWrongSelection
                      ? 'border-red-500 bg-red-50'
                      : 'border-gray-200'
                  }`}
                >
                  <input
                    type="radio"
                    name={`question-${question.id}`}
                    value={value}
                    checked={isSelected}
                    onChange={() => handleChange(value)}
                    disabled={disabled}
                  />
                  <span className="font-medium text-gray-900 capitalize">{value}</span>
                </label>
              );
            })}
          </div>
        );

      case 'fill_blank':
        return (
          <div>
            <input
              type="text"
              value={selectedAnswer || ''}
              onChange={(e) => handleChange(e.target.value)}
              disabled={disabled}
              placeholder="Type your answer..."
              className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                showResult && isCorrect
                  ? 'border-green-500 bg-green-50'
                  : showResult && !isCorrect
                  ? 'border-red-500 bg-red-50'
                  : 'border-gray-200'
              }`}
            />
            {showResult && correctAnswer && (
              <p className="mt-2 text-sm text-gray-600">
                <span className="font-medium">Correct answer:</span> {correctAnswer}
              </p>
            )}
          </div>
        );

      default:
        return <div className="text-gray-500">Unknown question type</div>;
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      {/* Question header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="px-2 py-1 bg-gray-100 text-gray-600 text-sm font-medium rounded">
            Q{questionNumber}/{totalQuestions}
          </span>
          <span className="text-sm text-gray-500">{question.points} point{question.points !== 1 ? 's' : ''}</span>
        </div>
        {showResult && (
          <span
            className={`px-2 py-1 text-sm font-medium rounded ${
              isCorrect ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}
          >
            {isCorrect ? 'Correct' : 'Incorrect'}
          </span>
        )}
      </div>

      {/* Question text */}
      <p className="text-lg text-gray-900 mb-4">{question.question_text}</p>

      {/* Answer input */}
      {renderQuestionInput()}

      {/* Explanation (shown after submission) */}
      {showResult && explanation && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-800">
            <span className="font-medium">Explanation:</span> {explanation}
          </p>
        </div>
      )}
    </div>
  );
}

export default QuestionCard;
