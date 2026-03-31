/**
 * 颜色映射 API 服务
 */
import { apiClient } from '../lib/axios';
import type {
  ColorMapping,
  ColorMappingResponse,
  ColorMappingSearchResponse,
} from '../types/api';
import fallbackColorMappings from '../data/colorMapping';

export const mappingApi = {
  // 获取所有颜色映射
  getAll: async (): Promise<ColorMapping> => {
    try {
      const { data } = await apiClient.get<ColorMappingResponse>('/api/mapping');
      const mappings = data.data || {};
      if (Object.keys(mappings).length > 0) {
        return mappings;
      }
      return fallbackColorMappings;
    } catch {
      return fallbackColorMappings;
    }
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
