# EP Standalone Customization Plan

## Goal
Split the EP backend and frontend under `ep/` into an EP-only standalone project without touching files outside `ep/`.

## Steps
- [completed] Inspect EP target files and isolate non-EP logic to remove
- [completed] Patch backend config/processors/API to EPUS-only behavior
- [completed] Patch frontend template defaults/store labels to EP-only
- [completed] Add `ep/docker-compose.yml` for standalone local run
- [completed] Run focused verification on edited files

## Constraints
- Only modify files under `/Users/melodylu/PycharmProjects/BU2Ama/ep/`
- Keep existing shared EP logic intact where requested
