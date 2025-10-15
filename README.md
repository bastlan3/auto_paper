# AI Science Brief Backend

This project is the backend for the "AI Science Brief" application, a tool designed to help researchers and enthusiasts stay up-to-date with the latest advancements in Artificial Intelligence. The application automatically fetches the latest papers from arXiv, uses generative AI to create various forms of summaries, and can even initiate a process to generate boilerplate code based on the paper's methodology.

This backend is built with Python in a modular structure, allowing for easy testing and extension of its components.

## Table of Contents

1.  [Features](#features)
2.  [Project Structure](#project-structure)
3.  [Setup and Installation](#setup-and-installation)
    - [Prerequisites](#prerequisites)
    - [Install Dependencies](#install-dependencies)
    - [API Key Management](#api-key-management)
4.  [How to Test](#how-to-test)
5.  [Running the Full-Stack Application](#running-the-full-stack-application)

---

## Features

-   **Daily Paper Fetching**: Schedules a daily job to fetch the latest papers from the `cs.AI` category on arXiv.
-   **AI-Powered Content Generation**: Uses the Google Gemini API to generate multiple forms of content:
    -   A concise 3-sentence summary for a quick overview.
    -   A detailed, 10-minute conversational audio summary between a curious "Interviewer" and a knowledgeable "Author."
    -   A technical implementation plan based on the paper's abstract.
    -   In-depth answers to user questions, using the **full text** of the paper for context.
-   **Multi-Speaker Text-to-Speech**: Converts the generated dialogue script into a high-quality audio file using two distinct voices.
-   **Automated Repo Creation**: Creates a new private GitHub repository for a paper.
-   **JULES Integration**: Sends the implementation plan to the JULES API to start a code generation task in the newly created repository.
-   **Robust & Testable**: Designed to run even without full API credentials, allowing for safe testing and development.

## Project Structure

The project is organized into modular components for clarity and maintainability:

```
.
├── .env.example        # Example environment file for API keys
├── .gitignore          # Prevents secrets and compiled files from being committed
├── config.py           # Handles loading of all configuration and API keys
├── requirements.txt    # Lists all Python dependencies
├── arxiv_client.py     # Client for interacting with the arXiv API and fetching PDFs
├── gemini_client.py    # Client for the Google Gemini API (text and TTS)
├── github_client.py    # Client for the GitHub API
├── jules_client.py     # Client for the JULES API for code generation
└── server.py           # FastAPI server and main application entrypoint
```

## Setup and Installation

### Prerequisites

-   Python 3.8+
-   A Google Cloud Platform (GCP) account for the Gemini API.
-   A GitHub account.
-   Access to the JULES API.

### Install Dependencies

1.  Clone the repository to your local machine.
2.  It is highly recommended to create a virtual environment to keep dependencies isolated:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```
3.  Install all the required Python packages using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

### API Key Management

This project requires several API keys to function fully. To handle these securely and avoid committing them to version control, we use a `.env` file.

1.  **Create a `.env` file** in the root directory of the project by copying the example: `cp .env.example .env`
2.  **Add your API keys** and configuration to the `.env` file.

    ```env
    # Google AI Studio API Key (for Gemini and TTS)
    # Get your key from https://aistudio.google.com/app/apikey
    GOOGLE_API_KEY="your_google_api_key_here"

    # GitHub Fine-grained Personal Access Token
    # Get your token from https://github.com/settings/tokens?type=beta
    GITHUB_TOKEN="your_github_token_here"
    GITHUB_USERNAME="your_github_username"

    # JULES API Key
    JULES_API_KEY="your_jules_api_key_here"
    ```

#### How to Get API Keys:

-   **Google AI Studio (Gemini)**:
    1.  Go to **[Google AI Studio](https://aistudio.google.com/app/apikey)**.
    2.  Click "**Create API key**".
    3.  Copy the generated key and paste it into your `.env` file as `GOOGLE_API_KEY`.

-   **GitHub**:
    1.  Go to your [GitHub Developer Settings](https://github.com/settings/tokens?type=beta) to create a **Fine-grained personal access token**.
    2.  Give the token a name (e.g., "AI-Science-Brief-App").
    3.  Under "Repository access," select "All repositories" or choose specific ones.
    4.  Under "Permissions," go to "Repository permissions" and set **Administration** to **Read and write**. This is required for the application to create new repositories on your behalf.
    5.  Generate the token, copy it, and add it to your `.env` file as `GITHUB_TOKEN`.

-   **JULES API**:
    1.  Obtain your API key from the JULES developer console.
    2.  Paste it into your `.env` file as `JULES_API_KEY`.
    3.  **Install the JULES GitHub App**: For the JULES API to work, you must install the JULES GitHub App on your account. During installation, ensure you grant it access to **"All repositories"**. This is critical, as it allows JULES to see the new repositories created by this application. If you grant access only to specific repositories, the integration will fail with a `404 Not Found` error.

## How to Test

The application is designed to be tested without "going full send." Each API client can be run individually from your terminal, and the scripts are built to gracefully skip API calls if credentials are not configured.

```bash
# Test arXiv client (no key required)
python arxiv_client.py

# Test Gemini, GitHub, or JULES clients
# These will show a "skipping" message if keys are not set
python gemini_client.py
python github_client.py
python jules_client.py
```
If you **have** configured the keys, running the scripts will execute a live test against the respective API.

## Running the Full-Stack Application

There are two ways to run the application: in development mode with hot-reloading, or as a packaged desktop application.

### Development Mode

To run the application in development mode, you need to start the backend and frontend servers.

Navigate to the `frontend` directory and run the `dev` script:

```bash
cd frontend
npm install
npm run dev
```

This will start both the backend and frontend development servers concurrently. The frontend will be available at `http://localhost:3000`.

### Desktop Application

The application can be packaged into a standalone desktop application.

**Build the Application**

To build the application, navigate to the `frontend` directory and run the `dist` script:

```bash
cd frontend
npm install
npm run dist
```

This will create a distributable file in the `frontend/dist` directory.

**Run the Application**

Once the application is built, you can run it by double-clicking the executable file in the `frontend/dist` directory.