# Excel Color Mapping System - Design System

**Version:** 2.0
**Last Updated:** 2026-02-26
**Pattern:** Data-Dense Dashboard
**Stack:** React + TypeScript + Tailwind CSS

---

## 🎨 Visual Identity

### Style: Data-Dense Dashboard
- **Keywords:** Multiple charts/widgets, data tables, KPI cards, minimal padding, grid layout, space-efficient, maximum data visibility
- **Best For:** Business intelligence dashboards, financial analytics, enterprise reporting, operational dashboards, data warehousing
- **Performance:** ⚡ Excellent
- **Accessibility:** ✓ WCAG AA compliant

### Color Palette

```css
/* Primary Colors */
--color-primary: #1E40AF;      /* Blue-800 - Primary actions, headers */
--color-secondary: #3B82F6;    /* Blue-500 - Secondary elements */
--color-accent: #F59E0B;       /* Amber-500 - CTA, highlights, warnings */

/* Backgrounds */
--color-bg-primary: #F8FAFC;   /* Slate-50 - Main background */
--color-bg-card: #FFFFFF;      /* White - Card backgrounds */
--color-bg-hover: #F1F5F9;     /* Slate-100 - Hover states */

/* Text */
--color-text-primary: #1E3A8A;   /* Blue-900 - Headings */
--color-text-secondary: #475569; /* Slate-600 - Body text */
--color-text-muted: #64748B;     /* Slate-500 - Muted text */

/* Borders */
--color-border: #E2E8F0;       /* Slate-200 - Borders */
--color-border-focus: #3B82F6; /* Blue-500 - Focus rings */

/* Status Colors */
--color-success: #10B981;      /* Green-500 - Success states */
--color-error: #EF4444;        /* Red-500 - Error states */
--color-warning: #F59E0B;      /* Amber-500 - Warning states */
--color-info: #3B82F6;         /* Blue-500 - Info states */
```

### Typography

**Font Family:** Fira Code (monospace) / Fira Sans (sans-serif)

```css
/* Headings - Fira Sans */
font-family: 'Fira Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Body Text - Fira Sans */
font-family: 'Fira Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Code/Data - Fira Code */
font-family: 'Fira Code', 'Courier New', monospace;
```

**Font Sizes:**
- H1: 2.25rem (36px) - Page title
- H2: 1.5rem (24px) - Section headers
- H3: 1.25rem (20px) - Card headers
- Body: 0.875rem (14px) - Default text
- Small: 0.75rem (12px) - Labels, captions
- Code: 0.8125rem (13px) - SKU codes, data

**Line Heights:**
- Headings: 1.2
- Body: 1.5
- Code: 1.6

**Font Weights:**
- Regular: 400
- Medium: 500
- Semibold: 600
- Bold: 700

---

## 🧩 Component Patterns

### Layout Structure

```
┌─────────────────────────────────────────────────────┐
│ Header (Fixed)                                      │
│ - Logo + Title                                      │
│ - Navigation Tabs                                   │
│ - User Actions                                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Main Content (Grid Layout)                         │
│                                                     │
│ ┌──────────────────┐  ┌──────────────────┐        │
│ │ Excel Processing │  │ Color Mapping    │        │
│ │                  │  │ Management       │        │
│ │ - Upload         │  │                  │        │
│ │ - Analysis       │  │ - Search         │        │
│ │ - Process        │  │ - Table          │        │
│ │ - Download       │  │ - Actions        │        │
│ └──────────────────┘  └──────────────────┘        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Card Design

```tsx
// Standard card with shadow and border
<div className="bg-white rounded-lg border border-slate-200 shadow-sm hover:shadow-md transition-shadow duration-200">
  <div className="p-6">
    {/* Card content */}
  </div>
</div>
```

### Data Table

```tsx
// Responsive table with hover states
<div className="overflow-x-auto border border-slate-200 rounded-lg">
  <table className="min-w-full divide-y divide-slate-200">
    <thead className="bg-slate-50 sticky top-0">
      <tr>
        <th className="px-4 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
          Column
        </th>
      </tr>
    </thead>
    <tbody className="bg-white divide-y divide-slate-100">
      <tr className="hover:bg-slate-50 transition-colors duration-150 cursor-pointer">
        <td className="px-4 py-3 text-sm text-slate-900">
          Data
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

### Buttons

```tsx
// Primary button
<button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed">
  Primary Action
</button>

// Secondary button
<button className="px-4 py-2 bg-white hover:bg-slate-50 text-blue-600 font-medium border border-blue-600 rounded-lg transition-colors duration-200">
  Secondary Action
</button>

// Accent/CTA button
<button className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white font-medium rounded-lg transition-colors duration-200">
  Process Excel
</button>
```

### Form Inputs

```tsx
// Text input
<input
  type="text"
  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
  placeholder="Search..."
/>

// File upload
<label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-300 rounded-lg cursor-pointer hover:border-blue-500 hover:bg-slate-50 transition-colors duration-200">
  <input type="file" className="hidden" />
  <div className="flex flex-col items-center">
    <svg className="w-8 h-8 text-slate-400" />
    <p className="text-sm text-slate-600">Click to upload</p>
  </div>
</label>
```

### Status Badges

