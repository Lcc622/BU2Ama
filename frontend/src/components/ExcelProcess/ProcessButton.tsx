/**
 * Excel 处理按钮组件
 */
import { useMutation } from '@tanstack/react-query';
import { excelApi } from '../../services/excelApi';
import { useUploadStore } from '../../store/useUploadStore';
import { useProcessStore } from '../../store/useProcessStore';
import toast from 'react-hot-toast';

export function ProcessButton() {
  const uploadedFiles = useUploadStore((state) => state.uploadedFiles);
  const analysisResult = useUploadStore((state) => state.analysisResult);
  const selectedPrefixes = useUploadStore((state) => state.selectedPrefixes);
  const templateType = useProcessStore((state) => state.templateType);
  const targetColor = useProcessStore((state) => state.targetColor);
  const targetSize = useProcessStore((state) => state.targetSize);
  const setOutputFilename = useProcessStore((state) => state.setOutputFilename);
  const setIsProcessing = useProcessStore((state) => state.setIsProcessing);

  const processMutation = useMutation({
    mutationFn: excelApi.processExcel,
    onSuccess: (data) => {
      setOutputFilename(data.output_filename || null);
      setIsProcessing(false);
      toast.success(`处理完成！共处理 ${data.processed_count} 条数据`);
    },
    onError: (error: Error) => {
      setIsProcessing(false);
      toast.error(`处理失败: ${error.message}`);
    },
  });

  const handleProcess = async () => {
    if (uploadedFiles.length === 0) {
      toast.error('请先上传 Excel 文件');
      return;
    }

    if (!analysisResult) {
      toast.error('请先分析 Excel 文件');
      return;
    }

    if (selectedPrefixes.length === 0) {
      toast.error('请至少选择一个产品前缀');
      return;
    }

    if (analysisResult.unknown_colors.length > 0) {
      // 使用 toast 替代 confirm
      const confirmed = await new Promise<boolean>((resolve) => {
        toast((t) => (
          <div className="flex flex-col gap-3">
            <p className="text-sm font-medium text-slate-900">
              检测到 {analysisResult.unknown_colors.length} 个未知颜色代码
            </p>
            <p className="text-xs text-slate-600">
              未知颜色的 SKU 将被跳过，是否继续处理？
            </p>
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => {
                  toast.dismiss(t.id);
                  resolve(false);
                }}
                className="px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded hover:bg-slate-50 transition-colors"
              >
                取消
              </button>
              <button
                onClick={() => {
                  toast.dismiss(t.id);
                  resolve(true);
                }}
                className="px-3 py-1.5 text-xs font-medium text-white bg-primary-600 rounded hover:bg-primary-700 transition-colors"
              >
                继续处理
              </button>
            </div>
          </div>
        ), {
          duration: Infinity,
          style: { maxWidth: '400px' },
        });
      });

      if (!confirmed) return;
    }

    setIsProcessing(true);
    processMutation.mutate({
      template_type: templateType,
      filenames: uploadedFiles, // 使用所有上传的文件
      selected_prefixes: selectedPrefixes,
      target_color: targetColor,
      target_size: targetSize,
    });
  };

  const isDisabled =
    uploadedFiles.length === 0 ||
    !analysisResult ||
    selectedPrefixes.length === 0 ||
    processMutation.isPending;

  return (
    <button
      onClick={handleProcess}
      disabled={isDisabled}
      className={`
        w-full px-6 py-3 rounded-lg font-semibold text-sm transition-all duration-200
        focus:outline-none focus:ring-2 focus:ring-offset-2
        ${
          isDisabled
            ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
            : 'bg-accent text-white hover:bg-accent-600 focus:ring-accent-500 shadow-sm hover:shadow-md'
        }
      `}
    >
      {processMutation.isPending ? (
        <span className="flex items-center justify-center space-x-2">
          <svg
            className="animate-spin h-5 w-5 motion-reduce:animate-none"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <span>处理中…</span>
        </span>
      ) : (
        <span className="flex items-center justify-center gap-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>
            生成 Excel 文件
            {uploadedFiles.length > 1 && ` (${uploadedFiles.length} 个文件)`}
          </span>
        </span>
      )}
    </button>
  );
}
