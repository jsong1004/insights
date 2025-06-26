# 🧠 AI Insights Generator - Flask Web App

A powerful social web application that uses CrewAI's multi-agent system to generate intelligent insights on any topic. Users can sign up, log in, and share insights with the community while building their personal research library.

**Latest Update (June 2025)**: Now featuring advanced search parameters with source type filtering (General, News, Finance & Business) and time range controls (None, Day, Week, Month, Year), enhanced error handling for search tool compatibility, robust fallback mechanisms, and a health check endpoint for monitoring. Running on Flask 3.1.1 with CrewAI 0.134.0 for enhanced performance, user management, and collaborative insights.

## ✨ Features

### 🔍 Advanced Search Parameters (NEW)
- **Source Type Selection**: Choose between General Web Search, News Articles, or Finance & Business sources
- **Time Range Filtering**: Filter results by recency (None, Past Day, Past Week, Past Month, Past Year)
- **Intelligent Search Guidance**: AI agents receive specific instructions based on your search preferences
- **Enhanced Research Quality**: More targeted and relevant results based on user-selected parameters

### 🔐 Firebase Authentication & User Management
- **Email/Password Authentication**: Secure user registration and login with email verification
- **Google Sign-in**: One-click authentication with Google accounts
- **Session Management**: Persistent login sessions with automatic token refresh
- **User Dashboard**: Account information, usage statistics, and subscription management
- **Protected Routes**: Secure access to insight generation and personal data
- **Clean Auth Pages**: Dedicated authentication layouts without distracting sidebars

### 🌟 Social Features & Community
- **Public Sharing**: Insights are shared publicly by default (opt-out system)
- **Like System**: Users can like insights with real-time heart button interactions
- **Author Attribution**: All insights display author name and email for credibility
- **Privacy Controls**: Authors can toggle sharing status on their own insights
- **Community Feed**: Browse and discover insights from other users
- **User Profiles**: View insights by specific authors

### 🤖 Multi-Agent AI System (CrewAI 0.134.0)
- **Research Agent**: Finds comprehensive, up-to-date information using advanced search tools with source-specific guidance
- **Validation Agent**: Checks source credibility and assigns confidence scores with improved accuracy
- **Insights Agent**: Creates meaningful analysis and actionable intelligence with enhanced reasoning
- **Enhanced Search Tool Compatibility**: Robust error handling with automatic fallback mechanisms

### 🎨 Modern Web Interface & UX (Flask 3.1.1)
- **Enhanced Loading States**: Interactive buttons with "Generating Insights..." feedback
- **Real-time Processing**: Live updates during insight generation with progress indicators
- **Form Protection**: Prevents double submissions and accidental data loss
- **Authentication-Aware Navigation**: Dynamic navigation based on user login status
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Interactive Sidebar**: Browse and manage previous insights with social indicators
- **Beautiful UI**: Modern gradient design with smooth animations and accessibility features
- **Enhanced Security**: Latest Flask security features with Firebase authentication

### 📊 Intelligent Features
- **Advanced Confidence Scoring**: Enhanced validation algorithms with detailed metrics
- **Source Attribution**: All claims linked to original sources with quality assessment
- **Quality Assessment**: Research quality ratings for transparency and reliability
- **Detailed Analysis**: Comprehensive 500-800 word reports with "Read More" functionality
- **Smart Previews**: 200-character previews with expandable full content
- **Processing Metrics**: Token usage, timing and performance information with optimization insights

### 🔧 User Experience Enhancements
- **Smart Loading States**: Button becomes disabled and shows progress during insight generation
- **Form Validation**: Client-side validation with helpful error messages
- **Guest Access**: View shared insights without registration
- **Login-Protected Generation**: Insight creation requires user authentication
- **Topic Suggestions**: Clickable examples across multiple categories with trending topics
- **Custom Instructions**: Guide AI agents with specific requirements and constraints
- **Interactive Content**: Expandable detailed reports with smooth animations
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

