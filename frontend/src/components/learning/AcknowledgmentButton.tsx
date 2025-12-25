/**
 * AcknowledgmentButton - Training document acknowledgment button.
 *
 * Handles the complete acknowledgment flow:
 * 1. Check if quiz is required and passed
 * 2. Initiate acknowledgment (creates signature challenge)
 * 3. Re-authenticate with password
 * 4. Complete acknowledgment with electronic signature
 *
 * Sprint 9: Learning Module Basics
 * Compliance: 21 CFR Part 11 electronic signatures
 */

import { useState, useEffect, useCallback } from 'react';
import {
  learningApi,
  type AcknowledgmentStatus,
  type InitiateAcknowledgmentResponse,
  type TrainingAcknowledgment,
} from '../../lib/api';

interface AcknowledgmentButtonProps {
  pageId: string;
  documentTitle?: string;
  onAcknowledged?: (acknowledgment: TrainingAcknowledgment) => void;
  onTakeQuiz?: () => void;
}

type DialogStep = 'closed' | 'confirm' | 'authenticate' | 'success';

export function AcknowledgmentButton({
  pageId,
  documentTitle,
  onAcknowledged,
  onTakeQuiz,
}: AcknowledgmentButtonProps) {
  const [status, setStatus] = useState<AcknowledgmentStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [step, setStep] = useState<DialogStep>('closed');
  const [challenge, setChallenge] = useState<InitiateAcknowledgmentResponse | null>(null);
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [expiryCountdown, setExpiryCountdown] = useState(0);

  // Load acknowledgment status
  useEffect(() => {
    const loadStatus = async () => {
      try {
        setLoading(true);
        const statusData = await learningApi.getAcknowledgmentStatus(pageId);
        setStatus(statusData);
      } catch {
        // Silently fail - button just won't show
      } finally {
        setLoading(false);
      }
    };

    loadStatus();
  }, [pageId]);

  // Countdown timer for challenge expiry
  useEffect(() => {
    if (challenge && expiryCountdown > 0 && step === 'authenticate') {
      const timer = setTimeout(() => {
        setExpiryCountdown((prev) => prev - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (challenge && expiryCountdown === 0 && step === 'authenticate') {
      setError('Authentication window expired. Please try again.');
      setStep('confirm');
      setChallenge(null);
    }
  }, [challenge, expiryCountdown, step]);

  const handleInitiate = useCallback(async () => {
    setSubmitting(true);
    setError(null);

    try {
      const challengeData = await learningApi.initiateAcknowledgment(pageId);
      setChallenge(challengeData);
      setExpiryCountdown(300); // 5 minutes
      setStep('authenticate');
    } catch (err) {
      const error = err as { response?: { status?: number; data?: { detail?: string } } };
      if (error.response?.status === 400 && error.response.data?.detail?.includes('quiz')) {
        setError('You must pass the assessment before acknowledging this document.');
      } else {
        setError(error.response?.data?.detail || 'Failed to initiate acknowledgment.');
      }
    } finally {
      setSubmitting(false);
    }
  }, [pageId]);

  const handleComplete = useCallback(async () => {
    if (!challenge || !password) return;

    setSubmitting(true);
    setError(null);

    try {
      const acknowledgment = await learningApi.completeAcknowledgment(
        challenge.challenge_token,
        password
      );

      setStep('success');

      // Refresh status
      const newStatus = await learningApi.getAcknowledgmentStatus(pageId);
      setStatus(newStatus);

      if (onAcknowledged) {
        onAcknowledged(acknowledgment);
      }
    } catch (err) {
      const error = err as { response?: { status?: number; data?: { detail?: string } } };
      if (error.response?.status === 401) {
        setError('Invalid password. Please try again.');
        setPassword('');
      } else if (error.response?.status === 410) {
        setError('Authentication window expired. Please start again.');
        setStep('confirm');
        setChallenge(null);
      } else {
        setError(error.response?.data?.detail || 'Failed to complete acknowledgment.');
      }
    } finally {
      setSubmitting(false);
    }
  }, [challenge, password, pageId, onAcknowledged]);

  const handleClose = useCallback(() => {
    setStep('closed');
    setChallenge(null);
    setPassword('');
    setError(null);
    setExpiryCountdown(0);
  }, []);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Don't show button while loading or if not required
  if (loading || !status || !status.requires_training) {
    return null;
  }

  // Show "Already Acknowledged" badge if already acknowledged
  if (status.has_valid_acknowledgment && status.acknowledgment) {
    const validUntil = status.acknowledgment.valid_until
      ? new Date(status.acknowledgment.valid_until).toLocaleDateString()
      : null;

    return (
      <div className="inline-flex items-center gap-2 px-3 py-2 bg-green-50 border border-green-200 rounded-lg">
        <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
            clipRule="evenodd"
          />
        </svg>
        <div>
          <span className="text-sm font-medium text-green-800">Acknowledged</span>
          {validUntil && (
            <span className="text-xs text-green-600 ml-2">Valid until {validUntil}</span>
          )}
        </div>
      </div>
    );
  }

  // Show "Take Quiz" button if quiz required but not passed
  if (status.has_assessment && !status.has_passed_quiz) {
    return (
      <button
        onClick={onTakeQuiz}
        className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
          />
        </svg>
        Take Assessment
      </button>
    );
  }

  return (
    <>
      {/* Acknowledge button */}
      <button
        onClick={() => setStep('confirm')}
        disabled={!status.can_acknowledge}
        className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
          />
        </svg>
        Acknowledge Training
      </button>

      {/* Dialog */}
      {step !== 'closed' && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            {/* Header */}
            <div className="px-6 py-4 border-b">
              <div className="flex items-center gap-2">
                <svg
                  className="w-5 h-5 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
                <h2 className="text-lg font-semibold text-gray-900">
                  {step === 'success' ? 'Acknowledgment Complete' : 'Training Acknowledgment'}
                </h2>
              </div>
            </div>

            {/* Content */}
            <div className="px-6 py-4">
              {error && (
                <div className="mb-4 p-3 bg-red-50 text-red-700 text-sm rounded-md flex items-start gap-2">
                  <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clipRule="evenodd"
                    />
                  </svg>
                  {error}
                </div>
              )}

              {step === 'confirm' && (
                <div className="space-y-4">
                  <p className="text-gray-700">
                    By acknowledging this document, you confirm that you have read, understood, and
                    will comply with its contents.
                  </p>

                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-500">Document:</div>
                    <div className="font-medium text-gray-900">
                      {documentTitle || challenge?.document_title || 'Training Document'}
                    </div>
                  </div>

                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-md text-sm text-amber-800">
                    <strong>Legal Notice:</strong> This creates an electronic signature record in
                    compliance with 21 CFR Part 11. Your identity will be verified.
                  </div>
                </div>
              )}

              {step === 'authenticate' && challenge && (
                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">You are acknowledging:</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Document:</span>
                        <span className="font-medium">{challenge.document_title}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Content Hash:</span>
                        <span className="font-mono text-xs">{challenge.content_hash.slice(0, 16)}...</span>
                      </div>
                    </div>
                  </div>

                  {expiryCountdown < 60 && (
                    <div className="p-3 bg-amber-50 border border-amber-200 rounded-md text-sm text-amber-800">
                      <strong>Time remaining:</strong> {formatTime(expiryCountdown)}
                    </div>
                  )}

                  <div>
                    <label
                      htmlFor="ack-password"
                      className="block text-sm font-medium text-gray-700 mb-1"
                    >
                      Enter your password to sign <span className="text-red-500">*</span>
                    </label>
                    <input
                      id="ack-password"
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Your password"
                      className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                      autoFocus
                      autoComplete="current-password"
                    />
                    <p className="mt-1 text-xs text-gray-500">
                      Re-authentication required for electronic signatures (21 CFR Part 11)
                    </p>
                  </div>
                </div>
              )}

              {step === 'success' && (
                <div className="text-center py-4">
                  <svg
                    className="mx-auto h-12 w-12 text-green-600"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <h3 className="mt-2 text-lg font-medium text-gray-900">
                    Document Acknowledged
                  </h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Your acknowledgment has been recorded with an electronic signature.
                  </p>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t bg-gray-50 flex justify-end gap-3 rounded-b-lg">
              {step === 'confirm' && (
                <>
                  <button
                    onClick={handleClose}
                    disabled={submitting}
                    className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleInitiate}
                    disabled={submitting}
                    className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors disabled:opacity-50"
                  >
                    {submitting ? 'Processing...' : 'Continue'}
                  </button>
                </>
              )}

              {step === 'authenticate' && (
                <>
                  <button
                    onClick={() => {
                      setStep('confirm');
                      setPassword('');
                      setError(null);
                    }}
                    disabled={submitting}
                    className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50"
                  >
                    Back
                  </button>
                  <button
                    onClick={handleComplete}
                    disabled={submitting || !password}
                    className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {submitting ? 'Signing...' : 'Sign & Acknowledge'}
                  </button>
                </>
              )}

              {step === 'success' && (
                <button
                  onClick={handleClose}
                  className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors"
                >
                  Done
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default AcknowledgmentButton;
