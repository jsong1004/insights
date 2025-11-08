# UI Style Guide
## Mentorship Feedback Web Service

**Version**: 1.0
**Last Updated**: 2025-11-07
**Purpose**: This guide defines the visual language, design patterns, and UI standards for the Mentorship Feedback Web Service. Use this document to maintain consistency and guide AI-assisted development of similar applications.

---

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Spacing & Layout](#spacing--layout)
5. [Components](#components)
6. [Forms & Inputs](#forms--inputs)
7. [Feedback & Status](#feedback--status)
8. [Navigation Patterns](#navigation-patterns)
9. [Role-Based UI Patterns](#role-based-ui-patterns)
10. [Accessibility Guidelines](#accessibility-guidelines)
11. [Responsive Design](#responsive-design)
12. [Animation & Transitions](#animation--transitions)

---

## Design Philosophy

### Core Principles

**Professional & Trustworthy**
- Clean, minimalist aesthetic appropriate for educational/mentorship contexts
- High readability with generous whitespace
- Clear visual hierarchy that guides users through workflows
- Consistent, predictable interactions

**User-Centric**
- Role-appropriate interfaces (admin, organizer, mentor, mentee)
- Form-focused design optimized for feedback submission and review
- Clear feedback mechanisms for all user actions
- Progressive disclosure of complexity

**Accessible by Default**
- WCAG 2.1 AA compliance minimum
- Keyboard navigation support
- Screen reader compatibility
- Sufficient color contrast ratios

**Performance-Conscious**
- Lightweight components
- Optimized images and assets
- Minimal animation overhead
- Fast perceived load times

---

## Color System

### Primary Palette

```css
/* Primary - Blue (Trust, Professionalism) */
--primary-50:  #eff6ff;
--primary-100: #dbeafe;
--primary-200: #bfdbfe;
--primary-300: #93c5fd;
--primary-400: #60a5fa;
--primary-500: #3b82f6;  /* Main primary */
--primary-600: #2563eb;
--primary-700: #1d4ed8;
--primary-800: #1e40af;
--primary-900: #1e3a8a;

/* Secondary - Indigo (Support, Accent) */
--secondary-50:  #eef2ff;
--secondary-100: #e0e7ff;
--secondary-200: #c7d2fe;
--secondary-300: #a5b4fc;
--secondary-400: #818cf8;
--secondary-500: #6366f1;  /* Main secondary */
--secondary-600: #4f46e5;
--secondary-700: #4338ca;
--secondary-800: #3730a3;
--secondary-900: #312e81;
```

### Semantic Colors

```css
/* Success - Green */
--success-50:  #f0fdf4;
--success-100: #dcfce7;
--success-500: #22c55e;  /* Main success */
--success-600: #16a34a;
--success-700: #15803d;

/* Warning - Amber */
--warning-50:  #fffbeb;
--warning-100: #fef3c7;
--warning-500: #f59e0b;  /* Main warning */
--warning-600: #d97706;
--warning-700: #b45309;

/* Error - Red */
--error-50:  #fef2f2;
--error-100: #fee2e2;
--error-500: #ef4444;  /* Main error */
--error-600: #dc2626;
--error-700: #b91c1c;

/* Info - Sky */
--info-50:  #f0f9ff;
--info-100: #e0f2fe;
--info-500: #0ea5e9;  /* Main info */
--info-600: #0284c7;
--info-700: #0369a1;
```

### Neutral Palette

```css
/* Grays - UI Elements */
--gray-50:  #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-300: #d1d5db;
--gray-400: #9ca3af;
--gray-500: #6b7280;
--gray-600: #4b5563;
--gray-700: #374151;
--gray-800: #1f2937;
--gray-900: #111827;

/* Text Colors */
--text-primary:   #111827;  /* gray-900 */
--text-secondary: #4b5563;  /* gray-600 */
--text-tertiary:  #6b7280;  /* gray-500 */
--text-disabled:  #9ca3af;  /* gray-400 */
--text-inverse:   #ffffff;

/* Background Colors */
--bg-primary:   #ffffff;
--bg-secondary: #f9fafb;  /* gray-50 */
--bg-tertiary:  #f3f4f6;  /* gray-100 */
--bg-overlay:   rgba(17, 24, 39, 0.5);  /* gray-900 with opacity */
```

### Role-Specific Accent Colors

```css
/* Admin - Purple */
--role-admin: #a855f7;

/* Organizer - Blue */
--role-organizer: #3b82f6;

/* Mentor - Emerald */
--role-mentor: #10b981;

/* Mentee - Orange */
--role-mentee: #f97316;
```

### Usage Guidelines

**Do's:**
- Use primary colors for main CTAs and primary actions
- Use semantic colors consistently (green for success, red for errors)
- Maintain 4.5:1 contrast ratio for normal text, 3:1 for large text
- Use role-specific colors sparingly for badges, icons, or section headers

**Don'ts:**
- Don't use more than 3 colors in a single component
- Don't use semantic colors for decorative purposes
- Don't override semantic meaning (e.g., green for errors)

---

## Typography

### Font Families

```css
/* Primary Font - Inter (Sans-serif) */
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
                'Roboto', 'Helvetica Neue', Arial, sans-serif;

/* Monospace Font - JetBrains Mono */
--font-mono: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
```

**Rationale**: Inter provides excellent readability at small sizes, has a professional appearance, and includes extensive character support. JetBrains Mono is used for code snippets or technical identifiers.

### Type Scale

```css
/* Font Sizes (rem-based) */
--text-xs:   0.75rem;   /* 12px */
--text-sm:   0.875rem;  /* 14px */
--text-base: 1rem;      /* 16px */
--text-lg:   1.125rem;  /* 18px */
--text-xl:   1.25rem;   /* 20px */
--text-2xl:  1.5rem;    /* 24px */
--text-3xl:  1.875rem;  /* 30px */
--text-4xl:  2.25rem;   /* 36px */
--text-5xl:  3rem;      /* 48px */

/* Line Heights */
--leading-none:   1;
--leading-tight:  1.25;
--leading-snug:   1.375;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
--leading-loose:  2;

/* Font Weights */
--font-light:    300;
--font-normal:   400;
--font-medium:   500;
--font-semibold: 600;
--font-bold:     700;
```

### Typography Styles

#### Headings

```css
h1 {
  font-size: 2.25rem;      /* text-4xl */
  font-weight: 700;        /* bold */
  line-height: 1.25;       /* tight */
  color: var(--text-primary);
  letter-spacing: -0.025em;
  margin-bottom: 1rem;
}

h2 {
  font-size: 1.875rem;     /* text-3xl */
  font-weight: 700;        /* bold */
  line-height: 1.25;       /* tight */
  color: var(--text-primary);
  letter-spacing: -0.025em;
  margin-bottom: 0.875rem;
}

h3 {
  font-size: 1.5rem;       /* text-2xl */
  font-weight: 600;        /* semibold */
  line-height: 1.375;      /* snug */
  color: var(--text-primary);
  margin-bottom: 0.75rem;
}

h4 {
  font-size: 1.25rem;      /* text-xl */
  font-weight: 600;        /* semibold */
  line-height: 1.375;      /* snug */
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

h5 {
  font-size: 1.125rem;     /* text-lg */
  font-weight: 600;        /* semibold */
  line-height: 1.5;        /* normal */
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

h6 {
  font-size: 1rem;         /* text-base */
  font-weight: 600;        /* semibold */
  line-height: 1.5;        /* normal */
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}
```

#### Body Text

```css
p {
  font-size: 1rem;         /* text-base */
  font-weight: 400;        /* normal */
  line-height: 1.625;      /* relaxed */
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.text-lead {
  font-size: 1.25rem;      /* text-xl */
  font-weight: 400;        /* normal */
  line-height: 1.75;       /* loose */
  color: var(--text-secondary);
}

.text-small {
  font-size: 0.875rem;     /* text-sm */
  font-weight: 400;        /* normal */
  line-height: 1.5;        /* normal */
  color: var(--text-secondary);
}

.text-tiny {
  font-size: 0.75rem;      /* text-xs */
  font-weight: 400;        /* normal */
  line-height: 1.5;        /* normal */
  color: var(--text-tertiary);
}
```

#### Special Text Styles

```css
/* Labels */
label {
  font-size: 0.875rem;     /* text-sm */
  font-weight: 500;        /* medium */
  line-height: 1.5;        /* normal */
  color: var(--text-secondary);
  margin-bottom: 0.375rem;
}

/* Helper Text */
.helper-text {
  font-size: 0.75rem;      /* text-xs */
  font-weight: 400;        /* normal */
  line-height: 1.5;        /* normal */
  color: var(--text-tertiary);
  margin-top: 0.25rem;
}

/* Error Text */
.error-text {
  font-size: 0.75rem;      /* text-xs */
  font-weight: 500;        /* medium */
  line-height: 1.5;        /* normal */
  color: var(--error-600);
  margin-top: 0.25rem;
}

/* Code */
code {
  font-family: var(--font-mono);
  font-size: 0.875em;
  background: var(--gray-100);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  color: var(--gray-800);
}

/* Links */
a {
  font-weight: 500;        /* medium */
  color: var(--primary-600);
  text-decoration: none;
  transition: color 0.15s ease;
}

a:hover {
  color: var(--primary-700);
  text-decoration: underline;
}

a:focus {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}
```

### Usage Guidelines

**Do's:**
- Use system font stack for fast loading
- Maintain consistent line heights for readability
- Use semantic heading hierarchy (h1 → h2 → h3)
- Scale font sizes proportionally for responsive design

**Don'ts:**
- Don't skip heading levels
- Don't use font size alone to convey hierarchy
- Don't set line-height below 1.4 for body text
- Don't use more than 2 font families

---

## Spacing & Layout

### Spacing Scale

```css
/* Tailwind-compatible spacing scale */
--space-0:  0;
--space-px: 1px;
--space-0-5: 0.125rem;  /* 2px */
--space-1:   0.25rem;   /* 4px */
--space-1-5: 0.375rem;  /* 6px */
--space-2:   0.5rem;    /* 8px */
--space-2-5: 0.625rem;  /* 10px */
--space-3:   0.75rem;   /* 12px */
--space-4:   1rem;      /* 16px */
--space-5:   1.25rem;   /* 20px */
--space-6:   1.5rem;    /* 24px */
--space-7:   1.75rem;   /* 28px */
--space-8:   2rem;      /* 32px */
--space-10:  2.5rem;    /* 40px */
--space-12:  3rem;      /* 48px */
--space-16:  4rem;      /* 64px */
--space-20:  5rem;      /* 80px */
--space-24:  6rem;      /* 96px */
```

### Layout Grid

```css
/* Container */
.container {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1rem;
}

@media (min-width: 640px) {
  .container { padding: 0 1.5rem; }
}

@media (min-width: 1024px) {
  .container { padding: 0 2rem; }
}

/* Grid System (12-column) */
.grid {
  display: grid;
  gap: 1.5rem;
}

.grid-cols-1  { grid-template-columns: repeat(1, minmax(0, 1fr)); }
.grid-cols-2  { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.grid-cols-3  { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.grid-cols-4  { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.grid-cols-12 { grid-template-columns: repeat(12, minmax(0, 1fr)); }

/* Flexbox Utilities */
.flex {
  display: flex;
}

.flex-col { flex-direction: column; }
.flex-row { flex-direction: row; }

.items-start   { align-items: flex-start; }
.items-center  { align-items: center; }
.items-end     { align-items: flex-end; }
.items-stretch { align-items: stretch; }

.justify-start   { justify-content: flex-start; }
.justify-center  { justify-content: center; }
.justify-end     { justify-content: flex-end; }
.justify-between { justify-content: space-between; }
```

### Component Spacing Patterns

```css
/* Card Padding */
.card-sm  { padding: 1rem; }      /* 16px */
.card-md  { padding: 1.5rem; }    /* 24px */
.card-lg  { padding: 2rem; }      /* 32px */

/* Section Spacing */
.section-sm  { padding-top: 2rem; padding-bottom: 2rem; }   /* 32px */
.section-md  { padding-top: 4rem; padding-bottom: 4rem; }   /* 64px */
.section-lg  { padding-top: 6rem; padding-bottom: 6rem; }   /* 96px */

/* Stack Spacing (vertical rhythm) */
.stack-xs > * + * { margin-top: 0.5rem; }   /* 8px */
.stack-sm > * + * { margin-top: 1rem; }     /* 16px */
.stack-md > * + * { margin-top: 1.5rem; }   /* 24px */
.stack-lg > * + * { margin-top: 2rem; }     /* 32px */
.stack-xl > * + * { margin-top: 3rem; }     /* 48px */
```

### Border Radius

```css
--radius-none: 0;
--radius-sm:   0.125rem;  /* 2px */
--radius-md:   0.375rem;  /* 6px */
--radius-lg:   0.5rem;    /* 8px */
--radius-xl:   0.75rem;   /* 12px */
--radius-2xl:  1rem;      /* 16px */
--radius-full: 9999px;    /* Fully rounded */
```

### Shadows

```css
/* Elevation system */
--shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
--shadow-inner: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
```

### Usage Guidelines

**Do's:**
- Use 8px base unit for consistent spacing
- Apply generous whitespace for readability
- Use shadows to establish visual hierarchy
- Maintain consistent padding within component types

**Don'ts:**
- Don't use arbitrary spacing values
- Don't create visual clutter with too little spacing
- Don't rely solely on shadows for hierarchy

---

## Components

### Buttons

#### Primary Button

```css
.btn-primary {
  /* Layout */
  padding: 0.625rem 1.25rem;
  border-radius: var(--radius-lg);

  /* Typography */
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1.5;

  /* Colors */
  background: var(--primary-600);
  color: var(--text-inverse);
  border: none;

  /* Effects */
  box-shadow: var(--shadow-sm);
  transition: all 0.15s ease;
  cursor: pointer;
}

.btn-primary:hover {
  background: var(--primary-700);
  box-shadow: var(--shadow-md);
}

.btn-primary:active {
  background: var(--primary-800);
  box-shadow: var(--shadow-sm);
}

.btn-primary:focus {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}

.btn-primary:disabled {
  background: var(--gray-300);
  color: var(--text-disabled);
  cursor: not-allowed;
  box-shadow: none;
}
```

#### Secondary Button

```css
.btn-secondary {
  padding: 0.625rem 1.25rem;
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  font-weight: 500;

  background: var(--bg-primary);
  color: var(--primary-600);
  border: 1px solid var(--gray-300);

  box-shadow: var(--shadow-sm);
  transition: all 0.15s ease;
  cursor: pointer;
}

.btn-secondary:hover {
  background: var(--gray-50);
  border-color: var(--gray-400);
}

.btn-secondary:active {
  background: var(--gray-100);
}
```

#### Ghost Button

```css
.btn-ghost {
  padding: 0.625rem 1.25rem;
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  font-weight: 500;

  background: transparent;
  color: var(--primary-600);
  border: none;

  transition: background 0.15s ease;
  cursor: pointer;
}

.btn-ghost:hover {
  background: var(--primary-50);
}

.btn-ghost:active {
  background: var(--primary-100);
}
```

#### Button Sizes

```css
.btn-xs { padding: 0.375rem 0.75rem; font-size: 0.75rem; }
.btn-sm { padding: 0.5rem 1rem; font-size: 0.875rem; }
.btn-md { padding: 0.625rem 1.25rem; font-size: 0.875rem; }  /* Default */
.btn-lg { padding: 0.75rem 1.5rem; font-size: 1rem; }
.btn-xl { padding: 1rem 2rem; font-size: 1.125rem; }
```

#### Icon Buttons

```css
.btn-icon {
  padding: 0.625rem;
  border-radius: var(--radius-lg);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-icon svg {
  width: 1.25rem;
  height: 1.25rem;
}
```

### Cards

```css
.card {
  background: var(--bg-primary);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-xl);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.15s ease;
}

.card:hover {
  box-shadow: var(--shadow-md);
}

.card-header {
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--gray-200);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.card-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

.card-content {
  /* Main content area */
}

.card-footer {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--gray-200);
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
```

### Badges

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.625rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1.5;
}

.badge-primary {
  background: var(--primary-100);
  color: var(--primary-700);
}

.badge-success {
  background: var(--success-100);
  color: var(--success-700);
}

.badge-warning {
  background: var(--warning-100);
  color: var(--warning-700);
}

.badge-error {
  background: var(--error-100);
  color: var(--error-700);
}

/* Role-specific badges */
.badge-admin {
  background: #f3e8ff;
  color: #7e22ce;
}

.badge-organizer {
  background: var(--primary-100);
  color: var(--primary-700);
}

.badge-mentor {
  background: #d1fae5;
  color: #047857;
}

.badge-mentee {
  background: #ffedd5;
  color: #c2410c;
}
```

### Dialogs/Modals

```css
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: var(--bg-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.dialog {
  background: var(--bg-primary);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-2xl);
  max-width: 32rem;
  width: 90%;
  max-height: 90vh;
  overflow: auto;
}

.dialog-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--gray-200);
}

.dialog-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.dialog-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

.dialog-content {
  padding: 1.5rem;
}

.dialog-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--gray-200);
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
```

### Tables

```css
.table-container {
  overflow-x: auto;
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

thead {
  background: var(--gray-50);
  border-bottom: 1px solid var(--gray-200);
}

th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: 1rem;
  border-top: 1px solid var(--gray-200);
  color: var(--text-primary);
}

tbody tr:hover {
  background: var(--gray-50);
}

/* Responsive table */
@media (max-width: 768px) {
  table, thead, tbody, th, td, tr {
    display: block;
  }

  thead tr {
    position: absolute;
    top: -9999px;
    left: -9999px;
  }

  td {
    position: relative;
    padding-left: 50%;
  }

  td:before {
    position: absolute;
    left: 1rem;
    width: 45%;
    padding-right: 10px;
    white-space: nowrap;
    content: attr(data-label);
    font-weight: 600;
    color: var(--text-secondary);
  }
}
```

### Spinners/Loaders

```css
.spinner {
  display: inline-block;
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid var(--gray-200);
  border-top-color: var(--primary-600);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner-sm { width: 1rem; height: 1rem; border-width: 1.5px; }
.spinner-lg { width: 2rem; height: 2rem; border-width: 3px; }
.spinner-xl { width: 3rem; height: 3rem; border-width: 4px; }
```

---

## Forms & Inputs

### Text Input

```css
.input {
  /* Layout */
  width: 100%;
  padding: 0.625rem 0.875rem;
  border-radius: var(--radius-lg);

  /* Typography */
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--text-primary);

  /* Appearance */
  background: var(--bg-primary);
  border: 1px solid var(--gray-300);
  box-shadow: var(--shadow-xs);
  transition: all 0.15s ease;
}

.input::placeholder {
  color: var(--text-tertiary);
}

.input:hover {
  border-color: var(--gray-400);
}

.input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input:disabled {
  background: var(--gray-100);
  color: var(--text-disabled);
  cursor: not-allowed;
}

.input-error {
  border-color: var(--error-500);
}

.input-error:focus {
  border-color: var(--error-500);
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}
```

### Textarea

```css
textarea.input {
  min-height: 6rem;
  resize: vertical;
  font-family: var(--font-primary);
}
```

### Select

```css
.select {
  width: 100%;
  padding: 0.625rem 2.5rem 0.625rem 0.875rem;
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--text-primary);
  background: var(--bg-primary);
  border: 1px solid var(--gray-300);
  box-shadow: var(--shadow-xs);
  transition: all 0.15s ease;
  cursor: pointer;

  /* Custom arrow */
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
}

.select:hover {
  border-color: var(--gray-400);
}

.select:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
```

### Checkbox

```css
.checkbox {
  width: 1.125rem;
  height: 1.125rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--gray-300);
  background: var(--bg-primary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.checkbox:hover {
  border-color: var(--gray-400);
}

.checkbox:checked {
  background: var(--primary-600);
  border-color: var(--primary-600);
}

.checkbox:focus {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}

.checkbox:disabled {
  background: var(--gray-100);
  border-color: var(--gray-300);
  cursor: not-allowed;
}
```

### Radio Button

```css
.radio {
  width: 1.125rem;
  height: 1.125rem;
  border-radius: 50%;
  border: 1px solid var(--gray-300);
  background: var(--bg-primary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.radio:hover {
  border-color: var(--gray-400);
}

.radio:checked {
  background: var(--primary-600);
  border-color: var(--primary-600);
  box-shadow: inset 0 0 0 3px white;
}

.radio:focus {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}
```

### Rating Input

```css
.rating {
  display: flex;
  gap: 0.5rem;
}

.rating-button {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--gray-300);
  background: var(--bg-primary);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.rating-button:hover {
  border-color: var(--primary-500);
  color: var(--primary-600);
}

.rating-button.active {
  background: var(--primary-600);
  border-color: var(--primary-600);
  color: white;
}

.rating-button:focus {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}
```

### Form Field Pattern

```html
<!-- Standard form field structure -->
<div class="form-field">
  <label for="field-id" class="form-label">
    Field Label
    <span class="text-error-500">*</span> <!-- Required indicator -->
  </label>

  <input
    id="field-id"
    type="text"
    class="input"
    placeholder="Placeholder text"
    aria-describedby="field-help field-error"
  />

  <p id="field-help" class="helper-text">
    Optional helper text
  </p>

  <p id="field-error" class="error-text" role="alert">
    Error message appears here
  </p>
</div>
```

```css
.form-field {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 0.375rem;
}

.form-label .text-error-500 {
  color: var(--error-500);
  margin-left: 0.125rem;
}
```

### Usage Guidelines

**Do's:**
- Always pair inputs with labels
- Use placeholder text sparingly (not as labels)
- Provide clear error messages
- Use appropriate input types (email, tel, url)
- Implement keyboard navigation

**Don'ts:**
- Don't rely on placeholder text alone
- Don't use tiny clickable areas
- Don't show errors before user interaction
- Don't disable submit buttons unless necessary

---

## Feedback & Status

### Toast Notifications

```css
.toast {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  min-width: 20rem;
  max-width: 28rem;
  padding: 1rem 1.25rem;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  display: flex;
  align-items: start;
  gap: 0.75rem;
  z-index: 100;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast-success {
  background: var(--success-50);
  border-left: 4px solid var(--success-500);
  color: var(--success-800);
}

.toast-error {
  background: var(--error-50);
  border-left: 4px solid var(--error-500);
  color: var(--error-800);
}

.toast-warning {
  background: var(--warning-50);
  border-left: 4px solid var(--warning-500);
  color: var(--warning-800);
}

.toast-info {
  background: var(--info-50);
  border-left: 4px solid var(--info-500);
  color: var(--info-800);
}

.toast-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.toast-content {
  flex: 1;
}

.toast-title {
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.toast-message {
  font-size: 0.875rem;
  line-height: 1.5;
}

.toast-close {
  width: 1.25rem;
  height: 1.25rem;
  padding: 0;
  background: transparent;
  border: none;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.15s;
}

.toast-close:hover {
  opacity: 1;
}
```

### Alert Banners

```css
.alert {
  padding: 1rem 1.25rem;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: start;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.alert-success {
  background: var(--success-50);
  border: 1px solid var(--success-200);
  color: var(--success-800);
}

.alert-error {
  background: var(--error-50);
  border: 1px solid var(--error-200);
  color: var(--error-800);
}

.alert-warning {
  background: var(--warning-50);
  border: 1px solid var(--warning-200);
  color: var(--warning-800);
}

.alert-info {
  background: var(--info-50);
  border: 1px solid var(--info-200);
  color: var(--info-800);
}

.alert-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.alert-message {
  font-size: 0.875rem;
  line-height: 1.5;
}
```

### Progress Indicators

```css
/* Progress Bar */
.progress {
  width: 100%;
  height: 0.5rem;
  background: var(--gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--primary-600);
  border-radius: var(--radius-full);
  transition: width 0.3s ease;
}

/* Step Indicator */
.steps {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2rem;
}

.step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.step:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 1rem;
  left: 50%;
  width: 100%;
  height: 2px;
  background: var(--gray-200);
  z-index: -1;
}

.step.completed:not(:last-child)::after {
  background: var(--primary-600);
}

.step-circle {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: var(--gray-200);
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  transition: all 0.15s ease;
}

.step.completed .step-circle {
  background: var(--primary-600);
  color: white;
}

.step.active .step-circle {
  background: var(--primary-600);
  color: white;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
}

.step-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-align: center;
}
```

### Empty States

```css
.empty-state {
  text-align: center;
  padding: 3rem 1.5rem;
}

.empty-state-icon {
  width: 4rem;
  height: 4rem;
  margin: 0 auto 1rem;
  color: var(--gray-400);
}

.empty-state-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.empty-state-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  max-width: 28rem;
  margin: 0 auto 1.5rem;
}

.empty-state-action {
  /* Usually contains a primary button */
}
```

---

## Navigation Patterns

### Top Navigation Bar

```css
.navbar {
  height: 4rem;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--gray-200);
  box-shadow: var(--shadow-sm);
}

.navbar-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  max-width: 1280px;
  margin: 0 auto;
}

.navbar-brand {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary-600);
  text-decoration: none;
}

.navbar-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.navbar-link {
  padding: 0.5rem 1rem;
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.15s ease;
}

.navbar-link:hover {
  background: var(--gray-100);
  color: var(--text-primary);
}

.navbar-link.active {
  background: var(--primary-50);
  color: var(--primary-700);
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.navbar-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  object-fit: cover;
}
```

### Sidebar Navigation

```css
.sidebar {
  width: 16rem;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  background: var(--bg-primary);
  border-right: 1px solid var(--gray-200);
  padding: 1.5rem;
  overflow-y: auto;
}

.sidebar-header {
  margin-bottom: 2rem;
}

.sidebar-brand {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary-600);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.sidebar-section {
  margin-top: 1.5rem;
}

.sidebar-section-title {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-tertiary);
  margin-bottom: 0.5rem;
  padding: 0 0.75rem;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.15s ease;
}

.sidebar-link:hover {
  background: var(--gray-100);
  color: var(--text-primary);
}

.sidebar-link.active {
  background: var(--primary-50);
  color: var(--primary-700);
}

.sidebar-link-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.sidebar-link-badge {
  margin-left: auto;
}

/* Layout adjustment for content */
.main-content {
  margin-left: 16rem;
  padding: 2rem;
}
```

### Breadcrumbs

```css
.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.breadcrumb-link {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.15s ease;
}

.breadcrumb-link:hover {
  color: var(--primary-600);
}

.breadcrumb-separator {
  color: var(--text-tertiary);
}

.breadcrumb-current {
  color: var(--text-primary);
  font-weight: 500;
}
```

### Tabs

```css
.tabs {
  border-bottom: 1px solid var(--gray-200);
  margin-bottom: 1.5rem;
}

.tabs-list {
  display: flex;
  gap: 0.5rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.tab {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab:hover {
  color: var(--text-primary);
  border-bottom-color: var(--gray-300);
}

.tab.active {
  color: var(--primary-600);
  border-bottom-color: var(--primary-600);
}

.tab:focus {
  outline: 2px solid var(--primary-500);
  outline-offset: -2px;
}

.tab-panel {
  padding: 1.5rem 0;
}
```

### Dropdown Menu

```css
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-trigger {
  /* Usually a button */
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  min-width: 12rem;
  background: var(--bg-primary);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 0.5rem;
  z-index: 50;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.625rem 0.75rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--text-primary);
  background: transparent;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s ease;
}

.dropdown-item:hover {
  background: var(--gray-100);
}

.dropdown-item.danger {
  color: var(--error-600);
}

.dropdown-item.danger:hover {
  background: var(--error-50);
}

.dropdown-divider {
  height: 1px;
  background: var(--gray-200);
  margin: 0.5rem 0;
}
```

---

## Role-Based UI Patterns

### Role Indicators

Each role has a consistent visual identity throughout the application:

```css
/* Admin - Purple */
.role-admin-bg { background: #f3e8ff; }
.role-admin-text { color: #7e22ce; }
.role-admin-border { border-color: #c084fc; }

/* Organizer - Blue */
.role-organizer-bg { background: var(--primary-50); }
.role-organizer-text { color: var(--primary-700); }
.role-organizer-border { border-color: var(--primary-300); }

/* Mentor - Green */
.role-mentor-bg { background: #d1fae5; }
.role-mentor-text { color: #047857; }
.role-mentor-border { border-color: #6ee7b7; }

/* Mentee - Orange */
.role-mentee-bg { background: #ffedd5; }
.role-mentee-text { color: #c2410c; }
.role-mentee-border { border-color: #fdba74; }
```

### Dashboard Layouts

#### Admin Dashboard
- **Primary Actions**: User management, role assignments
- **Key Metrics**: Total users, active events, feedback submissions
- **Color Accent**: Purple (#a855f7)

```css
.admin-dashboard {
  /* Full-width layout with sidebar */
}

.admin-card {
  border-left: 4px solid #a855f7;
}
```

#### Organizer Dashboard
- **Primary Actions**: Create event, manage forms, view reports
- **Key Metrics**: Events created, feedback received, participation rate
- **Color Accent**: Blue (#3b82f6)

```css
.organizer-dashboard {
  /* Grid layout for events and forms */
}

.event-card {
  border-left: 4px solid var(--primary-600);
}
```

#### Mentor Dashboard
- **Primary Actions**: Submit feedback, view assignments
- **Key Metrics**: Mentees assigned, feedback pending, feedback completed
- **Color Accent**: Green (#10b981)

```css
.mentor-dashboard {
  /* List-based layout with assignments */
}

.assignment-card {
  border-left: 4px solid #10b981;
}
```

#### Mentee Dashboard
- **Primary Actions**: View feedback, track progress
- **Key Metrics**: Feedback received, mentors, events participated
- **Color Accent**: Orange (#f97316)

```css
.mentee-dashboard {
  /* Timeline/card layout for feedback */
}

.feedback-card {
  border-left: 4px solid #f97316;
}
```

### Access Control UI Patterns

Show/hide elements based on user roles:

```tsx
{/* Visual indicator for role-restricted actions */}
<Button
  disabled={!hasRole('organizer')}
  className="btn-primary"
>
  Create Event
  {!hasRole('organizer') && (
    <Tooltip>Only organizers can create events</Tooltip>
  )}
</Button>

{/* Role-based navigation items */}
<nav className="sidebar-nav">
  {hasRole('admin') && (
    <NavLink href="/admin/users" icon={UsersIcon}>
      User Management
    </NavLink>
  )}

  {hasRole('organizer') && (
    <NavLink href="/organizer/events" icon={CalendarIcon}>
      My Events
    </NavLink>
  )}

  {hasRole('mentor') && (
    <NavLink href="/mentor/assignments" icon={UserGroupIcon}>
      My Mentees
    </NavLink>
  )}

  {hasRole('mentee') && (
    <NavLink href="/mentee/feedback" icon={DocumentTextIcon}>
      My Feedback
    </NavLink>
  )}
</nav>
```

---

## Accessibility Guidelines

### WCAG 2.1 AA Compliance

#### Color Contrast
- **Normal Text**: Minimum 4.5:1 contrast ratio
- **Large Text**: Minimum 3:1 contrast ratio (18pt+ or 14pt+ bold)
- **UI Components**: Minimum 3:1 contrast ratio for interactive elements

**Testing**: Use Chrome DevTools or axe DevTools to verify contrast ratios.

#### Keyboard Navigation
All interactive elements must be keyboard accessible:

```css
/* Focus visible styles */
*:focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}

/* Skip to main content link */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--primary-600);
  color: white;
  padding: 0.5rem 1rem;
  z-index: 100;
  text-decoration: none;
}

.skip-link:focus {
  top: 0;
}
```

**Tab Order**: Ensure logical tab order follows visual layout.

#### Screen Reader Support

```html
<!-- Use semantic HTML -->
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/dashboard">Dashboard</a></li>
  </ul>
</nav>

<!-- Label all form inputs -->
<label for="email">Email Address</label>
<input
  id="email"
  type="email"
  aria-required="true"
  aria-describedby="email-help"
/>
<span id="email-help">We'll never share your email.</span>

<!-- Use ARIA roles appropriately -->
<div role="alert" aria-live="polite">
  Form submitted successfully
</div>

<!-- Describe icon-only buttons -->
<button aria-label="Close dialog">
  <CloseIcon />
</button>

<!-- Use ARIA states -->
<button aria-expanded="false" aria-controls="menu">
  Menu
</button>
<div id="menu" hidden>
  <!-- Menu content -->
</div>
```

#### Alternative Text

```html
<!-- Informative images -->
<img
  src="/user-avatar.jpg"
  alt="Profile photo of Jane Doe"
/>

<!-- Decorative images -->
<img
  src="/decorative-pattern.svg"
  alt=""
  aria-hidden="true"
/>

<!-- Icons with text -->
<button>
  <CheckIcon aria-hidden="true" />
  <span>Submit</span>
</button>

<!-- Icon-only buttons -->
<button aria-label="Delete item">
  <TrashIcon />
</button>
```

#### Loading States

```html
<!-- Loading indicator -->
<div role="status" aria-live="polite">
  <Spinner />
  <span className="sr-only">Loading...</span>
</div>

<!-- Screen reader only class */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

---

## Responsive Design

### Breakpoints

```css
/* Mobile-first approach */
/* xs: 0-639px (default, no media query) */

/* sm: Small devices (tablets) */
@media (min-width: 640px) { }

/* md: Medium devices (landscape tablets) */
@media (min-width: 768px) { }

/* lg: Large devices (laptops) */
@media (min-width: 1024px) { }

/* xl: Extra large devices (desktops) */
@media (min-width: 1280px) { }

/* 2xl: 2X large devices (large desktops) */
@media (min-width: 1536px) { }
```

### Responsive Patterns

#### Container Query

```css
.container {
  width: 100%;
  padding: 0 1rem;
}

@media (min-width: 640px) {
  .container {
    max-width: 640px;
    padding: 0 1.5rem;
  }
}

@media (min-width: 768px) {
  .container {
    max-width: 768px;
  }
}

@media (min-width: 1024px) {
  .container {
    max-width: 1024px;
    padding: 0 2rem;
  }
}

@media (min-width: 1280px) {
  .container {
    max-width: 1280px;
  }
}
```

#### Responsive Grid

```css
.grid-responsive {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: 1fr; /* Mobile: 1 column */
}

@media (min-width: 640px) {
  .grid-responsive {
    grid-template-columns: repeat(2, 1fr); /* Tablet: 2 columns */
  }
}

@media (min-width: 1024px) {
  .grid-responsive {
    grid-template-columns: repeat(3, 1fr); /* Desktop: 3 columns */
  }
}
```

#### Responsive Typography

```css
h1 {
  font-size: 1.875rem; /* 30px mobile */
}

@media (min-width: 768px) {
  h1 {
    font-size: 2.25rem; /* 36px tablet */
  }
}

@media (min-width: 1024px) {
  h1 {
    font-size: 3rem; /* 48px desktop */
  }
}
```

#### Mobile Navigation

```css
/* Hamburger menu for mobile */
@media (max-width: 767px) {
  .navbar-nav {
    position: fixed;
    top: 4rem;
    left: 0;
    right: 0;
    background: var(--bg-primary);
    border-bottom: 1px solid var(--gray-200);
    padding: 1rem;
    flex-direction: column;
    display: none;
  }

  .navbar-nav.open {
    display: flex;
  }

  .mobile-menu-button {
    display: block;
  }
}

@media (min-width: 768px) {
  .mobile-menu-button {
    display: none;
  }
}
```

#### Responsive Sidebar

```css
/* Hide sidebar on mobile, show toggle button */
@media (max-width: 1023px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .main-content {
    margin-left: 0;
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: var(--bg-overlay);
    z-index: 40;
  }
}

@media (min-width: 1024px) {
  .sidebar {
    transform: translateX(0);
  }

  .sidebar-toggle {
    display: none;
  }
}
```

### Touch Targets

Ensure minimum touch target size of 44×44px for mobile:

```css
@media (max-width: 767px) {
  button,
  a,
  input,
  select {
    min-height: 44px;
    min-width: 44px;
  }
}
```

---

## Animation & Transitions

### Transition Duration

```css
--duration-fast: 0.1s;
--duration-normal: 0.15s;
--duration-slow: 0.3s;
--duration-slower: 0.5s;
```

### Easing Functions

```css
--ease-linear: linear;
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

### Common Transitions

```css
/* Hover transitions */
.transition-colors {
  transition: background-color 0.15s ease, color 0.15s ease;
}

.transition-shadow {
  transition: box-shadow 0.15s ease;
}

.transition-transform {
  transition: transform 0.15s ease;
}

/* Scale on hover */
.hover-scale:hover {
  transform: scale(1.05);
}

/* Lift on hover */
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}
```

### Animations

```css
/* Fade in */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.fade-in {
  animation: fadeIn 0.3s ease;
}

/* Slide in from right */
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.slide-in-right {
  animation: slideInRight 0.3s ease;
}

/* Pulse */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Skeleton loading */
@keyframes shimmer {
  0% {
    background-position: -468px 0;
  }
  100% {
    background-position: 468px 0;
  }
}

.skeleton {
  background: linear-gradient(
    to right,
    var(--gray-200) 0%,
    var(--gray-100) 20%,
    var(--gray-200) 40%,
    var(--gray-200) 100%
  );
  background-size: 800px 104px;
  animation: shimmer 1.5s linear infinite;
}
```

### Motion Preferences

Respect user preferences for reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Performance Guidelines

**Do's:**
- Use `transform` and `opacity` for animations (GPU-accelerated)
- Keep animations under 0.5s for UI interactions
- Use `will-change` sparingly for performance-critical animations
- Test animations on low-end devices

**Don'ts:**
- Don't animate `width`, `height`, or `top/left` (causes layout reflow)
- Don't use excessive shadows or blur effects in animations
- Don't animate more than a few elements simultaneously
- Don't forget to handle `prefers-reduced-motion`

---

## Implementation Checklist

### Setting Up the Design System

- [ ] Install and configure TailwindCSS
- [ ] Set up CSS custom properties for colors, spacing, and typography
- [ ] Create base component library (Button, Input, Card, etc.)
- [ ] Implement responsive layout system
- [ ] Set up icon library (Heroicons or similar)
- [ ] Configure font loading (Inter from Google Fonts)

### Accessibility

- [ ] Test all components with keyboard navigation
- [ ] Verify color contrast ratios meet WCAG 2.1 AA
- [ ] Add ARIA labels and roles where appropriate
- [ ] Test with screen reader (NVDA, JAWS, or VoiceOver)
- [ ] Implement focus management for modals and dialogs
- [ ] Add skip navigation links

### Responsive Design

- [ ] Test on mobile devices (320px - 767px)
- [ ] Test on tablets (768px - 1023px)
- [ ] Test on desktops (1024px+)
- [ ] Verify touch targets are at least 44×44px on mobile
- [ ] Test with browser zoom at 200%

### Performance

- [ ] Optimize images (use Next.js Image component)
- [ ] Lazy load non-critical components
- [ ] Minimize animation overhead
- [ ] Use CSS containment where appropriate
- [ ] Monitor Core Web Vitals (LCP, FID, CLS)

---

## AI Prompt Template

When using this guide to instruct AI in building similar applications:

```
Create a [component/page] for a web application following these design specifications:

**Technology Stack**: Next.js, TypeScript, TailwindCSS

**Design System**:
- Primary color: Blue (#3b82f6)
- Font family: Inter
- Spacing: 8px base unit
- Border radius: 8px default
- Shadows: Subtle elevation system

**Component Requirements**:
- [Specific component details]
- Must be keyboard accessible (WCAG 2.1 AA)
- Responsive (mobile-first)
- Use semantic HTML

**Role Context**: [Admin/Organizer/Mentor/Mentee]
- Role-specific accent color: [Color from role palette]

**Additional Constraints**:
- [Any specific requirements]

Reference the UI Style Guide in /docs/UI_STYLE_GUIDE.md for detailed specifications.
```

---

## Version History

- **v1.0** (2025-11-07): Initial style guide creation

---

## Credits & Resources

**Fonts**:
- Inter: https://fonts.google.com/specimen/Inter
- JetBrains Mono: https://www.jetbrains.com/lp/mono/

**Icon Libraries**:
- Heroicons: https://heroicons.com/
- Lucide Icons: https://lucide.dev/

**Color Tools**:
- Coolors: https://coolors.co/
- Contrast Checker: https://webaim.org/resources/contrastchecker/

**Accessibility**:
- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
- axe DevTools: https://www.deque.com/axe/devtools/

**Design Inspiration**:
- Tailwind UI: https://tailwindui.com/
- Shadcn UI: https://ui.shadcn.com/
