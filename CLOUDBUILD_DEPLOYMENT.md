# Cloud Build Deployment Guide

This guide explains how to deploy the AI Insights Generator to Google Cloud Run using Cloud Build for automated CI/CD.

## Overview

The application uses Google Cloud Build for automated deployment with:
- **Multi-stage Docker build** (Node.js for frontend + Python for backend)
- **TypeScript/Vite frontend compilation** during build
- **Automated Cloud Run deployment**
- **Secret Manager integration** for API keys and credentials
- **Multiple environment support** (dev/staging/production)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Cloud Build Pipeline                    │
│                                                          │
│  1. Build Docker Image (multi-stage)                    │
│     ├─ Stage 1: Node.js - Build TypeScript frontend     │
│     └─ Stage 2: Python - Package Flask backend          │
│                                                          │
│  2. Push to Artifact Registry                           │
│     └─ Tagged with commit SHA and 'latest'              │
│                                                          │
│  3. Deploy to Cloud Run                                 │
│     ├─ Inject secrets from Secret Manager              │
│     ├─ Configure environment variables                  │
│     └─ Set resource limits and scaling                  │
│                                                          │
│  4. Health Check Verification                           │
│     └─ Test /status endpoint                            │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Docker** installed (for local testing)
4. **Firebase project** configured (same as GCP project)

## Quick Start

### 1. Initial GCP Setup

Run the automated setup script:

```bash
# Make script executable
chmod +x setup-gcp-cloudbuild.sh

# Run setup (uses current gcloud project or specify PROJECT_ID)
./setup-gcp-cloudbuild.sh [PROJECT_ID]
```

This script will:
- ✅ Enable required GCP APIs
- ✅ Create Artifact Registry repository
- ✅ Create service account with proper IAM roles
- ✅ Configure Cloud Build permissions
- ✅ Create Secret Manager secrets (with placeholders)
- ✅ Set up Cloud Storage bucket for artifacts

### 2. Update Secrets

Replace placeholder values with actual credentials:

```bash
# OpenAI API Key
echo 'sk-...' | gcloud secrets versions add OPENAI_API_KEY --data-file=-

# Tavily Search API Key
echo 'tvly-...' | gcloud secrets versions add TAVILY_API_KEY --data-file=-

# Firebase Web API Key (from Firebase Console)
echo 'AIza...' | gcloud secrets versions add FIREBASE_WEB_API_KEY --data-file=-

# Firebase Messaging Sender ID
echo '123456789' | gcloud secrets versions add FIREBASE_MESSAGING_SENDER_ID --data-file=-

# Firebase App ID
echo '1:123456789:web:abc123...' | gcloud secrets versions add FIREBASE_APP_ID --data-file=-

# Firebase Measurement ID (optional)
echo 'G-ABC123XYZ' | gcloud secrets versions add FIREBASE_MEASUREMENT_ID --data-file=-
```

### 3. Deploy with Cloud Build

#### Production Deployment

```bash
# Deploy to production
gcloud builds submit --config cloudbuild.yaml

# Or with custom substitutions
gcloud builds submit \
  --config cloudbuild.yaml \
  --substitutions=_SERVICE_NAME=ai-insights-prod,_MEMORY=8Gi
```

#### Development Deployment

```bash
# Deploy to development environment
gcloud builds submit --config cloudbuild-dev.yaml
```

## Configuration Files

### `cloudbuild.yaml` (Production)

Main deployment configuration with:
- **Resources**: 2 CPU, 4Gi memory
- **Scaling**: 0-10 instances
- **Timeout**: 3600s
- **Build time**: ~20 minutes (first build), ~5 minutes (subsequent)

### `cloudbuild-dev.yaml` (Development)

Development environment with reduced resources:
- **Resources**: 1 CPU, 2Gi memory
- **Scaling**: 0-3 instances
- **Timeout**: 1800s
- **Service name**: `ai-insights-generator-dev`

## Customization

### Override Default Settings

Use substitution variables to customize deployment:

```bash
gcloud builds submit \
  --config cloudbuild.yaml \
  --substitutions=\
_REGION=us-central1,\
_SERVICE_NAME=my-custom-service,\
_CPU=4,\
_MEMORY=8Gi,\
_MAX_INSTANCES=20
```

### Available Substitutions

| Variable | Default | Description |
|----------|---------|-------------|
| `_REGION` | `us-west1` | GCP region |
| `_REPOSITORY` | `cloud-run-source-deploy` | Artifact Registry repo |
| `_IMAGE_NAME` | `ai-insights-generator` | Docker image name |
| `_SERVICE_NAME` | `ai-insights-generator` | Cloud Run service name |
| `_SERVICE_ACCOUNT` | `ai-insights-service` | Service account |
| `_BUILD_ENV` | `production` | Build environment |
| `_CPU` | `2` | CPU allocation |
| `_MEMORY` | `4Gi` | Memory allocation |
| `_TIMEOUT` | `3600` | Request timeout (seconds) |
| `_CONCURRENCY` | `1000` | Max requests per instance |
| `_MIN_INSTANCES` | `0` | Minimum instances |
| `_MAX_INSTANCES` | `10` | Maximum instances |

