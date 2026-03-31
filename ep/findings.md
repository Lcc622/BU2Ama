# Findings

- `config.py` still derives template/store availability from `STORE_GROUP`; this needs to collapse to EPUS-only constants.
- `excel_processor.py` contains several DM/PZ-only branches around suffix families, quantity handling, date/tax columns, variation theme forcing, and embellishment field handling.
- `api/excel.py` still exposes store-group-aware labels and broader file filtering/error text.
- Frontend store/template types still include `DaMaUS` and `PZUS`.
- Backend now compiles after the EP-only cleanup.
- Frontend verification is limited in this environment because `npm run build` fails at `tsc -b` with `sh: tsc: command not found`.