### 4. Run the Application

```bash
# Start the Flask development server
python3 app.py

# Or use Flask command (with latest CLI features)
flask run --debug --port 5001

# For production with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

Visit `http://localhost:5001` to access the application.

### 5. Docker Deployment (Production Ready)

```bash
# Build the Docker image
docker build --platform linux/amd64 -f Dockerfile.insight -t ai-insights-app .

# Run locally with Docker
docker-compose -f docker-compose.insight.yml up

# Deploy to Google Cloud Run
./build-insight-app.sh
```

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

### 3. Enhanced User Experience
- **Loading Feedback**: Button shows "Generating Insights..." with spinning icon
- **Form Protection**: Prevents accidental double submissions
- **Progress Updates**: Flash messages keep you informed during processing
- **Error Prevention**: Client-side validation prevents common mistakes
- **Topic Suggestions**: Click example topics to auto-fill the form

### 4. Social Features
- **Share Insights**: Your insights are public by default (toggle privacy in sidebar)
- **Like Content**: Click heart buttons to like insights from other users
- **Browse Community**: View insights from all users in the main feed
- **Author Information**: See who created each insight for credibility
- **Privacy Control**: Authors can make their insights private anytime

### 5. Manage Your Content
- **View Your Insights**: Your insights appear in the sidebar with special indicators
- **Control Privacy**: Toggle sharing status on insights you authored
- **Delete Content**: Only you can delete your own insights
- **Download Reports**: Generate HTML reports with improved styling

## 🏗️ Architecture (Updated January 2025)

### Frontend
- **Bootstrap 5.3**: Latest responsive UI framework with new components
- **Font Awesome 6**: Updated icon library with social interaction symbols
- **Custom CSS3**: Modern gradient design with CSS Grid and Flexbox
- **Firebase SDK**: Client-side authentication and user management
- **Enhanced JavaScript**: Interactive features with real-time social updates and loading states

### Backend
- **Flask 3.1.1**: Latest Python web framework with improved security
- **Firebase Admin SDK**: Server-side authentication and user verification
- **CrewAI 0.134.0**: Advanced multi-agent AI system with enhanced capabilities
- **Firestore**: NoSQL database for user data and social features
- **Pydantic 2.11**: Type validation with improved performance
- **Google Cloud Integration**: Secret Manager, Cloud Run deployment support

### Authentication Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Firebase  │ -> │   Backend   │ -> │  Protected  │
│Client Auth  │    │Token Verify │    │   Routes    │
│(Frontend)   │    │(Flask)      │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Social Features Pipeline
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Generate   │ -> │    Save     │ -> │   Share     │
│  Insight    │    │  with User  │    │ with Like   │
│             │    │    Data     │    │  Feature    │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Enhanced User Experience Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Form      │ -> │   Loading   │ -> │   Results   │
│Validation & │    │States with  │    │with Social  │
│ Protection  │    │ Feedback    │    │ Features    │
└─────────────┘    └─────────────┘    └─────────────┘
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
│   ├── base_auth.html      # Clean auth template without sidebar
│   ├── index.html          # Home page with enhanced UX
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
- `POST /generate` - Generate insights (requires login) with loading states
- `GET /insights/<id>` - View specific insights with social data
- `POST /delete/<id>` - Delete insights (owner only)
- `GET /api/shared-insights` - JSON API for public insights
- `POST /api/insights/<id>/like` - Like/unlike insights (requires login)
- `POST /api/insights/<id>/share` - Toggle privacy (author only)
- `POST /auth/api/login` - Firebase authentication endpoint
- `POST /auth/api/signup` - User registration endpoint
- `GET /auth/dashboard` - User account dashboard
- `GET /auth/profile` - User profile management
- `GET /debug/insights` - Debug endpoint for troubleshooting
- `GET /status` - Health check and system status

## 🔐 Authentication & Security

