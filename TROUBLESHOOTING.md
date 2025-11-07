# Troubleshooting Guide

## Common Issues and Solutions

### 431 Request Header Fields Too Large

**Problem**: Vite dev server shows "431 Request Header Fields Too Large" error.

**Cause**: Large cookies (often from Firebase authentication or session data) exceed the default Node.js header size limit (8KB).

**Solutions**:

#### Solution 1: Clear Browser Cookies (Recommended)
1. Open browser DevTools (F12)
2. Go to Application > Cookies
3. Delete cookies for `localhost:3000` and `localhost:5001`
4. Refresh the page
5. Restart Vite dev server: `npm run dev`

#### Solution 2: Use Updated npm Script (Already Done)
The `package.json` has been updated with increased header size:
```bash
npm run dev
```

This runs with `NODE_OPTIONS='--max-http-header-size=16384'`

#### Solution 3: Manually Set Node Options
```bash
# Mac/Linux
export NODE_OPTIONS='--max-http-header-size=16384'
npm run dev

# Windows (PowerShell)
$env:NODE_OPTIONS='--max-http-header-size=16384'
npm run dev

# Windows (CMD)
set NODE_OPTIONS=--max-http-header-size=16384
npm run dev
```

#### Solution 4: Use Incognito/Private Mode
Open `http://localhost:3000` in incognito/private browsing mode (no cookies).

#### Solution 5: Bypass Vite Dev Server
If the issue persists, you can skip the Vite dev server and use Flask directly:

1. Build assets: `npm run build`
2. Update templates to load from `static/dist/`
3. Run only Flask: `python app.py`
4. Access at `http://localhost:5001`

### Firebase Session Issues

**Problem**: Firebase creates large session tokens that exceed header limits.

**Solution**: Configure Firebase to use shorter-lived tokens or clear old sessions:

```javascript
// In your Firebase config
firebase.auth().setPersistence(firebase.auth.Auth.Persistence.SESSION);
```

### Port Already in Use

**Problem**: `Error: listen EADDRINUSE: address already in use :::3000`

**Solutions**:

#### Kill Process on Port 3000
```bash
# Mac/Linux
lsof -ti:3000 | xargs kill -9

# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

#### Use Different Port
Edit `vite.config.js`:
```javascript
server: {
  port: 3001, // Change to any available port
}
```

### Module Not Found Errors

**Problem**: `Error: Cannot find module 'X'`

**Solutions**:

1. **Reinstall dependencies**:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Check import paths** (case-sensitive):
   ```typescript
   // Correct
   import { API } from '../core/api';

   // Wrong (case mismatch)
   import { API } from '../core/API';
   ```

3. **Verify file exists**:
   ```bash
   ls static/src/ts/core/api.ts
   ```

### TypeScript Compilation Errors

**Problem**: Type errors when running `npm run type-check`

**Solutions**:

1. **Check for missing types**:
   ```bash
   npm install --save-dev @types/node
   ```

2. **Review error messages** and fix type annotations

3. **Use type assertions** when necessary:
   ```typescript
   const element = document.querySelector('.button') as HTMLButtonElement;
   ```

4. **Check tsconfig.json** for strict settings

### Build Failures

**Problem**: `npm run build` fails

**Solutions**:

1. **Clean dist folder**:
   ```bash
   rm -rf static/dist
   npm run build
   ```

2. **Check for empty CSS files** (warnings are OK, errors are not):
   - Ensure all imported CSS files exist
   - Add placeholder content if needed

3. **Verify imports**:
   - Check all import statements
   - Ensure no circular dependencies

### Hot Module Replacement Not Working

**Problem**: Changes don't reflect in browser

**Solutions**:

1. **Hard refresh**: Cmd/Ctrl + Shift + R
2. **Restart dev server**: Stop (Ctrl+C) and run `npm run dev` again
3. **Clear browser cache**
4. **Check console** for errors
5. **Verify file is saved**

### Flask API Not Responding

**Problem**: API calls fail with CORS or connection errors

**Solutions**:

1. **Verify Flask is running**:
   ```bash
   curl http://localhost:5001/status
   ```

2. **Check proxy configuration** in `vite.config.js`

3. **Ensure ports match**:
   - Vite: 3000
   - Flask: 5001

4. **Check Flask logs** for errors

### CSS Not Loading

**Problem**: Styles not applied to pages

**Solutions**:

1. **Verify build output**:
   ```bash
   ls static/dist/css/
   ```

2. **Check template** has correct link:
   ```html
   <link rel="stylesheet" href="{{ url_for('static', filename='dist/css/styles.[hash].css') }}">
   ```

3. **Rebuild assets**:
   ```bash
   npm run build
   ```

### Large Bundle Size

**Problem**: JavaScript bundle > 500 KB

**Solutions**:

1. **Check what's included**:
   ```bash
   npm run build -- --mode production
   ```

2. **Use dynamic imports** for large modules:
   ```typescript
   // Instead of:
   import { HugeLibrary } from 'huge-library';

   // Use:
   const { HugeLibrary } = await import('huge-library');
   ```

3. **Remove unused imports**

4. **Check for duplicate dependencies**

### Development Server Slow

**Problem**: Vite dev server is slow to start or respond

**Solutions**:

1. **Clear Vite cache**:
   ```bash
   rm -rf node_modules/.vite
   npm run dev
   ```

2. **Reduce file watchers**:
   - Close unnecessary editors
   - Exclude `node_modules` from IDE indexing

3. **Check system resources** (RAM, CPU)

### Firebase Authentication Issues

**Problem**: Firebase auth not working with dev server

**Solutions**:

1. **Add localhost:3000 to Firebase authorized domains**:
   - Go to Firebase Console
   - Authentication > Settings > Authorized domains
   - Add `localhost:3000`

2. **Check CORS configuration** in Flask

3. **Verify Firebase config** in templates

## Environment-Specific Issues

### macOS

**Large cookies**: macOS Safari may create larger cookies. Use Chrome/Firefox for development.

### Windows

**Path issues**: Use forward slashes in import paths:
```typescript
// Good
import { API } from '../core/api';

