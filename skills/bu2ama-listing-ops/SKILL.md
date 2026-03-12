---
name: bu2ama-listing-ops
description: "Run BU2Ama listing operations from the BU2Ama repo: add-color/add-size exports, follow-sell SKC lookup, source-file upload, and EP/DM/PZ store index rebuild. Use when the user asks for 加色加码, 查 SKC 尺码, 跟卖, 上传源文件, 更新店铺数据, or 重建索引. 【重要】本 skill 仅用于 BU2Ama listing 操作，不用于 FBA 货件同步、FBA 库存同步、SP-API 数据入库等操作（那些用 fba-ingest skill）。"
---

# BU2Ama Listing Ops

Use this skill only for the BU2Ama project.

Default install path: `~/.claude/skills/bu2ama-listing-ops`

## Quick Start

1. Run environment validation first:

   ```bash
   python3 ~/.claude/skills/bu2ama-listing-ops/scripts/check_env.py --json
   ```

2. If validation fails, read `references/troubleshooting.md` before doing anything else.
3. Normalize any `DA` store request to `DM`.
4. Prefer `--json` on every command so results are machine-readable.

If the repo root cannot be found automatically, run commands with `BU2AMA_ROOT=/absolute/path/to/BU2Ama`.

## Task Routing

### Add Color / Add Size

Use when the user wants to generate an output workbook for 加色 or 加码.

Collect:
- store: `EP`, `DM`, or `PZ`
- one or more product prefixes, for example `EE00466`
- processing mode: `add-color` or `add-code`
- color codes, for example `BD`, `WH`, `BK`
- size range or size list
- optional source filenames

Default behavior:
- Prefer the web-style flow by default: collect `prefix + mode + colors + sizes`, let the CLI generate concrete `generated_skus`, then export the workbook.
- Do not ask the user for a template filename unless they explicitly want the legacy template-driven flow.
- For Telegram/OpenClaw, run silently by default. The wrapper will stage exported Excel files into an OpenClaw-approved media directory automatically, then reply with the final short summary plus a standalone `MEDIA:<absolute-path>` line so the Excel file is sent back as an attachment.

Web-style command:

```bash
python3 ~/.claude/skills/bu2ama-listing-ops/scripts/add_color_size.py \
  --store <EP|DM|PZ> \
  --prefix <PREFIX1> \
  [--prefix <PREFIX2>] \
  --mode <add-color|add-code> \
  --colors <BD,WH,...> \
  [--start-size <04> --end-size <26> --size-step <2>] \
  [--sizes <04,06,08>] \
  [--sources <source1> <source2> ...] \
  --json
```

Legacy template-driven command:

```bash
python3 ~/.claude/skills/bu2ama-listing-ops/scripts/add_color_size.py \
  --template <template-file> \
  --store <EP|DM|PZ> \
  [--sources <source1> <source2> ...] \
  [--price-report <report-file>] \
  --json
```

Read `references/file-contracts.md` if the user is unsure where template/source files must live, or how `prefix + mode` maps to generated SKUs.

### Follow Sell

Use when the user wants size coverage for one or more SKCs.

Default behavior:
- For a plain query request, return the web-style table by default using `size_details` rows with `size`, `suffix`, and generated `sku`.
- Do not ask the user whether they want the compact list or the table unless they explicitly request a shorter answer.
- For an export request, generate the workbook silently and then reply directly with the final short summary plus a standalone `MEDIA:<absolute-path>` line so OpenClaw sends the staged Excel file back to Telegram as an attachment.

Collect:
- store: `EP`, `DM`, or `PZ`
- one or more SKCs in `7位款号 + 2位颜色` format, for example `EE00756WH`
- whether the user wants query only or Excel export

Run one or more `--skc` flags:

```bash
python3 ~/.claude/skills/bu2ama-listing-ops/scripts/follow_sell.py \
  --skc <SKC1> \
  --skc <SKC2> \
  --store <EP|DM|PZ> \
  --json
```

To generate the same follow-sell export workbook that the web flow uses:

```bash
python3 ~/.claude/skills/bu2ama-listing-ops/scripts/follow_sell.py \
  --skc <SKC1> \
  --store <EP|DM|PZ> \
  --export-excel \
  --json
```

Or read from a text file:

```bash
python3 ~/.claude/skills/bu2ama-listing-ops/scripts/follow_sell.py \
  --skc-file <path/to/skc.txt> \
  --store <EP|DM|PZ> \
  --json
```

Read `references/store-rules.md` for suffix and store normalization rules.

### Upload Source File

Use when the user uploads a new store workbook or asks to refresh store data.

Collect:
- local file path
- store only if filename does not clearly imply it
- whether indexes should be rebuilt immediately

Run:

```bash
python3 ~/.claude/skills/bu2ama-listing-ops/scripts/upload_source.py \
  --file <local-file> \
  [--store <EP|DM|PZ>] \
  [--rebuild-index] \
  --json
```

If indexes are stale or missing, rebuild during upload.

## Result Handling

- `check_env.py` returns `valid`, `files`, `indexes`, `warnings`, and `errors`.
- `add_color_size.py` returns `output_file`, `processed_count`, and `skipped_count`.
  In web-style mode it also returns `mode`, `template_type`, `selected_prefixes`, `source_files`, `total_skus`, and `generated_skus_preview`.
- `follow_sell.py` returns `results`, `not_found`, and `errors`.
  Each successful result includes `new_style`, `old_style`, `color_code`, `sizes`, `size_details`, and `source_files`.
  When `--export-excel` is used it also returns an `export` object with `output_file` and `total_skus`.
- `upload_source.py` returns `file_saved`, `store`, `index_rebuilt`, and `sku_count`.

Treat any non-zero exit code as failure, even if partial JSON output exists.

For Telegram/OpenClaw replies:
- Query replies should present a compact table-like block from `size_details`.
- Export replies should include the staged file path as `MEDIA:<absolute-path>` on its own line after the summary text.
- Do not send intermediate progress messages such as `正在检查环境...` or `正在生成结果文件...` for normal BU2Ama runs.
- Only send an intermediate message if the run fails, needs user input, or is clearly taking unusually long.

## References

- Read `references/store-rules.md` for store/template/source/suffix rules.
- Read `references/file-contracts.md` for input and output file expectations.
- Read `references/troubleshooting.md` for path, index, SKC, and mapping failures.
- Read `references/telegram-integration.md` only when the task runs through OpenClaw or Telegram file exchange.

## Examples

- `examples/add-color-example.md`
- `examples/follow-sell-example.md`
