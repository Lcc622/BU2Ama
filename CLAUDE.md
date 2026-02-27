# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Excel color mapping system (Excel颜色加色系统) for processing SKU data with color codes. **Version 2.0** is a complete rewrite using Python (FastAPI) backend and React (TypeScript) frontend.

### Features

1. Manages color code mappings (e.g., "LV" → "Lavender", "BK" → "Black")
2. Analyzes Excel files containing SKU data to identify color distributions
3. Generates new Excel files from templates with color-mapped SKU data
4. Supports multiple Excel templates (DaMaUS and EPUS)

The system is designed for e-commerce product data management, specifically handling SKU formats like `EG02230LV14-DA` where:
- `EG02230` = product code (7-8 characters)
- `LV` = color code (2 characters)
- `14` = size (2 digits)
- `-DA` = suffix (optional)

## Technology Stack

### Backend (Python)
- **FastAPI** - Modern async web framework
- **openpyxl** - Excel file processing
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server

### Frontend (React)
- **React 18 + TypeScript** - UI framework with type safety
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **React Query** - Server state management
- **Zustand** - Client state management
- **Axios** - HTTP client

## Commands

### Using Docker Compose (Recommended)
```bash
# Start all services
docker-compose up

# Stop all services
docker-compose down
```

### Backend (Python)
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start server
python -m app.main
# or
uvicorn app.main:app --reload

