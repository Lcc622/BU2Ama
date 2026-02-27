/**
 * 文件上传组件 - 支持多文件上传
 */
import { useCallback, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { excelApi } from '../../services/excelApi';
import { useUploadStore } from '../../store/useUploadStore';
import type { AnalysisResult } from '../../types/api';
import toast from 'react-hot-toast';

export function FileUploader() {
  const [isDragging, setIsDragging] = useState(false);
  const uploadedFiles = useUploadStore((state) => state.uploadedFiles);
  const addUploadedFile = useUploadStore((state) => state.addUploadedFile);
  const removeUploadedFile = useUploadStore((state) => state.removeUploadedFile);
  const setAnalysisResult = useUploadStore((state) => state.setAnalysisResult);

  const uploadMutation = useMutation({
    mutationFn: excelApi.analyzeFile,
    onSuccess: (data: AnalysisResult) => {
      addUploadedFile(data.filename);
      // 如果是第一个文件，直接设置分析结果
      // 如果是后续文件，需要合并分析结果
      setAnalysisResult(data);
      toast.success(`文件 ${data.filename} 上传成功！`);
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
    const excelFiles = files.filter(
      (file) =>
        file.name.endsWith('.xlsx') ||
        file.name.endsWith('.xlsm') ||
        file.name.endsWith('.xls')
    );

    if (excelFiles.length > 0) {
      // 上传第一个文件
      uploadMutation.mutate(excelFiles[0]);
    } else {
      toast.error('请上传 Excel 文件（.xlsx, .xlsm, .xls）');
    }
  }, [uploadMutation]);

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        // 支持多文件选择，但一次只上传一个
        uploadMutation.mutate(files[0]);
      }
      // 清空 input 以允许重复上传同一文件
      e.target.value = '';
    },
    [uploadMutation]
  );

  const handleRemoveFile = useCallback(
    (filename: string) => {
      removeUploadedFile(filename);
      // 如果删除的是当前分析的文件，清空分析结果
      setAnalysisResult(null);
    },
    [removeUploadedFile, setAnalysisResult]
  );

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
          accept=".xlsx,.xlsm,.xls"
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
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                上传中…
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
            支持 .xlsx, .xlsm, .xls 格式 | 可多次上传
          </div>
        </label>
      </div>

      {/* 已上传文件列表 */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="text-sm font-semibold text-slate-700">
              已上传文件
            </div>
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
              {uploadedFiles.length} 个文件
            </span>
          </div>
          <div className="space-y-2">
            {uploadedFiles.map((filename) => (
              <div
                key={filename}
                className="flex items-center justify-between px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-lg hover:bg-slate-100 transition-colors duration-150"
              >
                <div className="flex items-center space-x-2 flex-1 min-w-0">
                  <svg
                    className="w-5 h-5 text-green-500 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <span className="text-sm text-slate-700 truncate">{filename}</span>
                </div>
                <button
                  onClick={() => handleRemoveFile(filename)}
                  className="ml-2 p-1 text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors duration-150 flex-shrink-0"
                  title="删除"
                  aria-label={`删除 ${filename}`}
                >
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            ))}
          </div>
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
