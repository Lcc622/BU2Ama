/**
 * Excel 处理按钮组件
 */
import { useMutation } from '@tanstack/react-query';
import { excelApi } from '../../services/excelApi';
import { useUploadStore } from '../../store/useUploadStore';
import { useProcessStore } from '../../store/useProcessStore';
import toast from 'react-hot-toast';

const buildGeneratedSkus = (
  prefixes: string[],
  mode: 'add-color' | 'add-code',
  startSize: string,
  endSize: string,
  sizeStep: number,
  colorList: string
): string[] => {
  const normalizedPrefixes = prefixes
    .map((p) => p.trim().toUpperCase())
    .filter((p) => p.length > 0);

  if (normalizedPrefixes.length === 0) return [];

  const colors = colorList
    .split(/[,，、;；\s]+/)
    .map((c) => c.trim().toUpperCase())
    .filter((c) => c.length === 2);

  if (colors.length === 0) return [];

  if (mode === 'add-color') {
    const size = parseInt(startSize, 10);
    if (Number.isNaN(size)) return [];
    const sizeStr = size.toString().padStart(2, '0');

    return normalizedPrefixes.flatMap((prefix) =>
      colors.map((color) => `${prefix}${color}${sizeStr}`)
    );
  }

  const start = parseInt(startSize, 10);
  const end = parseInt(endSize, 10);
  if (Number.isNaN(start) || Number.isNaN(end) || start > end || sizeStep <= 0) return [];

  const skus: string[] = [];
  for (const prefix of normalizedPrefixes) {
    const color = colors[0];
    for (let size = start; size <= end; size += sizeStep) {
      skus.push(`${prefix}${color}${size.toString().padStart(2, '0')}`);
    }
  }
  return skus;
};

export function ProcessButton() {
  const uploadedFiles = useUploadStore((state) => state.uploadedFiles);
  const selectedPrefixes = useUploadStore((state) => state.selectedPrefixes);
  const templateType = useProcessStore((state) => state.templateType);
  const targetColor = useProcessStore((state) => state.targetColor);
  const targetSize = useProcessStore((state) => state.targetSize);
  const mode = useProcessStore((state) => state.mode);
  const startSize = useProcessStore((state) => state.startSize);
  const endSize = useProcessStore((state) => state.endSize);
  const sizeStep = useProcessStore((state) => state.sizeStep);
  const colorList = useProcessStore((state) => state.colorList);
  const setOutputFilename = useProcessStore((state) => state.setOutputFilename);
  const setIsProcessing = useProcessStore((state) => state.setIsProcessing);
  const processMutation = useMutation({
    mutationFn: async (request: Parameters<typeof excelApi.processExcel>[0]) => {
      const start = await excelApi.processExcelAsync(request);
      const jobId = start.job_id;

      const pollIntervalMs = 2500;
      const timeoutMs = 1000 * 60 * 10;
      const begin = Date.now();

      while (Date.now() - begin < timeoutMs) {
        const status = await excelApi.getProcessStatus(jobId);
        if (status.status === 'completed') {
          return {
            success: true,
            output_filename: status.output_filename,
            message: status.message || '处理完成',
            processed_count: status.processed_count,
          };
        }
        if (status.status === 'failed') {
          throw new Error(status.error || status.message || '处理失败');
        }
        await new Promise((resolve) => setTimeout(resolve, pollIntervalMs));
      }

      throw new Error('处理超时，请稍后重试');
    },
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
    if (selectedPrefixes.length === 0) {
      toast.error('请至少添加一个产品前缀');
      return;
    }

    setIsProcessing(true);

    // 过滤掉模板文件，只传递数据文件
    const fallbackFiles = [
      'EP-2.xlsm',
      'EP-1.xlsm',
      'EP-0.xlsm',
      'All+Listings+Report.txt',
    ];
    const sourceFiles = uploadedFiles.length > 0 ? uploadedFiles : fallbackFiles;

    const dataFiles = sourceFiles.filter(filename => {
      const lower = filename.toLowerCase();
      return !(lower.includes('模板') || lower.includes('模版') || lower.includes('template'));
    });
    const generatedSkus = buildGeneratedSkus(
      selectedPrefixes,
      mode,
      startSize,
      endSize,
      sizeStep,
      colorList
    );
    if (generatedSkus.length === 0) {
      setIsProcessing(false);
      toast.error('请先填写颜色和尺码条件，生成目标 SKU');
      return;
    }

    processMutation.mutate({
      template_type: templateType,
      filenames: dataFiles, // 只使用数据文件
      selected_prefixes: selectedPrefixes,
      mode,
      generated_skus: generatedSkus,
      target_color: targetColor,
      target_size: targetSize,
    });
  };

  const isDisabled =
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
            {(() => {
              const dataFiles = uploadedFiles.filter(filename => {
                const lower = filename.toLowerCase();
                return !(lower.includes('模板') || lower.includes('模版') || lower.includes('template'));
              });
              if (uploadedFiles.length === 0) {
                return ' (固定数据文件)';
              }
              return dataFiles.length > 1 ? ` (${dataFiles.length} 个数据文件)` : '';
            })()}
          </span>
        </span>
      )}
    </button>
  );
}
