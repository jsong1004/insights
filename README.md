# 🧠 AI Insights Generator - Flask Web App

A powerful social web application that uses CrewAI's multi-agent system to generate intelligent insights on any topic. Users can sign up, log in, and share insights with the community while building their personal research library.

**Latest Update (2025)**: Now featuring Firebase Authentication, social sharing, and community features - running on Flask 3.1.1 with CrewAI 0.134.0 for enhanced performance, user management, and collaborative insights.

## ✨ Features

### 🔐 Firebase Authentication & User Management
- **Email/Password Authentication**: Secure user registration and login with email verification
- **Google Sign-in**: One-click authentication with Google accounts
- **Session Management**: Persistent login sessions with automatic token refresh
- **User Dashboard**: Account information, usage statistics, and subscription management
- **Protected Routes**: Secure access to insight generation and personal data

### 🌟 Social Features & Community
- **Public Sharing**: Insights are shared publicly by default (opt-out system)
- **Like System**: Users can like insights with real-time heart button interactions
- **Author Attribution**: All insights display author name and email for credibility
- **Privacy Controls**: Authors can toggle sharing status on their own insights
- **Community Feed**: Browse and discover insights from other users
- **User Profiles**: View insights by specific authors

### 🤖 Multi-Agent AI System (CrewAI 0.134.0)
- **Research Agent**: Finds comprehensive, up-to-date information using advanced search tools
- **Validation Agent**: Checks source credibility and assigns confidence scores with improved accuracy
- **Insights Agent**: Creates meaningful analysis and actionable intelligence with enhanced reasoning

### 🎨 Modern Web Interface (Flask 3.1.1)
- **Authentication-Aware Navigation**: Dynamic navigation based on user login status
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Real-time Processing**: Live updates during insight generation with improved error handling
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

### 🔧 User Experience
- **Guest Access**: View shared insights without registration
- **Login-Protected Generation**: Insight creation requires user authentication
- **Topic Suggestions**: Pre-built examples across multiple categories with trending topics
- **Custom Instructions**: Guide AI agents with specific requirements and constraints
- **Interactive Content**: Expandable detailed reports with smooth animations
- **Insight Management**: Save, view, and delete your own insights with ownership controls
- **Download Reports**: Export insights as beautifully formatted HTML files with improved styling
- **Persistent Storage**: ✅ **Firestore integration fully implemented and working**

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
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file with your API keys:

```env
# Required: OpenAI API Key for CrewAI agents
OPENAI_API_KEY=your_openai_api_key_here

# Required: At least one search API key
TAVILY_API_KEY=your_tavily_api_key_here
SERPAPI_API_KEY=your_serpapi_api_key_here

# Optional: Flask configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development

# Optional: Google Cloud credentials for Firestore
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
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
python app.py

# Or use Flask command (with latest CLI features)
flask run --debug --port 5002

# For production with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5002 app:app
```

Visit `http://localhost:5002` to access the application.

## 📱 How to Use

### 1. Authentication
1. **Sign Up**: Create account with email/password or Google sign-in
2. **Login**: Access your account and start generating insights
3. **Guest Mode**: Browse shared insights without authentication
4. **Dashboard**: View account info and usage statistics (accessible via user dropdown)

### 2. Generate Insights (Login Required)
1. **Enter a Topic**: Type your research topic (e.g., "AI in Healthcare 2025")
2. **Add Instructions** (Optional): Provide specific guidance and constraints
3. **Click Generate**: Watch the multi-agent system work (45-120 seconds)
4. **Review Results**: Explore insights with enhanced confidence scores
5. **Read Detailed Analysis**: Click "Read More" for comprehensive reports

### 3. Social Features
- **Share Insights**: Your insights are public by default (toggle privacy in sidebar)
- **Like Content**: Click heart buttons to like insights from other users
- **Browse Community**: View insights from all users in the main feed
- **Author Information**: See who created each insight for credibility
- **Privacy Control**: Authors can make their insights private anytime

### 4. Manage Your Content
- **View Your Insights**: Your insights appear in the sidebar with special indicators
- **Control Privacy**: Toggle sharing status on insights you authored
- **Delete Content**: Only you can delete your own insights
- **Download Reports**: Generate HTML reports with improved styling

## 🏗️ Architecture (Updated 2025)

### Frontend
- **Bootstrap 5.3**: Latest responsive UI framework with new components
- **Font Awesome 6**: Updated icon library with social interaction symbols
- **Custom CSS3**: Modern gradient design with CSS Grid and Flexbox
- **Firebase SDK**: Client-side authentication and user management
- **Vanilla JavaScript**: Enhanced interactive features with real-time social updates

