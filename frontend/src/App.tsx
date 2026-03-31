import { QueryClientProvider, useQuery } from '@tanstack/react-query';
import { queryClient } from './lib/queryClient';
import { mappingApi } from './services/mappingApi';
import { FileUploader } from './components/ExcelUpload/FileUploader';
import { TemplateSelector } from './components/ExcelProcess/TemplateSelector';
import { ColorSelector } from './components/ExcelProcess/ColorSelector';
import { PrefixInput } from './components/ExcelProcess/PrefixInput';
import { ProcessButton } from './components/ExcelProcess/ProcessButton';
import { DownloadLink } from './components/ExcelProcess/DownloadLink';
import { AddMappingModal } from './components/ColorMapping/AddMappingModal';
import { FollowSellUpload } from './components/FollowSell/FollowSellUpload';
import { ExportHistory } from './components/ExportHistory';
import { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import fallbackColorMappings from './data/colorMapping';

function ColorMappingList() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data: mappings, isLoading, error } = useQuery({
    queryKey: ['mappings'],
    queryFn: mappingApi.getAll,
    initialData: fallbackColorMappings,
  });

  if (isLoading) {
    return (
      <div className="space-y-3">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-slate-200 rounded w-3/4"></div>
          <div className="h-4 bg-slate-200 rounded w-1/2"></div>
          <div className="h-4 bg-slate-200 rounded w-5/6"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 border border-red-200 p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">加载失败</h3>
            <p className="text-sm text-red-700 mt-1">{error.message}</p>
          </div>
        </div>
      </div>
    );
  }

  const mappingEntries = Object.entries(mappings || {});

  return (
    <>
      <div className="space-y-4">
        {/* Stats Bar */}
        <div className="flex items-center justify-between px-1">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
              {mappingEntries.length} 个映射
            </span>
          </div>
          <button
            onClick={() => setIsModalOpen(true)}
            className="text-sm text-primary-600 hover:text-primary-700 font-medium transition-colors duration-200 flex items-center gap-1"
            aria-label="打开添加颜色映射对话框"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            添加映射
          </button>
        </div>

        {/* Table */}
        <div className="overflow-x-auto border border-slate-200 rounded-lg">
          <div className="max-h-96 overflow-y-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50 sticky top-0">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                    颜色代码
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                    颜色名称
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-100">
                {mappingEntries.map(([code, name]) => (
                  <tr key={code} className="hover:bg-slate-50 transition-colors duration-150">
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="font-mono text-sm font-semibold text-primary-900">
                        {code}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-slate-700">
                      {name}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <AddMappingModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </>
  );
}

function ExcelProcessPanel() {
  return (
    <div className="space-y-6">
      <FileUploader />

      <div className="border-t pt-6 space-y-4">
        <TemplateSelector />
        <PrefixInput />
        <ColorSelector />
      </div>

      <ProcessButton />
      <DownloadLink />
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState<'excel' | 'mapping' | 'followsell' | 'history'>('excel');

  return (
    <QueryClientProvider client={queryClient}>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#fff',
            color: '#334155',
            border: '1px solid #E2E8F0',
            borderRadius: '0.5rem',
            fontSize: '0.875rem',
          },
          success: {
            iconTheme: {
              primary: '#10B981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#EF4444',
              secondary: '#fff',
            },
          },
        }}
      />
      <div className="min-h-screen bg-slate-50">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-primary-900">
                  Excel 颜色加色系统
                  {import.meta.env.VITE_STORE_GROUP === 'EP' && (
                    <span className="ml-2 text-base font-semibold text-blue-600">· EP 店铺</span>
                  )}
                  {import.meta.env.VITE_STORE_GROUP === 'DM_PZ' && (
                    <span className="ml-2 text-base font-semibold text-orange-600">· DM/PZ 店铺</span>
                  )}
                </h1>
                <p className="text-sm text-slate-600 mt-0.5">
                  SKU 颜色映射和处理系统 v2.0
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  系统运行中
                </span>
              </div>
            </div>
          </div>
        </header>

        {/* Tabs */}
        <div className="bg-white border-b border-slate-200">
          <div className="max-w-7xl mx-auto px-6">
            <nav className="flex space-x-8" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('excel')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'excel'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
              >
                Excel 处理
              </button>
              <button
                onClick={() => setActiveTab('mapping')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'mapping'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
              >
                颜色映射
              </button>
              <button
                onClick={() => setActiveTab('followsell')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'followsell'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
              >
                跟卖上新
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'history'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
              >
                历史记录
              </button>
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-6 py-6">
          {activeTab === 'excel' && (
            <div className="bg-white rounded-lg border border-slate-200 shadow-sm">
              <div className="border-b border-slate-200 px-6 py-4">
                <h2 className="text-xl font-semibold text-primary-900">Excel 处理</h2>
                <p className="text-xs text-slate-500 mt-1">上传、分析和处理 Excel 文件</p>
              </div>
              <div className="p-6">
                <ExcelProcessPanel />
              </div>
            </div>
          )}

          {activeTab === 'mapping' && (
            <div className="bg-white rounded-lg border border-slate-200 shadow-sm">
              <div className="border-b border-slate-200 px-6 py-4">
                <h2 className="text-xl font-semibold text-primary-900">颜色映射管理</h2>
                <p className="text-xs text-slate-500 mt-1">管理 SKU 颜色代码映射</p>
              </div>
              <div className="p-6">
                <ColorMappingList />
              </div>
            </div>
          )}

          {activeTab === 'followsell' && (
            <FollowSellUpload />
          )}

          {activeTab === 'history' && (
            <div className="bg-white rounded-lg border border-slate-200 shadow-sm">
              <div className="border-b border-slate-200 px-6 py-4">
                <h2 className="text-xl font-semibold text-primary-900">导出历史记录</h2>
                <p className="text-xs text-slate-500 mt-1">查看所有模块的导出历史（跟卖、加色、加码）</p>
              </div>
              <div className="p-6">
                <ExportHistory title="" defaultModule="all" />
              </div>
            </div>
          )}
        </main>
      </div>
    </QueryClientProvider>
  );
}

export default App;
