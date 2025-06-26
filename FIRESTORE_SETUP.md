# Firestore Database Setup Guide

This guide explains how to set up Google Cloud Firestore to persist your AI insights data.

## 📋 Prerequisites

1. **Google Cloud Project**: You need a Google Cloud project with billing enabled
2. **Firestore Database**: Database named `ai-biz` (configured in the app)
3. **Authentication**: Service account or Application Default Credentials

## 🚀 Quick Setup

### Step 1: Create Google Cloud Project (if needed)

```bash
# Install Google Cloud CLI if not already installed
# Visit: https://cloud.google.com/sdk/docs/install

# Create a new project (optional)
gcloud projects create your-project-id
gcloud config set project your-project-id
```

### Step 2: Enable Firestore API

```bash
# Enable required APIs
gcloud services enable firestore.googleapis.com
gcloud services enable firebase.googleapis.com
```

### Step 3: Create Firestore Database

```bash
# Create Firestore database named 'ai-biz'
gcloud firestore databases create --database=ai-biz --location=us-central1
```

Or via Google Cloud Console:
1. Go to [Firestore Console](https://console.cloud.google.com/firestore)
2. Click "Create Database"
3. Choose "Firestore Native mode"
4. Set database ID to: `ai-biz`
5. Choose location (e.g., `us-central1`)

### Step 4: Set Up Authentication

#### Option A: Service Account (Recommended for Production)

```bash
# Create service account
gcloud iam service-accounts create ai-insights-service \
    --description="Service account for AI Insights app" \
    --display-name="AI Insights Service"

# Grant Firestore permissions
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:ai-insights-service@your-project-id.iam.gserviceaccount.com" \
    --role="roles/datastore.user"

# Create and download service account key
gcloud iam service-accounts keys create ./service-account-key.json \
    --iam-account=ai-insights-service@your-project-id.iam.gserviceaccount.com
```

#### Option B: Application Default Credentials (Development)

```bash
# Authenticate with your Google account
gcloud auth application-default login
```

### Step 5: Configure Authentication

The app supports multiple authentication methods (tried in order):

#### Option A: Google Cloud Secret Manager (Recommended for Production)
The app is pre-configured to use the secret:
```
projects/711582759542/secrets/AI-Biz-Service-Account-Key
```

No additional configuration needed - the app will automatically retrieve the service account key from Secret Manager.

#### Option B: Local Service Account File
Create or update your `.env` file:

```bash
# For Service Account authentication
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# Your existing API keys
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key  # or SERPER_API_KEY
```

#### Option C: Application Default Credentials (Development)
```bash
# Authenticate with your Google account
gcloud auth application-default login

# Your existing API keys  
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key  # or SERPER_API_KEY
```

### Step 6: Install Dependencies

```bash
# Install the updated requirements
pip install -r requirements-flask.txt
```

## 🔧 Configuration Details

### Database Structure

The app uses the following Firestore structure:

```
ai-biz (database)
└── insights (collection)
    ├── {insight-id-1} (document)
    │   ├── id: string
    │   ├── topic: string
    │   ├── instructions: string
    │   ├── timestamp: string
    │   ├── insights: array
    │   ├── total_insights: number
    │   ├── processing_time: number
    │   ├── total_tokens: number
    │   ├── agent_notes: string
    │   ├── created_at: timestamp (auto-generated)
    │   └── updated_at: timestamp (auto-generated)
    └── {insight-id-2} (document)
        └── ... (same structure)
```

### Security Rules (Optional)

For production, consider setting up Firestore security rules:

```javascript
// Firestore Security Rules
rules_version = '2';
service cloud.firestore {
  match /databases/ai-biz/documents {
    // Allow read/write access to insights collection
    match /insights/{insightId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## 🧪 Testing the Setup

1. **Start the Flask app**:
   ```bash
   python app.py
   ```

2. **Check the logs** for Firestore connection status:
   - ✅ Success: "Connected to Firestore database: ai-biz"
   - ⚠️ Fallback: "Failed to initialize Firestore" (will use in-memory storage)

3. **Generate insights** through the web interface and verify they appear in Firestore Console

## 🔍 Troubleshooting

### Common Issues

1. **"Failed to initialize Firestore"**
   - Check if the `ai-biz` database exists
   - Verify authentication credentials
   - Ensure Firestore API is enabled

2. **"Permission denied"**
   - Check service account permissions
   - Verify the service account has `roles/datastore.user` role

3. **"Database not found"**
   - Ensure database is named exactly `ai-biz`
   - Check if you're in the correct Google Cloud project

### Verification Commands

```bash
# Check if Firestore API is enabled
gcloud services list --enabled | grep firestore

# List Firestore databases
gcloud firestore databases list

# Test authentication
gcloud auth application-default print-access-token
```

## 📊 Monitoring

You can monitor your Firestore usage in the [Google Cloud Console](https://console.cloud.google.com/firestore):

- **Documents**: Number of insights stored
- **Reads/Writes**: API usage for billing
- **Storage**: Data storage usage

## 💰 Pricing

Firestore pricing is based on:
- **Document reads/writes**: $0.06 per 100K operations
- **Storage**: $0.18 per GB/month
- **Network egress**: Variable by region

For typical usage (hundreds of insights), costs should be minimal (< $1/month).

## 🔄 Migration

If you have existing insights in memory, they will be automatically cached when accessed. To migrate all data to Firestore:

1. Start the app with Firestore configured
2. Access each insight through the web interface
3. They will be automatically saved to Firestore

## 🆘 Support

If you encounter issues:

1. Check the Flask app logs for detailed error messages
2. Verify your Google Cloud project setup
3. Test authentication with `gcloud auth application-default login`
4. Ensure the `ai-biz` database exists and is accessible

The app will gracefully fall back to in-memory storage if Firestore is unavailable, so your app will continue to work even during setup. 