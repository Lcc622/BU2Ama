# Task Plan

## Goal
为 BU2Ama 跟卖导出链路新增输出校验模块，在单个 SKC 导出和批量导出完成后自动执行规则校验，并把结果附加到 API 响应的 `validation` 字段中；当规则存在 error 时可选触发 LLM 语义校验，但不阻断文件下载。

## Phases
- [in_progress] Inspect current follow-sell export flow, response schemas, and workbook header conventions
- [pending] Implement `app/core/output_validator.py` with rule validation and optional Anthropic-based semantic validation
- [pending] Wire validation into follow-sell single and batch export responses plus config/model updates
- [pending] Add focused tests for validator behavior and API integration, then run verification

## Notes
- Priority files: `backend/app/api/excel.py`, `backend/app/config.py`
- Validation target format:
  - `{'passed': bool, 'warnings': list, 'errors': list, 'summary': str}`
- Optional LLM validation only runs when rule validation has errors.