```tsx
// Success
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
  Success
</span>

// Error
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
  Error
</span>

// Warning
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
  Warning
</span>
```

### Loading States

```tsx
// Skeleton loader for table rows
<div className="animate-pulse space-y-3">
  <div className="h-4 bg-slate-200 rounded w-3/4"></div>
  <div className="h-4 bg-slate-200 rounded w-1/2"></div>
</div>

// Spinner
<svg className="animate-spin h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
</svg>
```

---

## 📊 Data Visualization

### Chart Types for SKU Analysis

1. **Bar Chart** - Color distribution comparison
   - Library: Recharts
   - Colors: Use primary palette with distinct colors per bar
   - Accessibility: Add value labels on bars

2. **Funnel Chart** - SKU processing flow
   - Library: Recharts or Custom SVG
   - Colors: Gradient from blue-600 to blue-400
   - Show conversion percentages

3. **Table with Sorting** - Detailed SKU data
   - Sortable columns
   - Row highlighting on hover
   - Pagination for large datasets

### KPI Cards

```tsx
<div className="bg-white rounded-lg border border-slate-200 p-4">
  <div className="flex items-center justify-between">
    <div>
      <p className="text-xs font-medium text-slate-500 uppercase">Total SKUs</p>
      <p className="text-2xl font-bold text-blue-900 mt-1">1,234</p>
    </div>
    <div className="p-3 bg-blue-100 rounded-lg">
      <svg className="w-6 h-6 text-blue-600" />
    </div>
  </div>
  <div className="mt-2 flex items-center text-xs">
    <span className="text-green-600 font-medium">+12%</span>
    <span className="text-slate-500 ml-1">vs last week</span>
  </div>
</div>
```

---

## 🎯 Key Effects & Interactions

### Hover States
- **Cards:** `hover:shadow-md transition-shadow duration-200`
- **Table Rows:** `hover:bg-slate-50 transition-colors duration-150`
- **Buttons:** `hover:bg-blue-700 transition-colors duration-200`

### Focus States
- **Inputs:** `focus:ring-2 focus:ring-blue-500 focus:border-transparent`
- **Buttons:** `focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`

### Loading States
- **Skeleton screens** for table data
- **Spinners** for button actions
- **Progress bars** for file uploads

### Smooth Animations
- Transitions: 150-300ms
- Use `transition-colors`, `transition-shadow`, `transition-transform`
- Respect `prefers-reduced-motion`

---

## ♿ Accessibility Requirements

### WCAG AA Compliance

1. **Color Contrast**
   - Text on white: minimum 4.5:1 ratio
   - Primary text (#1E3A8A) on white: 11.8:1 ✓
   - Secondary text (#475569) on white: 7.5:1 ✓

2. **Keyboard Navigation**
   - All interactive elements focusable
   - Visible focus rings
   - Tab order matches visual order

3. **Screen Readers**
   - Alt text for all images
   - aria-label for icon-only buttons
   - aria-live for dynamic content updates

4. **Form Accessibility**
   - Labels with `for` attribute
   - Error messages linked with `aria-describedby`
   - Required fields marked with `aria-required`

5. **Table Accessibility**
   - `<th>` with `scope` attribute
   - Caption or aria-label for table purpose
   - Sortable columns announced to screen readers

---

## 🚫 Anti-Patterns to Avoid

1. **No emoji icons** - Use Heroicons or Lucide React instead
2. **No ornate design** - Keep it clean and data-focused
3. **No missing filters** - Always provide search/filter for tables
4. **No layout shifts** - Reserve space for loading content
5. **No invisible borders** - Ensure borders visible in light mode
6. **No scale transforms on hover** - Use color/opacity instead

---

## 📱 Responsive Breakpoints

```css
/* Mobile First */
sm: 640px   /* Small tablets */
md: 768px   /* Tablets */
lg: 1024px  /* Laptops */
xl: 1280px  /* Desktops */
2xl: 1536px /* Large screens */
```

### Layout Adjustments
- **Mobile (< 768px):** Single column, stacked cards
- **Tablet (768px - 1024px):** Two columns, side-by-side
- **Desktop (> 1024px):** Full grid layout with sidebars

---

## ✅ Pre-Delivery Checklist

- [ ] No emojis as icons (use Heroicons/Lucide)
- [ ] `cursor-pointer` on all clickable elements
- [ ] Hover states with smooth transitions (150-300ms)
- [ ] Light mode: text contrast 4.5:1 minimum
- [ ] Focus states visible for keyboard nav
- [ ] `prefers-reduced-motion` respected
- [ ] Responsive: 375px, 768px, 1024px, 1440px
- [ ] Loading states for all async operations
- [ ] Error states with clear messages
- [ ] Alt text for all images
- [ ] Form labels with `for` attribute
- [ ] Table headers with proper semantics

---

## 🔗 Resources

- **Google Fonts:** https://fonts.google.com/share?selection.family=Fira+Code:wght@400;500;600;700|Fira+Sans:wght@300;400;500;600;700
- **Icons:** Heroicons (https://heroicons.com) or Lucide React (https://lucide.dev)
- **Charts:** Recharts (https://recharts.org)
- **Tailwind Docs:** https://tailwindcss.com/docs
