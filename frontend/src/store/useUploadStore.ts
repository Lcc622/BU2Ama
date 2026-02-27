/**
 * Zustand Store - 上传状态管理
 */
import { create } from 'zustand';
import type { AnalysisResult } from '../types/api';

interface UploadStore {
  // 已上传的文件列表
  uploadedFiles: string[];
  addUploadedFile: (filename: string) => void;
  removeUploadedFile: (filename: string) => void;
  clearUploadedFiles: () => void;

  // 当前分析结果（合并后的）
  analysisResult: AnalysisResult | null;
  setAnalysisResult: (result: AnalysisResult | null) => void;

  // 选中的前缀
  selectedPrefixes: string[];
  setSelectedPrefixes: (prefixes: string[]) => void;
  togglePrefix: (prefix: string) => void;

  // 重置状态
  reset: () => void;
}

export const useUploadStore = create<UploadStore>((set) => ({
  uploadedFiles: [],
  addUploadedFile: (filename) =>
    set((state) => ({
      uploadedFiles: state.uploadedFiles.includes(filename)
        ? state.uploadedFiles
        : [...state.uploadedFiles, filename],
    })),
  removeUploadedFile: (filename) =>
    set((state) => ({
      uploadedFiles: state.uploadedFiles.filter((f) => f !== filename),
    })),
  clearUploadedFiles: () => set({ uploadedFiles: [] }),

  analysisResult: null,
  setAnalysisResult: (result) => set({ analysisResult: result }),

  selectedPrefixes: [],
  setSelectedPrefixes: (prefixes) => set({ selectedPrefixes: prefixes }),
  togglePrefix: (prefix) =>
    set((state) => ({
      selectedPrefixes: state.selectedPrefixes.includes(prefix)
        ? state.selectedPrefixes.filter((p) => p !== prefix)
        : [...state.selectedPrefixes, prefix],
    })),

  reset: () =>
    set({
      uploadedFiles: [],
      analysisResult: null,
      selectedPrefixes: [],
    }),
}));
