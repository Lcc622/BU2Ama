# Troubleshooting

## Project Root Not Found

Symptom:
- `Unable to locate the BU2Ama project root`

Fix:
1. Run the command from the BU2Ama repo root.
2. Or export `BU2AMA_ROOT=/absolute/path/to/BU2Ama`.
3. Confirm `backend/app/config.py` exists under that root.

## Environment Validation Fails

Common failures:
- missing `backend/data/colorMapping.json`
- missing `backend/uploads/新老款映射信息(1).xlsx`
- missing Python dependencies such as `openpyxl`

Fix:
1. Run `python3 ~/.claude/skills/bu2ama-listing-ops/scripts/check_env.py --json`.
2. Read the `errors` array first, then the `warnings` array.
3. Restore missing mapping files before retrying any data task.

## Template File Not Found

Symptom:
- `Template file not found: ...`

Fix:
1. Upload or copy the template workbook into `backend/uploads/`.
2. Pass the uploaded filename to `--template`.
3. Do not assume an arbitrary absolute path will be used directly; the CLI only uses the basename.

## No Source Files Found

Symptom:
- `No source files found for store EP`

Fix:
1. Confirm the source files exist in `backend/uploads/`.
2. For DM, check both `DA-*` and `DM-*` naming.
3. If files were just uploaded, rerun with `upload_source.py --rebuild-index`.
4. If auto-discovery is still wrong, pass explicit `--sources`.

## Follow-Sell Mapping Missing or Stale

Symptom:
- empty follow-sell results
- warnings about `新老款映射信息(1).xlsx`

Fix:
1. Confirm `backend/uploads/新老款映射信息(1).xlsx` exists.
2. Replace it with the current mapping workbook if business data changed.
3. Re-run the query after the file is restored.

## SKC Format Errors

Symptom:
- `SKC 格式错误`

Fix:
1. Use exactly `7` style characters plus `2` uppercase color characters.
2. Example: `EE00756WH`
3. Do not include size or suffix when calling `follow_sell.py`.

## Index Problems

Symptoms:
- results are unexpectedly empty
- a legacy `ep_index.db` warning appears
- one store returns stale data after uploading files

Fix:
1. Rebuild indexes during upload:

   ```bash
   python3 ~/.claude/skills/bu2ama-listing-ops/scripts/upload_source.py \
     --file <new-file> \
     --store <EP|DM|PZ> \
     --rebuild-index \
     --json
   ```

2. If the source filename does not imply the store, pass `--store` explicitly.
