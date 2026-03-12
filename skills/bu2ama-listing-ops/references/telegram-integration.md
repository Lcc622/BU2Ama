# Telegram Integration

Use this reference only when BU2Ama tasks are executed through OpenClaw or a Telegram bot.

## Upload Flow

1. Save the incoming Telegram attachment to a local temporary path.
2. Call `scripts/upload_source.py --file <temp-path> --json`.
3. If the user expects immediate availability, add `--rebuild-index`.
4. Return the parsed JSON result to the chat.

## Export Flow

1. Run `scripts/add_color_size.py --json`.
2. Read the `output_file` value from JSON.
3. By default, do not send any progress update before the final answer.
4. The skill wrapper will copy the exported file into `~/.openclaw/media/bu2ama/` automatically.
5. In OpenClaw replies, put the staged file on its own line as `MEDIA:<absolute-path>`.
6. OpenClaw will turn that line into a Telegram file attachment.
7. If the file cannot be sent, return the absolute path and the failure reason.

For 加色加码, prefer the web-style parameter set by default:

- `--prefix`
- `--mode`
- `--colors`
- `--start-size` / `--end-size` / `--size-step`
- or `--sizes`

## Follow-Sell Flow

1. Run `scripts/follow_sell.py --json` for normal queries.
2. By default, format the reply from `results[].size_details` so Telegram matches the web UI columns:
   - `size`
   - `suffix`
   - `sku`
3. If the user asks to export, run `scripts/follow_sell.py --export-excel --json`.
4. When `export.output_file` is present, return a short summary followed by:

   ```text
   MEDIA:/absolute/path/to/file.xlsx
   ```

5. If the user uploaded a text file of SKCs, pass it through `--skc-file`.

## Progress Messaging

Default behavior for Telegram/OpenClaw is silent execution:

- Do not send progress updates for normal environment checks, exports, or queries.
- Return the final result only.
- Send an intermediate update only if:
  - execution fails,
  - user action is required,
  - or the task is unusually slow and would otherwise look stuck.

## Failure Handling

- Always surface the raw `errors` array from JSON.
- Distinguish between transport failure and BU2Ama processing failure.
- Keep the saved local file until the result is confirmed delivered or the retry window ends.
- If `MEDIA:` delivery fails, tell the user the absolute path and keep the textual summary.