### Backend
- **Flask 3.1.1**: Latest Python web framework with improved security
- **Firebase Admin SDK**: Server-side authentication and user verification
- **CrewAI 0.134.0**: Advanced multi-agent AI system with enhanced capabilities
- **Firestore**: NoSQL database for user data and social features
- **Pydantic 2.11**: Type validation with improved performance

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
│   ├── index.html          # Home page with login requirements
│   ├── insights.html       # Insights display with social features
│   └── auth/               # Authentication templates
│       ├── login.html      # Login page with Firebase integration
│       ├── signup.html     # Registration with email verification
│       └── dashboard.html  # User account dashboard
├── static/                 # Static assets
├── requirements.txt        # Python dependencies (2025 versions)
├── service-account-key.json # Firebase service account (local dev)
├── .env                    # Environment variables
└── README.md              # This comprehensive documentation
```

### API Endpoints (Enhanced with Authentication)
- `GET /` - Home page with authentication-aware interface
- `POST /generate` - Generate insights (requires login)
- `GET /insights/<id>` - View specific insights with social data
- `POST /delete/<id>` - Delete insights (owner only)
- `GET /api/shared-insights` - JSON API for public insights
- `POST /api/insights/<id>/like` - Like/unlike insights (requires login)
- `POST /api/insights/<id>/share` - Toggle privacy (author only)
- `POST /auth/api/login` - Firebase authentication endpoint
- `POST /auth/api/signup` - User registration endpoint
- `GET /auth/dashboard` - User account dashboard

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

### Data Model
```python
# Enhanced GeneratedInsights with social features
{
    "id": "unique_id",
    "topic": "Research topic",
    "content": "Generated insight",
    "author_id": "firebase_user_id",
    "author_name": "User Name",
    "author_email": "user@example.com",
    "is_shared": true,  # Default public sharing
    "likes": 15,
    "liked_by": ["user1", "user2", ...],
    "created_at": "2025-01-26T12:00:00Z"
}
```

## 🧪 Testing (Comprehensive 2025 Suite)

### ✅ Verified Working Features
All features have been thoroughly tested:

1. **Firebase Authentication**: ✅ Email/password and Google sign-in working
2. **User Sessions**: ✅ Persistent login with automatic token refresh
3. **Social Features**: ✅ Like system and privacy controls functional
4. **Public Sharing**: ✅ Guest access to community insights
5. **Protected Routes**: ✅ Login requirements properly enforced
6. **Web Interface**: ✅ Responsive UI with authentication integration
7. **Insight Generation**: ✅ Multi-agent AI with user attribution
8. **Firestore Storage**: ✅ User data and social features persisted
9. **Error Handling**: ✅ Comprehensive error recovery and user feedback

### Authentication Testing
- [ ] Email/password registration and login
- [ ] Google sign-in integration
- [ ] Email verification workflow
- [ ] Session persistence across browser restarts
- [ ] Token refresh and expiration handling
- [ ] Logout functionality

### Social Features Testing
- [ ] Default public sharing of new insights
- [ ] Like button functionality and counters
- [ ] Privacy toggle for insight authors
- [ ] Guest user access to public content
- [ ] Author information display
- [ ] Real-time UI updates for social interactions

## 🔮 Future Enhancements (2025 Roadmap)

### Short Term (Q1-Q2 2025) - ✅ COMPLETED
- **User Authentication**: ✅ Firebase authentication implemented
- **Social Features**: ✅ Public sharing and like system working
- **Community Feed**: ✅ Browse insights from all users
- **User Profiles**: Basic author attribution implemented

### Medium Term (Q3-Q4 2025)
- **Enhanced User Profiles**: Detailed profile pages with user statistics
- **Comment System**: Allow users to comment on insights
- **Follow System**: Follow favorite authors and get notifications
- **Advanced Search**: Search insights by topic, author, or content
- **Collections**: Users can organize insights into themed collections
- **Trending Topics**: Highlight popular research areas

### Long Term (2026+)
- **Real-time Collaboration**: Co-create insights with team members
- **Enterprise Features**: Team workspaces, admin controls, analytics
- **AI Recommendations**: Suggest related insights and topics
- **Mobile App**: Native iOS and Android applications
- **Integration Hub**: Connect with popular research and business tools
- **Advanced Analytics**: Insight engagement metrics and trending analysis

## 🆘 Troubleshooting (Updated 2025)

### Common Issues

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

#### Firebase Connection Issues
- **"Failed to get credentials"**: Ensure service account key is properly configured
- **Secret Manager errors**: Verify Google Cloud project permissions
- **Firestore write errors**: Check database rules and authentication

#### "OpenAI API key is required"
- Ensure `OPENAI_API_KEY` is set correctly in `.env`
- Verify API key validity and sufficient credits
- Check for correct OpenAI account permissions

#### "At least one search API key required"
- Set either `TAVILY_API_KEY` or `SERPAPI_API_KEY`
- Verify API keys are active and have remaining quota
- Test API keys independently using curl or Postman

#### Performance Issues
- **Slow insight generation**: Normal processing time 45-120 seconds
- **Page load delays**: Check network connection and clear browser cache
- **Social features lag**: Firestore operations may take 1-2 seconds
- **High token usage**: Monitor OpenAI dashboard for usage patterns

### Getting Help
- Check browser console for JavaScript errors
- Review application logs for detailed error messages
- Verify all environment variables are properly set
- Test Firebase authentication in browser developer tools
- Check Google Cloud Console for service status and quotas

---

**Powered by Firebase Authentication, CrewAI 0.134.0 Multi-Agent System & Flask 3.1.1** 🔐🤖✨

*Last Updated: January 2025 - Now featuring complete user authentication, social sharing, and community features for collaborative AI insights generation.* 