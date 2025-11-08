# 🧠 AI Insights Generator - Flask Web App

A powerful social web application that uses CrewAI's multi-agent system to generate intelligent insights on any topic. Users can sign up, log in, and share insights with the community while building their personal research library. Features comprehensive usage statistics tracking, automated session timeout management, and plan-based subscription limits with a modern, professional light theme design.

**Latest Update (November 2025)**: Major UI/UX overhaul with modern light theme design (#F8FAFC background, #2563EB blue accents), consistent navigation across all pages, and critical Firestore integration fixes. Now featuring comprehensive usage statistics tracking with multi-tier subscription plans, automated 15-minute session timeout management, advanced search parameters with source type filtering (General, News, Finance & Business) and time range controls (None, Day, Week, Month, Year), enhanced error handling for search tool compatibility, robust fallback mechanisms, and a health check endpoint for monitoring. **NEW**: Interactive My Insights table with sortable columns (Title, Tokens, Date) replacing Recent Activity for better insights management. Running on Flask 3.1.1 with CrewAI 0.134.0 for enhanced performance, user management, and collaborative insights.

## 🎨 Recent Updates (November 2025)

### UI/UX Improvements
- **Modern Light Theme**: Refreshed design with clean, professional color scheme
  - Background: #F8FAFC (off-white / light gray) for better readability
  - Primary Accent: #2563EB (vivid blue) for AI tech aesthetic
  - Secondary Accent: #1E40AF (deep navy) for depth
  - Text: #0F172A (dark slate) for optimal contrast
- **Consistent Navigation**: Fixed navbar width consistency across all pages (Home, Insights, Generate, Dashboard)
- **Complete Menu Links**: Added missing "Insights" link to Dashboard and Generate Insights pages
- **Enhanced Visual Hierarchy**: Blue accent borders replace gradient backgrounds for cleaner look
- **Professional Design**: Airy, easy-to-read layout with excellent contrast ratios

### Critical Bug Fixes
- **Firestore Integration**: Fixed circular import issue causing "Firestore unavailable" errors
  - Profile updates now properly persist to database
  - All authentication routes now correctly access Firestore manager
  - Resolved 8 incorrect import patterns in auth routes
- **Session Management**: Improved reliability of user data persistence
- **Data Storage**: All social features, usage statistics, and user profiles now working correctly

## ✨ Features

### 🌟 Enhanced Community Platform (NEW)
- **Interactive Community Page**: Browse shared insights with expandable details for space-efficient viewing
- **Toggleable Insight Details**: Click "Show Details" to expand full insight context with confidence scores
- **Full-Width Display**: Insight details span all table columns for maximum readability
- **Confidence Scoring**: Each insight displays confidence percentages (e.g., "90% Confidence")
- **Smart Previews**: Truncated summaries with full context available on demand
- **Badge Indicators**: Shows number of available insights per topic
- **Animated Interactions**: Smooth expand/collapse with rotating chevron icons
- **Community Engagement**: Encouraging messages to build a collaborative learning environment

### 🔍 Advanced Search Parameters
- **Source Type Selection**: Choose between General Web Search, News Articles, or Finance & Business sources
- **Time Range Filtering**: Filter results by recency (None, Past Day, Past Week, Past Month, Past Year)
- **Intelligent Search Guidance**: AI agents receive specific instructions based on your search preferences
- **Enhanced Research Quality**: More targeted and relevant results based on user-selected parameters

### 🔐 Firebase Authentication & User Management
- **Email/Password Authentication**: Secure user registration and login with email verification
- **Google Sign-in**: One-click authentication with Google accounts
- **Session Management**: Persistent login sessions with automatic token refresh and 15-minute timeout
- **User Dashboard**: Account information, usage statistics, and subscription management
- **Protected Routes**: Secure access to insight generation and personal data
- **Consistent Navigation**: Community link available across all pages including Generate Insights and Dashboard
- **Clean Auth Pages**: Dedicated authentication layouts with proper navigation
- **Automated Session Timeout**: Dual-layer session management with inactivity-based expiration

### 🌟 Social Features & Community
- **Public Sharing**: Insights are shared publicly by default (opt-out system)
- **One-Time Like System**: Users can like insights once with disabled state after liking
- **Author Attribution**: All insights display author name and email for credibility
- **Privacy Controls**: Authors can toggle sharing status on their own insights
- **Community Feed**: Browse and discover insights with sorting options (Recent, Trending, Most Liked, Featured)
- **Interactive Filters**: Easy navigation between different insight categories
- **Engagement Messaging**: Clear guidance on how likes help surface quality content

### 🤖 Multi-Agent AI System (CrewAI 0.134.0)
- **Research Agent**: Finds comprehensive, up-to-date information using advanced search tools with source-specific guidance
- **Validation Agent**: Checks source credibility and assigns confidence scores with improved accuracy
- **Insights Agent**: Creates meaningful analysis and actionable intelligence with enhanced reasoning
- **Enhanced Search Tool Compatibility**: Robust error handling with automatic fallback mechanisms

### 🎨 Modern Web Interface & UX (Flask 3.1.1)
- **Modern Light Theme**: Professional design with clean color scheme for optimal readability
- **Consistent Navigation**: Uniform navbar layout and menu structure across all pages
- **Enhanced Loading States**: Interactive buttons with "Generating Insights..." feedback
- **Real-time Processing**: Live updates during insight generation with progress indicators
- **Form Protection**: Prevents double submissions and accidental data loss
- **Authentication-Aware Navigation**: Dynamic navigation based on user login status with consistent Community access
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Interactive Sidebar**: Browse and manage previous insights with social indicators
- **Beautiful UI**: Airy, professional design with blue accent borders and smooth animations
- **Enhanced Security**: Latest Flask security features with Firebase authentication
- **Excellent Contrast**: Dark slate text on light background for easy reading

### 📊 Usage Statistics & Analytics
- **Comprehensive Tracking**: Multi-level usage metrics (daily, monthly, total)
- **Token-based Metering**: Accurate AI usage cost tracking with intelligent estimation
- **Plan-based Limits**: Free (20/month), Basic (100/month), Pro (500/month), Enterprise (unlimited)
- **Real-time Dashboard**: Visual progress bars, charts, and 7-day activity tracking
- **Proactive Warnings**: Usage alerts when approaching limits (80%+ quota used)
- **Historical Data**: 30-day rolling usage history with monthly breakdowns
- **Automated Management**: Monthly reset via Firebase Cloud Functions

### 📋 My Insights Management
- **Interactive Table**: Sortable table displaying all user's generated insights
- **Smart Sorting**: Click column headers to sort by Title (alphabetical), Tokens (numerical), or Date (chronological)
- **Rich Information**: View insight topics, token usage, processing time, and creation dates
- **Direct Actions**: Quick access to view full insights and toggle sharing status
- **Visual Feedback**: Modern table design with hover effects and sort indicators
- **Empty State Handling**: Friendly prompts for new users to generate their first insight
- **Real-time Updates**: Instant table updates when sharing status changes

### 📊 Intelligent Features
- **Advanced Confidence Scoring**: Enhanced validation algorithms with detailed metrics displayed in community
- **Source Attribution**: All claims linked to original sources with quality assessment
- **Quality Assessment**: Research quality ratings for transparency and reliability
- **Detailed Analysis**: Comprehensive 500-800 word reports with expandable content
- **Smart Previews**: 150-character summaries with full context available on toggle
- **Processing Metrics**: Token usage, timing and performance information with optimization insights

### 🔧 User Experience Enhancements
- **Smart Loading States**: Button becomes disabled and shows progress during insight generation
- **Form Validation**: Client-side validation with helpful error messages
- **Guest Access**: View shared insights without registration
- **Login-Protected Generation**: Insight creation requires user authentication
- **Topic Suggestions**: Clickable examples across multiple categories with trending topics
- **Custom Instructions**: Guide AI agents with specific requirements and constraints
- **Interactive Content**: Expandable detailed reports with smooth animations and space-efficient design
- **Insight Management**: Save, view, and delete your own insights with ownership controls
- **Download Reports**: Export insights as beautifully formatted HTML files with improved styling
- **Persistent Storage**: ✅ **Firestore integration fully implemented and working**

### 🐳 Docker & Deployment Support
- **Containerized Deployment**: Complete Docker support with multi-stage builds
- **Google Cloud Run**: Production-ready deployment configuration
- **Secret Management**: Secure credential handling via Google Cloud Secret Manager
- **Environment Templates**: Comprehensive configuration examples for all environments
- **CI/CD Ready**: Automated build and deployment pipelines

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd topic_insights

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies with latest versions
pip install -r requirements-firebase.txt
```

### 2. Environment Configuration

Create a `.env` file with your API keys:

```env
# Required: OpenAI API Key for CrewAI agents
OPENAI_API_KEY=your_openai_api_key_here

# Required: At least one search API key
TAVILY_API_KEY=your_tavily_api_key_here
SERPER_API_KEY=your_serper_api_key_here

# Optional: Flask configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development

# Optional: Google Cloud credentials for Firestore
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Firebase Configuration (for production)
FIREBASE_WEB_API_KEY=your_firebase_web_api_key
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
FIREBASE_MEASUREMENT_ID=your_measurement_id
```

### 3. Firebase Setup (Required for Authentication)

The application uses Firebase for user authentication. You'll need:

1. **Firebase Project**: Create a project at [Firebase Console](https://console.firebase.google.com)
2. **Authentication**: Enable Email/Password and Google sign-in methods
3. **Configuration**: The app is pre-configured for project `ai-biz-6b7ec`
4. **Service Account**: Set up Google Cloud service account for backend authentication

For production deployment, ensure the Firebase service account key is available via:
- Local development: `service-account-key.json` file
- Production: Google Cloud Secret Manager secret named `AI-Biz-Service-Account-Key`

### 4. PDF Export Setup (macOS)

PDF downloads require WeasyPrint system libraries. Install via Homebrew:

```bash
# Install system libraries
brew install pango gdk-pixbuf libffi

# Start Flask with PDF support
./run_flask.sh

# Or manually set library paths
export DYLD_LIBRARY_PATH="/opt/homebrew/lib"
python app.py
```

**Permanent setup**: Add to `~/.zshrc`:
```bash
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
```

For detailed PDF setup troubleshooting, refer to the WeasyPrint documentation or the installation guide above.

### 5. Run the Application

```bash
# Start with PDF support (recommended)
./run_flask.sh

# Or standard Flask development server
python3 app.py

# Or use Flask command (with latest CLI features)
flask run --debug --port 5001

# For production with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

Visit `http://localhost:5001` (Flask direct) or `http://localhost:5000` (Docker) to access the application.

### 6. Docker Deployment (Production Ready)

```bash
# Build the Docker image with multi-stage build
docker build --platform linux/amd64 -f Dockerfile.insight -t ai-insights-app .

# Run locally with Docker Compose (recommended for local testing)
docker-compose -f docker-compose.insight.yml up -d

# View container logs
docker-compose -f docker-compose.insight.yml logs -f

# Stop and remove containers
docker-compose -f docker-compose.insight.yml down

# Deploy to Google Cloud Run (production)
./build-insight-app.sh
```

The application will be available at `http://localhost:5000` when running with Docker.

### 6. PDF Export (WeasyPrint Dependencies)

The `/download/<insight_id>?format=pdf` route uses WeasyPrint, which in turn depends on several native graphics libraries (Pango, Cairo, GDK-PixBuf, libffi, etc.). If those libraries are missing, the server will disable PDF downloads and prompt you to either install the dependencies or download HTML instead.

**macOS (Homebrew):**

```bash
brew install pango cairo gdk-pixbuf libffi
```

**Ubuntu / Debian:**

```bash
sudo apt-get update
sudo apt-get install -y build-essential libpangocairo-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf2.0-0 libffi-dev
```

After the system libraries are installed, reinstall Python dependencies (or run `pip install weasyprint --force-reinstall`) inside your virtual environment. Restart the Flask server to re-enable PDF generation.

## 📱 How to Use

### 1. Authentication
1. **Sign Up**: Create account with email/password or Google sign-in
2. **Login**: Access your account and start generating insights
3. **Guest Mode**: Browse shared insights without authentication
4. **Dashboard**: View account info and usage statistics (accessible via user dropdown)

### 2. Generate Insights (Login Required)
1. **Enter a Topic**: Type your research topic (e.g., "AI in Healthcare 2025")
2. **Select Source Type**: Choose from General Web Search, News Articles, or Finance & Business
3. **Set Time Range** (Optional): Filter by recency - None (default), Past Day, Week, Month, or Year
4. **Add Instructions** (Optional): Provide specific guidance and constraints
5. **Click Generate**: Watch the enhanced loading state and progress feedback
6. **Wait for Completion**: Processing takes 45-120 seconds with real-time updates
7. **Review Results**: Explore insights with enhanced confidence scores and search parameters used
8. **Read Detailed Analysis**: Click "Read More" for comprehensive reports

### 3. Enhanced Community Experience (NEW)
- **Browse Community**: Visit the Community page to explore shared insights
- **Space-Efficient Viewing**: All insights start collapsed to save space and improve scanning
- **Expand Details**: Click "Show Details" button to see full insight context with confidence scores
- **Full-Width Display**: Expanded insights span the entire table width for optimal readability
- **Filter Content**: Use tabs to sort by Recent, Trending, Most Liked, or Featured insights
- **Engage with Content**: Like insights you find valuable to help surface quality content
- **Community Building**: Your likes help others discover great insights and strengthen the learning community

### 4. Social Features
- **Share Insights**: Your insights are public by default (toggle privacy in sidebar)
- **One-Time Likes**: Click heart buttons to like insights (disabled after liking)
- **Browse Community**: View insights from all users with interactive filtering
- **Author Information**: See who created each insight for credibility
- **Privacy Control**: Authors can make their insights private anytime

### 5. Manage Your Content
- **My Insights Table**: View all your insights in an organized, sortable table on the dashboard
- **Smart Sorting**: Click column headers to sort by Title, Tokens used, or Date created
- **Quick Actions**: View full insights or toggle sharing status directly from the table
- **Content Overview**: See insight count, token usage, and processing time at a glance
- **View Your Insights**: Your insights also appear in the sidebar with special indicators
- **Control Privacy**: Toggle sharing status on insights you authored
- **Delete Content**: Only you can delete your own insights
- **Download Reports**: Generate HTML reports with improved styling

## 🏗️ Architecture (Updated November 2025)

### Frontend
- **Bootstrap 5.3**: Latest responsive UI framework with new components
- **Font Awesome 6**: Updated icon library with social interaction symbols
- **Custom CSS3**: Modern gradient design with CSS Grid and Flexbox
- **Firebase SDK**: Client-side authentication and user management
- **Enhanced JavaScript**: Interactive features with toggleable content, real-time social updates and loading states

### Backend
- **Flask 3.1.1**: Latest Python web framework with improved security
- **Firebase Admin SDK**: Server-side authentication and user verification
- **CrewAI 0.134.0**: Advanced multi-agent AI system with enhanced capabilities
- **Firestore**: NoSQL database for user data and social features
- **Pydantic 2.11**: Type validation with improved performance
- **Google Cloud Integration**: Secret Manager, Cloud Run deployment support

### Authentication Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Firebase  │ -> │   Backend   │ -> │  Session    │ -> │  Protected  │
│Client Auth  │    │Token Verify │    │ Timeout     │    │   Routes    │
│(Frontend)   │    │(Flask)      │    │(15 min)     │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Community Features Pipeline
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Generate   │ -> │    Save     │ -> │   Share     │ -> │  Community  │
│  Insight    │    │  with User  │    │ with Like   │    │  Display    │
│             │    │    Data     │    │  Feature    │    │ (Toggleable)│
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Enhanced User Experience Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Form      │ -> │   Loading   │ -> │   Results   │ -> │  Community  │
│Validation & │    │States with  │    │with Social  │    │  Sharing    │
│ Protection  │    │ Feedback    │    │ Features    │    │ & Toggle    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Project Structure (Updated)
```
├── app.py                    # Main Flask application with auth integration
├── auth/                     # Authentication module
│   ├── __init__.py          # Auth blueprint registration
│   ├── firebase_auth.py     # Firebase authentication manager
│   ├── firestore_manager.py # User data management
│   └── routes.py            # Authentication routes
├── templates/               # Jinja2 templates with auth features
│   ├── base.html           # Base template with user navigation
│   ├── base_auth.html      # Clean auth template with consistent navigation
│   ├── index.html          # Home page with enhanced UX
│   ├── community.html      # Community page with toggleable insights (NEW)
│   ├── insights.html       # Insights display with social features
│   └── auth/               # Authentication templates
│       ├── login.html      # Login page with Firebase integration
│       ├── signup.html     # Registration with email verification
│       ├── dashboard.html  # User account dashboard
│       └── profile.html    # User profile management
├── static/                 # Static assets
├── requirements-firebase.txt # Optimized dependencies for Firebase
├── Dockerfile.insight      # Production Docker configuration
├── docker-compose.insight.yml # Docker Compose setup
├── build-insight-app.sh    # Google Cloud Run deployment script
├── environment-template.txt # Configuration template
├── service-account-key.json # Firebase service account (local dev)
├── .env                    # Environment variables
└── README.md              # This comprehensive documentation
```

### API Endpoints (Enhanced with Authentication)
- `GET /` - Home page with authentication-aware interface
- `POST /generate` - Generate insights (requires login) with loading states and usage tracking
- `GET /insights/<id>` - View specific insights with social data
- `POST /delete/<id>` - Delete insights (owner only)
- `GET /community` - Community page with toggleable insight details and filtering
- `GET /api/shared-insights` - JSON API for public insights
- `GET /api/my-insights` - Get current user's insights for dashboard table (requires login)
- `GET /api/usage-stats` - Get user's current usage statistics and limits
- `GET /api/dashboard-analytics` - Comprehensive dashboard analytics and metrics
- `POST /api/insights/<id>/like` - Like/unlike insights (requires login)
- `POST /api/insights/<id>/share` - Toggle privacy (author only)
- `GET /api/insights/trending` - Get trending insights for community feed
- `GET /api/insights/feed` - Paginated community feed with filtering
- `POST /auth/api/login` - Firebase authentication endpoint with session setup
- `POST /auth/api/signup` - User registration endpoint with session setup
- `GET /auth/dashboard` - User account dashboard with usage analytics and My Insights table
- `GET /auth/profile` - User profile management
- `GET /debug/insights` - Debug endpoint for troubleshooting
- `GET /status` - Health check and system status

## 🔐 Authentication & Security

### Firebase Authentication Setup
The application uses Firebase for secure user authentication:

1. **Client-side**: Firebase SDK handles login/signup with email or Google
2. **Server-side**: Firebase Admin SDK verifies tokens and manages sessions
3. **Session Management**: Flask sessions with automated 15-minute timeout and activity tracking
4. **Route Protection**: Decorators ensure only authenticated users can generate insights
5. **Dual-layer Timeout**: Server-side cleanup with client-side auto-logout for comprehensive session management

### Security Features
- **Token Verification**: All protected routes verify Firebase tokens
- **CSRF Protection**: Flask-WTF protection against cross-site requests
- **Session Security**: Secure cookie settings with automated timeout and expiration
- **Input Validation**: Pydantic models validate all user inputs
- **Error Handling**: Graceful error handling without exposing sensitive data
- **Secret Management**: Production secrets stored in Google Cloud Secret Manager
- **Usage Limits**: Plan-based rate limiting and quota enforcement for resource protection

### User Permissions
- **Public**: Browse shared insights, view community feed with toggleable details
- **Authenticated**: Generate insights, like content once per insight, manage privacy
- **Author**: Full control over own insights (edit privacy, delete)
- **Admin**: Future role for content moderation

## 🌟 Social Features Implementation

### Enhanced Community Platform
- **Toggleable Details**: Space-efficient design with expandable insight context
- **Full-Width Display**: Expanded insights span all table columns for maximum readability
- **Confidence Scoring**: Visual confidence badges with percentage display
- **Smart Filtering**: Recent, Trending, Most Liked, and Featured categories
- **Engagement Messaging**: Clear guidance on community participation and value of likes

### Sharing System
- **Default Public**: New insights are shared by default (opt-out model)
- **Privacy Toggle**: Authors can make insights private anytime
- **Author Attribution**: All insights show creator's name and email
- **Guest Access**: Non-authenticated users can browse public content

### Like System
- **One-Time Interaction**: Users can like each insight once with disabled state after liking
- **User Tracking**: Prevents duplicate likes from same user
- **Atomic Operations**: Firestore transactions ensure data consistency
- **Login Required**: Only authenticated users can like content

### Enhanced User Experience
- **Loading States**: Buttons provide clear feedback during operations
- **Form Validation**: Prevents errors before they occur
- **Progress Indicators**: Keep users informed during long operations
- **Double-click Protection**: Prevents accidental duplicate submissions
- **Graceful Error Handling**: User-friendly error messages and recovery
- **Interactive Toggles**: Smooth expand/collapse animations with visual feedback

### Data Model
```python
# Enhanced GeneratedInsights with social features and search parameters
{
    "id": "unique_id",
    "topic": "Research topic",
    "source_type": "finance",  # general, news, or finance
    "time_range": "week",      # none, day, week, month, or year
    "instructions": "User-provided guidance",
    "insights": [              # List of InsightItem objects with confidence scores
        {
            "title": "Insight title",
            "summary": "Detailed summary",
            "confidence_score": 0.90,  # 0-1 scale for percentage display
            "key_points": ["point1", "point2"],
            "detailed_report": "Full analysis",
            "significance": "Why this matters",
            "sources": ["url1", "url2"]
        }
    ],
    "author_id": "firebase_user_id",
    "author_name": "User Name",
    "author_email": "user@example.com",
    "is_shared": true,  # Default public sharing
    "likes": 15,
    "liked_by": ["user1", "user2", ...],
    "created_at": "2025-01-26T12:00:00Z",
    "updated_at": "2025-01-26T12:00:00Z"
}

# User document with comprehensive usage tracking
{
    "id": "firebase_user_id",
    "email": "user@example.com",
    "name": "User Name",
    "usage": {
        "insights_generated": 15,
        "total_tokens_used": 45000,
        "current_month": "2025-01",
        "insights_remaining": 5,
        "monthly_breakdown": {
            "2025-01": {
                "insights": 15,
                "tokens": 45000,
                "search_requests": 45,
                "days_active": 8
            }
        },
        "daily_usage": {
            "2025-01-26": {
                "insights": 3,
                "tokens": 8500,
                "search_requests": 9
            }
        }
    },
    "limits": {
        "monthly_insights": 20,  # Plan-based limits
        "monthly_tokens": 100000,
        "daily_insights": 5,
        "rate_limit_per_hour": 10
    },
    "last_activity": "2025-01-26T12:00:00Z"
}
```

## 🐳 Docker Deployment

### Local Development with Docker

**Quick Start:**
```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.insight.yml up --build

# Run in detached mode (background)
docker-compose -f docker-compose.insight.yml up -d

# View logs
docker-compose -f docker-compose.insight.yml logs -f

# Stop and clean up
docker-compose -f docker-compose.insight.yml down
```

**Rebuild After Code Changes:**
```bash
# Rebuild with no cache (ensures fresh build)
docker-compose -f docker-compose.insight.yml build --no-cache
docker-compose -f docker-compose.insight.yml up -d
```

The application will be available at `http://localhost:5000`.

### Production Deployment to Google Cloud Run

**Automated Deployment (Recommended):**
```bash
# Run the complete deployment script
chmod +x build-insight-app.sh
./build-insight-app.sh
```

The script automatically handles:
- Service account creation and IAM permissions
- API enablement (Firebase, Firestore, Identity Toolkit)
- Docker image building with multi-stage optimization
- Container Registry push
- Cloud Run service deployment with auto-scaling

**Manual Deployment:**
```bash
# Build Docker image
docker build --platform linux/amd64 -f Dockerfile.insight -t gcr.io/[PROJECT_ID]/ai-insights-app .

# Push to Google Container Registry
docker push gcr.io/[PROJECT_ID]/ai-insights-app

# Deploy to Cloud Run
gcloud run deploy ai-insights-app \
  --image gcr.io/[PROJECT_ID]/ai-insights-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300
```

### Docker Configuration Features
- **Multi-stage builds**: Frontend (Node.js + Vite) → Backend (Python + Flask) for optimized image size
- **Production server**: Gunicorn with 4 workers for concurrent request handling
- **Security**: Non-root user, minimal attack surface, secure credential handling
- **Environment variables**: Flexible configuration for dev/staging/production environments
- **Health checks**: Built-in `/status` endpoint for monitoring and auto-healing
- **Port configuration**: Automatic port detection for Cloud Run (PORT environment variable)
- **Secret management**: Google Cloud Secret Manager integration for sensitive credentials

## 🧪 Testing (Comprehensive 2025 Suite)

### ✅ Verified Working Features
All features have been thoroughly tested:

1. **Firebase Authentication**: ✅ Email/password and Google sign-in working
2. **User Sessions**: ✅ Persistent login with automatic token refresh and 15-minute timeout
3. **Usage Statistics**: ✅ Comprehensive tracking with multi-tier subscription plans
4. **Session Timeout Management**: ✅ Automated 15-minute inactivity-based expiration
5. **Advanced Search Parameters**: ✅ Source type and time range filtering working
6. **Search Tool Fallback**: ✅ Robust error handling and automatic fallback mechanisms
7. **Social Features**: ✅ One-time like system and privacy controls functional
8. **Public Sharing**: ✅ Guest access to community insights
9. **Protected Routes**: ✅ Login requirements properly enforced
10. **Web Interface**: ✅ Responsive UI with modern light theme and consistent navigation
11. **Insight Generation**: ✅ Multi-agent AI with user attribution and search guidance
12. **Firestore Storage**: ✅ User data, social features, and search parameters persisted correctly
13. **Firestore Integration**: ✅ Fixed circular import issue - profile updates now working properly
14. **Error Handling**: ✅ Comprehensive error recovery and user feedback
15. **Loading States**: ✅ Interactive buttons with progress feedback
16. **Form Protection**: ✅ Double-submission prevention and validation
17. **Docker Deployment**: ✅ Containerized deployment working
18. **Health Monitoring**: ✅ System status endpoint for monitoring
19. **Dependency Management**: ✅ All required packages properly installed
20. **Usage Dashboard**: ✅ Real-time analytics with visual progress tracking
21. **Plan-based Limits**: ✅ Quota enforcement and proactive warnings
22. **My Insights Table**: ✅ Interactive sortable table with column sorting functionality
23. **Insights Management**: ✅ View, sort, and manage user insights efficiently
24. **UI/UX Consistency**: ✅ Consistent navbar width and menu structure across all pages

### Authentication Testing
- [x] Email/password registration and login
- [x] Google sign-in integration
- [x] Email verification workflow
- [x] Session persistence across browser restarts
- [x] Token refresh and expiration handling
- [x] Logout functionality
- [x] 15-minute session timeout with automatic logout
- [x] Activity tracking and session renewal
- [x] Dual-layer timeout (server + client-side)

### Community Platform Testing
- [x] Toggleable insight details functionality
- [x] Full-width insight display across table columns
- [x] Confidence score display with percentage formatting
- [x] Smooth expand/collapse animations
- [x] Space-efficient collapsed state
- [x] Navigation consistency across all templates
- [x] Community engagement messaging
- [x] Filter tabs (Recent, Trending, Most Liked, Featured)

### Social Features Testing
- [x] Default public sharing of new insights
- [x] One-time like button functionality with disabled state
- [x] Privacy toggle for insight authors
- [x] Guest user access to public content
- [x] Author information display
- [x] Real-time UI updates for social interactions
- [x] Most Liked filter with proper sorting

### UX Enhancement Testing
- [x] Loading button states during insight generation
- [x] Form validation and error prevention
- [x] Double-submission protection
- [x] Progress feedback and user communication
- [x] Topic suggestion functionality
- [x] Character counters and form helpers
- [x] Toggleable content with smooth animations

### Search Parameters Testing
- [x] Source type dropdown (General, News, Finance & Business)
- [x] Time range dropdown (None, Day, Week, Month, Year)
- [x] Default values and form state management
- [x] AI agent guidance based on search parameters
- [x] Search parameters display in generated insights
- [x] Backend parameter processing and validation

### Usage Statistics Testing
- [x] Real-time usage tracking and metrics collection
- [x] Token-based metering with intelligent estimation
- [x] Plan-based limit enforcement (Free, Basic, Pro, Enterprise)
- [x] Monthly and daily usage breakdowns
- [x] Proactive warnings when approaching limits
- [x] Usage dashboard with visual progress indicators
- [x] Historical data retention and monthly reset functionality

### Search Tool Compatibility Testing
- [x] TavilySearchTool initialization error handling
- [x] Automatic fallback to SerperDevTool when Tavily fails
- [x] Graceful degradation when search tools unavailable
- [x] User-friendly error messages for search tool issues
- [x] Comprehensive logging for debugging search problems

### My Insights Table Testing
- [x] Table loads automatically on dashboard access
- [x] Column sorting functionality (Title, Tokens, Date)
- [x] Sort direction indicators with visual feedback
- [x] Empty state display with call-to-action
- [x] Loading states during data fetch
- [x] Error handling with retry functionality
- [x] View insight button navigation
- [x] Share toggle functionality with immediate updates
- [x] Responsive table design on all screen sizes
- [x] User-specific data filtering (author_id based)

### UI/UX Consistency Testing
- [x] Modern light theme applied across all pages
- [x] Navbar width consistency (Home, Insights, Generate, Dashboard)
- [x] Navigation menu structure uniform across all pages
- [x] "Insights" link present on all pages
- [x] Color scheme consistency (#F8FAFC background, #2563EB blue accents)
- [x] Text contrast and readability optimized
- [x] Blue accent borders replacing gradient backgrounds
- [x] Professional, airy design maintained throughout

### Firestore Integration Testing
- [x] Profile updates properly persist to database
- [x] Circular import issue resolved in auth routes
- [x] All 8 auth routes using correct Firestore access pattern
- [x] Login/signup user data creation working
- [x] Dashboard data loading correctly
- [x] Session management with proper Firestore integration
- [x] Activity tracking and usage statistics persisting

## 🆘 Troubleshooting (Updated November 2025)

### Common Issues

#### Community Platform Issues
- **Toggle not working**: Ensure JavaScript is enabled and try refreshing the page
- **Insights not expanding**: Check browser console for JavaScript errors
- **Details showing incorrectly**: Clear browser cache and reload the page
- **Navigation missing Community link**: Verify you're using updated templates

#### Dependency Issues
- **"ModuleNotFoundError: google.cloud.secretmanager"**: Install missing dependency with `pip3 install google-cloud-secret-manager`
- **Import errors**: Ensure all packages from `requirements-firebase.txt` are installed
- **Version conflicts**: Use the specific versions in the requirements file

#### Authentication Issues
- **"Login failed"**: Check Firebase configuration and internet connection
- **"Invalid token"**: Clear browser cache and try logging in again
- **"Email not verified"**: Check email inbox for verification link
- **Google sign-in popup blocked**: Allow popups for the application domain

#### Social Features Issues
- **Like button not working**: Ensure you're logged in and try refreshing
- **Like button not disabling**: Check that you haven't already liked the insight
- **Privacy toggle not saving**: Check network connection and try again
- **Can't see own insights**: Verify you're logged in with the correct account
- **Delete button missing**: Only insight authors can delete their content

#### Loading State Issues
- **Button stuck in loading state**: Refresh the page to reset the form
- **Form not submitting**: Check browser console for JavaScript errors
- **Double submission**: The protection is working correctly - wait for processing
- **Empty topic error**: Ensure the topic field has content before submitting

#### My Insights Table Issues
- **Table not loading**: Check authentication status and refresh the page
- **Sorting not working**: Ensure JavaScript is enabled and try clearing browser cache
- **Empty table despite having insights**: Verify you're logged in with the correct account
- **Share toggle not responding**: Check network connection and try again
- **View button not working**: Ensure insight ID is valid and try refreshing the page

#### Firebase Connection Issues
- **"Failed to get credentials"**: Ensure service account key is properly configured
- **Secret Manager errors**: Verify Google Cloud project permissions
- **Firestore write errors**: Check database rules and authentication
- **Index errors**: Follow the provided URL to create required Firestore indexes
- **"Profile updated (not persisted - Firestore unavailable)"**: ✅ FIXED - This was caused by circular import issue, now resolved
- **Firestore connection working but showing unavailable**: Ensure using `current_app.extensions.get('firestore_manager')` pattern

#### "OpenAI API key is required"
- Ensure `OPENAI_API_KEY` is set correctly in `.env`
- Verify API key validity and sufficient credits
- Check for correct OpenAI account permissions

#### "At least one search API key required"
- Set either `TAVILY_API_KEY` or `SERPER_API_KEY`
- Verify API keys are active and have remaining quota
- Test API keys independently using curl or Postman

#### Search Tool Configuration Issues
- **"TavilyClient proxies error"**: The system automatically falls back to SerperDevTool
- **"Search tool configuration issue detected"**: Refresh the page and try again
- **Limited search capabilities**: Ensure at least one search API key is properly configured
- **Search parameters not working**: Check that dropdown selections are properly saved in form state

#### Performance Issues
- **Slow insight generation**: Normal processing time 45-120 seconds
- **Page load delays**: Check network connection and clear browser cache
- **Social features lag**: Firestore operations may take 1-2 seconds
- **High token usage**: Monitor OpenAI dashboard for usage patterns
- **Toggle animations slow**: Check browser performance and disable animations if needed

#### Docker Issues
- **Build failures**: Ensure all dependencies are available and Docker has sufficient resources
- **Port conflicts**: Use different ports if 5001 is already in use
- **Permission errors**: Ensure Docker has proper file access permissions
- **Environment variables**: Verify all required variables are set in docker-compose file

### Getting Help
- Check browser console for JavaScript errors
- Review application logs for detailed error messages
- Verify all environment variables are properly set
- Test Firebase authentication in browser developer tools
- Check Google Cloud Console for service status and quotas
- Use the `/debug/insights` endpoint to troubleshoot data issues
- Check the `/status` endpoint for system health information

### Debug Endpoints
- `GET /debug/insights` - Shows Firestore connection status and insight counts
- `GET /status` - Comprehensive system health check
- Browser Console - Check for JavaScript errors and form validation issues

## 🔮 Future Enhancements (2025 Roadmap)

### Short Term (Q1-Q2 2025) - ✅ COMPLETED
- **User Authentication**: ✅ Firebase authentication implemented
- **Social Features**: ✅ One-time like system and privacy controls working
- **Community Feed**: ✅ Browse insights from all users with toggleable details
- **User Profiles**: ✅ Basic author attribution implemented
- **Loading States**: ✅ Enhanced UX with progress feedback
- **Docker Support**: ✅ Production-ready containerization
- **Dependency Management**: ✅ Optimized package requirements
- **Community Platform**: ✅ Toggleable insight details with full-width display
- **Navigation Consistency**: ✅ Community link across all templates

### Medium Term (Q3-Q4 2025)
- **Enhanced User Profiles**: Detailed profile pages with user statistics
- **Comment System**: Allow users to comment on insights
- **Follow System**: Follow favorite authors and get notifications
- **Advanced Search**: Search insights by topic, author, or content
- **Collections**: Users can organize insights into themed collections
- **Trending Topics**: Highlight popular research areas
- **Real-time Notifications**: Live updates for likes and comments
- **Improved Loading UX**: Progress bars and estimated completion times
- **Bulk Actions**: Select multiple insights for batch operations

### Long Term (2026+)
- **Real-time Collaboration**: Co-create insights with team members
- **Enterprise Features**: Team workspaces, admin controls, analytics
- **AI Recommendations**: Suggest related insights and topics
- **Mobile App**: Native iOS and Android applications
- **Integration Hub**: Connect with popular research and business tools
- **Advanced Analytics**: Insight engagement metrics and trending analysis
- **Voice Integration**: Generate insights via voice commands
- **API Platform**: Public API for third-party integrations

---

**Powered by Firebase Authentication, CrewAI 0.134.0 Multi-Agent System, Flask 3.1.1 & Docker** 🔐🤖✨🐳

*Last Updated: November 2025 - Now featuring modern light theme design with professional color scheme, consistent navigation across all pages, critical Firestore integration fixes for proper data persistence, advanced search parameters with source type filtering (General, News, Finance & Business) and time range controls, enhanced search tool error handling with robust fallback mechanisms, health monitoring endpoint, interactive My Insights table with sortable columns for better insights management, and production-ready infrastructure for collaborative AI insights generation.* 
