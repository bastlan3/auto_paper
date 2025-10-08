# --- API Keys and Configuration ---
# It's recommended to load these from environment variables for security
import os
import pprint
from dotenv import load_dotenv

# Google AI Studio API Key
# Print all environment variables (be careful with sensitive data)
# Load environment variables from .env file
load_dotenv()

# Get your key from https://aistudio.google.com/app/apikey
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "your_google_api_key_here")
# GitHub
# Use a Fine-grained Personal Access Token with 'repo' scope
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "your_github_token_here")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "your_github_username")

# JULES API
JULES_API_KEY = os.environ.get("JULES_API_KEY", "your_jules_api_key_here")
JULES_API_BASE_URL = "https://jules.googleapis.com/v1alpha" # Official endpoint