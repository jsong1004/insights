# PDF Export Setup Guide

## ✅ WeasyPrint is Now Configured!

I've set up WeasyPrint to work with your Flask app. Here's what was done and how to use it.

---

## 🚀 How to Run Flask with PDF Support

### Option 1: Use the Run Script (Recommended)

```bash
./run_flask.sh
```

This script automatically sets the library paths and starts Flask.

### Option 2: Manual Command

```bash
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib"
python app.py
```

### Option 3: Add to Your Shell Profile (Permanent)

Add these lines to your `~/.zshrc` (or `~/.bash_profile` if using bash):

```bash
# WeasyPrint library paths for macOS
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib"
```

Then reload your shell:
```bash
source ~/.zshrc
```

After this, you can just run `python app.py` normally.

---

## 📋 What Was Installed

### System Libraries (via Homebrew)
- ✅ **pango** - Text rendering library
- ✅ **gdk-pixbuf** - Image loading library
- ✅ **libffi** - Foreign function interface
- ✅ **glib** - Core library (includes gobject)

All installed at: `/opt/homebrew/lib/`

### Python Package
- ✅ **WeasyPrint 62.3** - PDF generation library

---

## 🧪 Test PDF Export

### Quick Test

```bash
# Start Flask with the script
./run_flask.sh

# Or manually
export DYLD_LIBRARY_PATH="/opt/homebrew/lib"
python app.py

# Visit an insight and click "Download PDF"
```

### Python Test

```python
# Test WeasyPrint directly
export DYLD_LIBRARY_PATH="/opt/homebrew/lib"
python -c "import weasyprint; print('WeasyPrint version:', weasyprint.__version__)"
```

---

## 🔧 Files Created

1. **`run_flask.sh`** - Startup script with library paths
   ```bash
   #!/bin/bash
   export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
   export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib"
   python app.py
   ```

2. **`.env.local`** - Environment variables (for reference)
   ```
   DYLD_LIBRARY_PATH=/opt/homebrew/lib
   DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
   ```

---

## 🐛 Troubleshooting

### Error: "cannot load library 'gobject-2.0-0'"

**Cause**: Library path not set correctly.

**Solution**: Use the run script or set environment variables:
```bash
./run_flask.sh
```

### Error: "Library not found"

**Verify libraries are installed**:
```bash
ls -la /opt/homebrew/lib/libgobject*
ls -la /opt/homebrew/lib/libpango*
```

**Reinstall if needed**:
```bash
brew reinstall pango gdk-pixbuf libffi glib
```

### PDF Export Still Failing

**Check WeasyPrint works**:
```bash
export DYLD_LIBRARY_PATH="/opt/homebrew/lib"
python -c "import weasyprint; print('OK')"
```

**Check Flask logs** for specific error messages.

**Verify route is working** (check `routes/main.py`):
```python
@main.route('/download/<insight_id>')
def download_report(insight_id):
    # Should have WeasyPrint import
```

---

## 📊 How PDF Export Works

### In Your App

1. User clicks "Download PDF" button
2. Request goes to `/download/<insight_id>?format=pdf`
3. Flask route checks if WeasyPrint is available
4. If available: Generates PDF using `weasyprint.HTML(...).write_pdf()`
5. If not available: Falls back to HTML download

### Current Status

- ✅ WeasyPrint Python package installed
- ✅ System libraries installed (pango, gdk-pixbuf, etc.)
- ✅ Library paths configured
- ✅ Run script created for easy startup
- ✅ PDF export should work when using `./run_flask.sh`

---

## 🎯 Quick Start

**To enable PDF exports**:

```bash
# Stop current Flask if running (Ctrl+C)

# Start with the run script
./run_flask.sh

# Visit your app
http://localhost:5001/

# Test PDF download on any insight
```

---

## 🔄 Alternative: Use Docker

If you want a cleaner setup, you can use Docker (already configured in your project):

```bash
# Build Docker image
docker build --platform linux/amd64 -f Dockerfile.insight -t ai-insights-app .

# Run container
docker run -p 5001:5001 ai-insights-app
```

Docker already has all WeasyPrint dependencies bundled.

---

## 📝 Summary

**Problem**: WeasyPrint needs system libraries that aren't in Python's default search path on macOS.

**Solution**: Set `DYLD_LIBRARY_PATH` to point to Homebrew's library directory.

**Easiest Method**: Use `./run_flask.sh` to start Flask with correct paths.

**Permanent Solution**: Add environment variables to your shell profile.

---

## ✅ Verification Checklist

- [x] Homebrew installed
- [x] System libraries installed (pango, gdk-pixbuf, libffi)
- [x] WeasyPrint Python package installed
- [x] Library paths configured
- [x] Run script created and executable
- [x] WeasyPrint verified working with test command

**Status**: ✅ **Ready to use! Run `./run_flask.sh` to start Flask with PDF support.**

---

## 🆘 Need Help?

If PDF export still doesn't work:

1. Check Flask logs for error messages
2. Verify libraries: `ls /opt/homebrew/lib/libgobject*`
3. Test WeasyPrint: `export DYLD_LIBRARY_PATH="/opt/homebrew/lib" && python -c "import weasyprint"`
4. Check this file: `routes/main.py` for WeasyPrint import errors
5. See `TROUBLESHOOTING.md` for more solutions

---

**Quick Commands**:

```bash
# Start Flask with PDF support
./run_flask.sh

# Test WeasyPrint
export DYLD_LIBRARY_PATH="/opt/homebrew/lib"
python -c "import weasyprint; print('OK')"

# Check installed libraries
ls /opt/homebrew/lib/libgobject*
ls /opt/homebrew/lib/libpango*
```
