import { create } from 'zustand';

interface FollowSellState {
  uploadedFile: File | null;
  newProductCode: string;
  processing: boolean;
  result: {
    totalSkus: number;
    oldProductCode: string;
    newProductCode: string;
    outputFilename: string;
    priceAdjustment: number;
    dateUsed: string;
  } | null;
  error: string | null;

  setUploadedFile: (file: File | null) => void;
  setNewProductCode: (code: string) => void;
  setProcessing: (processing: boolean) => void;
  setResult: (result: any) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useFollowSellStore = create<FollowSellState>((set) => ({
  uploadedFile: null,
  newProductCode: '',
  processing: false,
  result: null,
  error: null,

  setUploadedFile: (file) => set({ uploadedFile: file, error: null }),
  setNewProductCode: (code) => set({ newProductCode: code, error: null }),
  setProcessing: (processing) => set({ processing }),
  setResult: (result) => set({ result, error: null }),
  setError: (error) => set({ error, result: null }),

  reset: () => set({
    uploadedFile: null,
    newProductCode: '',
    processing: false,
    result: null,
    error: null,
  }),
}));
