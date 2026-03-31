import React, { useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Download,
  History,
  Search,
  Trash2,
} from 'lucide-react';
import { excelApi } from '@/services/excelApi';
import type { ExportHistoryItem } from '@/types/api';

type ModuleType = 'all' | 'follow-sell' | 'add-color' | 'add-code';

interface ExportHistoryProps {
  title?: string;
  defaultModule?: ModuleType;
}

const PAGE_SIZE = 20;

const moduleLabelMap: Record<Exclude<ModuleType, 'all'>, string> = {
  'follow-sell': '跟卖',
  'add-color': '加色',
  'add-code': '加码',
};

export const ExportHistory: React.FC<ExportHistoryProps> = ({
  title = '导出历史',
  defaultModule = 'all',
}) => {
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<ExportHistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [moduleFilter, setModuleFilter] = useState<ModuleType>(defaultModule);
  const [searchText, setSearchText] = useState('');
  const [searchDebounced, setSearchDebounced] = useState('');
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const normalizedModuleFilter = useMemo(
    () => (moduleFilter === 'all' ? undefined : moduleFilter),
    [moduleFilter]
  );

  const loadHistory = async (targetPage = 1, append = false, keyword = searchDebounced) => {
    setLoading(true);
    setError(null);
    try {
      const response = await excelApi.getExportHistory(
        targetPage,
        PAGE_SIZE,
        normalizedModuleFilter,
        keyword || undefined
      );
      setTotal(response.total);
      setPage(targetPage);
      setItems((prev) => (append ? [...prev, ...response.data] : response.data));
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '获取历史记录失败');
      if (!append) {
        setItems([]);
        setTotal(0);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('确定删除该历史记录及对应文件吗？')) {
      return;
    }
    setDeletingId(id);
    setError(null);
    try {
      await excelApi.deleteExportHistory(id);
      await loadHistory(1, false);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '删除历史记录失败');
    } finally {
      setDeletingId(null);
    }
  };

  const handleDownload = async (item: ExportHistoryItem) => {
    setError(null);
    const url = excelApi.downloadExportHistory(item.id);
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('下载失败');
      }
      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        const payload = await response.json();
        setError(payload?.message || '文件不存在');
        await loadHistory(1, false);
        return;
      }

      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = item.filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(blobUrl);
    } catch (err: any) {
      setError(err.message || '下载失败');
    }
  };

  const renderInputData = (item: ExportHistoryItem) => {
    const input = item.input_data || {};
    if (item.module === 'follow-sell') {
      return `SKC: ${input.skc || '-'} | 新款: ${input.new_style || '-'} | 老款: ${input.old_style || '-'}`;
    }
    const prefixes = Array.isArray(input.prefixes) ? input.prefixes.join(', ') : '-';
    const colors = Array.isArray(input.colors) ? input.colors.join(', ') : '-';
    const sizes = Array.isArray(input.sizes) ? input.sizes.join(', ') : '-';
    return `前缀: ${prefixes} | 颜色: ${colors} | 尺码: ${sizes} | 模式: ${input.mode || item.module}`;
  };

  const formatDateTime = (utcStr: string) => {
    if (!utcStr) return '-';
    // SQLite CURRENT_TIMESTAMP 格式 "YYYY-MM-DD HH:MM:SS"，无 timezone 标记，实为 UTC
    const normalized = utcStr.includes('T') ? utcStr : utcStr.replace(' ', 'T') + 'Z';
    return new Date(normalized).toLocaleString('zh-CN', {
      timeZone: 'Asia/Shanghai',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
  };

  const formatFileSize = (bytes: number) => {
    if (!bytes) return '-';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const statusNode = (status: ExportHistoryItem['status']) => {
    if (status === 'success') {
      return (
        <span className="inline-flex items-center gap-1 text-xs text-green-700">
          <CheckCircle2 className="w-4 h-4" /> success
        </span>
      );
    }
    if (status === 'file_missing') {
      return (
        <span className="inline-flex items-center gap-1 text-xs text-yellow-700">
          <AlertTriangle className="w-4 h-4" /> file_missing
        </span>
      );
    }
    return <span className="inline-flex items-center gap-1 text-xs text-red-700">✕ failed</span>;
  };

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSearchDebounced(searchText.trim());
    }, 350);
    return () => window.clearTimeout(timer);
  }, [searchText]);

  useEffect(() => {
    setModuleFilter(defaultModule);
  }, [defaultModule]);

  useEffect(() => {
    if (expanded) {
      void loadHistory(1, false, searchDebounced);
    }
  }, [expanded, normalizedModuleFilter, searchDebounced]);

  const hasMore = items.length < total;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <button
        type="button"
        onClick={() => {
          const next = !expanded;
          setExpanded(next);
          if (next && items.length === 0) {
            void loadHistory(1, false);
          }
        }}
        className="w-full flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-gray-700" />
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
        {expanded ? <ChevronUp className="w-5 h-5 text-gray-600" /> : <ChevronDown className="w-5 h-5 text-gray-600" />}
      </button>

      {expanded && (
        <div className="mt-4 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <select
              value={moduleFilter}
              onChange={(e) => setModuleFilter(e.target.value as ModuleType)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">全部模块</option>
              <option value="follow-sell">跟卖</option>
              <option value="add-color">加色</option>
              <option value="add-code">加码</option>
            </select>
            <div className="relative">
              <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                placeholder="搜索输入参数"
                className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {error && <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">{error}</div>}

          <div className="border border-gray-200 rounded-lg divide-y divide-gray-100">
            {items.length === 0 && !loading && (
              <div className="p-4 text-sm text-gray-500">暂无历史记录</div>
            )}
            {items.map((item) => (
              <div key={item.id} className="p-4 flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <p className="text-sm text-gray-900 font-medium">
                    模块: {moduleLabelMap[item.module] || item.module} | 模板: {item.template_type || '-'} | 处理数: {item.processed_count}
                  </p>
                  <p className="text-sm text-gray-700">{renderInputData(item)}</p>
                  <p className="text-xs text-gray-500">
                    时间: {formatDateTime(item.created_at)} | 大小: {formatFileSize(item.file_size)} | 文件: {item.filename}
                  </p>
                  {statusNode(item.status)}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => void handleDownload(item)}
                    className="inline-flex items-center gap-1 px-3 py-1.5 text-xs rounded bg-blue-600 text-white hover:bg-blue-700"
                  >
                    <Download className="w-3.5 h-3.5" />
                    下载
                  </button>
                  <button
                    type="button"
                    onClick={() => void handleDelete(item.id)}
                    disabled={deletingId === item.id}
                    className={`inline-flex items-center gap-1 px-3 py-1.5 text-xs rounded ${
                      deletingId === item.id
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        : 'bg-red-600 text-white hover:bg-red-700'
                    }`}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    {deletingId === item.id ? '删除中...' : '删除'}
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between">
            <p className="text-xs text-gray-500">已加载 {items.length} / {total} 条</p>
            {hasMore && (
              <button
                type="button"
                onClick={() => void loadHistory(page + 1, true)}
                disabled={loading}
                className={`px-3 py-1.5 text-xs rounded ${
                  loading ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-gray-800 text-white hover:bg-gray-900'
                }`}
              >
                {loading ? '加载中...' : '加载更多'}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
