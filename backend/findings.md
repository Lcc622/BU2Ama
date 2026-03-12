# Findings

- The current fixed code successfully generated 7 DAMA rows for `ES01819NT` sizes `14,16,18,20,22,24,26`.
- New output workbook: `results/processed_20260306_131248.xlsx`.
- Historical workbook: `results/processed_20260305_091424.xlsx`.
- Requested fixes are reflected in the new output:
  - Seller SKU / Style Number / Manufacturer Part Number now end with `-PLPH` for all tested sizes.
  - Parent SKU now resolves to `ES01819-PLPH` instead of inheriting `EE0168B-PLPH` from source data.
  - Variation Theme now outputs `SizeName-ColorName` instead of `SizeColor`.
- `Outer Material Type` is populated as `100%Polyester` for all 7 rows in the new output.
- In this specific historical workbook, `Outer Material Type` was already populated, so this field shows no regression rather than a visible diff for this case.
