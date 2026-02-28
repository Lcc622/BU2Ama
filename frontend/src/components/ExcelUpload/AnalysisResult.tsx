/**
 * Excel 分析结果展示组件
 */
import { useUploadStore } from '../../store/useUploadStore';

export function AnalysisResult() {
  const analysisResult = useUploadStore((state) => state.analysisResult);

  if (!analysisResult) {
    return null;
  }

  const unknownColors = Array.isArray(analysisResult.unknown_colors)
    ? analysisResult.unknown_colors
    : [];

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
        </div>
      </div>

      {/* 未知颜色 */}
      {unknownColors.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h4 className="font-semibold text-yellow-900 mb-2">
            ⚠️ 未知颜色代码（{unknownColors.length}）
          </h4>
          <div className="flex flex-wrap gap-2">
            {unknownColors.map((code) => (
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
    </div>
  );
}
