import React, { useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { excelApi } from '@/services/excelApi';
import type { SKCQueryResponse } from '@/types/api';

type SKCQueryItem = {
  inputSkc: string;
  result: SKCQueryResponse;
};

export const FollowSellUpload: React.FC = () => {
  const [skcInput, setSkcInput] = useState('');
  const selectedTemplate = 'EPUS';
  const [queryLoading, setQueryLoading] = useState(false);
  const [queryResults, setQueryResults] = useState<SKCQueryItem[]>([]);
  const [queryError, setQueryError] = useState<string | null>(null);
  const [exportingSkc, setExportingSkc] = useState<string | null>(null);
  const [batchExporting, setBatchExporting] = useState(false);

  const handleSkcQuery = async () => {
    if (!skcInput.trim()) {
      setQueryError('请输入至少 1 条 SKC（7位款号+2位颜色）');
      setQueryResults([]);
      return;
    }

    const skcList = Array.from(
      new Set(
        skcInput
          .toUpperCase()
          .split(/[\n,，\s]+/)
          .map((item) => item.trim())
          .filter(Boolean)
      )
    );

    if (skcList.length === 0) {
      setQueryError('请输入至少 1 条有效 SKC');
      setQueryResults([]);
      return;
    }

    setQueryLoading(true);
    setQueryError(null);
    setQueryResults([]);

    try {
      const settled = await Promise.allSettled(
        skcList.map(async (skc) => {
          const result = await excelApi.queryFollowSellSkc(skc, selectedTemplate);
          return { inputSkc: skc, result };
        })
      );

      const merged: SKCQueryItem[] = settled.map((item, index) => {
        if (item.status === 'fulfilled') {
          return item.value;
        }

        return {
          inputSkc: skcList[index],
          result: {
            success: false,
            skc: skcList[index],
            new_style: '',
            old_style: '',
            color_code: '',
            sizes: [],
            message: item.reason?.response?.data?.detail || item.reason?.message || '查询失败',
          },
        };
      });

      setQueryResults(merged);
    } catch (err: any) {
      setQueryError(err.response?.data?.detail || err.message || '查询失败，请重试');
    } finally {
      setQueryLoading(false);
    }
  };

  const triggerDownloadByFilename = (filename: string) => {
    const url = excelApi.getDownloadUrl(filename);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const handleExportSingleSkc = async (skc: string) => {
    setExportingSkc(skc);
    setQueryError(null);
    try {
      const response = await excelApi.processFollowSellSkc(skc, selectedTemplate);
      if (response.success && response.output_filename) {
        triggerDownloadByFilename(response.output_filename);
      } else {
        setQueryError(response.message || `导出 ${skc} 失败`);
      }
    } catch (err: any) {
      setQueryError(err.response?.data?.detail || err.message || `导出 ${skc} 失败`);
    } finally {
      setExportingSkc(null);
    }
  };

  const handleBatchExport = async () => {
    const successSkcs = queryResults
      .filter((item) => item.result.success)
      .map((item) => item.inputSkc);
    if (successSkcs.length === 0) {
      setQueryError('没有可导出的成功 SKC');
      return;
    }

    setBatchExporting(true);
    setQueryError(null);
    try {
      const response = await excelApi.processFollowSellSkcBatch(successSkcs, selectedTemplate);
      if (response.success && response.output_filename) {
        triggerDownloadByFilename(response.output_filename);
      } else {
        setQueryError(response.message || '合并导出失败');
      }
    } catch (err: any) {
      setQueryError(err.response?.data?.detail || err.message || '合并导出失败');
    } finally {
      setBatchExporting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-6">SKC 尺码查询（跟卖映射）</h2>

        {/* 店铺模板（EP 固定） */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">店铺模板</label>
          <div className="flex gap-3">
            <button
              className="px-4 py-2 rounded-lg font-medium bg-blue-600 text-white"
            >
              EPUS
            </button>
          </div>
          <p className="mt-1 text-xs text-gray-500">
            将从 EP 店铺的源数据中查询和导出
          </p>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            🔎 输入 SKC（支持多条，换行/逗号分隔）
          </label>
          <div className="flex gap-3">
            <textarea
              value={skcInput}
              onChange={(e) => setSkcInput(e.target.value.toUpperCase())}
              placeholder={'例如:\nEE00756DB\nES02522BK'}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[104px]"
              maxLength={2000}
              disabled={queryLoading}
            />
            <div className="flex items-start">
              <button
                onClick={handleSkcQuery}
                disabled={queryLoading || !skcInput.trim()}
                className={`px-5 py-2 rounded-lg font-medium transition-colors ${
                  queryLoading || !skcInput.trim()
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {queryLoading ? '查询中...' : '批量查询尺码'}
              </button>
            </div>
          </div>
          <p className="mt-1 text-xs text-gray-500">按每条 SKC 自动查新老款映射，再到 EP-0/1/2 聚合表提取全部尺码</p>
        </div>

        {queryError && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
            <AlertCircle className="w-5 h-5 text-red-500 mr-3 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-700">{queryError}</p>
          </div>
        )}

        {queryResults.length > 0 && (
          <div className="space-y-4">
            <div className="flex justify-end">
              <button
                onClick={handleBatchExport}
                disabled={batchExporting || queryResults.every((item) => !item.result.success)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  batchExporting || queryResults.every((item) => !item.result.success)
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-emerald-600 text-white hover:bg-emerald-700'
                }`}
              >
                {batchExporting ? '合并导出中...' : '导出全部成功 SKC（一个 Excel）'}
              </button>
            </div>
            {queryResults.map(({ inputSkc, result }) => (
              <div
                key={`${inputSkc}-${result.message}`}
                className={`rounded-lg border p-4 ${result.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}
              >
                <div className="flex items-start justify-between gap-3 mb-3">
                  <p className={`text-sm ${result.success ? 'text-green-800' : 'text-red-700'}`}>
                    SKC: {inputSkc} | {result.message}
                    {result.success && ` | 新款号: ${result.new_style} | 老款号: ${result.old_style} | 颜色: ${result.color_code}`}
                  </p>
                  {result.success && (
                    <button
                      onClick={() => handleExportSingleSkc(inputSkc)}
                      disabled={exportingSkc === inputSkc || batchExporting}
                      className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                        exportingSkc === inputSkc || batchExporting
                          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                          : 'bg-green-600 text-white hover:bg-green-700'
                      }`}
                    >
                      {exportingSkc === inputSkc ? '导出中...' : '导出该 SKC'}
                    </button>
                  )}
                </div>

                {result.success && (
                  <div className="overflow-x-auto border border-gray-200 rounded-lg bg-white">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">尺码</th>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">后缀</th>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">生成 SKU</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-100">
                        {result.sizes.map((item) => (
                          <tr key={`${inputSkc}-${item.size}-${item.suffix}-${item.sku}`}>
                            <td className="px-4 py-2 text-sm text-gray-700">{item.size}</td>
                            <td className="px-4 py-2 text-sm text-gray-700">{item.suffix || '-'}</td>
                            <td className="px-4 py-2 text-sm font-mono text-gray-900">{item.sku}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
