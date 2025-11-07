# Quick Start Guide - Modern Frontend

**For**: Flask AI Insights Application
**Updated**: 2025-01-06

---

## Getting Started

### First Time Setup

```bash
# Install Node.js dependencies
npm install

# Verify TypeScript compilation
npm run type-check

# Build production assets
npm run build
```

---

## Development

### Running the Dev Environment

**Terminal 1** - Frontend Dev Server (with HMR):
```bash
npm run dev
```
- Runs on http://localhost:3000
- Hot Module Replacement enabled
- Auto-recompiles on file changes

**Terminal 2** - Flask Backend:
```bash
python app.py
```
- Runs on http://localhost:5001
- Serves API and templates
- Proxied by Vite for CORS

### Making Changes

**TypeScript Files** (`static/src/ts/**/*.ts`):
- Edit any TypeScript file
- Vite automatically recompiles
- Browser refreshes instantly (HMR)
- Check console for type errors

**CSS Files** (`static/src/css/**/*.css`):
- Edit any CSS file
- Vite automatically rebuilds
- Changes apply without refresh

**Templates** (`templates/**/*.html`):
- Edit template files
- Manual browser refresh needed
- Consider adding data-page attribute

---

## File Organization

### Where to Put Code

**Core Utilities** → `static/src/ts/core/`
- API calls → `api.ts`
- Authentication → `auth.ts`
- Shared utilities → `utils.ts`
- Type definitions → `types.ts`

**Reusable Components** → `static/src/ts/components/`
- FlashMessages.ts
- LoadingStates.ts
- FormValidation.ts
- SocialInteractions.ts

**Page-Specific Features** → `static/src/ts/features/`
- community.ts (Community page)
- insights.ts (Insights display)
- dashboard.ts (Dashboard)
- insightsForm.ts (Insights generation form)

**Styles** → `static/src/css/`
- Base → `base/` (variables, reset, typography)
- Components → `components/` (buttons, cards, forms)
- Pages → `pages/` (home, community, insights)

---

## Common Tasks

### Adding a New Feature Module

1. **Create the file**:
   ```bash
   touch static/src/ts/features/myFeature.ts
   ```

2. **Write the module**:
   ```typescript
   // static/src/ts/features/myFeature.ts
   export function initializeMyFeature(): void {
     console.log('[MyFeature] Initializing...');

     // Your code here

     console.log('[MyFeature] Initialized');
   }
   ```

3. **Import in main.ts**:
   ```typescript
   import { initializeMyFeature } from './features/myFeature';

   // In initializeApp():
   case 'my-page':
     initializeMyFeature();
     break;
   ```

4. **Add data-page to template**:
   ```html
   <body data-page="my-page">
   ```

### Adding a New Component

1. **Create the component**:
   ```typescript
   // static/src/ts/components/MyComponent.ts
   export class MyComponent {
     constructor(selector: string) {
       const element = document.querySelector(selector);
       // Initialize component
     }

     public doSomething(): void {
       // Component method
     }
   }
   ```

2. **Use in feature**:
   ```typescript
   import { MyComponent } from '../components/MyComponent';

   const component = new MyComponent('#my-element');
   component.doSomething();
   ```

### Making API Calls

```typescript
import { API } from '../core/api';
import type { MyDataType } from '../core/types';

// GET request
const data = await API.get<MyDataType>('/api/endpoint');

// POST request
const result = await API.post<ResponseType>('/api/endpoint', {
  key: 'value',
});

// Error handling
try {
  const data = await API.get('/api/endpoint');
} catch (error) {
  if (error instanceof APIException) {
    showFlashMessage(error.message, 'error');
  }
}
```

### Showing Flash Messages

```typescript
import { showFlashMessage } from '../core/utils';

// Success message
showFlashMessage('Operation successful!', 'success');

// Error message
showFlashMessage('Something went wrong', 'error');

// With custom duration
showFlashMessage('Quick message', 'info', 2000);
```

### Managing Loading States

```typescript
import { showLoading, hideLoading } from '../core/utils';

const button = document.querySelector('#submit-btn') as HTMLButtonElement;

// Show loading
showLoading(button, 'Processing...');

// Perform async operation
await someAsyncOperation();

// Hide loading
hideLoading(button);
```

---

## Type Definitions

### Adding New Types

Add to `static/src/ts/core/types.ts`:

```typescript
export interface MyNewType {
  id: string;
  name: string;
  createdAt: string;
}

export type MyStatus = 'pending' | 'active' | 'completed';
```

### Using Types

```typescript
import type { MyNewType } from '../core/types';

function processData(data: MyNewType): void {
  console.log(data.name);
}
```

---

## Building for Production

### Build Command

```bash
npm run build
```

**Output**:
- `static/dist/js/main.[hash].js` - JavaScript bundle
- `static/dist/css/styles.[hash].css` - CSS bundle
- `static/dist/.vite/manifest.json` - Asset manifest

### Build Verification

```bash
# Check output
ls -lh static/dist/

# Verify type checking
npm run type-check

# Check bundle sizes
du -sh static/dist/*
```

### Updating Templates for Production

