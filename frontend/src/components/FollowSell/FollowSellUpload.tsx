import React, { useState } from 'react';
import { Upload, FileText, Download, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useFollowSellStore } from '@/store/useFollowSellStore';
import { followsellApi } from '@/services/followsellApi';

export const FollowSellUpload: React.FC = () => {
  const {
    uploadedFile,
    newProductCode,
    processing,
    result,
    error,
    setUploadedFile,
    setNewProductCode,
    setProcessing,
    setResult,
    setError,
    reset,
  } = useFollowSellStore();

  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (file: File) => {
    // 验证文件格式
    const validExtensions = ['.xlsx', '.xlsm', '.xls'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

    if (!validExtensions.includes(fileExtension)) {
      setError('不支持的文件格式，请上传 .xlsx、.xlsm 或 .xls 文件');
      return;
    }

    setUploadedFile(file);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileChange(e.target.files[0]);
    }
  };

  const handleProcess = async () => {
    if (!uploadedFile) {
      setError('请先上传老版本 Excel 文件');
      return;
    }

    if (!newProductCode || newProductCode.length < 7) {
      setError('请输入有效的产品代码（7-8位字符）');
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      const response = await followsellApi.process(uploadedFile, newProductCode);

      if (response.success) {
        setResult(response.data);
      } else {
        setError(response.message || '处理失败');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '处理失败，请重试');
    } finally {
      setProcessing(false);
    }
  };

  const handleDownload = async () => {
    if (!result) return;

    try {
      const blob = await followsellApi.download(result.outputFilename);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = result.outputFilename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError('下载失败，请重试');
    }
  };

  const handleReset = () => {
    reset();
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-6">跟卖上新</h2>

        {/* 文件上传区域 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            📤 上传老版本 Excel
          </label>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              id="file-upload"
              className="hidden"
              accept=".xlsx,.xlsm,.xls"
              onChange={handleFileInputChange}
              disabled={processing}
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer flex flex-col items-center"
            >
              <Upload className="w-12 h-12 text-gray-400 mb-3" />
              <p className="text-sm text-gray-600 mb-1">
                点击选择文件或拖拽文件到此处
              </p>
              <p className="text-xs text-gray-500">
                支持 .xlsx、.xlsm、.xls 格式
              </p>
            </label>
          </div>

          {uploadedFile && (
            <div className="mt-3 flex items-center text-sm text-gray-600">
              <FileText className="w-4 h-4 mr-2" />
              <span>{uploadedFile.name}</span>
              <span className="ml-2 text-gray-400">
                ({(uploadedFile.size / 1024 / 1024).toFixed(2)} MB)
              </span>
            </div>
          )}
        </div>

        {/* 产品代码输入 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            ✏️ 输入新产品代码
          </label>
          <input
            type="text"
            value={newProductCode}
            onChange={(e) => setNewProductCode(e.target.value.toUpperCase())}
            placeholder="例如: ES01846"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={processing}
            maxLength={8}
          />
          <p className="mt-1 text-xs text-gray-500">
            产品代码长度为 7-8 位字符
          </p>
        </div>

        {/* 提示信息 */}
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm font-medium text-blue-800 mb-2">ℹ️ 系统将自动：</p>
          <ul className="text-sm text-blue-700 space-y-1 ml-4">
            <li>• 识别老产品代码并替换</li>
            <li>• 价格 -0.1 美元</li>
            <li>• 更新日期（3PM 规则）</li>
            <li>• 清空图片字段</li>
            <li>• 保持 ASIN 不变（跟卖核心）</li>
          </ul>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
            <AlertCircle className="w-5 h-5 text-red-500 mr-3 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* 处理按钮 */}
        {!result && (
          <button
            onClick={handleProcess}
            disabled={processing || !uploadedFile || !newProductCode}
            className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
              processing || !uploadedFile || !newProductCode
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {processing ? '处理中...' : '生成跟卖表'}
          </button>
        )}

        {/* 处理结果 */}
        {result && (
          <div className="space-y-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start">
                <CheckCircle2 className="w-5 h-5 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-green-800 mb-2">
                    ✅ 处理完成！
                  </p>
                  <div className="text-sm text-green-700 space-y-1">
                    <p>• 处理了 {result.totalSkus} 个 SKU</p>
                    <p>• 老产品代码: {result.oldProductCode}</p>
                    <p>• 新产品代码: {result.newProductCode}</p>
                    <p>• 价格调整: {result.priceAdjustment} 美元</p>
                    <p>• 使用日期: {result.dateUsed}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleDownload}
                className="flex-1 py-3 px-4 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors flex items-center justify-center"
              >
                <Download className="w-5 h-5 mr-2" />
                下载新版本 Excel
              </button>
              <button
                onClick={handleReset}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
              >
                重新处理
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
