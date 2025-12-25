/**
 * SignatureDialog - Two-step electronic signature dialog.
 *
 * Step 1: Preview what will be signed, select meaning, add optional reason
 * Step 2: Re-authenticate with password to complete signature
 *
 * 21 CFR Part 11 compliant - requires re-authentication at signature time.
 */

import { useState, useEffect, useCallback } from 'react';
import {
  signatureApi,
  type SignatureMeaning,
  type InitiateSignatureResponse,
  type ElectronicSignature,
} from '../../lib/api';

interface SignatureDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSigned: (signature: ElectronicSignature) => void;
  pageId?: string;
  changeRequestId?: string;
  documentTitle?: string;
  defaultMeaning?: SignatureMeaning;
}

const MEANING_OPTIONS: { value: SignatureMeaning; label: string; description: string }[] = [
  {
    value: 'authored',
    label: 'Authored',
    description: 'I authored this document and certify its accuracy.',
  },
  {
    value: 'reviewed',
    label: 'Reviewed',
    description: 'I have reviewed this document for accuracy and completeness.',
  },
  {
    value: 'approved',
    label: 'Approved',
    description: 'I approve this document for release and use.',
  },
  {
    value: 'witnessed',
    label: 'Witnessed',
    description: 'I witnessed the signing of this document.',
  },
  {
    value: 'acknowledged',
    label: 'Acknowledged',
    description: 'I have read and understood this document.',
  },
];

type Step = 'preview' | 'authenticate';

