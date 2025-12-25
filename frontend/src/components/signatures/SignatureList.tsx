/**
 * SignatureList - Displays all signatures on a document with verification.
 */

import { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { signatureApi, type ElectronicSignature, type SignatureVerification } from '../../lib/api';
import { SignatureBadge } from './SignatureBadge';

interface SignatureListProps {
  pageId?: string;
  changeRequestId?: string;
  showVerification?: boolean;
  onSignatureClick?: (signature: ElectronicSignature) => void;
}

export function SignatureList({
  pageId,
  changeRequestId,
  showVerification = false,
  onSignatureClick,
}: SignatureListProps) {
  const [includeInvalid, setIncludeInvalid] = useState(false);
  const [verifying, setVerifying] = useState<string | null>(null);
  const [verificationResults, setVerificationResults] = useState<
    Record<string, SignatureVerification>
  >({});

  // Fetch signatures
  const { data, isLoading, error } = useQuery({
    queryKey: ['signatures', pageId, changeRequestId, includeInvalid],
    queryFn: async () => {
      if (pageId) {
        return signatureApi.listForPage(pageId, includeInvalid);
      }
      if (changeRequestId) {
        return signatureApi.listForChangeRequest(changeRequestId, includeInvalid);
      }
      return { signatures: [], total: 0, has_valid_signatures: false };
    },
    enabled: !!(pageId || changeRequestId),
  });

  const handleVerify = useCallback(async (signatureId: string) => {
    setVerifying(signatureId);
    try {
      const result = await signatureApi.verify(signatureId);
      setVerificationResults((prev) => ({
        ...prev,
        [signatureId]: result,
      }));
    } catch (err) {
      console.error('Verification failed:', err);
    } finally {
      setVerifying(null);
    }
  }, []);

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-3">
        {[1, 2].map((i) => (
          <div key={i} className="h-16 bg-gray-100 rounded-md" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-600 text-sm">Failed to load signatures</div>
    );
  }

  if (!data || data.signatures.length === 0) {
    return (
      <div className="text-center py-6 text-gray-500">
        <svg
          className="w-10 h-10 mx-auto mb-2 text-gray-300"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
          />
        </svg>
        <p className="text-sm">No signatures yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-900">
          Signatures ({data.total})
        </h3>
        <label className="flex items-center gap-2 text-xs text-gray-500">
          <input
            type="checkbox"
            checked={includeInvalid}
            onChange={(e) => setIncludeInvalid(e.target.checked)}
            className="rounded text-blue-600"
          />
          Show invalid
        </label>
      </div>

      {/* Signature list */}
      <div className="divide-y divide-gray-100">
        {data.signatures.map((signature) => {
          const verification = verificationResults[signature.id];

          return (
            <div
              key={signature.id}
              className={`py-3 ${onSignatureClick ? 'cursor-pointer hover:bg-gray-50' : ''}`}
              onClick={() => onSignatureClick?.(signature)}
            >
              <SignatureBadge signature={signature} showDetails />

              {/* Verification section */}
              {showVerification && (
                <div className="mt-2 ml-10">
                  {verification ? (
                    <div
                      className={`text-xs p-2 rounded ${
                        verification.is_valid
                          ? 'bg-green-50 text-green-700'
                          : 'bg-red-50 text-red-700'
                      }`}
                    >
                      <div className="flex items-center gap-1 font-medium">
                        {verification.is_valid ? (
                          <>
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                              <path
                                fillRule="evenodd"
                                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                clipRule="evenodd"
                              />
                            </svg>
                            Verified
                          </>
                        ) : (
                          <>
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                              <path
                                fillRule="evenodd"
                                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                                clipRule="evenodd"
                              />
                            </svg>
                            Verification Failed
                          </>
                        )}
                      </div>
                      {verification.issues.length > 0 && (
                        <ul className="mt-1 space-y-0.5 list-disc list-inside">
                          {verification.issues.map((issue, i) => (
                            <li key={i}>{issue}</li>
                          ))}
                        </ul>
                      )}
                      <div className="mt-1 text-gray-500">
                        <span>Content match: {verification.content_hash_matches ? 'Yes' : 'No'}</span>
                        {' • '}
                        <span>Git verified: {verification.git_commit_verified ? 'Yes' : 'N/A'}</span>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleVerify(signature.id);
                      }}
                      disabled={verifying === signature.id}
                      className="text-xs text-blue-600 hover:text-blue-700 disabled:opacity-50"
                    >
                      {verifying === signature.id ? 'Verifying...' : 'Verify signature'}
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Summary */}
      {data.has_valid_signatures && (
        <div className="pt-2 border-t text-xs text-gray-500 flex items-center gap-1">
          <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
          This document has valid electronic signatures
        </div>
      )}
    </div>
  );
}

export default SignatureList;