### Firebase Authentication Setup
The application uses Firebase for secure user authentication:

1. **Client-side**: Firebase SDK handles login/signup with email or Google
2. **Server-side**: Firebase Admin SDK verifies tokens and manages sessions
3. **Session Management**: Flask sessions with 30-day persistence
4. **Route Protection**: Decorators ensure only authenticated users can generate insights

### Security Features
- **Token Verification**: All protected routes verify Firebase tokens
- **CSRF Protection**: Flask-WTF protection against cross-site requests
- **Session Security**: Secure cookie settings and automatic expiration
- **Input Validation**: Pydantic models validate all user inputs
- **Error Handling**: Graceful error handling without exposing sensitive data
- **Secret Management**: Production secrets stored in Google Cloud Secret Manager

### User Permissions
- **Public**: Browse shared insights, view community feed
- **Authenticated**: Generate insights, like content, manage privacy
- **Author**: Full control over own insights (edit privacy, delete)
- **Admin**: Future role for content moderation

## 🌟 Social Features Implementation

### Sharing System
- **Default Public**: New insights are shared by default (opt-out model)
- **Privacy Toggle**: Authors can make insights private anytime
- **Author Attribution**: All insights show creator's name and email
- **Guest Access**: Non-authenticated users can browse public content

### Like System
- **Real-time Interaction**: Heart buttons with immediate visual feedback
- **User Tracking**: Prevents duplicate likes from same user
- **Atomic Operations**: Firestore transactions ensure data consistency
- **Login Required**: Only authenticated users can like content

### Enhanced User Experience
- **Loading States**: Buttons provide clear feedback during operations
- **Form Validation**: Prevents errors before they occur
- **Progress Indicators**: Keep users informed during long operations
- **Double-click Protection**: Prevents accidental duplicate submissions
- **Graceful Error Handling**: User-friendly error messages and recovery

### Data Model
```python
# Enhanced GeneratedInsights with social features and search parameters
{
    "id": "unique_id",
    "topic": "Research topic",
    "source_type": "finance",  # general, news, or finance
    "time_range": "week",      # none, day, week, month, or year
    "instructions": "User-provided guidance",
    "content": "Generated insight",
    "author_id": "firebase_user_id",
    "author_name": "User Name",
    "author_email": "user@example.com",
    "is_shared": true,  # Default public sharing
    "likes": 15,
    "liked_by": ["user1", "user2", ...],
    "created_at": "2025-01-26T12:00:00Z",
    "updated_at": "2025-01-26T12:00:00Z"
}
```

## 🐳 Docker Deployment

### Local Development with Docker
```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.insight.yml up --build

# View logs
docker-compose -f docker-compose.insight.yml logs -f

# Stop and clean up
docker-compose -f docker-compose.insight.yml down
```

