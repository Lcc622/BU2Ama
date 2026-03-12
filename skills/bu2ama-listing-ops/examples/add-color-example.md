# Add Color Example

## Request

用户：给 EP 店铺 `EE00466` 加色，颜色 `BD`，尺码 `04` 到 `26`，步长 `2`，导出 Excel。

## Command

```bash
python3 ~/.claude/skills/bu2ama-listing-ops/scripts/add_color_size.py \
  --store EP \
  --prefix EE00466 \
  --mode add-color \
  --colors BD \
  --start-size 04 \
  --end-size 26 \
  --size-step 2 \
  --json
```

## Expected Result Shape

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

## Response Pattern

- Confirm the selected store, prefixes, mode, and source files.
- Report `output_file`, `processed_count`, `total_skus`, and any warnings.
- For Telegram/OpenClaw export replies, end with:

```text
MEDIA:/abs/path/to/backend/results/processed_20260309_100503.xlsx
```

- If `success` is `false`, quote the first error and move to troubleshooting.