# Server runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Frontend (React)
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Server runs on http://localhost:5173
```

### Legacy Node.js Version
The original Node.js version is preserved in the `legacy/` directory (if moved).

## Architecture

### Backend Structure (`backend/`)

**app/main.py** - FastAPI application entry point:
- CORS configuration
- Route registration
- Global exception handling

**app/api/** - API route handlers:
- `mapping.py` - Color mapping CRUD operations (`/api/mapping/*`)
- `excel.py` - Excel file upload, analysis, and processing (`/api/analyze`, `/api/process`, `/api/download/*`)

**app/core/** - Core business logic:
- `color_mapper.py` - Color mapping management (loads/saves `data/colorMapping.json`)
- `excel_processor.py` - Excel parsing and generation logic

**app/models/** - Pydantic data models:
- `mapping.py` - Color mapping request/response models
- `excel.py` - Excel processing request/response models

**app/config.py** - Configuration management:
- Directory paths (data, uploads, templates)
- Template configurations (DaMaUS, EPUS)
- CORS settings

### Frontend Structure (`frontend/`)

**src/App.tsx** - Main application component with React Query provider

**src/components/** - React components:
- `ColorMapping/` - Color mapping management UI
- `ExcelUpload/` - File upload and analysis UI
- `ExcelProcess/` - Excel processing UI
- `Layout/` - Layout components
- `ui/` - Reusable UI components (shadcn/ui style)

**src/services/** - API client services:
- `mappingApi.ts` - Color mapping API calls
- `excelApi.ts` - Excel processing API calls

**src/store/** - Zustand state management:
- `useUploadStore.ts` - Upload and analysis state
- `useProcessStore.ts` - Processing state

**src/types/** - TypeScript type definitions:
- `api.ts` - API request/response types

**src/lib/** - Utility functions:
- `axios.ts` - Axios configuration and interceptors
- `queryClient.ts` - React Query configuration
- `utils.ts` - Helper functions (cn for className merging)

**lib/excelProcessor.js** - Excel file processing logic:
- Parses SKU formats to extract product code, color code, size, and suffix
- Analyzes Excel files to identify SKU distributions and unknown colors
- Generates new Excel files from templates with mapped colors
- Supports two template types: `DaMaUS` and `EPUS` with different column configurations
- Handles multi-file input and multi-sheet output (one sheet per suffix)
- Automatically calculates launch dates based on Beijing timezone (UTC+8)

### Data Flow

1. **Upload** → User uploads Excel file(s) containing SKU data
2. **Analyze** → System parses SKUs, identifies color codes, and reports statistics
3. **Process** → User selects SKU prefixes to filter; system generates new Excel from template
4. **Download** → User downloads the generated Excel file with color-mapped data

### Template System

Templates are Excel files (`.xlsm`) located in the project root:
- `加色模板.xlsm` - DaMaUS template
- `EP-ES01840FL-加色-Coco-2.4新表.xlsm` - EPUS template

Each template has a `TEMPLATES` configuration in `excelProcessor.js` defining:
- Column indices for SKU, product name, color, size, images, etc.
- Different image URL patterns (DaMaUS uses `-PL10.jpg`, EPUS uses `-L1.jpg`)
- Launch date column position

### SKU Parsing Logic

The system uses regex patterns to extract components from SKU strings:
- Supports 7-8 character product codes (e.g., `EG02230` or `EE0164A`)
- Color codes are always 2 uppercase letters
- Size is always 2 digits
- Suffix is optional and starts with `-`

### Launch Date Calculation

Launch dates are calculated based on Beijing time (UTC+8):
- Before 3 PM Beijing time → use previous day
- After 3 PM Beijing time → use current day
- Format: `YYYY-MM-DD`

## File Structure

```
/
├── server.js              # Express server and API routes
├── lib/
│   ├── colorMapper.js     # Color mapping CRUD operations
│   └── excelProcessor.js  # Excel parsing and generation logic
├── data/
│   └── colorMapping.json  # Color code mappings (persistent storage)
├── public/
│   └── index.html         # Web UI (single-page application)
├── uploads/               # Temporary storage for uploaded/generated files
├── 加色模板.xlsm           # DaMaUS template
└── EP-ES01840FL-加色-Coco-2.4新表.xlsm  # EPUS template
```

## Important Implementation Details

### Multi-file Processing
The `/api/process` endpoint supports multiple input files and generates multiple sheets (one per suffix) in the output file. When processing:
- All input files are scanned to collect sizes and suffixes
- Each unique suffix gets its own sheet in the output
- Product Name, Key Features, and Generic Keyword are copied from sample rows matching the suffix

### Color Map Categories
The `getColorMapValue()` function categorizes color names into standard categories (Purple, Blue, Green, Red, Pink, Orange, Yellow, Brown, Black, White, Grey, Multicolor) for the COLOR_MAP column.

### Image URL Generation
Image URLs follow the pattern: `https://eppic.s3.amazonaws.com/{productCode}{colorCode}-{variant}.jpg`
- DaMaUS: `-PL10.jpg`, `-PL2.jpg`, `-PL3.jpg`, etc.
- EPUS: `-L1.jpg`, `-L2.jpg`, `-L3.jpg`, etc.

### File Format Handling
- Input files can be `.xlsx`, `.xlsm`, or `.xls`
- Output files are always `.xlsx` (even if template is `.xlsm`) because the `xlsx` library doesn't preserve macros when creating new workbooks
- All Excel files must have a sheet named "Template"

## API Endpoints

### Color Mapping
- `GET /api/mapping` - Get all color mappings
- `GET /api/mapping/search?keyword=xxx` - Search mappings
- `POST /api/mapping` - Add/update mapping (single or batch)
- `DELETE /api/mapping/:code` - Delete mapping

### Excel Processing
- `GET /api/templates` - List available templates
- `POST /api/analyze` - Analyze uploaded Excel file(s)
- `POST /api/process` - Generate new Excel from template
- `GET /api/download/:filename` - Download generated file
- `GET /api/files` - List uploaded files
- `DELETE /api/files/:filename` - Delete uploaded file

## Common Development Patterns

### Adding a New Template
1. Add template file to project root
2. Add configuration to `TEMPLATES` object in `excelProcessor.js`
3. Define column indices for all required fields
4. Update image URL generation logic if needed

### Modifying SKU Format
Update the regex patterns in `extractColorFromSKU()` and `parseSkuInput()` functions in `excelProcessor.js`.

### Adding New Color Mappings
Either use the API (`POST /api/mapping`) or directly edit `data/colorMapping.json`. All color codes must be uppercase.
