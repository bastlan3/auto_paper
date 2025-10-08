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
    - [Testing Individual API Clients](#testing-individual-api-clients)
    - [Running the Full Integration Test](#running-the-full-integration-test)
5.  [Running the Scheduler](#running-the-scheduler)

---

## Features

-   **Daily Paper Fetching**: Schedules a daily job to fetch the latest papers from the `cs.AI` category on arXiv.
-   **AI-Powered Summaries**: Uses the Google Gemini API to generate multiple forms of content:
    -   A concise 3-sentence summary for a "newspaper view."
    -   A two-voice dialogue script for an audio summary.
    -   A detailed implementation plan based on the paper's abstract.
-   **Text-to-Speech**: Converts the generated dialogue script into audio files using the Google TTS API.
-   **Automated Repo Creation**: Creates a new private GitHub repository for a paper.
-   **Conceptual Code Generation**: Sends the implementation plan to a conceptual "JULES API" to start a code generation task.
-   **Robust & Testable**: Designed to run even without full API credentials, allowing for safe testing and development.

## Project Structure

The project is organized into modular components for clarity and maintainability:

```
.
├── .gitignore          # Prevents secrets and compiled files from being committed
├── config.py           # Handles loading of all configuration and API keys
├── requirements.txt    # Lists all Python dependencies
├── arxiv_client.py     # Client for interacting with the arXiv API
├── gemini_client.py    # Client for the Google Gemini API
├── tts_client.py       # Client for the Google Text-to-Speech API
├── github_client.py    # Client for the GitHub API
├── jules_client.py     # Conceptual client for the JULES API
└── server.py           # FastAPI server and main application entrypoint
```

## Setup and Installation

### Prerequisites

-   Python 3.8+
-   A Google Cloud Platform (GCP) account
-   A GitHub account

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
    # Google AI Studio API Key
    # Get your key from https://aistudio.google.com/app/apikey
    GOOGLE_API_KEY="your_google_api_key_here"

    # GitHub Fine-grained Personal Access Token
    # Get your token from https://github.com/settings/tokens?type=beta
    GITHUB_TOKEN="your_github_token_here"
    GITHUB_USERNAME="your_github_username"

    # JULES API (Hypothetical)
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
    4.  Under "Permissions," go to "Repository permissions" and set **Contents** to **Read and write**. This is required for the application to create new repositories on your behalf.
    5.  Generate the token, copy it, and add it to your `.env` file as `GITHUB_TOKEN`.

## How to Test

The application is designed to be tested without "going full send." Each API client can be run individually, and the scripts are built to gracefully skip API calls if credentials are not configured.

### Testing Individual API Clients

You can test each module by running it as a script from your terminal.

-   **arXiv Client**: This client does not require an API key.
    ```bash
    python arxiv_client.py
    ```
    This will fetch the 5 most recent papers from `cs.AI` and print their details.

-   **Gemini, TTS, GitHub, JULES Clients**:
    If you have **not** configured the API keys in your `.env` file, running these scripts will demonstrate the safe-skip functionality:
    ```bash
    python gemini_client.py
    # Output: Skipping Gemini client initialization...

    python github_client.py
    # Output: Skipping test, GITHUB_TOKEN or GITHUB_USERNAME not set.
    ```
    If you **have** configured the keys, running the scripts will execute a live test against the respective API.

### Running the Full Integration Test

The `main.py` script can be run directly to test the entire workflow.

```bash
python main.py
```

-   **Without API Keys**: The test will run, fetch papers from arXiv, and then gracefully fail at the Gemini step, logging an error message. This confirms the workflow orchestration is correct.
-   **With API Keys**: The test will execute the full process: fetch a paper, generate a summary, create a GitHub repo, and call the JULES API.

## Running the Full-Stack Application

To run the application, you need to start both the backend server and the frontend development server in two separate terminals.

**Terminal 1: Start the Backend API Server**

Navigate to the project's root directory and run the FastAPI server:

```bash
python server.py
```

You should see output indicating the server has started, usually at `http://localhost:8000`.

**Terminal 2: Start the Frontend Development Server**

Navigate to the `frontend` directory and run the Next.js development server:

```bash
cd frontend
npm run dev
```

The frontend will now be available at `http://localhost:3000`. Open this URL in your browser to use the application. API requests from the frontend will be automatically proxied to your backend server.