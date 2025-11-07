#!/bin/bash

# Setup script for Google Cloud Platform Cloud Build deployment
# This script prepares your GCP project for automated Cloud Build deployments
#
# Usage: ./setup-gcp-cloudbuild.sh [PROJECT_ID]

set -e

# Configuration
PROJECT_ID=${1:-"${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}"}
REGION="us-west1"
SERVICE_ACCOUNT_NAME="ai-insights-service"
REPOSITORY_NAME="cloud-run-source-deploy"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo ""
log_info "🚀 Setting up Google Cloud Platform for AI Insights Generator Cloud Build"
log_info "Project ID: $PROJECT_ID"
log_info "Region: $REGION"
echo ""

# Check if logged in to gcloud
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    log_error "Please log in to gcloud first: gcloud auth login"
    exit 1
fi

# Set the project
log_info "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Step 1: Enable required APIs
log_info "📋 Enabling required Google Cloud APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    iam.googleapis.com \
    firebase.googleapis.com \
    firestore.googleapis.com \
    identitytoolkit.googleapis.com \
    logging.googleapis.com \
    storage-api.googleapis.com

log_success "APIs enabled"

# Step 2: Create Artifact Registry repository
log_info "📦 Setting up Artifact Registry repository..."
if ! gcloud artifacts repositories describe $REPOSITORY_NAME \
    --location=$REGION \
    --project=$PROJECT_ID >/dev/null 2>&1; then

    gcloud artifacts repositories create $REPOSITORY_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="Repository for AI Insights Generator with TypeScript frontend" \
        --project=$PROJECT_ID

    log_success "Artifact Registry repository created"
else
    log_info "Repository $REPOSITORY_NAME already exists"
fi

# Step 3: Create service account
log_info "👤 Creating service account..."
if ! gcloud iam service-accounts describe \
    "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    >/dev/null 2>&1; then

    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="AI Insights Generator Service" \
        --description="Service account for AI Insights Generator with Firebase auth and TypeScript frontend"

    log_success "Service account created"
else
    log_info "Service account already exists"
fi

# Step 4: Grant necessary IAM permissions
log_info "🔑 Granting IAM permissions to service account..."

# Cloud Run and logging permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.invoker" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter" \
    --condition=None

# Secret Manager permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None

# Firestore permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/datastore.user" \
    --condition=None

# Firebase permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/firebase.admin" \
    --condition=None

log_success "IAM permissions granted"

# Step 5: Grant Cloud Build service account permissions
log_info "🔧 Configuring Cloud Build service account..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Grant Cloud Build permission to deploy to Cloud Run
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${CLOUDBUILD_SA}" \
    --role="roles/run.admin" \
    --condition=None

# Grant Cloud Build permission to act as service accounts
gcloud iam service-accounts add-iam-policy-binding \
    "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --member="serviceAccount:${CLOUDBUILD_SA}" \
    --role="roles/iam.serviceAccountUser"

log_success "Cloud Build service account configured"

# Step 6: Create secrets with placeholder values
log_info "🔐 Creating Secret Manager secrets (with placeholder values)..."

create_secret_if_not_exists() {
    local SECRET_NAME=$1
    local PLACEHOLDER_VALUE=$2

    if ! gcloud secrets describe $SECRET_NAME --project=$PROJECT_ID >/dev/null 2>&1; then
        echo "$PLACEHOLDER_VALUE" | gcloud secrets create $SECRET_NAME \
            --data-file=- \
            --project=$PROJECT_ID \
            --replication-policy="automatic"

        log_warning "Created $SECRET_NAME with placeholder value - UPDATE THIS!"
    else
        log_info "Secret $SECRET_NAME already exists"
    fi
}

# AI API secrets
create_secret_if_not_exists "OPENAI_API_KEY" "your-openai-api-key-here"
create_secret_if_not_exists "TAVILY_API_KEY" "your-tavily-api-key-here"
create_secret_if_not_exists "SERPER_API_KEY" "your-serper-api-key-here"

