# Docker + Firebase Authentication Update

## Overview
The Dockerfile.insight and build-insight-app.sh have been updated to support Firebase Authentication and social features for the AI Insights Generator.

## Files Updated

### 1. Dockerfile.insight
**Changes:**
- Updated requirements file from `requirements-flask.txt` to `requirements-firebase.txt`
- Added copying of `auth/` directory containing Firebase authentication code
- Added copying of `static/` directory for frontend assets
- Added optional copying of `service-account-key.json` for development
- Removed hardcoded Firebase environment variables for security
- Updated metadata and version to reflect Firebase integration

**Key Features:**
- Secure credential handling (no sensitive data in image)
- Support for both development and production environments
- Proper file permissions and non-root user setup

### 2. build-insight-app.sh
**Changes:**
- Added Firebase API enablement (firebase.googleapis.com, firestore.googleapis.com, identitytoolkit.googleapis.com)
- Created Firebase-specific secrets in Google Secret Manager
- Added Firebase service account permissions (firebase.admin, firestore.serviceAgent)
- Updated Cloud Run deployment with Firebase environment variables
- Enhanced error handling for API enablement
- Added comprehensive post-deployment instructions

**New Secrets Created:**
- `FIREBASE_WEB_API_KEY`
- `FIREBASE_MESSAGING_SENDER_ID`
- `FIREBASE_APP_ID`
- `FIREBASE_MEASUREMENT_ID`

### 3. requirements-firebase.txt
**Changes:**
- Simplified to avoid dependency conflicts
- Uses flexible version ranges for automatic dependency resolution
- Includes essential packages only:
  - Flask >= 3.0.0
  - firebase-admin >= 6.0.0
  - google-cloud-firestore >= 2.10.0
  - crewai >= 0.100.0
  - openai >= 1.50.0
  - Core data processing libraries

### 4. docker-compose.insight.yml
**Changes:**
- Added Firebase environment variables
- Added volume mount for Firebase service account key
- Fixed healthcheck endpoint to `/status`
- Added Firebase configuration section

### 5. environment-template.txt
**New File:**
- Template for setting up environment variables
- Includes all required Firebase configuration
- Instructions for secure credential management

## Deployment Process

### Local Development
1. Copy `environment-template.txt` to `.env`
2. Fill in your Firebase configuration values
3. Download Firebase service account key to `service-account-key.json`
4. Run: `docker-compose -f docker-compose.insight.yml up`

### Google Cloud Run Production
1. Run: `./build-insight-app.sh prod`
2. Update secrets with actual values:
   ```bash
   gcloud secrets versions add FIREBASE_WEB_API_KEY --data-file=- <<< 'your-key'
   gcloud secrets versions add FIREBASE_MESSAGING_SENDER_ID --data-file=- <<< 'your-id'
   gcloud secrets versions add FIREBASE_APP_ID --data-file=- <<< 'your-app-id'
   gcloud secrets versions add FIREBASE_MEASUREMENT_ID --data-file=- <<< 'your-measurement-id'
   ```
3. Configure Firebase Authentication in Firebase Console
4. Add Cloud Run URL to Firebase authorized domains

## Security Features

### Credential Management
- No sensitive data stored in Docker image
- Secrets managed via Google Secret Manager in production
- Environment variables for local development
- Optional service account key file mounting

### Firebase Authentication
- Email/password authentication
- Google Sign-in integration
- Protected routes with decorators
- User session management
- Firestore user data storage

### Social Features
- Public insight sharing (default)
- Like/unlike functionality
- User profiles and preferences
- Community-driven content

## Testing

### Docker Build Test
```bash
docker build --platform linux/amd64 -f Dockerfile.insight -t ai-insights-test .
```

### Local Run Test
```bash
docker run --rm -p 5000:5000 --env-file .env ai-insights-test
```

### Health Check
```bash
curl http://localhost:5000/status
```

## Troubleshooting

### Common Issues
1. **Dependency conflicts:** Use the simplified requirements-firebase.txt
2. **Firebase not initialized:** Check service account key and environment variables
3. **Secret Manager import errors:** Normal in development, app will use local files
4. **Port conflicts:** Ensure port 5000 is available

### Debug Commands
```bash
# Check container logs
docker logs ai-insights-generator

# Check Firebase initialization
curl http://localhost:5000/status

# Test authentication
curl http://localhost:5000/auth/dashboard
```

## Production Checklist

- [ ] Firebase project configured with Authentication enabled
- [ ] Service account key generated and stored securely
- [ ] All secrets updated in Google Secret Manager
- [ ] Firebase authorized domains configured
- [ ] Cloud Run service deployed successfully
- [ ] Health checks passing
- [ ] User registration and login tested

## Architecture

The updated system now supports:
- **Authentication Layer:** Firebase Authentication with JWT tokens
- **User Management:** Firestore user profiles and preferences
- **Social Features:** Public insights, likes, sharing controls
- **Security:** Protected routes, user session management
- **Scalability:** Cloud Run with auto-scaling
- **Monitoring:** Health checks and logging

This creates a full-featured social AI insights platform with enterprise-grade authentication and cloud deployment capabilities. 