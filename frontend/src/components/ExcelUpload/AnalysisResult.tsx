/**
 * Excel 分析结果展示组件
 */
import { useUploadStore } from '../../store/useUploadStore';

export function AnalysisResult() {
  const analysisResult = useUploadStore((state) => state.analysisResult);
  const setSelectedPrefixes = useUploadStore((state) => state.setSelectedPrefixes);

  if (!analysisResult) {
    return null;
  }

  const handleSelectAllPrefixes = () => {
    setSelectedPrefixes(analysisResult.prefixes);
  };

  return (
    <div className="space-y-4 mt-6">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">分析结果</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">文件名：</span>
            <span className="font-medium">{analysisResult.filename}</span>
          </div>
          <div>
            <span className="text-gray-600">总 SKU 数：</span>
            <span className="font-medium">{analysisResult.total_skus}</span>
          </div>
          <div>
            <span className="text-gray-600">颜色种类：</span>
            <span className="font-medium">{analysisResult.unique_colors}</span>
          </div>
          <div>
            <span className="text-gray-600">产品前缀：</span>
            <span className="font-medium">{analysisResult.prefixes.length}</span>
          </div>
        </div>
      </div>

      {/* 颜色分布 */}
      <div>
        <h4 className="font-semibold text-gray-900 mb-2">颜色分布（前 10）</h4>
        <div className="max-h-48 overflow-y-auto border rounded-lg">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  颜色代码
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  颜色名称
                </th>
                <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                  数量
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {analysisResult.color_distribution.slice(0, 10).map((item) => (
                <tr key={item.color_code} className="hover:bg-gray-50">
                  <td className="px-3 py-2 text-sm font-medium text-gray-900">
                    {item.color_code}
                  </td>
                  <td className="px-3 py-2 text-sm text-gray-600">
                    {item.color_name || (
                      <span className="text-red-600">未知</span>
                    )}
                  </td>
                  <td className="px-3 py-2 text-sm text-gray-900 text-right">
                    {item.count}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 未知颜色 */}
      {analysisResult.unknown_colors.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h4 className="font-semibold text-yellow-900 mb-2">
            ⚠️ 未知颜色代码（{analysisResult.unknown_colors.length}）
          </h4>
          <div className="flex flex-wrap gap-2">
            {analysisResult.unknown_colors.map((code) => (
              <span
                key={code}
                className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded"
              >
                {code}
              </span>
            ))}
          </div>
          <p className="text-xs text-yellow-700 mt-2">
            请先在右侧添加这些颜色的映射
          </p>
        </div>
      )}

      {/* 产品前缀选择 */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <h4 className="font-semibold text-gray-900">
            选择产品前缀（{analysisResult.prefixes.length}）
          </h4>
          <button
            onClick={handleSelectAllPrefixes}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            全选
          </button>
        </div>
        <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-2 border rounded-lg">
          {analysisResult.prefixes.map((prefix) => (
            <PrefixCheckbox key={prefix} prefix={prefix} />
          ))}
        </div>
      </div>
    </div>
  );
}

function PrefixCheckbox({ prefix }: { prefix: string }) {
  const selectedPrefixes = useUploadStore((state) => state.selectedPrefixes);
  const togglePrefix = useUploadStore((state) => state.togglePrefix);

  const isSelected = selectedPrefixes.includes(prefix);

  return (
    <label className="flex items-center space-x-2 cursor-pointer">
      <input
        type="checkbox"
        checked={isSelected}
        onChange={() => togglePrefix(prefix)}
        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
      />
      <span className="text-sm text-gray-700">{prefix}</span>
    </label>
  );
}
