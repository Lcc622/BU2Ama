# Design System Quick Reference

## 🎨 Color Classes

### Primary (Blue)
```tsx
bg-primary-50   #EFF6FF  // Lightest
bg-primary-100  #DBEAFE
bg-primary-500  #3B82F6  // Secondary actions
bg-primary-600  #2563EB
bg-primary-800  #1E40AF  // Primary (DEFAULT)
bg-primary-900  #1E3A8A  // Darkest (headings)

text-primary-600  // Links
text-primary-900  // Headings
```

### Accent (Amber)
```tsx
bg-accent       #F59E0B  // CTA buttons (DEFAULT)
bg-accent-600   #D97706  // Hover state

text-accent     // Highlights
```

### Neutrals (Slate)
```tsx
bg-slate-50     #F8FAFC  // Page background
bg-slate-100    #F1F5F9  // Hover states
bg-white        #FFFFFF  // Cards

border-slate-200  #E2E8F0  // Borders
border-slate-300  #CBD5E1  // Input borders

text-slate-500  #64748B  // Muted text
text-slate-600  #475569  // Secondary text
text-slate-700  #334155  // Body text
text-slate-900  #0F172A  // Dark text
```

### Status
```tsx
bg-green-100 text-green-800   // Success
bg-red-100 text-red-800       // Error
bg-amber-100 text-amber-800   // Warning
bg-blue-100 text-blue-800     // Info
```

---

## 📝 Typography

### Font Families
```tsx
font-sans  // Fira Sans (default)
font-mono  // Fira Code (for SKU codes)
```

### Sizes
```tsx
text-xs    // 12px - Labels, captions
text-sm    // 14px - Body text (default)
text-base  // 14px - Same as sm
text-lg    // 16px - Large body
text-xl    // 20px - H3
text-2xl   // 24px - H2
text-4xl   // 36px - H1
```

### Weights
```tsx
font-light     // 300
font-normal    // 400
font-medium    // 500
font-semibold  // 600
font-bold      // 700
```

---

## 🧩 Component Snippets

### Card
```tsx
<div className="bg-white rounded-lg border border-slate-200 shadow-sm hover:shadow-md transition-shadow duration-200">
  <div className="border-b border-slate-200 px-6 py-4">
    <h2 className="text-xl font-semibold text-primary-900">Title</h2>
    <p className="text-xs text-slate-500 mt-1">Description</p>
  </div>
  <div className="p-6">
    {/* Content */}
  </div>
</div>
```

### Button - Primary
```tsx
<button className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500">
  Primary
</button>
```

### Button - CTA (Accent)
```tsx
<button className="px-4 py-2 bg-accent hover:bg-accent-600 text-white font-semibold rounded-lg transition-colors duration-200 shadow-sm hover:shadow-md">
  Process
</button>
```

### Button - Disabled
```tsx
<button disabled className="px-4 py-2 bg-slate-300 text-slate-500 cursor-not-allowed rounded-lg">
  Disabled
</button>
```

### Badge
```tsx
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
  Badge
</span>
```

### Input
```tsx
<input
  type="text"
  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
  placeholder="Search..."
/>
```

### Table
```tsx
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
        <td className="px-4 py-3 text-sm text-slate-700">Data</td>
      </tr>
    </tbody>
  </table>
</div>
```

### Skeleton Loader
```tsx
<div className="animate-pulse space-y-3">
  <div className="h-4 bg-slate-200 rounded w-3/4"></div>
  <div className="h-4 bg-slate-200 rounded w-1/2"></div>
  <div className="h-4 bg-slate-200 rounded w-5/6"></div>
</div>
```

### Spinner
```tsx
<svg className="animate-spin h-5 w-5 text-primary-600" fill="none" viewBox="0 0 24 24">
  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
</svg>
```

### Error Alert
```tsx
<div className="rounded-lg bg-red-50 border border-red-200 p-4">
  <div className="flex items-start">
    <svg className="h-5 w-5 text-red-400 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
    </svg>
    <div className="ml-3">
      <h3 className="text-sm font-medium text-red-800">Error Title</h3>
      <p className="text-sm text-red-700 mt-1">Error message</p>
    </div>
  </div>
</div>
```

### Success Alert
```tsx
<div className="rounded-lg bg-green-50 border border-green-200 p-4">
  <div className="flex items-start">
    <svg className="h-5 w-5 text-green-400 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
    </svg>
    <div className="ml-3">
      <h3 className="text-sm font-medium text-green-800">Success</h3>
      <p className="text-sm text-green-700 mt-1">Success message</p>
    </div>
  </div>
</div>
```

---

## 🎯 Common Patterns

### Hover Effect
```tsx
hover:bg-slate-50 transition-colors duration-150
```

### Focus Ring
```tsx
focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
```

### Shadow Elevation
```tsx
shadow-sm hover:shadow-md transition-shadow duration-200
```

### Disabled State
```tsx
disabled:opacity-50 disabled:cursor-not-allowed
```

### Truncate Text
```tsx
truncate  // Single line
line-clamp-2  // Multiple lines (requires @tailwindcss/line-clamp plugin)
```

---

## 📐 Spacing Scale

```tsx
p-1   // 0.25rem (4px)
p-2   // 0.5rem (8px)
p-3   // 0.75rem (12px)
p-4   // 1rem (16px)
p-6   // 1.5rem (24px)
p-8   // 2rem (32px)

gap-2  // 0.5rem (8px)
gap-4  // 1rem (16px)
gap-6  // 1.5rem (24px)
```

---

## 🎨 Icon Guidelines

### Use SVG Icons (Not Emojis)
```tsx
// ✅ Good
<svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
</svg>

// ❌ Bad
<span>✅</span>
```

### Icon Sizes
```tsx
w-4 h-4  // 16px - Small icons
w-5 h-5  // 20px - Default icons
w-6 h-6  // 24px - Large icons
w-8 h-8  // 32px - Hero icons
```

---

## ⚡ Performance Tips

1. **Use `transition-colors` instead of `transition-all`**
   ```tsx
   // ✅ Good
   transition-colors duration-200

   // ❌ Bad
   transition-all duration-200
   ```

2. **Respect reduced motion**
   ```tsx
   motion-reduce:transition-none
   ```

3. **Use `flex-shrink-0` for icons**
   ```tsx
   <svg className="w-5 h-5 flex-shrink-0" />
   ```

---

## ♿ Accessibility Checklist

- [ ] All buttons have `cursor-pointer`
- [ ] Focus states visible (`focus:ring-2`)
- [ ] Color contrast ≥ 4.5:1
- [ ] Icon buttons have `aria-label`
- [ ] Form inputs have labels
- [ ] Loading states announced
- [ ] Error messages descriptive

---

## 🚀 Quick Start

1. **Import fonts in `index.html`**
   ```html
   <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
   ```

2. **Use design tokens from `tailwind.config.js`**
   ```tsx
   bg-primary  // Instead of bg-blue-800
   bg-accent   // Instead of bg-amber-500
   ```

3. **Follow component patterns**
   - Copy snippets from this guide
   - Maintain consistency across components

---

**Quick Reference Version:** 1.0
**Design System:** Data-Dense Dashboard
**Last Updated:** 2026-02-26
