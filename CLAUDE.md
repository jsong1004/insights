# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a Flask web application that generates AI insights using CrewAI's multi-agent system. The app features Firebase authentication, social sharing capabilities, comprehensive usage statistics tracking, automated session timeout management, and a modern web interface.

## Technology Stack
- **Backend**: Flask 3.1.1, Python 3.11+
- **Authentication**: Firebase Authentication & Admin SDK
- **Database**: Google Firestore
- **AI**: CrewAI 0.134.0 with multi-agent system
- **Frontend**: Bootstrap 5.3, Font Awesome 6, Vanilla JavaScript
- **APIs**: OpenAI API, Tavily/SerpAPI for search
- **Deployment**: Docker with Google Cloud Run support

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt
# OR for Firebase-specific build
pip install -r requirements-firebase.txt

# Start development server
python app.py
# OR with Flask CLI
flask run --debug --port 5001

# Run tests and validation
python test_flask_app.py
```

### Docker Development
```bash
# Build Docker image
docker build --platform linux/amd64 -f Dockerfile.insight -t ai-insights-app .

# Run with Docker Compose
docker-compose -f docker-compose.insight.yml up

# Deploy to Google Cloud Run (production)
./build-insight-app.sh
```

### Testing & Validation
- **Test script**: `python test_flask_app.py` - validates environment setup and dependencies
- **Health check**: `GET /status` endpoint for system health
- **Debug endpoint**: `GET /debug/insights` for Firestore connection status

## Architecture Overview

### Application Factory Pattern
The app uses Flask's application factory pattern in `app.py:create_app()`. Key components are initialized during app creation:
- Firebase Authentication Manager (`auth.firebase_auth.FirebaseAuthManager`)
- User Firestore Manager (`auth.firestore_manager.UserFirestoreManager`)
- Blueprint registration for main routes and API endpoints

### Core Modules
- **`core/crew_ai.py`**: Multi-agent AI system with Research, Validation, and Insights agents
- **`core/insights_manager.py`**: Firestore manager for insights data persistence
- **`auth/`**: Complete authentication system with Firebase integration
- **`routes/main.py`**: Main application routes (home, insights generation)
- **`routes/api.py`**: API endpoints for AJAX functionality and social features
- **`config.py`**: Configuration management including Firebase settings

### Multi-Agent AI System
The CrewAI system orchestrates three specialized agents:
1. **Research Agent**: Conducts web searches using Tavily/SerpAPI
2. **Validation Agent**: Verifies sources and assigns confidence scores
3. **Insights Agent**: Generates structured analysis with detailed reports

### Authentication Flow
1. Client-side Firebase SDK handles login/signup
2. Server-side Firebase Admin SDK verifies JWT tokens
3. Flask sessions with automated timeout management (15-minute inactivity timeout)
4. Protected routes require authentication for insight generation
5. Dual-layer session timeout with server-side cleanup and client-side auto-logout

### Database Schema (Firestore)
- **Users collection**: User profiles, metadata, and comprehensive usage statistics
- **GeneratedInsights collection**: Insights with social features (likes, sharing)
- **Usage tracking**: Multi-level metrics (daily, monthly, total) with token-based metering
- **Structured data models**: Pydantic models in `core/crew_ai.py` define insight structure

## Environment Configuration

### Required Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # OR SERPAPI_API_KEY
FLASK_SECRET_KEY=your_secret_key_here
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
```

### Firebase Configuration
The app is pre-configured for Firebase project `ai-biz-6b7ec`. See `config.py` for Firebase client configuration and `environment-template.txt` for setup guide.

## Key Features Implementation

### Social Features
- **Public sharing**: Insights shared by default (opt-out model)
- **Like system**: Real-time heart button interactions with Firestore persistence
- **Author attribution**: User profiles linked to insights
- **Privacy controls**: Authors can toggle sharing status

### Usage Statistics & Analytics
- **Comprehensive tracking**: Multi-level usage metrics (daily, monthly, total)
- **Token-based metering**: Accurate AI usage cost tracking with intelligent estimation
- **Plan-based limits**: Free, Basic, Pro, Enterprise subscription tiers
- **Real-time dashboard**: Visual progress bars, charts, and 7-day activity tracking
- **Proactive warnings**: Usage alerts and limit notifications
- **Historical data**: 30-day rolling usage history with monthly breakdowns
- **Automated management**: Monthly reset via Firebase Cloud Functions

### Session Management
- **Automated timeouts**: 15-minute inactivity-based session expiration
- **Activity tracking**: Real-time `last_activity` timestamp updates
- **Dual-layer protection**: Server-side cleanup with client-side auto-logout
- **Timezone-aware**: UTC timestamps for consistent session management
- **Graceful handling**: Automatic session cleanup and user redirection

### Security Features
- **JWT token verification**: Server-side validation of Firebase tokens
- **Session management**: Secure Flask sessions with automated timeout and renewal
- **Protected routes**: Decorator-based route protection
- **Input validation**: Pydantic models validate all user inputs
- **Usage limits**: Plan-based rate limiting and quota enforcement

### UI/UX Enhancements
- **Loading states**: Interactive buttons with progress feedback
- **Form protection**: Prevents double submissions
- **Real-time updates**: Live social interactions and usage statistics
- **Usage dashboard**: Visual progress bars, charts, and activity tracking
- **Responsive design**: Bootstrap 5.3 with mobile-first approach
- **Proactive notifications**: Usage warnings and limit alerts

## Deployment Architecture

### Docker Configuration
- **Multi-stage build**: Optimized Docker image in `Dockerfile.insight`
- **Production server**: Gunicorn with proper configuration
- **Secret management**: Google Cloud Secret Manager integration
- **Health monitoring**: Built-in health checks and logging

### Google Cloud Run Deployment
The `build-insight-app.sh` script handles complete deployment pipeline:
- Service account creation and permissions
- API enablement (Firebase, Firestore, Identity Toolkit)
- Docker image building and registry push
- Cloud Run service deployment with auto-scaling

## Common Development Patterns

### Adding New Routes
1. Add route handlers to `routes/main.py` or `routes/api.py`
2. Use `@login_required` decorator for protected routes
3. Access Firebase auth via `current_app.extensions['firebase_auth']`
4. Use Firestore manager via `current_app.extensions['firestore_manager']`

### Working with AI Agents
The `AIInsightsCrew` class in `core/crew_ai.py` handles all AI operations:
- Initialize with API keys (OpenAI, Tavily/Serper)
- Call `generate_insights(topic, instructions, user_data)` for insight generation
- Returns structured `GeneratedInsights` Pydantic model

### Database Operations  
Use `UserFirestoreManager` and `InsightsFirestoreManager` classes for:
- User data management and profile operations
- Insights CRUD operations with social features
- Atomic operations for likes and sharing controls
- Usage statistics tracking and limit enforcement
- Session timeout and activity management

## Testing Strategy
The `test_flask_app.py` provides comprehensive validation:
- Environment variable checking
- Dependency import validation
- Firebase authentication testing
- Database connection verification
- API endpoint functionality testing

Additional test suites:
- **`test_usage_stats.py`**: Usage statistics tracking and limit validation
- **Session timeout testing**: Automated session management verification

Run tests before deployment to ensure system integrity and proper configuration.

## Key API Endpoints

### Usage Statistics
- **`GET /api/usage-stats`**: Retrieve user's current usage statistics
- Includes daily, monthly, and total usage metrics
- Returns plan limits and remaining quotas

### Session Management
- Session timeout handled automatically via `@app.before_request`
- 15-minute inactivity timeout with timezone-aware tracking
- Client-side auto-logout via meta refresh tag