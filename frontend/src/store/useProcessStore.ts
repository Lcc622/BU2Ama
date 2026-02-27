/**
 * Zustand Store - 处理状态管理
 */
import { create } from 'zustand';

interface ProcessStore {
  // 选中的模板类型
  templateType: string;
  setTemplateType: (type: string) => void;

  // 目标颜色（换色）
  targetColor: string | null;
  setTargetColor: (color: string | null) => void;

  // 目标尺码（加码）
  targetSize: string | null;
  setTargetSize: (size: string | null) => void;

  // 处理进度
  isProcessing: boolean;
  setIsProcessing: (processing: boolean) => void;

  // 生成的文件名
  outputFilename: string | null;
  setOutputFilename: (filename: string | null) => void;

  // 重置状态
  reset: () => void;
}

export const useProcessStore = create<ProcessStore>((set) => ({
  templateType: 'DaMaUS',
  setTemplateType: (type) => set({ templateType: type }),

  targetColor: null,
  setTargetColor: (color) => set({ targetColor: color }),

  targetSize: null,
  setTargetSize: (size) => set({ targetSize: size }),

  isProcessing: false,
  setIsProcessing: (processing) => set({ isProcessing: processing }),

  outputFilename: null,
  setOutputFilename: (filename) => set({ outputFilename: filename }),

  reset: () =>
    set({
      templateType: 'DaMaUS',
      targetColor: null,
      targetSize: null,
      isProcessing: false,
      outputFilename: null,
    }),
}));
