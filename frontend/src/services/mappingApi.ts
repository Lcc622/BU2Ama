/**
 * 颜色映射 API 服务
 */
import { apiClient } from '../lib/axios';
import type {
  ColorMapping,
  ColorMappingResponse,
  ColorMappingSearchResponse,
} from '../types/api';

export const mappingApi = {
  // 获取所有颜色映射
  getAll: async (): Promise<ColorMapping> => {
    const { data } = await apiClient.get<ColorMappingResponse>('/api/mapping');
    return data.data || {};
  },

  // 搜索颜色映射
  search: async (keyword: string): Promise<ColorMapping> => {
    const { data } = await apiClient.get<ColorMappingSearchResponse>(
      '/api/mapping/search',
      { params: { keyword } }
    );
    return data.data || {};
  },

  // 添加或更新颜色映射
  addMapping: async (code: string, name: string): Promise<void> => {
    await apiClient.post('/api/mapping', { code, name });
  },

  // 批量添加颜色映射
  addMappingsBatch: async (mappings: ColorMapping): Promise<void> => {
    await apiClient.post('/api/mapping', mappings);
  },

  // 删除颜色映射
  deleteMapping: async (code: string): Promise<void> => {
    await apiClient.delete(`/api/mapping/${code}`);
  },
};