## Automated Triggers

### GitHub Integration

Set up automatic deployments on git push:

```bash
gcloud builds triggers create github \
  --repo-name=YOUR_REPO_NAME \
  --repo-owner=YOUR_GITHUB_USERNAME \
  --branch-pattern='^main$' \
  --build-config=cloudbuild.yaml \
  --description="Deploy to production on main branch"

# Development branch trigger
gcloud builds triggers create github \
  --repo-name=YOUR_REPO_NAME \
  --repo-owner=YOUR_GITHUB_USERNAME \
  --branch-pattern='^develop$' \
  --build-config=cloudbuild-dev.yaml \
  --description="Deploy to dev on develop branch"
```

### Cloud Source Repositories

```bash
gcloud builds triggers create cloud-source-repositories \
  --repo=YOUR_REPO_NAME \
  --branch-pattern='^main$' \
  --build-config=cloudbuild.yaml
```

### Manual Trigger via Console

1. Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers)
2. Click **Create Trigger**
3. Configure source repository
4. Set branch pattern (e.g., `^main$`)
5. Select build configuration: `cloudbuild.yaml`
6. Add substitution variables if needed
7. Click **Create**

## Monitoring and Troubleshooting

### View Build Logs

```bash
# List recent builds
gcloud builds list --limit=10

# View specific build logs
gcloud builds log BUILD_ID

# Stream logs in real-time
gcloud builds log BUILD_ID --stream
```

### View Service Logs

```bash
# View Cloud Run service logs
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="ai-insights-generator"' \
  --project=PROJECT_ID \
  --limit=50 \
  --format=json

# Tail logs in real-time
gcloud alpha logging tail \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="ai-insights-generator"' \
  --project=PROJECT_ID
```

### Check Service Status

```bash
# Get service details
gcloud run services describe ai-insights-generator \
  --region=us-west1 \
  --format=yaml

# Test service endpoint
SERVICE_URL=$(gcloud run services describe ai-insights-generator \
  --region=us-west1 \
  --format="value(status.url)")

curl $SERVICE_URL/status
```

### Common Issues

#### Build Fails: "npm ci requires package-lock.json"

**Solution**: Ensure `package-lock.json` is committed to git and not in `.dockerignore`

```bash
git add package-lock.json
git commit -m "Add package-lock.json for reproducible builds"
```

#### Build Fails: "Permission denied"

**Solution**: Grant Cloud Build service account proper permissions

```bash
PROJECT_NUMBER=$(gcloud projects describe PROJECT_ID --format="value(projectNumber)")
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"
```

#### Service Health Check Fails

**Solution**: Check service logs and verify secrets are set correctly

```bash
# Check which secrets are available
gcloud secrets list

# Verify secret access
gcloud secrets versions access latest --secret=OPENAI_API_KEY

# Check service environment
gcloud run services describe ai-insights-generator \
  --region=us-west1 \
  --format="value(spec.template.spec.containers[0].env)"
```

## Cost Optimization

### Reduce Build Costs

1. **Use smaller machine type** for simple builds:
   ```yaml
   options:
     machineType: 'E2_HIGHCPU_4'  # Instead of E2_HIGHCPU_8
   ```

2. **Cache Docker layers** by using consistent layer ordering

3. **Use Cloud Build cache** for Node.js dependencies:
   ```yaml
   - name: 'gcr.io/cloud-builders/docker'
     args: ['--cache-from', 'previous-image']
   ```

### Reduce Runtime Costs

1. **Reduce min instances** to 0 (cold start acceptable)
2. **Lower memory allocation** if not needed
3. **Set appropriate timeout** (don't use 3600s if not needed)
4. **Enable CPU allocation only during request** (default for Cloud Run Gen2)

## Security Best Practices

1. **Never commit secrets** to source code
2. **Use Secret Manager** for all sensitive data
3. **Enable VPC connector** for private services (if needed)
4. **Use least privilege IAM** for service accounts
5. **Enable Cloud Armor** for DDoS protection (if needed)
6. **Set up Cloud Audit Logs** for compliance

## Production Checklist

Before deploying to production:

- [ ] All secrets updated with production values
- [ ] Firebase authentication configured
- [ ] Custom domain configured (if needed)
- [ ] Cloud Armor enabled (if needed)
- [ ] Monitoring and alerting configured
- [ ] Backup strategy in place for Firestore
- [ ] Load testing completed
- [ ] Security scan completed
- [ ] Cost estimation reviewed
- [ ] Rollback plan documented

## Additional Resources

- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Firebase Authentication](https://firebase.google.com/docs/auth)

## Support

For issues or questions:
1. Check service logs: `gcloud logging read`
2. Review build logs: `gcloud builds log BUILD_ID`
3. Test locally: `docker-compose -f docker-compose.insight.yml up`
4. Verify secrets: `gcloud secrets list`
