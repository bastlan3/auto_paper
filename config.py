# --- API Keys and Configuration ---
# It's recommended to load these from environment variables for security
import os

# Google Cloud
GOOGLE_PROJECT_ID = os.environ.get("GOOGLE_PROJECT_ID", "your-gcp-project-id")
GOOGLE_LOCATION = os.environ.get("GOOGLE_LOCATION", "us-central1")
# Make sure to set GOOGLE_APPLICATION_CREDENTIALS environment variable

# GitHub
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "your_personal_access_token_here")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "your_github_username")

# JULES API (Hypothetical)
JULES_API_KEY = os.environ.get("JULES_API_KEY", "your_jules_api_key_here")
JULES_API_ENDPOINT = "https://api.jules.ai/v1/sessions" # Hypothetical endpoint

# Scheduler
SCHEDULER_TIMEZONE = "UTC"
SCHEDULER_HOUR = 6
SCHEDULER_MINUTE = 0