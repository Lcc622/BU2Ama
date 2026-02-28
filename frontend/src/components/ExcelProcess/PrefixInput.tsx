/**
 * 产品前缀输入组件
 */
import { useState } from 'react';
import { useUploadStore } from '../../store/useUploadStore';

export function PrefixInput() {
  const [inputValue, setInputValue] = useState('');
  const selectedPrefixes = useUploadStore((state) => state.selectedPrefixes);
  const setSelectedPrefixes = useUploadStore((state) => state.setSelectedPrefixes);

  const handleAdd = () => {
    const prefix = inputValue.trim().toUpperCase();
    if (!prefix) return;

    if (selectedPrefixes.includes(prefix)) {
      return; // 已存在，不重复添加
    }

    setSelectedPrefixes([...selectedPrefixes, prefix]);
    setInputValue('');
  };

  const handleRemove = (prefix: string) => {
    setSelectedPrefixes(selectedPrefixes.filter((p) => p !== prefix));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAdd();
    }
  };

  return (
    <div className="space-y-3">
      <div>
        <label className="block text-sm font-semibold text-slate-700 mb-2">
          产品前缀
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="例如：EG02230"
            className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <button
            onClick={handleAdd}
            disabled={!inputValue.trim()}
            className={`
              px-4 py-2 rounded-lg text-sm font-medium transition-colors
              ${
                inputValue.trim()
                  ? 'bg-primary-600 text-white hover:bg-primary-700'
                  : 'bg-slate-200 text-slate-400 cursor-not-allowed'
              }
            `}
          >
            添加
          </button>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          输入产品前缀（7-8位字符），按回车或点击添加
        </p>
      </div>

      {/* 已添加的前缀列表 */}
      {selectedPrefixes.length > 0 && (
        <div>
          <div className="text-xs font-medium text-slate-600 mb-2">
            已添加 ({selectedPrefixes.length})
          </div>
          <div className="flex flex-wrap gap-2">
            {selectedPrefixes.map((prefix) => (
              <div
                key={prefix}
                className="inline-flex items-center gap-2 px-3 py-1.5 bg-primary-50 border border-primary-200 rounded-lg"
              >
                <span className="text-sm font-medium text-primary-900">
                  {prefix}
                </span>
                <button
                  onClick={() => handleRemove(prefix)}
                  className="text-primary-600 hover:text-primary-800 transition-colors"
                  aria-label={`删除 ${prefix}`}
                >
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
