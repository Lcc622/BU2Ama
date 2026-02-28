/**
 * Excel 处理 API 服务
 */
import { apiClient } from '../lib/axios';
import type {
  AnalysisResult,
  ProcessRequest,
  ProcessResponse,
  ProcessAsyncStartResponse,
  ProcessJobStatusResponse,
  TemplateInfo,
  FileInfo,
  SKCQueryResponse,
  SKCProcessResponse,
  SKCBatchProcessResponse,
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

  // 分析服务器上已存在的文件
  analyzeExistingFile: async (filename: string): Promise<AnalysisResult> => {
    const { data } = await apiClient.post<AnalysisResult>(
      '/api/analyze-existing',
      null,
      {
        params: { filename },
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

  // 异步处理：创建任务
  processExcelAsync: async (request: ProcessRequest): Promise<ProcessAsyncStartResponse> => {
    const { data } = await apiClient.post<ProcessAsyncStartResponse>(
      '/api/process-async',
      request
    );
    return data;
  },

  // 异步处理：查询任务状态
  getProcessStatus: async (jobId: string): Promise<ProcessJobStatusResponse> => {
    const { data } = await apiClient.get<ProcessJobStatusResponse>(`/api/process-status/${jobId}`);
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

  // 跟卖 SKC 查询尺码
  queryFollowSellSkc: async (skc: string): Promise<SKCQueryResponse> => {
    const { data } = await apiClient.post<SKCQueryResponse>(
      '/api/follow-sell/query-skc',
      { skc }
    );
    return data;
  },

  processFollowSellSkc: async (skc: string, templateType = 'EPUS'): Promise<SKCProcessResponse> => {
    const { data } = await apiClient.post<SKCProcessResponse>(
      '/api/follow-sell/process-skc',
      { skc, template_type: templateType }
    );
    return data;
  },

  processFollowSellSkcBatch: async (skcs: string[], templateType = 'EPUS'): Promise<SKCBatchProcessResponse> => {
    const { data } = await apiClient.post<SKCBatchProcessResponse>(
      '/api/follow-sell/process-skc-batch',
      { skcs, template_type: templateType }
    );
    return data;
  },
};
