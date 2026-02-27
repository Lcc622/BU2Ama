/**
 * 模板选择组件
 */
import { useQuery } from '@tanstack/react-query';
import { excelApi } from '../../services/excelApi';
import { useProcessStore } from '../../store/useProcessStore';

export function TemplateSelector() {
  const templateType = useProcessStore((state) => state.templateType);
  const setTemplateType = useProcessStore((state) => state.setTemplateType);

  const { data: templates, isLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: excelApi.getTemplates,
  });

  if (isLoading) {
    return <div className="text-sm text-gray-600">加载模板...</div>;
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        选择模板类型
      </label>
      <div className="flex gap-4">
        {templates?.map((template) => (
          <label
            key={template.name}
            className={`
              flex items-center space-x-2 px-4 py-2 border rounded-lg cursor-pointer transition-colors
              ${
                templateType === template.name
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-300 hover:border-gray-400'
              }
              ${!template.exists ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <input
              type="radio"
              name="template"
              value={template.name}
              checked={templateType === template.name}
              onChange={(e) => setTemplateType(e.target.value)}
              disabled={!template.exists}
              className="text-blue-600 focus:ring-blue-500"
            />
            <div>
              <div className="font-medium">{template.name}</div>
              <div className="text-xs text-gray-500">{template.file}</div>
              {!template.exists && (
                <div className="text-xs text-red-600">模板文件不存在</div>
              )}
            </div>
          </label>
        ))}
      </div>
    </div>
  );
}
