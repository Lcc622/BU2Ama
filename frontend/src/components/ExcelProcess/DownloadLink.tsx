/**
 * 下载链接组件
 */
import { useProcessStore } from '../../store/useProcessStore';
import { excelApi } from '../../services/excelApi';

export function DownloadLink() {
  const outputFilename = useProcessStore((state) => state.outputFilename);

  if (!outputFilename) {
    return null;
  }

  const downloadUrl = excelApi.getDownloadUrl(outputFilename);

  return (
    <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="font-semibold text-green-900">✓ 处理完成</h4>
          <p className="text-sm text-green-700 mt-1">
            文件名：{outputFilename}
          </p>
        </div>
        <a
          href={downloadUrl}
          download
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          下载文件
        </a>
      </div>
    </div>
  );
}
