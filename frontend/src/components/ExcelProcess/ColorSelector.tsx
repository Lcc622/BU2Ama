import { useQuery } from '@tanstack/react-query';
import { mappingApi } from '../../services/mappingApi';
import { useProcessStore } from '../../store/useProcessStore';
import fallbackColorMappings from '../../data/colorMapping';

export function ColorSelector() {
  const {
    mode,
    setMode,
    startSize,
    setStartSize,
    endSize,
    setEndSize,
    sizeStep,
    setSizeStep,
    colorList,
    setColorList,
    generateSKUs,
  } = useProcessStore();

  const { data: mappings } = useQuery({
    queryKey: ['mappings'],
    queryFn: mappingApi.getAll,
    initialData: fallbackColorMappings,
  });

  // 获取所有颜色代码用于 datalist
  const colorCodes = mappings ? Object.keys(mappings).sort() : [];

  // 生成尺码选项（02, 04, 06...30）
  const sizeOptions = Array.from({ length: 15 }, (_, i) => {
    const size = ((i + 1) * 2).toString().padStart(2, '0');
    return size;
  });

  // 实时生成 SKU 预览
  const previewSKUs = generateSKUs();

  return (
    <div className="space-y-6">
      {/* 模式选择 */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">
          处理模式 <span className="text-red-500">*</span>
        </label>
        <div className="flex gap-4">
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              name="mode"
              value="add-color"
              checked={mode === 'add-color'}
              onChange={() => setMode('add-color')}
              className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">
              加色（一码多色）
            </span>
          </label>
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              name="mode"
              value="add-code"
              checked={mode === 'add-code'}
              onChange={() => setMode('add-code')}
              className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">
              加码（一色多码）
            </span>
          </label>
        </div>
      </div>

      {/* 加码模式 */}
      {mode === 'add-code' && (
        <div className="space-y-4 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm text-gray-700 font-medium">
            加码模式：选择一个颜色，生成多个尺码的 SKU
          </p>

          {/* 颜色选择 */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">
              颜色代码 <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              <input
                type="text"
                value={colorList}
                onChange={(e) => setColorList(e.target.value.toUpperCase())}
                placeholder="手动输入颜色代码（例如: LV）"
                maxLength={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <select
                value={colorCodes.includes(colorList) ? colorList : ''}
                onChange={(e) => setColorList(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">从下拉选择颜色代码</option>
                {colorCodes.map((code) => (
                  <option key={code} value={code}>
                    {code} - {mappings?.[code]}
                  </option>
                ))}
              </select>
            </div>
            {colorList && mappings?.[colorList] && (
              <p className="text-xs text-green-600">
                {colorList} - {mappings[colorList]}
              </p>
            )}
          </div>

          {/* 尺码范围 */}
          <div className="grid grid-cols-3 gap-3">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                起始尺码 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                list="size-list-start"
                value={startSize}
                onChange={(e) => setStartSize(e.target.value)}
                placeholder="02"
                maxLength={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <datalist id="size-list-start">
                {sizeOptions.map((size) => (
                  <option key={size} value={size} />
                ))}
              </datalist>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                结束尺码 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                list="size-list-end"
                value={endSize}
                onChange={(e) => setEndSize(e.target.value)}
                placeholder="30"
                maxLength={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <datalist id="size-list-end">
                {sizeOptions.map((size) => (
                  <option key={size} value={size} />
                ))}
              </datalist>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                尺码步长 <span className="text-red-500">*</span>
              </label>
              <select
                value={sizeStep}
                onChange={(e) => setSizeStep(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={1}>1</option>
                <option value={2}>2</option>
                <option value={4}>4</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* 加色模式 */}
      {mode === 'add-color' && (
        <div className="space-y-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <p className="text-sm text-gray-700 font-medium">
            加色模式：选择一个尺码，生成多个颜色的 SKU
          </p>

          {/* 尺码选择 */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">
              尺码 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              list="size-list-single"
              value={startSize}
              onChange={(e) => setStartSize(e.target.value)}
              placeholder="输入或选择尺码（例如: 14）"
              maxLength={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <datalist id="size-list-single">
              {sizeOptions.map((size) => (
                <option key={size} value={size} />
              ))}
            </datalist>
          </div>

          {/* 颜色列表 */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">
              颜色列表 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={colorList}
              onChange={(e) => setColorList(e.target.value.toUpperCase())}
              placeholder="输入多个颜色代码，用逗号分隔（例如: LV,BK,WH）"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500">
              支持逗号、中文逗号或空格分隔
            </p>
            {colorList && (
              <div className="flex flex-wrap gap-2 mt-2">
                {colorList
                  .split(/[,，、;；\s]+/)
                  .map((c) => c.trim().toUpperCase())
                  .filter((c) => c.length === 2)
                  .map((code) => (
                    <span
                      key={code}
                      className={`px-2 py-1 text-xs rounded ${
                        mappings?.[code]
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {code}
                      {mappings?.[code] && ` - ${mappings[code]}`}
                    </span>
                  ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* SKU 预览 */}
      {previewSKUs.length > 0 && (
        <div className="space-y-2 p-4 bg-gray-50 border border-gray-200 rounded-md">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700">
              SKU 预览
            </label>
            <span className="text-xs text-gray-500">
              共 {previewSKUs.length} 个 SKU
            </span>
          </div>
          <div className="max-h-40 overflow-y-auto">
            <div className="flex flex-wrap gap-2">
              {previewSKUs.map((sku) => (
                <span
                  key={sku}
                  className="px-2 py-1 text-xs bg-white border border-gray-300 rounded font-mono"
                >
                  {sku}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
