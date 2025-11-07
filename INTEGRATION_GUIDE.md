# TypeScript-Flask Integration Guide

## Overview

This document describes the complete TypeScript-Flask integration for the AI Insights application, including the modern build system, social features, and admin functionality.

**Integration Status:** ✅ Complete (v2.0.0)

## Quick Links

- [Development Setup](#development-setup)
- [Build System](#build-system)
- [Social Features](#social-features)
- [Admin Features](#admin-features)
- [Testing](#testing)

---

## Architecture

### Technology Stack

**Backend:**
- Flask 3.1.1, Python 3.11+
- Firebase Admin SDK
- Google Firestore

**Frontend:**
- TypeScript 5.3.3
- Vite 5.0.10 (Build system)
- Bootstrap 5.3
- Modern ES2020+

**Key Features:**
- Hot Module Replacement (HMR) in development
- Asset hashing and minification
- Type-safe API client
- Admin role system
- Social features (likes, sharing, pinning)

---

## Development Setup

### Installation

```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install

# Environment
cp environment-template.txt .env
```

### Running Development Servers

**Terminal 1 - Frontend (Vite):**
```bash
npm run dev
# Runs on http://localhost:3000
# Hot reload enabled
```

**Terminal 2 - Backend (Flask):**
```bash
python app.py
# Runs on http://localhost:5001
# API endpoints available
```

---

## Build System

### Commands

```bash
# Production build
npm run build

# Type checking
npm run type-check

# Watch mode
npm run watch
```

### Build Output

```
static/dist/
├── js/main.[hash].js      # 16.11 KB (5.44 KB gzipped)
├── css/styles.[hash].css  #  3.94 KB (1.40 KB gzipped)
└── .vite/manifest.json    # Asset mapping
```

### Asset Loading

**Template Usage:**
```html
<!-- base.html -->
<link rel="stylesheet" href="{{ url_for('static', filename=get_vite_asset('css/main.css')) }}">
<script type="module" src="{{ url_for('static', filename=get_vite_asset('ts/main.ts')) }}"></script>
```

---

## Backend Integration

### Enhanced Data Models

**GeneratedInsights (core/crew_ai.py):**

Added 9 new fields:
- `is_pinned`, `pinned_by`, `pinned_at` (Admin features)
- `view_count`, `featured`, `category`, `language` (Metadata)
- `quality_score`, `engagement_score` (Quality metrics)

### New Backend Methods

**core/insights_manager.py:**
```python
get_community_insights(sort_by, page, per_page)
search_community_insights(query, sort_by, page, per_page)
update_pin_status(insight_id, is_pinned, admin_user_id)
get_community_stats()
get_trending_topics(limit)
```

**auth/firestore_manager.py:**
```python
set_admin_status(user_id, is_admin, admin_email)
is_user_admin(user_id)
get_admin_users()
```

### New API Endpoints

```python
POST   /api/insights/<id>/pin        # Admin pin/unpin
GET    /api/community-stats          # Statistics
GET    /api/trending-topics?limit=10 # Trending topics
```

---

## Frontend Integration

### TypeScript Modules

**Core Modules:**
1. **auth.ts** - Authentication, admin checking, logout
2. **api.ts** - Typed API client with `InsightsAPI` object
3. **utils.ts** - Flash messages, loading states
4. **types.ts** - TypeScript interfaces

**Components:**
- **SocialInteractions.ts** - Like, share, pin functionality

**Features:**
- **community.ts** - Search, stats, admin features

### Type Definitions

```typescript
// types.ts
export interface GeneratedInsights {
  // ... existing fields
  is_pinned?: boolean;
  pinned_by?: string;
  view_count?: number;
  quality_score?: number;
}

export interface PinResponse {
  success: boolean;
  is_pinned: boolean;
  message: string;
}
```

### API Client Usage

```typescript
// TypeScript
import { InsightsAPI } from '@ts/core/api';

// Pin an insight
const response = await InsightsAPI.pinInsight(insightId, true);

// Get community stats
const stats = await InsightsAPI.getCommunityStats();
```

---

## Social Features

### Like System

**Features:**
- One like per user
- Real-time count updates
- Atomic Firestore operations
- Accessible (ARIA labels)

**Usage:**
```html
<button class="like-button" data-insight-id="{{ insight.id }}">
  <i class="fas fa-heart"></i>
  <span class="like-count">{{ insight.likes }}</span>
</button>
```

### Sharing Controls

**Author-Only:**
```html
<input class="share-toggle" 
       type="checkbox" 
       data-insight-id="{{ insight.id }}"
       {{ 'checked' if insight.is_shared else '' }}>
```

### Community Page

**Features:**
- Search by topic/content
- Sort: Recent, Trending, Most Liked, Featured
- Pagination (12 per page)
- Expandable details
- Real-time statistics

---

## Admin Features

### Admin Role Management

**Set Admin:**
```python
from auth.firestore_manager import UserFirestoreManager

mgr = UserFirestoreManager()
mgr.set_admin_status(
    user_id='abc123',
    is_admin=True,
    admin_email='admin@example.com'
)
```

**Check Admin:**
```python
# Backend
is_admin = firestore_manager.is_user_admin(user_id)
```

```typescript
// Frontend
import { isAdmin } from '@ts/core/auth';

if (isAdmin()) {
  // Show admin controls
}
```

### Pin/Unpin Insights

**Backend:**
- Admin-only endpoint
- Tracks who pinned and when
- Updates Firestore atomically

**Frontend:**
- Pin button (admin-only)
- Optimistic UI updates
- Success/error feedback

**UI:**
```html
<button class="pin-button admin-only"
        data-insight-id="{{ insight.id }}"
        data-is-pinned="{{ 'true' if insight.is_pinned else 'false' }}">
  <i class="fas fa-thumbtack"></i>
  {{ 'Unpin' if insight.is_pinned else 'Pin' }}
</button>
```

---

## Testing

### Automated Tests

**Type Checking:**
```bash
npm run type-check
# Must pass with no errors
```

**Build Test:**
```bash
npm run build
# Expected: ✓ built in ~70ms
```

**Backend Validation:**
```bash
# Verify methods exist
grep -n "def get_community_insights" core/insights_manager.py
grep -n "def set_admin_status" auth/firestore_manager.py

# Verify routes exist
grep -n "@api_bp.route.*pin" routes/api.py
```

### Manual Testing Checklist

**Authentication:**
- [ ] Login/logout works
- [ ] Session timeout (15 min)
- [ ] Admin badge shows

**Social Features:**
- [ ] Like button toggles
- [ ] Share toggle works
- [ ] Community page displays

**Search & Stats:**
- [ ] Search finds insights
- [ ] Sort options work
- [ ] Pagination works
- [ ] Stats display

**Admin Features:**
- [ ] Pin button visible (admin only)
- [ ] Pin/unpin works
- [ ] Pinned insights at top

**Build System:**
- [ ] Dev mode HMR works
- [ ] Production build succeeds
- [ ] Assets load correctly

---

## Deployment

### Production Build

```bash
# 1. Build frontend
npm run build

# 2. Verify manifest
cat static/dist/.vite/manifest.json

# 3. Deploy
# Docker
docker build -t ai-insights .
docker run -p 5001:5001 ai-insights

# Or Cloud Run
./build-insight-app.sh
```

### Environment Variables

```bash
OPENAI_API_KEY=your_key
TAVILY_API_KEY=your_key
FLASK_SECRET_KEY=your_secret
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
```

---

## Troubleshooting

### Common Issues

**1. Vite 431 Error (Request Header Fields Too Large):**
```bash
NODE_OPTIONS='--max-http-header-size=16384' npm run dev
```

**2. Manifest Not Found:**
```bash
npm run build
ls static/dist/.vite/manifest.json
```

**3. TypeScript Errors:**
```bash
npm run type-check
# Fix reported errors
```

**4. Admin Features Not Showing:**
```python
# Set admin status
from auth.firestore_manager import UserFirestoreManager
mgr = UserFirestoreManager()
mgr.set_admin_status('user_id', True)
```

---

## Best Practices

### Development

1. **Always run type checking:**
   ```bash
   npm run type-check
   ```

2. **Test both modes:**
   - Development (Vite HMR)
   - Production (Built assets)

3. **Keep types updated:**
   - Update `types.ts` for new models
   - Maintain strict typing

### Production

1. **Build before deploying:**
   ```bash
   npm run build
   ```

2. **Verify environment variables**

3. **Monitor performance:**
   - Asset sizes
   - API response times
   - Error rates

---

## Integration Summary

### What Was Integrated

✅ **Phase 1:** Backend data models & managers (9 new fields, 10 new methods)
✅ **Phase 2:** Routes & API endpoints (3 new endpoints)
✅ **Phase 3:** Template integration (removed 320+ lines inline code)
✅ **Phase 4:** TypeScript enhancement (5 modules updated)
✅ **Phase 5:** CSS migration (260+ lines to modules)
✅ **Phase 6:** Build configuration (Vite + Flask integration)
✅ **Phase 7:** Testing & validation (all tests pass)
✅ **Phase 8:** Documentation (this guide)

### Key Metrics

- **Code Removed:** 320+ lines of inline CSS/JS
- **TypeScript Added:** 500+ lines of typed code
- **Build Size:** ~20 KB total (~7 KB gzipped)
- **Build Time:** ~70ms
- **Type Safety:** 100% (tsc --noEmit passes)

### Files Modified

**Backend (6 files):**
- core/crew_ai.py
- core/insights_manager.py
- auth/firestore_manager.py
- routes/main.py
- routes/api.py
- app.py

**Frontend (7 files):**
- static/src/ts/core/auth.ts
- static/src/ts/core/api.ts
- static/src/ts/core/types.ts
- static/src/ts/components/SocialInteractions.ts
- static/src/ts/features/community.ts
- static/src/css/pages/community.css
- templates/base.html (+4 page templates)

---

## Resources

- **Vite:** https://vitejs.dev/
- **TypeScript:** https://www.typescriptlang.org/
- **Flask:** https://flask.palletsprojects.com/
- **Firebase Admin:** https://firebase.google.com/docs/admin/setup

---

**Version:** 2.0.0  
**Last Updated:** November 2024  
**Status:** ✅ Production Ready
