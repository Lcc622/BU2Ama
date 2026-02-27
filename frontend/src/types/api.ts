/**
 * API 类型定义
 */

// 颜色映射
export interface ColorMapping {
  [code: string]: string;
}

export interface ColorMappingResponse {
  success: boolean;
  data?: ColorMapping;
  message?: string;
}

export interface ColorMappingSearchResponse {
  success: boolean;
  data?: ColorMapping;
  count: number;
}

// Excel 分析
export interface ColorDistribution {
  color_code: string;
  color_name: string | null;
  count: number;
}

export interface AnalysisResult {
  success: boolean;
  filename: string;
  total_skus: number;
  unique_colors: number;
  color_distribution: ColorDistribution[];
  unknown_colors: string[];
  prefixes: string[];
  suffixes: string[];
}

// Excel 处理
export interface ProcessRequest {
  template_type: string;
  filenames: string[];
  selected_prefixes: string[];
  target_color?: string | null;
  target_size?: string | null;
}

export interface ProcessResponse {
  success: boolean;
  output_filename?: string;
  message?: string;
  processed_count: number;
}

// 模板信息
export interface TemplateInfo {
  name: string;
  file: string;
  exists: boolean;
}

// 文件信息
export interface FileInfo {
  filename: string;
  size: number;
  upload_time: string;
}
