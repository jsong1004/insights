#!/bin/bash

# AI Insights Generator Flask App - Deploy to Google Cloud Run Service
# Usage: ./build-insight-app.sh [dev|prod] [--push] [PROJECT_ID]

set -e

# Configuration
PROJECT_ID=${3:-"${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}"}
REGION="us-west1"
SERVICE_ACCOUNT_NAME="ai-insights-service"
SERVICE_NAME="ai-insights-generator"
REPOSITORY_NAME="cloud-run-source-deploy"
IMAGE_NAME="ai-insights-generator"
IMAGE_TAG="latest"

# Firebase Configuration (update these with your actual values)
FIREBASE_PROJECT_ID="${PROJECT_ID}"  # Usually same as Google Cloud project
FIREBASE_WEB_API_KEY=""  # Get from Firebase console
FIREBASE_AUTH_DOMAIN="${PROJECT_ID}.firebaseapp.com"
FIREBASE_STORAGE_BUCKET="${PROJECT_ID}.appspot.com"
FIREBASE_MESSAGING_SENDER_ID=""  # Get from Firebase console
FIREBASE_APP_ID=""  # Get from Firebase console
FIREBASE_MEASUREMENT_ID=""  # Optional, from Firebase console

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_usage() {
    echo "Usage: $0 [dev|prod] [--push] [PROJECT_ID]"
    echo ""
    echo "Arguments:"
    echo "  dev        Build and deploy development service (default)"
    echo "  prod       Build and deploy production service"
    echo "  --push     Push image to registry after building (auto for Cloud Run)"
    echo "  PROJECT_ID Google Cloud project ID (optional, uses current project)"
    echo ""
    echo "Examples:"
    echo "  $0                           # Deploy development service"
    echo "  $0 prod                      # Deploy production service"
    echo "  $0 prod --push my-project    # Deploy to specific project"
    echo ""
    echo "Environment variables (set these before running):"
    echo "  OPENAI_API_KEY          - Required for CrewAI agents"
    echo "  TAVILY_API_KEY          - Required for search functionality"
    echo "  SERPER_API_KEY          - Optional alternative search"
    echo "  FIREBASE_WEB_API_KEY    - Required for Firebase authentication"
    echo "  FIREBASE_MESSAGING_SENDER_ID - Required for Firebase"
    echo "  FIREBASE_APP_ID         - Required for Firebase"
    echo "  FIREBASE_MEASUREMENT_ID - Optional for Firebase analytics"
}

# Parse arguments
BUILD_TYPE="dev"
PUSH_IMAGE=false

