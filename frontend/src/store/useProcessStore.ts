/**
 * Zustand Store - 处理状态管理
 */
import { create } from 'zustand';

interface ProcessStore {
  // 选中的模板类型
  templateType: 'DaMaUS' | 'EPUS' | 'PZUS';
  setTemplateType: (type: 'DaMaUS' | 'EPUS' | 'PZUS') => void;

  // 产品前缀（新增）
  productPrefix: string;
  setProductPrefix: (prefix: string) => void;

  // 处理模式（新增）
  mode: 'add-color' | 'add-code';
  setMode: (mode: 'add-color' | 'add-code') => void;

  // 尺码范围（新增）
  startSize: string;
  setStartSize: (size: string) => void;
  endSize: string;
  setEndSize: (size: string) => void;
  sizeStep: number;
  setSizeStep: (step: number) => void;

  // 颜色列表（新增）
  colorList: string;
  setColorList: (colors: string) => void;

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

  // SKU 生成方法（新增）
  generateSKUs: () => string[];

  // 重置状态
  reset: () => void;
}

export const useProcessStore = create<ProcessStore>((set, get) => ({
  templateType: 'DaMaUS',
  setTemplateType: (type) => set({ templateType: type }),

  productPrefix: '',
  setProductPrefix: (prefix) => set({ productPrefix: prefix }),

  mode: 'add-color',
  setMode: (mode) => set({ mode }),

  startSize: '',
  setStartSize: (size) => set({ startSize: size }),

  endSize: '',
  setEndSize: (size) => set({ endSize: size }),

  sizeStep: 2,
  setSizeStep: (step) => set({ sizeStep: step }),

  colorList: '',
  setColorList: (colors) => set({ colorList: colors }),

  targetColor: null,
  setTargetColor: (color) => set({ targetColor: color }),

  targetSize: null,
  setTargetSize: (size) => set({ targetSize: size }),

  isProcessing: false,
  setIsProcessing: (processing) => set({ isProcessing: processing }),

  outputFilename: null,
  setOutputFilename: (filename) => set({ outputFilename: filename }),

  generateSKUs: () => {
    const state = get();
    const { productPrefix, mode, startSize, endSize, sizeStep, colorList } = state;

    if (!productPrefix) return [];

    if (mode === 'add-color') {
      // 加色模式：一个颜色 × 多个尺码
      const colors = colorList
        .split(/[,，\s]+/)
        .map((c) => c.trim().toUpperCase())
        .filter((c) => c.length === 2);

      if (colors.length === 0) return [];

      const start = parseInt(startSize, 10);
      const end = parseInt(endSize, 10);

      if (isNaN(start) || isNaN(end) || start > end) return [];

      const skus: string[] = [];
      const color = colors[0]; // 只取第一个颜色

      for (let size = start; size <= end; size += sizeStep) {
        const sizeStr = size.toString().padStart(2, '0');
        skus.push(`${productPrefix}${color}${sizeStr}`);
      }

      return skus;
    } else {
      // 加码模式：多个颜色 × 一个尺码
      const colors = colorList
        .split(/[,，\s]+/)
        .map((c) => c.trim().toUpperCase())
        .filter((c) => c.length === 2);

      if (colors.length === 0) return [];

      const size = parseInt(startSize, 10);
      if (isNaN(size)) return [];

      const sizeStr = size.toString().padStart(2, '0');

      return colors.map((color) => `${productPrefix}${color}${sizeStr}`);
    }
  },

  reset: () =>
    set({
      templateType: 'DaMaUS',
      productPrefix: '',
      mode: 'add-color',
      startSize: '',
      endSize: '',
      sizeStep: 2,
      colorList: '',
      targetColor: null,
      targetSize: null,
      isProcessing: false,
      outputFilename: null,
    }),
}));