// Bad (may fail on Windows)
import { API } from '..\\core\\api';
```

**Node.js version**: Ensure Node.js 18+ is installed:
```bash
node --version  # Should be >= 18.0.0
```

### Linux

**Permission issues**: Ensure Node.js can write to `static/dist/`:
```bash
chmod -R 755 static/dist/
```

## Getting More Help

### Check These First

1. **Browser console** (F12 > Console)
2. **Terminal output** from Vite and Flask
3. **Network tab** (F12 > Network)
4. **Vite error overlay** (appears automatically)

### Logs to Collect

When reporting issues, include:

```bash
# Node and npm versions
node --version
npm --version

# Package versions
npm list vite typescript

# Build output
npm run build

# Type check output
npm run type-check
```

### Clean Slate Reset

If all else fails, reset everything:

```bash
# 1. Clean Node.js
rm -rf node_modules package-lock.json
npm install

# 2. Clean build artifacts
rm -rf static/dist

# 3. Clear browser data
# - Clear cache
# - Clear cookies for localhost

# 4. Rebuild
npm run build

# 5. Restart dev servers
npm run dev  # Terminal 1
python app.py  # Terminal 2
```

## Performance Optimization

### Slow Build Times

1. **Use Vite's `--mode` flag**:
   ```bash
   npm run build -- --mode production
   ```

2. **Disable source maps** in production (edit `vite.config.js`):
   ```javascript
   build: {
     sourcemap: false, // Disable for faster builds
   }
   ```

### Memory Issues

**Increase Node.js memory**:
```bash
NODE_OPTIONS='--max-old-space-size=4096' npm run dev
```

## Best Practices to Avoid Issues

1. **Keep dependencies updated**:
   ```bash
   npm outdated
   npm update
   ```

2. **Use `.env` files** for environment-specific config

3. **Clear cookies regularly** during development

4. **Use incognito mode** for testing

5. **Keep browser DevTools open** to catch errors early

6. **Test in production mode** before deploying:
   ```bash
   npm run build
   npm run preview
   ```

---

**Quick Fixes Checklist**:
- [ ] Clear browser cookies
- [ ] Hard refresh (Cmd/Ctrl + Shift + R)
- [ ] Restart Vite dev server
- [ ] Check browser console for errors
- [ ] Verify Flask is running
- [ ] Check terminal for error messages
- [ ] Try incognito mode
- [ ] Rebuild: `npm run build`

**Still stuck?** Check the detailed logs and error messages above.
