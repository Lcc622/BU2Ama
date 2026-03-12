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

Size `14` and above is treated as plus-size for suffix generation.
