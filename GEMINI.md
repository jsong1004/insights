# Gemini CLI - AI Topic Insights Project

This document provides guidance for using the Gemini CLI to build, debug, and manage the AI Topic Insights project.

## Project Overview

This project is a Flask-based web application that allows users to generate deep insights on any topic using a multi-agent AI system powered by CrewAI. The application features a modern web interface for user interaction, and it uses Firestore for persistent data storage. It also includes a full-featured authentication system using Firebase Authentication, with social features like sharing and liking insights.

## Core Technologies

*   **Python 3.11+**
*   **Flask:** A lightweight web framework for Python.
*   **CrewAI:** For creating and managing multi-agent AI systems.
*   **OpenAI/OpenRouter:** For language model tasks.
*   **Tavily/Serper:** For AI-focused search.
*   **Google Cloud Firestore:** For persistent data storage.
*   **Firebase Authentication:** For user authentication and management.
*   **Google Cloud Secret Manager:** For API key storage.
*   **Docker:** For containerization and deployment.
*   **Bootstrap 5:** For the frontend UI.

## File-by-File Breakdown

### `app.py`

This is the main application file. It contains the Flask routes, the CrewAI agent definitions, and the logic for generating and storing insights. It also includes the `FirestoreManager` class for interacting with the Firestore database, and it initializes the Firebase Authentication manager.

### `auth/`

This directory contains the authentication-related code.

*   `__init__.py`: Initializes the authentication blueprint.
*   `firebase_auth.py`: Contains the `FirebaseAuthManager` class, which handles user authentication and session management.
*   `firestore_manager.py`: Contains the `UserFirestoreManager` class, which handles user data in Firestore.
*   `routes.py`: Contains the authentication-related routes, such as `/login`, `/signup`, and `/logout`.

### `requirements.txt` and `requirements-firebase.txt`

These files list the Python dependencies for the project. `requirements.txt` is the main dependencies file, while `requirements-firebase.txt` is used for the Docker build.

### `Dockerfile.insight`

This file defines the Docker image for the application. It sets up the Python environment, installs the dependencies, and configures the application to run with Gunicorn.

### `docker-compose.insight.yml`

This file is used to run the application with Docker Compose. It defines the `ai-insights-app` service and configures its environment variables, ports, and volumes.

### `build-insight-app.sh`

This is a shell script for building and deploying the application to Google Cloud Run. It handles creating the service account, enabling APIs, building the Docker image, and deploying the service.

### `test_flask_app.py`

This file contains a set of tests for the Flask application. It checks the environment setup, the required imports, and the basic functionality of the app.

### `templates/`

This directory contains the Jinja2 templates for the web interface.

*   `base.html`: The base template that all other templates extend. It includes the common HTML structure, CSS, and JavaScript.
*   `index.html`: The home page of the application. It contains the form for generating new insights.
*   `insights.html`: The page for displaying the generated insights.
*   `download_report.html`: The template for the downloadable HTML report of the insights.
*   `auth/`: This subdirectory contains the authentication-related templates, such as `login.html`, `signup.html`, and `dashboard.html`.

### `docs/`

This directory contains project documentation.

*   `enhancement.md`: A guide for enhancing the app for commercial operations.
*   `phase1.md`: A detailed development guide for Phase 1 of the commercialization plan.

## Getting Started

### Prerequisites

*   You have the Gemini CLI installed and configured.
*   You have `gcloud` CLI installed and authenticated.
*   You have Docker installed.
*   You have the required API keys:
    *   OpenAI
    *   Tavily or Serper
    *   A Google Cloud project with Firestore and Firebase Authentication enabled.

### Local Development

1.  **Set up the environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Configure environment variables:**
    Create a `.env` file and add your API keys and Firebase project details. See `environment-template.txt` for a template.

3.  **Run the application:**
    ```bash
    python app.py
    ```

## Deployment

The application can be deployed to Google Cloud Run using the `build-insight-app.sh` script.

```bash
./build-insight-app.sh
```

## Debugging with Gemini

Here are some useful commands for debugging the project with the Gemini CLI.

### Reading Files

*   **Read a specific file:**
    ```
    read_file /Users/jaeheesong/projects/python/topic_insights/app.py
    ```

*   **Read multiple files at once:**
    ```
    read_many_files paths=["/Users/jaeheesong/projects/python/topic_insights/app.py", "/Users/jaeheesong/projects/python/topic_insights/Dockerfile.insight"]
    ```

### Searching the Codebase

*   **Find all occurrences of "CrewAI":**
    ```
    search_file_content "CrewAI"
    ```

### Running Shell Commands

*   **Execute a script:**
    ```
    run_shell_command "python /Users/jaeheesong/projects/python/topic_insights/app.py"
    ```

*   **Check for running Docker containers:**
    ```
    run_shell_command "docker ps"
    ```