for arg in "$@"; do
    case $arg in
        dev|prod)
            BUILD_TYPE="$arg"
            ;;
        --push)
            PUSH_IMAGE=true
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            # Check if it's a project ID (third argument)
            if [[ $arg =~ ^[a-z][a-z0-9-]*[a-z0-9]$ ]] && [ ${#arg} -ge 6 ] && [ ${#arg} -le 30 ]; then
                PROJECT_ID="$arg"
            else
                log_error "Unknown argument: $arg"
                show_usage
                exit 1
            fi
            ;;
    esac
done

# Set image tag and full image name for Google Cloud
if [ "$BUILD_TYPE" = "prod" ]; then
    IMAGE_TAG="latest"
    SERVICE_NAME="ai-insights-generator"
else
    IMAGE_TAG="dev"
    SERVICE_NAME="ai-insights-generator-dev"
fi

FULL_IMAGE_NAME="${REGION}-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$IMAGE_NAME:$IMAGE_TAG"

log_info "🚀 Deploying AI Insights Generator with Firebase Auth to Google Cloud Run Service"
log_info "Project ID: $PROJECT_ID"
log_info "Region: $REGION"
log_info "Service: $SERVICE_NAME"
log_info "Image: $FULL_IMAGE_NAME"

# Check if logged in to gcloud
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    log_error "Please log in to gcloud first: gcloud auth login"
    exit 1
fi

# Set the project
gcloud config set project $PROJECT_ID

# Check if required files exist
if [ ! -f "Dockerfile.insight" ]; then
    log_error "Dockerfile.insight not found!"
    exit 1
fi

if [ ! -f "requirements-firebase.txt" ]; then
    log_error "requirements-firebase.txt not found!"
    exit 1
fi

if [ ! -f "app.py" ]; then
    log_error "app.py not found!"
    exit 1
fi

if [ ! -d "templates" ]; then
    log_error "templates directory not found!"
    exit 1
fi

if [ ! -d "auth" ]; then
    log_error "auth directory not found!"
    exit 1
fi

# Enable required APIs
log_info "📋 Enabling required Google Cloud APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    iam.googleapis.com \
    firebase.googleapis.com \
    firestore.googleapis.com \
    identitytoolkit.googleapis.com || {
    log_warning "Some APIs may not be available - continuing with basic deployment"
}

# Create service account if it doesn't exist
log_info "👤 Creating service account..."
if ! gcloud iam service-accounts describe "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" >/dev/null 2>&1; then
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="AI Insights Generator Service" \
        --description="Service account for AI Insights Generator Flask app with Firebase auth"
fi

# Grant necessary permissions
log_info "🔑 Granting permissions to service account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/datastore.user"

# Additional Firebase/Firestore permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/firebase.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/firestore.serviceAgent"

# Create secrets (you'll need to add the actual values)
log_info "🔐 Creating secrets (please update with actual values later)..."

# Create AI API secrets
if ! gcloud secrets describe OPENAI_API_KEY >/dev/null 2>&1; then
    echo "your-openai-api-key-here" | gcloud secrets create OPENAI_API_KEY --data-file=-
    log_warning "Please update OPENAI_API_KEY secret with your actual OpenAI API key"
fi

if ! gcloud secrets describe TAVILY_API_KEY >/dev/null 2>&1; then
    echo "your-tavily-api-key-here" | gcloud secrets create TAVILY_API_KEY --data-file=-
    log_warning "Please update TAVILY_API_KEY secret with your actual Tavily API key"
fi

if ! gcloud secrets describe SERPER_API_KEY >/dev/null 2>&1; then
    echo "your-serper-api-key-here" | gcloud secrets create SERPER_API_KEY --data-file=-
    log_warning "Please update SERPER_API_KEY secret with your actual Serper API key (optional)"
fi

# Create Firebase secrets
if ! gcloud secrets describe FIREBASE_WEB_API_KEY >/dev/null 2>&1; then
    echo "your-firebase-web-api-key-here" | gcloud secrets create FIREBASE_WEB_API_KEY --data-file=-
    log_warning "Please update FIREBASE_WEB_API_KEY secret with your actual Firebase Web API key"
fi

if ! gcloud secrets describe FIREBASE_MESSAGING_SENDER_ID >/dev/null 2>&1; then
    echo "your-firebase-messaging-sender-id" | gcloud secrets create FIREBASE_MESSAGING_SENDER_ID --data-file=-
    log_warning "Please update FIREBASE_MESSAGING_SENDER_ID secret with your actual Firebase Messaging Sender ID"
fi

if ! gcloud secrets describe FIREBASE_APP_ID >/dev/null 2>&1; then
    echo "your-firebase-app-id" | gcloud secrets create FIREBASE_APP_ID --data-file=-
    log_warning "Please update FIREBASE_APP_ID secret with your actual Firebase App ID"
fi

if ! gcloud secrets describe FIREBASE_MEASUREMENT_ID >/dev/null 2>&1; then
    echo "your-firebase-measurement-id" | gcloud secrets create FIREBASE_MEASUREMENT_ID --data-file=-
    log_warning "Please update FIREBASE_MEASUREMENT_ID secret with your actual Firebase Measurement ID (optional)"
fi

# Check if Artifact Registry repository exists, create if not
log_info "📦 Setting up Artifact Registry repository..."
if ! gcloud artifacts repositories describe $REPOSITORY_NAME --location=$REGION --project=$PROJECT_ID >/dev/null 2>&1; then
    log_info "Creating Artifact Registry repository..."
    gcloud artifacts repositories create $REPOSITORY_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="Repository for AI Insights Generator Service with Firebase" \
        --project=$PROJECT_ID
else
    log_info "Repository $REPOSITORY_NAME already exists"
fi

# Configure Docker authentication
log_info "🔐 Configuring Docker authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# Build the Docker image
log_info "🏗️ Building container image..."
if [ "$BUILD_TYPE" = "prod" ]; then
    docker build --platform linux/amd64 \
        -f Dockerfile.insight \
        -t "$FULL_IMAGE_NAME" \
        --build-arg BUILD_ENV=production \
        .
else
    docker build --platform linux/amd64 \
        -f Dockerfile.insight \
        -t "$FULL_IMAGE_NAME" \
        --build-arg BUILD_ENV=development \
        .
fi

if [ $? -eq 0 ]; then
    log_success "Docker image built successfully: $FULL_IMAGE_NAME"
else
    log_error "Docker build failed!"
    exit 1
fi

# Show image size
IMAGE_SIZE=$(docker images "$FULL_IMAGE_NAME" --format "table {{.Size}}" | tail -n 1)
log_info "Image size: $IMAGE_SIZE"

# Push the image to Google Container Registry
log_info "📤 Pushing container image to Artifact Registry..."
docker push "$FULL_IMAGE_NAME"

if [ $? -eq 0 ]; then
    log_success "Image pushed successfully: $FULL_IMAGE_NAME"
else
    log_error "Failed to push image!"
    exit 1
fi

# Deploy the Cloud Run Service
log_info "🚀 Deploying Cloud Run Service..."

# Prepare Firebase environment variables
FIREBASE_ENV_VARS="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,FIREBASE_PROJECT_ID=$FIREBASE_PROJECT_ID,FIREBASE_AUTH_DOMAIN=$FIREBASE_AUTH_DOMAIN,FIREBASE_STORAGE_BUCKET=$FIREBASE_STORAGE_BUCKET"

# Prepare secrets configuration
SECRETS_CONFIG="OPENAI_API_KEY=OPENAI_API_KEY:latest,TAVILY_API_KEY=TAVILY_API_KEY:latest,SERPER_API_KEY=SERPER_API_KEY:latest,FIREBASE_WEB_API_KEY=FIREBASE_WEB_API_KEY:latest,FIREBASE_MESSAGING_SENDER_ID=FIREBASE_MESSAGING_SENDER_ID:latest,FIREBASE_APP_ID=FIREBASE_APP_ID:latest,FIREBASE_MEASUREMENT_ID=FIREBASE_MEASUREMENT_ID:latest"

# Check if service exists, if not create it, otherwise update it
if gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID >/dev/null 2>&1; then
    log_info "Updating existing service..."
    gcloud run deploy $SERVICE_NAME \
        --image $FULL_IMAGE_NAME \
        --region $REGION \
        --platform managed \
        --allow-unauthenticated \
        --port 5000 \
        --cpu 2 \
        --memory 4Gi \
        --timeout 3600 \
        --concurrency 1000 \
        --min-instances 0 \
        --max-instances 10 \
        --set-env-vars "$FIREBASE_ENV_VARS" \
        --set-secrets "$SECRETS_CONFIG" \
        --service-account "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --project=$PROJECT_ID
else
    log_info "Creating new service..."
    gcloud run deploy $SERVICE_NAME \
        --image $FULL_IMAGE_NAME \
        --region $REGION \
        --platform managed \
        --allow-unauthenticated \
        --port 5000 \
        --cpu 2 \
        --memory 4Gi \
        --timeout 3600 \
        --concurrency 1000 \
        --min-instances 0 \
        --max-instances 10 \
        --set-env-vars "$FIREBASE_ENV_VARS" \
        --set-secrets "$SECRETS_CONFIG" \
        --service-account "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --project=$PROJECT_ID
fi

if [ $? -eq 0 ]; then
    log_success "Service deployed successfully!"
else
    log_error "Service deployment failed!"
    exit 1
fi

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")

# Show deployment details
echo ""
log_success "🎉 AI Insights Generator with Firebase Auth deployment complete!"
echo ""
echo "📋 Service Details:"
gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="table(metadata.name,status.url,status.conditions[0].type,status.conditions[0].status)"

echo ""
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "🔧 Next steps:"
echo ""
echo "1. Update AI API secrets with your actual keys:"
echo "   gcloud secrets versions add OPENAI_API_KEY --data-file=- <<< 'your-actual-openai-key'"
echo "   gcloud secrets versions add TAVILY_API_KEY --data-file=- <<< 'your-actual-tavily-key'"
echo "   gcloud secrets versions add SERPER_API_KEY --data-file=- <<< 'your-actual-serper-key'"
echo ""
echo "2. Update Firebase secrets with your actual configuration:"
echo "   gcloud secrets versions add FIREBASE_WEB_API_KEY --data-file=- <<< 'your-firebase-web-api-key'"
echo "   gcloud secrets versions add FIREBASE_MESSAGING_SENDER_ID --data-file=- <<< 'your-messaging-sender-id'"
echo "   gcloud secrets versions add FIREBASE_APP_ID --data-file=- <<< 'your-firebase-app-id'"
echo "   gcloud secrets versions add FIREBASE_MEASUREMENT_ID --data-file=- <<< 'your-measurement-id'"
echo ""
echo "3. Configure Firebase Authentication:"
echo "   - Enable Email/Password and Google sign-in in Firebase Console"
echo "   - Add $SERVICE_URL to authorized domains"
echo ""
echo "4. Test the service:"
echo "   curl $SERVICE_URL"
echo "   curl $SERVICE_URL/status"
echo ""
echo "5. Monitor service logs:"
echo "   gcloud logging read 'resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$SERVICE_NAME\"' --project=$PROJECT_ID --limit=50"
echo ""
echo "6. View service details:"
echo "   gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
echo ""
echo "🔥 The AI Insights Generator with Firebase Authentication is now running as a Cloud Run service!"
echo "📱 Users can now sign up, log in, and share insights with the community!" 