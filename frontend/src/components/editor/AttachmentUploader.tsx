/**
 * AttachmentUploader Component
 *
 * Sprint F: Attachments & Media Support
 *
 * Provides drag-and-drop and click-to-upload functionality for file attachments.
 * Shows upload progress and handles errors.
 */

import React, { useCallback, useRef, useState } from 'react';
import { attachmentApi } from '../../lib/api';
import type { AttachmentResponse } from '../../lib/api';

interface AttachmentUploaderProps {
  pageId: string;
  onUploadComplete: (attachment: AttachmentResponse) => void;
  onError?: (error: string) => void;
  accept?: string;
  className?: string;
}

interface UploadState {
  file: File;
  progress: number;
  status: 'uploading' | 'complete' | 'error';
  error?: string;
}

export const AttachmentUploader: React.FC<AttachmentUploaderProps> = ({
  pageId,
  onUploadComplete,
  onError,
  accept,
  className = '',
}) => {
  const [uploads, setUploads] = useState<UploadState[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback(
    async (files: FileList | File[]) => {
      const fileArray = Array.from(files);

      for (const file of fileArray) {
        const uploadState: UploadState = {
          file,
          progress: 0,
          status: 'uploading',
        };

        setUploads((prev) => [...prev, uploadState]);

        try {
          const result = await attachmentApi.upload(
            pageId,
            file,
            undefined,
            undefined,
            (percent) => {
              setUploads((prev) =>
                prev.map((u) =>
                  u.file === file ? { ...u, progress: percent } : u
                )
              );
            }
          );

          setUploads((prev) =>
            prev.map((u) =>
              u.file === file ? { ...u, status: 'complete', progress: 100 } : u
            )
          );

          onUploadComplete(result);

          // Remove completed upload after a delay
          setTimeout(() => {
            setUploads((prev) => prev.filter((u) => u.file !== file));
          }, 2000);
        } catch (err) {
          const errorMsg = err instanceof Error ? err.message : 'Upload failed';
          setUploads((prev) =>
            prev.map((u) =>
              u.file === file
                ? { ...u, status: 'error', error: errorMsg }
                : u
            )
          );
          onError?.(errorMsg);
        }
      }
    },
    [pageId, onUploadComplete, onError]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      if (e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
      }
    },
    [handleFiles]
  );

  const handleClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFiles(e.target.files);
        e.target.value = ''; // Reset for re-upload
      }
    },
    [handleFiles]
  );

  return (
    <div className={className}>
      {/* Drop zone */}
      <div
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          border-2 border-dashed rounded-lg p-6 text-center cursor-pointer
          transition-colors
          ${
            isDragOver
              ? 'border-blue-400 bg-blue-500/10 text-blue-300'
              : 'border-slate-600 hover:border-slate-500 text-slate-400 hover:text-slate-300'
          }
        `}
      >
        <div className="text-2xl mb-2">📎</div>
        <div className="text-sm font-medium">
          Drop files here or click to browse
        </div>
        <div className="text-xs mt-1 text-slate-500">
          Images, PDFs, documents, audio, video (max 100 MB)
        </div>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept={accept}
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Upload progress */}
      {uploads.length > 0 && (
        <div className="mt-3 space-y-2">
          {uploads.map((upload, index) => (
            <div
              key={`${upload.file.name}-${index}`}
              className="flex items-center gap-3 p-2 bg-slate-800 rounded border border-slate-700"
            >
              <span className="text-sm truncate flex-1 text-slate-300">
                {upload.file.name}
              </span>

              {upload.status === 'uploading' && (
                <div className="w-24 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full transition-all"
                    style={{ width: `${upload.progress}%` }}
                  />
                </div>
              )}

              {upload.status === 'complete' && (
                <span className="text-green-400 text-sm">Done</span>
              )}

              {upload.status === 'error' && (
                <span className="text-red-400 text-xs truncate max-w-32">
                  {upload.error}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AttachmentUploader;
