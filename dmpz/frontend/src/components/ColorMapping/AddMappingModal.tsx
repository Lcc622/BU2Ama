/**
 * 添加颜色映射模态框
 */
import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { mappingApi } from '../../services/mappingApi';
import toast from 'react-hot-toast';

interface AddMappingModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AddMappingModal({ isOpen, onClose }: AddMappingModalProps) {
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const queryClient = useQueryClient();

  const addMutation = useMutation({
    mutationFn: () => mappingApi.addMapping(code.toUpperCase(), name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mappings'] });
      toast.success('颜色映射添加成功！');
      setCode('');
      setName('');
      onClose();
    },
    onError: (error: Error) => {
      toast.error(`添加失败: ${error.message}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!code.trim() || !name.trim()) {
      toast.error('请填写颜色代码和名称');
      return;
    }

    if (code.length !== 2) {
      toast.error('颜色代码必须是2个字符');
      return;
    }

    addMutation.mutate();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overscroll-contain">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-lg w-full max-w-md mx-4 z-10 overscroll-contain">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h3 className="text-lg font-semibold text-primary-900">添加颜色映射</h3>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 rounded transition-colors duration-150"
            aria-label="关闭"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label htmlFor="code" className="block text-sm font-medium text-slate-700 mb-1">
              颜色代码 <span className="text-red-500">*</span>
            </label>
            <input
              id="code"
              name="colorCode"
              type="text"
              autoComplete="off"
              value={code}
              onChange={(e) => setCode(e.target.value.toUpperCase())}
              maxLength={2}
              placeholder="LV, BK…"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm font-mono uppercase"
              disabled={addMutation.isPending}
            />
            <p className="text-xs text-slate-500 mt-1">必须是2个大写字母</p>
          </div>

          <div>
            <label htmlFor="name" className="block text-sm font-medium text-slate-700 mb-1">
              颜色名称 <span className="text-red-500">*</span>
            </label>
            <input
              id="name"
              name="colorName"
              type="text"
              autoComplete="off"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Lavender, Black…"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              disabled={addMutation.isPending}
            />
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors duration-200"
              disabled={addMutation.isPending}
            >
              取消
            </button>
            <button
              type="submit"
              disabled={addMutation.isPending}
              className="px-4 py-2 text-sm font-semibold text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {addMutation.isPending ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4 motion-reduce:animate-none" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  添加中…
                </span>
              ) : (
                '添加'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
