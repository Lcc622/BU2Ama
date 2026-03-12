# File Contracts

## Repo Layout

The skill assumes a BU2Ama repo containing:

- `backend/app/cli/`
- `backend/uploads/`
- `backend/results/`
- `backend/data/colorMapping.json`
- `backend/uploads/新老款映射信息(1).xlsx`

## Input Contracts

### `check_env.py`

- No positional inputs.
- Run from the BU2Ama repo root, or set `BU2AMA_ROOT`.

### `add_color_size.py`

- Web-style mode:
  - `--prefix`:
    - may be repeated
    - comma-splitting is supported
    - accepts product prefixes such as `EE00466`
  - `--mode`:
    - `add-color` or `add-code`
  - `--colors`:
    - may be repeated
    - comma-splitting is supported
    - values should be two-letter color codes such as `BD`
  - `--start-size` / `--end-size` / `--size-step`:
    - used for range generation in `add-color`
  - `--sizes`:
    - optional explicit size list
    - may be repeated
    - comma-splitting is supported
- Legacy mode:
  - `--template`:
  - accepts a filename or path
  - only the basename is used by the CLI
  - the file must already exist in `backend/uploads/`
- `--store`: `EP`, `DM`, or `PZ`
- `--sources`:
  - optional
  - each item is resolved by basename inside `backend/uploads/`
- `--price-report`:
  - optional
  - basename must exist in `backend/uploads/`

### `follow_sell.py`

- `--skc`:
  - may be repeated
  - values are uppercased and comma-splitting is supported
  - format must be `^[A-Z0-9]{7}[A-Z]{2}$`
- `--export-excel`:
  - optional
  - exports the follow-sell result into a workbook under `backend/results/`
- `--skc-file`:
  - local UTF-8 text file
  - one SKC per non-empty line
- `--output`:
  - optional JSON file path
  - parent directories are created automatically

### `upload_source.py`

- `--file`:
  - local file path
  - copied into `backend/uploads/`
- `--store`:
  - optional if filename implies store, for example `EP-3.xlsm`
- `--rebuild-index`:
  - rebuilds both Excel and follow-sell indexes for the resolved store

## Output Contracts

### `check_env.py`

JSON shape:

```json
{
  "valid": true,
  "project_root": "/abs/path/to/BU2Ama",
  "python_version": "3.x.x",
  "dependencies": {
    "openpyxl": "installed"
  },
  "files": {
    "backend/data/colorMapping.json": "exists"
  },
  "indexes": {
    "EP": {
      "excel_index": "exists",
      "ep_index": "exists"
    }
  },
  "warnings": [],
  "errors": []
}
```

### `add_color_size.py`

JSON shape:

```json
{
  "success": true,
  "mode": "add-color",
  "template_type": "EPUS",
  "selected_prefixes": [
    "EE00466"
  ],
  "source_files": [
    "EP-0.xlsm",
    "EP-1.xlsm",
    "EP-2.xlsm",
    "EP-All+Listings+Report.txt"
  ],
  "output_file": "/abs/path/to/backend/results/processed_20260309_100503.xlsx",
  "processed_count": 12,
  "skipped_count": 0,
  "total_skus": 12,
  "generated_skus_preview": [
    "EE00466BD04"
  ],
  "errors": [],
  "warnings": []
}
```

### `follow_sell.py`

JSON shape:

```json
{
  "success": true,
  "results": [
    {
      "skc": "EE00756WH",
      "new_style": "EE00756",
      "old_style": "EP00751",
      "color_code": "WH",
      "sizes": [
        "02",
        "04"
      ],
      "size_details": [
        {
          "size": "02",
          "suffix": "-USA",
          "sku": "EE00756WH02-USA"
        }
      ],
      "source_files": [
        "EP-0.xlsm"
      ],
      "total_sizes": 12,
      "message": "找到 12 个尺码"
    }
  ],
  "not_found": [],
  "errors": [],
  "export": null
}
```

Notes:
- `success` becomes `false` if any lookup produces an error.
- `not_found` may still be populated together with `errors`.
- `size_details` is the field to use when rendering the same columns as the web UI.
- With `--export-excel`, `export.output_file` points to the generated workbook in `backend/results/`.

### `upload_source.py`

JSON shape:

```json
{
  "success": true,
  "file_saved": "/abs/path/to/backend/uploads/EP-3.xlsm",
  "store": "EP",
  "index_rebuilt": true,
  "sku_count": 20324,
  "errors": []
}
```

## Exit Codes

- `0`: success
- `1`: validation or processing failure
