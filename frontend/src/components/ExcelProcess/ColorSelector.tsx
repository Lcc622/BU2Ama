import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { mappingApi } from '../../services/mappingApi';
import { useProcessStore } from '../../store/useProcessStore';

export function ColorSelector() {
  const { targetColor, setTargetColor, targetSize, setTargetSize } = useProcessStore();
  const [mode, setMode] = useState<'add-code' | 'add-color'>('add-code');

  const { data: mappings, isLoading } = useQuery({
    queryKey: ['mappings'],
    queryFn: mappingApi.getAll,
  });

  if (isLoading) {
    return <div className="text-sm text-gray-600">加载颜色列表...</div>;
  }

  const colorEntries = Object.entries(mappings || {}).sort((a, b) =>
    a[0].localeCompare(b[0])
  );

  // 生成尺码选项（02, 04, 06...30，只有偶数）
  const sizeOptions = Array.from({ length: 15 }, (_, i) => {
    const size = ((i + 1) * 2).toString().padStart(2, '0');
    return size;
  });

  const handleModeChange = (newMode: 'add-code' | 'add-color') => {
    setMode(newMode);
    if (newMode === 'add-code') {
      // 切换到加码模式，清除目标颜色
      setTargetColor(null);
    } else {
      // 切换到加色模式，清除目标尺码
      setTargetSize(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* 模式选择 */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">
          处理模式
        </label>
        <div className="flex gap-4">
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              name="mode"
              value="add-code"
              checked={mode === 'add-code'}
              onChange={() => handleModeChange('add-code')}
              className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">
              加码（替换尺码）
            </span>
          </label>
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              name="mode"
              value="add-color"
              checked={mode === 'add-color'}
              onChange={() => handleModeChange('add-color')}
              className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">
              加色（替换颜色）
            </span>
          </label>
        </div>

        {/* 模式说明 */}
        {mode === 'add-code' && (
          <p className="text-xs text-gray-600 bg-blue-50 border border-blue-200 rounded p-2">
            加码模式：保持原始颜色，替换 SKU 中的尺码（10-11位）
          </p>
        )}
      </div>

      {/* 尺码选择器 - 只在加码模式下显示 */}
      {mode === 'add-code' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700">
              目标尺码
            </label>
            {targetSize && (
              <button
                onClick={() => setTargetSize('')}
                className="text-xs text-blue-600 hover:text-blue-800"
              >
                清除选择
              </button>
            )}
          </div>

          <select
            value={targetSize || ''}
            onChange={(e) => setTargetSize(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">请选择目标尺码</option>
            {sizeOptions.map((size) => (
              <option key={size} value={size}>
                {size}
              </option>
            ))}
          </select>

          {targetSize && (
            <p className="text-xs text-gray-600">
              将把所有 SKU 的尺码替换为: <span className="font-semibold">{targetSize}</span>
            </p>
          )}
        </div>
      )}

      {/* 颜色选择器 - 只在加色模式下显示 */}
      {mode === 'add-color' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700">
              目标颜色
            </label>
            {targetColor && (
              <button
                onClick={() => setTargetColor(null)}
                className="text-xs text-blue-600 hover:text-blue-800"
              >
                清除选择
              </button>
            )}
          </div>

          <select
            value={targetColor || ''}
            onChange={(e) => setTargetColor(e.target.value || null)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">请选择目标颜色</option>
            {colorEntries.map(([code, name]) => (
              <option key={code} value={code}>
                {code} - {name}
              </option>
            ))}
          </select>

          {targetColor && (
            <p className="text-xs text-gray-600">
              将把所有 SKU 的颜色替换为: <span className="font-semibold">{targetColor} - {mappings?.[targetColor]}</span>
            </p>
          )}
        </div>
      )}
    </div>
  );
}
