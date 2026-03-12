# Follow Sell Example

## Request

用户：查一下 `EE00756WH` 在 EP 店铺有哪些尺码。

## Command

```bash
python3 ~/.claude/skills/bu2ama-listing-ops/scripts/follow_sell.py \
  --skc EE00756WH \
  --store EP \
  --json
```

## Expected Result Shape

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
        "04",
        "06"
      ],
      "size_details": [
        {
          "size": "02",
          "suffix": "-USA",
          "sku": "EE00756WH02-USA"
        }
      ],
      "source_files": [
        "EP-0.xlsm",
        "EP-1.xlsm"
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

## Response Pattern

- Use `size_details` by default so the reply matches the web UI columns.
- Report the matched old style.
- List sizes in ascending order.
- Mention source files when useful for debugging.
- If no record is found, return the `not_found` list and recommend checking mapping or indexes.

## Export Variant

```bash
python3 ~/.claude/skills/bu2ama-listing-ops/scripts/follow_sell.py \
  --skc EE00756WH \
  --store EP \
  --export-excel \
  --json
```

The JSON then includes:

```json
{
  "export": {
    "output_file": "/abs/path/to/backend/results/followsell_EE00756WH_20260309_120000.xlsx",
    "total_skus": 12,
    "success_skcs": 1,
    "failed_skcs": 0
  }
}
```

In Telegram/OpenClaw, the reply should end with:

```text
MEDIA:/abs/path/to/backend/results/followsell_EE00756WH_20260309_120000.xlsx
```
