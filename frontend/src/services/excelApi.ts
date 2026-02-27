/**
 * Excel 处理 API 服务
 */
import { apiClient } from '../lib/axios';
import type {
  AnalysisResult,
  ProcessRequest,
  ProcessResponse,
  TemplateInfo,
  FileInfo,
} from '../types/api';

export const excelApi = {
  // 获取可用模板
  getTemplates: async (): Promise<TemplateInfo[]> => {
    const { data } = await apiClient.get<TemplateInfo[]>('/api/templates');
    return data;
  },

  // 分析上传的文件
  analyzeFile: async (file: File): Promise<AnalysisResult> => {
    const formData = new FormData();
    formData.append('file', file);

    const { data } = await apiClient.post<AnalysisResult>(
      '/api/analyze',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return data;
  },

  // 处理 Excel 文件
  processExcel: async (request: ProcessRequest): Promise<ProcessResponse> => {
    const { data } = await apiClient.post<ProcessResponse>(
      '/api/process',
      request
    );
    return data;
  },

  // 获取下载链接
  getDownloadUrl: (filename: string): string => {
    return `${apiClient.defaults.baseURL}/api/download/${filename}`;
  },

  // 列出已上传的文件
  listFiles: async (): Promise<FileInfo[]> => {
    const { data } = await apiClient.get<FileInfo[]>('/api/files');
    return data;
  },

  // 删除文件
  deleteFile: async (filename: string): Promise<void> => {
    await apiClient.delete(`/api/files/${filename}`);
  },
};