### Production Deployment to Google Cloud Run
```bash
# Run the deployment script
chmod +x build-insight-app.sh
./build-insight-app.sh

# Or deploy manually
gcloud run deploy ai-insights-app \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Docker Configuration
- **Multi-stage builds**: Optimized image size and build time
- **Security**: Non-root user and minimal attack surface
- **Environment variables**: Flexible configuration for different environments
- **Health checks**: Built-in health monitoring
- **Port configuration**: Automatic port detection for Cloud Run

## 🧪 Testing (Comprehensive 2025 Suite)

### ✅ Verified Working Features
All features have been thoroughly tested:

1. **Firebase Authentication**: ✅ Email/password and Google sign-in working
2. **User Sessions**: ✅ Persistent login with automatic token refresh
3. **Advanced Search Parameters**: ✅ Source type and time range filtering working
4. **Search Tool Fallback**: ✅ Robust error handling and automatic fallback mechanisms
5. **Social Features**: ✅ Like system and privacy controls functional
6. **Public Sharing**: ✅ Guest access to community insights
7. **Protected Routes**: ✅ Login requirements properly enforced
8. **Web Interface**: ✅ Responsive UI with authentication integration
9. **Insight Generation**: ✅ Multi-agent AI with user attribution and search guidance
10. **Firestore Storage**: ✅ User data, social features, and search parameters persisted
11. **Error Handling**: ✅ Comprehensive error recovery and user feedback
12. **Loading States**: ✅ Interactive buttons with progress feedback
13. **Form Protection**: ✅ Double-submission prevention and validation
14. **Docker Deployment**: ✅ Containerized deployment working
15. **Health Monitoring**: ✅ System status endpoint for monitoring
16. **Dependency Management**: ✅ All required packages properly installed

### Authentication Testing
- [x] Email/password registration and login
- [x] Google sign-in integration
- [x] Email verification workflow
- [x] Session persistence across browser restarts
- [x] Token refresh and expiration handling
- [x] Logout functionality

### Social Features Testing
- [x] Default public sharing of new insights
- [x] Like button functionality and counters
- [x] Privacy toggle for insight authors
- [x] Guest user access to public content
- [x] Author information display
- [x] Real-time UI updates for social interactions

### UX Enhancement Testing
- [x] Loading button states during insight generation
- [x] Form validation and error prevention
- [x] Double-submission protection
- [x] Progress feedback and user communication
- [x] Topic suggestion functionality
- [x] Character counters and form helpers

### Search Parameters Testing
- [x] Source type dropdown (General, News, Finance & Business)
- [x] Time range dropdown (None, Day, Week, Month, Year)
- [x] Default values and form state management
- [x] AI agent guidance based on search parameters
- [x] Search parameters display in generated insights
- [x] Backend parameter processing and validation

### Search Tool Compatibility Testing
- [x] TavilySearchTool initialization error handling
- [x] Automatic fallback to SerperDevTool when Tavily fails
- [x] Graceful degradation when search tools unavailable
- [x] User-friendly error messages for search tool issues
- [x] Comprehensive logging for debugging search problems

## 🆘 Troubleshooting (Updated June 2025)

### Common Issues

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
- **Privacy toggle not saving**: Check network connection and try again
- **Can't see own insights**: Verify you're logged in with the correct account
- **Delete button missing**: Only insight authors can delete their content

#### Loading State Issues
- **Button stuck in loading state**: Refresh the page to reset the form
- **Form not submitting**: Check browser console for JavaScript errors
- **Double submission**: The protection is working correctly - wait for processing
- **Empty topic error**: Ensure the topic field has content before submitting

#### Firebase Connection Issues
- **"Failed to get credentials"**: Ensure service account key is properly configured
- **Secret Manager errors**: Verify Google Cloud project permissions
- **Firestore write errors**: Check database rules and authentication
- **Index errors**: Follow the provided URL to create required Firestore indexes

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
- **Social Features**: ✅ Public sharing and like system working
- **Community Feed**: ✅ Browse insights from all users
- **User Profiles**: ✅ Basic author attribution implemented
- **Loading States**: ✅ Enhanced UX with progress feedback
- **Docker Support**: ✅ Production-ready containerization
- **Dependency Management**: ✅ Optimized package requirements

### Medium Term (Q3-Q4 2025)
- **Enhanced User Profiles**: Detailed profile pages with user statistics
- **Comment System**: Allow users to comment on insights
- **Follow System**: Follow favorite authors and get notifications
- **Advanced Search**: Search insights by topic, author, or content
- **Collections**: Users can organize insights into themed collections
- **Trending Topics**: Highlight popular research areas
- **Real-time Notifications**: Live updates for likes and comments
- **Improved Loading UX**: Progress bars and estimated completion times

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

*Last Updated: June 2025 - Now featuring advanced search parameters with source type filtering (General, News, Finance & Business) and time range controls, enhanced search tool error handling with robust fallback mechanisms, health monitoring endpoint, and production-ready infrastructure for collaborative AI insights generation.* 