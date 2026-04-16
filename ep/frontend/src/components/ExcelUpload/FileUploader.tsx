import { useCallback, useEffect, useRef, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { excelApi } from '../../services/excelApi';
import { useUploadStore } from '../../store/useUploadStore';
import type { AnalysisResult } from '../../types/api';

const STORE_PREFIXES = ['EP', 'DM', 'DA', 'PZ'] as const;
const ALLOWED_FIXED_FILES = new Set(
  STORE_PREFIXES.flatMap((prefix) => [`${prefix}-0.xlsm`, `${prefix}-1.xlsm`, `${prefix}-2.xlsm`])
);
const UPLOAD_FILE_HINT = '支持文件名：{EP|DM|DA|PZ}-0/1/2.xlsm、{EP|DM|DA|PZ}-All+Listings+Report.txt';

const isAllowedUploadFilename = (filename: string): boolean => {
  const trimmed = String(filename || '').trim();
  if (!trimmed) return false;
  if (ALLOWED_FIXED_FILES.has(trimmed)) return true;
  return /^(EP|DM|DA|PZ)-All\+Listings\+Report\.txt$/i.test(trimmed);
};

export function FileUploader() {
  const [isDragging, setIsDragging] = useState(false);
  const [serverFilesChecked, setServerFilesChecked] = useState(false);
  const uploadedFiles = useUploadStore((state) => state.uploadedFiles);
  const addUploadedFile = useUploadStore((state) => state.addUploadedFile);
  const clearUploadedFiles = useUploadStore((state) => state.clearUploadedFiles);
  const hasLoadedServerFiles = useRef(false);

  useEffect(() => {
    if (hasLoadedServerFiles.current) {
      return;
    }
    hasLoadedServerFiles.current = true;

    const loadServerFiles = async () => {
      try {
        const files = await excelApi.listFiles();
        const existingFiles = files.filter((file) => isAllowedUploadFilename(file.filename));

        if (existingFiles.length > 0) {
          clearUploadedFiles();
          existingFiles.forEach((file) => {
            addUploadedFile(file.filename);
          });
          toast.success(`已加载 ${existingFiles.length} 个数据文件`);
        }
      } catch (err) {
        console.error('加载服务器文件失败', err);
        toast.error('加载服务器文件失败');
      } finally {
        setServerFilesChecked(true);
      }
    };

    loadServerFiles();
  }, [addUploadedFile, clearUploadedFiles]);

  const uploadMutation = useMutation({
    mutationFn: async (files: File[]): Promise<AnalysisResult[]> => {
      const results: AnalysisResult[] = [];
      for (const file of files) {
        const data = await excelApi.analyzeFile(file);
        results.push(data);
      }
      return results;
    },
    onSuccess: (results: AnalysisResult[]) => {
      results.forEach((item) => addUploadedFile(item.filename));
      toast.success(`上传完成：${results.length} 个文件`);
    },
    onError: (error: Error) => {
      toast.error(`上传失败: ${error.message}`);
    },
  });

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    const allowedFiles = files.filter((file) => isAllowedUploadFilename(file.name));

    if (allowedFiles.length > 0) {
      uploadMutation.mutate(allowedFiles);
      return;
    }

    toast.error(`仅支持上传：${UPLOAD_FILE_HINT}`);
  }, [uploadMutation]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const selectedFiles = Array.from(files).filter((file) => isAllowedUploadFilename(file.name));
      if (selectedFiles.length > 0) {
        uploadMutation.mutate(selectedFiles);
      } else {
        toast.error(`仅支持上传：${UPLOAD_FILE_HINT}`);
      }
    }
    e.target.value = '';
  }, [uploadMutation]);

  return (
    <div className="space-y-4">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200
          ${isDragging ? 'border-primary-500 bg-primary-50' : 'border-slate-300 hover:border-primary-400 hover:bg-slate-50'}
          ${uploadMutation.isPending ? 'opacity-50 pointer-events-none' : 'cursor-pointer'}
        `}
      >
        <input
          type="file"
          id="file-upload"
          accept=".xlsm,.txt"
          onChange={handleFileSelect}
          className="hidden"
          disabled={uploadMutation.isPending}
          multiple
        />

        <label
          htmlFor="file-upload"
          className="cursor-pointer flex flex-col items-center space-y-3"
        >
          <div className="p-3 bg-primary-100 rounded-full">
            <svg
              className="w-8 h-8 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>

          <div className="text-sm text-slate-700">
            {uploadMutation.isPending ? (
              <span className="flex items-center gap-2 text-primary-600 font-medium">
                <svg className="animate-spin h-4 w-4 motion-reduce:animate-none" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                上传中...
              </span>
            ) : (
              <>
                <span className="text-primary-600 hover:text-primary-700 font-medium">
                  点击上传
                </span>
                <span className="text-slate-600"> 或拖拽文件到此处</span>
              </>
            )}
          </div>

          <div className="text-xs text-slate-500">
            {UPLOAD_FILE_HINT}
          </div>
        </label>
      </div>

      {uploadedFiles.length > 0 && (
        <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700">
          <p className="font-medium">已加载 {uploadedFiles.length} 个数据文件</p>
          <ul className="mt-1 list-disc pl-5 text-xs text-slate-600">
            {uploadedFiles.map((filename) => (
              <li key={filename}>{filename}</li>
            ))}
          </ul>
        </div>
      )}

      {serverFilesChecked && uploadedFiles.length === 0 && !uploadMutation.isPending && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
          未检测到服务器中的固定数据文件，请先上传：{UPLOAD_FILE_HINT}
        </div>
      )}

      {uploadMutation.isError && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-3">
          <div className="flex items-start">
            <svg className="h-5 w-5 text-red-400 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <p className="text-sm text-red-800 font-medium">上传失败</p>
              <p className="text-sm text-red-700 mt-0.5">{uploadMutation.error.message}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
