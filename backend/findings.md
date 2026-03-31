# Findings

- Follow-sell export responses are produced by `process_skc` and `process_skc_batch` in `backend/app/api/excel.py`.
- Current response models in `backend/app/models/excel.py` do not expose any `validation` field, so schema changes are required.
- Workbook header utilities already exist in `backend/tests/test_export_regressions.py`:
  - headers are read from rows `2` and `3`
  - data rows start at row `4`
- `excel_processor.py` already treats output fields such as `Colour Map`, `Release Date`, `Restock Date`, `Product Tax Code`, `Your Price`, and `Business Price` as first-class output columns, which aligns with the new validator requirements.
- Project currently depends on `openpyxl` but not `anthropic`, so optional LLM validation must handle missing SDK and missing `ANTHROPIC_API_KEY` gracefully.
