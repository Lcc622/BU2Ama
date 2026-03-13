# Store Rules

## Store Normalization

- Supported store codes are `EP`, `DM`, and `PZ`.
- Treat any `DA` request as `DM`.
- Template mapping:
  - `EP` -> `EPUS`
  - `DM` -> `DaMaUS`
  - `PZ` -> `PZUS`

## Source File Resolution

- EP default source files: `EP-0.xlsm`, `EP-1.xlsm`, `EP-2.xlsm`
- DM config default source files: `DA-0.xlsm`, `DA-1.xlsm`, `DA-2.xlsm`
- PZ default source files: `PZ-0.xlsm`, `PZ-1.xlsm`, `PZ-2.xlsm`

Runtime behavior:
- `add_color_size.py` first checks configured defaults for the selected store.
- If none exist, it falls back to scanning `backend/uploads/` for matching store files.
- `follow_sell.py` accepts both `DA-*` and `DM-*` files for the DM store.

## Listing Report Files

- EP: `EP-All+Listings+Report.txt`
- DM: `DM-All+Listings+Report.txt`
- PZ: `PZ-All+Listings+Report.txt`

## Index Database Files

- Add-color/add-size indexes:
  - `backend/uploads/excel_index_EP.db`
  - `backend/uploads/excel_index_DM.db`
  - `backend/uploads/excel_index_PZ.db`
- Follow-sell indexes:
  - `backend/uploads/ep_index_EP.db`
  - `backend/uploads/ep_index_DM.db`
  - `backend/uploads/ep_index_PZ.db`

If a legacy `backend/uploads/ep_index.db` exists, rebuild store indexes after uploading fresh files.

## SKU Suffix Families

The processors derive standard suffixes from store and size:

- EP:
  - base: `-USA`
  - plus-size: `-PH`
- DM:
  - base: `-PL`
  - plus-size: `-PLPH`
- PZ:
  - base: `-DA`
  - plus-size: `-DAPH`

**Add-color suffix determination** (updated 2026-03-12):

In add-color mode, the processor first checks the source data index to determine which
suffix(es) actually exist for the given style+size combination:

- If only base suffix exists in source → use base suffix
- If only plus suffix exists in source → use plus suffix
- If both exist in source → expand both (generates two rows)
- If neither exists in source → fall back to size-threshold rule: size `14` and above
  uses plus suffix, smaller sizes use base suffix

The size `14` threshold is a **fallback only** for styles with no source data.
Most real SKUs follow what the source file actually has, not the threshold rule.

## EP Add-Color Image URL Convention (updated 2026-03-13)

EP store generated image URLs use sequential numbering:

- Base suffix (e.g. `-USA`): `...{style}{color}-{image_variant}1.jpg` through `...5.jpg`
- Plus suffix (e.g. `-PH`): `...{style}{color}-{image_variant}101.jpg` through `...105.jpg`

Previously the base branch incorrectly used `10/20/30/40/50`. The correct numbers are `1/2/3/4/5`.

## Attribute Consistency Rules (updated 2026-03-13)

### colour_map and color fields
Always recomputed from `final_color_code` — never copied from source row — when color has changed.
`preserve_source_color` is only `True` when all of:
1. Variation theme is SizeColor
2. `force_size_name_color_theme` is False
3. `color_changed` is False (source color == target color)

This prevents inconsistent colour_map values (e.g. "Blue" vs "Navy" vs "Haze Blue" for the same color) caused by copying from source rows that matched by size only.

### Follow-sell product attribute consistency
In follow-sell mode, style-level attributes (sleeve_type, neck_style, apparel_silhouette, pattern_type, etc.) are read from a **canonical source row per (style, color)** — the first matched source row for that style+color combination.

All sizes of the same style+color share the same canonical source row for these fields. This prevents the same style producing different sleeve types or necklines across sizes when source data is inconsistent.