Replace inline scripts with:

```html
<!-- In base template -->
<link rel="stylesheet" href="{{ url_for('static', filename='dist/css/styles.[hash].css') }}">
<script type="module" src="{{ url_for('static', filename='dist/js/main.[hash].js') }}"></script>
```

**Note**: Replace `[hash]` with actual hash from build output.

---

## Debugging

### TypeScript Errors

```bash
# Check for type errors
npm run type-check

# Common issues:
# - Missing type definitions
# - Incorrect type annotations
# - Missing imports
```

### Build Errors

```bash
# Clean build
rm -rf static/dist
npm run build

# Check for:
# - Missing CSS files
# - Import errors
# - Vite configuration issues
```

### Runtime Errors

1. **Check browser console** for JavaScript errors
2. **Check network tab** for failed requests
3. **Verify data-page attribute** matches route cases
4. **Check feature initialization** logs

### Hot Module Replacement Issues

```bash
# Restart dev server
# Ctrl+C to stop
npm run dev
```

---

## Code Style

### TypeScript Best Practices

```typescript
// Use explicit types for function parameters
function myFunction(param: string): void {
  // ...
}

// Use type imports
import type { MyType } from './types';

// Use async/await over promises
async function fetchData(): Promise<Data> {
  return await API.get('/api/data');
}

// Handle errors
try {
  await operation();
} catch (error) {
  console.error('Operation failed:', error);
}
```

### CSS Best Practices

```css
/* Use CSS custom properties */
.my-component {
  color: var(--color-primary);
  padding: var(--spacing-md);
}

/* Use BEM naming */
.component { }
.component__element { }
.component--modifier { }

/* Keep specificity low */
/* Good */
.card-title { }

/* Bad */
div.container .row .col .card .card-header .card-title { }
```

---

## Common Patterns

### Form Handling

```typescript
import { FormValidation } from '../components/FormValidation';

const validation = new FormValidation('#my-form');

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  if (!validation.validate()) {
    return;
  }

  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  await API.post('/api/submit', data);
});
```

### Event Delegation

```typescript
// Instead of individual listeners
document.addEventListener('click', (e) => {
  const target = e.target as HTMLElement;

  if (target.matches('.my-button')) {
    handleButtonClick(target);
  }
});
```

### Debouncing User Input

```typescript
import { debounce } from '../core/utils';

const handleInput = debounce((value: string) => {
  // Handle input
}, 300);

input.addEventListener('input', (e) => {
  handleInput((e.target as HTMLInputElement).value);
});
```

---

## Testing (Future)

### Unit Tests (Planned)

```bash
# When Jest/Vitest is set up
npm test
npm run test:watch
npm run test:coverage
```

### E2E Tests (Existing - Playwright)

```bash
# Run E2E tests
npx playwright test

# Run specific test
npx playwright test community.spec.ts
```

---

## Troubleshooting

### "Module not found"

- Check import path is correct
- Verify file exists
- Check for typos in filename
- Ensure proper file extension (.ts)

### "Type 'X' is not assignable to type 'Y'"

- Check type definitions in types.ts
- Verify API response structure
- Add type assertion if needed: `data as MyType`

### "Cannot find name 'X'"

- Add import statement
- Check if exported from module
- Verify global types are defined

### Changes Not Reflecting

1. Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)
2. Check if dev server is running
3. Check console for errors
4. Restart dev server
5. Clear browser cache

---

## Performance Tips

### Bundle Size

- Import only what you need
- Use dynamic imports for large modules
- Check bundle size after major changes
- Target: < 500 KB total

### Type Checking

- Use `--watch` mode during development
- Fix type errors early
- Don't use `any` type (use `unknown` instead)

### Build Speed

- Avoid circular dependencies
- Keep imports organized
- Use path aliases from vite.config.js

---

## Resources

### Documentation

- Vite: https://vitejs.dev/
- TypeScript: https://www.typescriptlang.org/
- Bootstrap: https://getbootstrap.com/

### Project Files

- `REFACTORING_SUMMARY.md` - Complete project overview
- `REFACTORING_PROGRESS.md` - Detailed progress report
- `package.json` - Dependencies and scripts
- `tsconfig.json` - TypeScript configuration
- `vite.config.js` - Build configuration

---

## Getting Help

### Check These First

1. **Console errors** in browser DevTools
2. **TypeScript errors** via `npm run type-check`
3. **Build errors** from `npm run build`
4. **Documentation** in REFACTORING_SUMMARY.md

### Common Issues

- Port 3000 already in use → Change port in vite.config.js
- TypeScript errors → Check types.ts and imports
- HMR not working → Restart dev server
- Build failing → Check for missing CSS files

---

**Quick Reference Card**:
- Dev: `npm run dev` (port 3000)
- Build: `npm run build`
- Type Check: `npm run type-check`
- Flask: `python app.py` (port 5001)

**File Locations**:
- TypeScript: `static/src/ts/`
- CSS: `static/src/css/`
- Build Output: `static/dist/`
- Templates: `templates/`

**Need More Info?** See `REFACTORING_SUMMARY.md`