export function SignatureDialog({
  isOpen,
  onClose,
  onSigned,
  pageId,
  changeRequestId,
  documentTitle,
  defaultMeaning = 'approved',
}: SignatureDialogProps) {
  const [step, setStep] = useState<Step>('preview');
  const [meaning, setMeaning] = useState<SignatureMeaning>(defaultMeaning);
  const [reason, setReason] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [challenge, setChallenge] = useState<InitiateSignatureResponse | null>(null);
  const [expiryCountdown, setExpiryCountdown] = useState(0);

  // Reset state when dialog opens
  useEffect(() => {
    if (isOpen) {
      setStep('preview');
      setMeaning(defaultMeaning);
      setReason('');
      setPassword('');
      setError(null);
      setChallenge(null);
      setExpiryCountdown(0);
    }
  }, [isOpen, defaultMeaning]);

  // Countdown timer for challenge expiry
  useEffect(() => {
    if (challenge && expiryCountdown > 0) {
      const timer = setTimeout(() => {
        setExpiryCountdown((prev) => prev - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (challenge && expiryCountdown === 0 && step === 'authenticate') {
      setError('Signature challenge expired. Please start again.');
      setStep('preview');
      setChallenge(null);
    }
  }, [challenge, expiryCountdown, step]);

  const handleInitiate = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await signatureApi.initiate({
        page_id: pageId,
        change_request_id: changeRequestId,
        meaning,
        reason: reason.trim() || undefined,
      });

      setChallenge(response);
      setExpiryCountdown(response.expires_in_seconds);
      setStep('authenticate');
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to initiate signature. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  }, [pageId, changeRequestId, meaning, reason]);

  const handleComplete = useCallback(async () => {
    if (!challenge || !password) return;

    setLoading(true);
    setError(null);

    try {
      const signature = await signatureApi.complete({
        challenge_token: challenge.challenge_token,
        password,
        reason: reason.trim() || undefined,
      });

      onSigned(signature);
      handleClose();
    } catch (err: unknown) {
      // Check for specific error types
      const error = err as { response?: { status?: number; data?: { detail?: string } } };
      if (error.response?.status === 401) {
        setError('Invalid password. Please try again.');
        setPassword('');
      } else if (error.response?.status === 410) {
        setError('Signature challenge expired. Please start again.');
        setStep('preview');
        setChallenge(null);
      } else if (error.response?.status === 409) {
        setError('Document content has changed. Please start a new signature.');
        setStep('preview');
        setChallenge(null);
      } else if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else {
        setError('Failed to complete signature. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  }, [challenge, password, reason, onSigned]);

  const handleClose = useCallback(() => {
    setStep('preview');
    setMeaning(defaultMeaning);
    setReason('');
    setPassword('');
    setError(null);
    setChallenge(null);
    onClose();
  }, [defaultMeaning, onClose]);

  const handleBack = useCallback(() => {
    setStep('preview');
    setPassword('');
    setError(null);
  }, []);

  if (!isOpen) {
    return null;
  }

  const selectedMeaning = MEANING_OPTIONS.find((m) => m.value === meaning);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
        {/* Header */}
        <div className="px-6 py-4 border-b">
          <div className="flex items-center gap-2">
            <svg
              className="w-5 h-5 text-blue-600"
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
            <h2 className="text-lg font-semibold text-gray-900">Electronic Signature</h2>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            {step === 'preview'
              ? `Sign "${documentTitle || challenge?.document_title || 'Document'}"`
              : 'Enter your password to confirm'}
          </p>
        </div>

        {/* Step indicator */}
        <div className="px-6 py-3 bg-gray-50 border-b">
          <div className="flex items-center gap-4 text-sm">
            <div
              className={`flex items-center gap-2 ${
                step === 'preview' ? 'text-blue-600 font-medium' : 'text-gray-400'
              }`}
            >
              <span
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                  step === 'preview'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-500'
                }`}
              >
                1
              </span>
              Review
            </div>
            <div className="flex-1 h-px bg-gray-200" />
            <div
              className={`flex items-center gap-2 ${
                step === 'authenticate' ? 'text-blue-600 font-medium' : 'text-gray-400'
              }`}
            >
              <span
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                  step === 'authenticate'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-500'
                }`}
              >
                2
              </span>
              Authenticate
            </div>
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

          {step === 'preview' && (
            <div className="space-y-4">
              {/* Meaning selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Signature Meaning <span className="text-red-500">*</span>
                </label>
                <div className="space-y-2">
                  {MEANING_OPTIONS.map((option) => (
                    <label
                      key={option.value}
                      className={`flex items-start gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                        meaning === option.value
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="meaning"
                        value={option.value}
                        checked={meaning === option.value}
                        onChange={(e) => setMeaning(e.target.value as SignatureMeaning)}
                        className="mt-0.5"
                      />
                      <div>
                        <div className="font-medium text-gray-900">{option.label}</div>
                        <div className="text-sm text-gray-500">{option.description}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Optional reason */}
              <div>
                <label
                  htmlFor="signature-reason"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Reason/Comment (optional)
                </label>
                <textarea
                  id="signature-reason"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="Add an optional comment..."
                  className="w-full px-3 py-2 border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 h-20"
                  maxLength={1000}
                />
              </div>

              {/* Legal notice */}
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-md text-sm text-amber-800">
                <strong>Legal Notice:</strong> By signing, you are creating a legally binding
                electronic signature in compliance with 21 CFR Part 11. Your identity will be
                verified and the signature will be permanently recorded.
              </div>
            </div>
          )}

          {step === 'authenticate' && challenge && (
            <div className="space-y-4">
              {/* Summary of what will be signed */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="text-sm font-medium text-gray-900 mb-2">You are signing:</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Document:</span>
                    <span className="font-medium">{challenge.document_title || 'Document'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Meaning:</span>
                    <span className="font-medium">{selectedMeaning?.label}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Content Hash:</span>
                    <span className="font-mono text-xs">{challenge.content_hash.slice(0, 16)}...</span>
                  </div>
                </div>
              </div>

              {/* Expiry warning */}
              {expiryCountdown < 60 && (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-md text-sm text-amber-800">
                  <strong>Time remaining:</strong> {expiryCountdown} seconds
                </div>
              )}

              {/* Password input */}
              <div>
                <label
                  htmlFor="signature-password"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Enter your password to sign <span className="text-red-500">*</span>
                </label>
                <input
                  id="signature-password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Your password"
                  className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  autoFocus
                  autoComplete="current-password"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Re-authentication is required for electronic signatures (21 CFR Part 11)
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t bg-gray-50 flex justify-between rounded-b-lg">
          {step === 'authenticate' && (
            <button
              type="button"
              onClick={handleBack}
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50"
            >
              Back
            </button>
          )}
          <div className={`flex gap-3 ${step === 'preview' ? 'ml-auto' : ''}`}>
            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            {step === 'preview' ? (
              <button
                type="button"
                onClick={handleInitiate}
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors disabled:opacity-50"
              >
                {loading ? 'Preparing...' : 'Continue'}
              </button>
            ) : (
              <button
                type="button"
                onClick={handleComplete}
                disabled={loading || !password}
                className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Signing...' : 'Sign Document'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default SignatureDialog;