# Firebase secrets
create_secret_if_not_exists "FIREBASE_WEB_API_KEY" "your-firebase-web-api-key"
create_secret_if_not_exists "FIREBASE_MESSAGING_SENDER_ID" "your-messaging-sender-id"
create_secret_if_not_exists "FIREBASE_APP_ID" "your-firebase-app-id"
create_secret_if_not_exists "FIREBASE_MEASUREMENT_ID" "your-measurement-id"

log_success "Secrets created"

# Step 7: Create Cloud Storage bucket for build artifacts (optional)
log_info "📁 Creating Cloud Storage bucket for build artifacts..."
BUCKET_NAME="${PROJECT_ID}-build-artifacts"

if ! gsutil ls -b "gs://${BUCKET_NAME}" >/dev/null 2>&1; then
    gsutil mb -p $PROJECT_ID -l $REGION "gs://${BUCKET_NAME}"
    log_success "Build artifacts bucket created: gs://${BUCKET_NAME}"
else
    log_info "Bucket already exists: gs://${BUCKET_NAME}"
fi

# Step 8: Configure Docker authentication
log_info "🔐 Configuring Docker authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet
log_success "Docker authentication configured"

# Summary
echo ""
log_success "✅ GCP setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Setup Summary:"
echo ""
echo "  Project ID:          $PROJECT_ID"
echo "  Region:              $REGION"
echo "  Repository:          ${REGION}-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME"
echo "  Service Account:     ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
echo "  Build Artifacts:     gs://${BUCKET_NAME}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔧 Next Steps:"
echo ""
echo "1. Update Secret Manager secrets with actual values:"
echo ""
echo "   # AI API Keys"
echo "   echo 'sk-...' | gcloud secrets versions add OPENAI_API_KEY --data-file=-"
echo "   echo 'tvly-...' | gcloud secrets versions add TAVILY_API_KEY --data-file=-"
echo ""
echo "   # Firebase Configuration"
echo "   echo 'AIza...' | gcloud secrets versions add FIREBASE_WEB_API_KEY --data-file=-"
echo "   echo '12345...' | gcloud secrets versions add FIREBASE_MESSAGING_SENDER_ID --data-file=-"
echo "   echo '1:12345...' | gcloud secrets versions add FIREBASE_APP_ID --data-file=-"
echo "   echo 'G-...' | gcloud secrets versions add FIREBASE_MEASUREMENT_ID --data-file=-"
echo ""
echo "2. Test manual deployment with Cloud Build:"
echo ""
echo "   # Production deployment"
echo "   gcloud builds submit --config cloudbuild.yaml"
echo ""
echo "   # Development deployment"
echo "   gcloud builds submit --config cloudbuild-dev.yaml"
echo ""
echo "3. Set up automated Cloud Build triggers (optional):"
echo ""
echo "   # GitHub integration"
echo "   gcloud builds triggers create github \\"
echo "     --repo-name=YOUR_REPO_NAME \\"
echo "     --repo-owner=YOUR_GITHUB_USERNAME \\"
echo "     --branch-pattern='^main$' \\"
echo "     --build-config=cloudbuild.yaml"
echo ""
echo "   # Cloud Source Repositories"
echo "   gcloud builds triggers create cloud-source-repositories \\"
echo "     --repo=YOUR_REPO_NAME \\"
echo "     --branch-pattern='^main$' \\"
echo "     --build-config=cloudbuild.yaml"
echo ""
echo "4. Configure Firebase Authentication:"
echo ""
echo "   - Go to Firebase Console: https://console.firebase.google.com"
echo "   - Enable Email/Password and Google sign-in methods"
echo "   - Add your Cloud Run service URL to authorized domains"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
log_success "🎉 Ready to deploy with Cloud Build!"
echo ""
