import requests
import json
import config
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO)

def _parse_github_url(repo_url: str):
    """Parses a GitHub URL to extract the owner and repo name."""
    try:
        # Handles both https:// and git@ URLs
        path = urlparse(repo_url).path
        parts = path.strip('/').split('/')
        if len(parts) >= 2:
            owner = parts[-2]
            repo = parts[-1].replace('.git', '')
            return owner, repo
    except Exception as e:
        logging.error(f"Failed to parse GitHub URL '{repo_url}': {e}")
    return None, None

def start_jules_build(repo_url: str, implementation_plan: str, title: str):
    """
    Creates a new session in the JULES API to start a code generation task.
    """
    if config.JULES_API_KEY == "your_jules_api_key_here":
        logging.warning("Skipping JULES build: JULES_API_KEY is not set.")
        return None

    owner, repo = _parse_github_url(repo_url)
    if not owner or not repo:
        logging.error(f"Could not parse owner and repo from URL: {repo_url}")
        return None

    # Construct the request URL, headers, and payload
    url = f"{config.JULES_API_BASE_URL}/sessions"
    headers = {
        "X-Goog-Api-Key": config.JULES_API_KEY,
        "Content-Type": "application/json",
    }
    source_name = f"sources/github/{owner}/{repo}"

    payload = {
        "prompt": implementation_plan,
        "sourceContext": {
            "source": source_name,
            "githubRepoContext": {
                "startingBranch": "main"
            }
        },
        "title": title
    }

    try:
        logging.info(f"Sending request to JULES API to create session for source: {source_name}")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        session_data = response.json()
        logging.info(f"JULES session created successfully: {session_data.get('name')}")
        return session_data
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred with the JULES API: {e}")
        if e.response is not None:
            logging.error(f"Response status code: {e.response.status_code}")
            logging.error(f"Response body: {e.response.text}")
        return None

if __name__ == '__main__':
    print("--- Running manual test of JULES API ---")

    # Ensure you have a GITHUB_USERNAME set in your .env file for this test
    if config.GITHUB_USERNAME != "your_github_username":
        test_plan = "1. Create a file named 'app.py'.\n2. Add a main function that prints 'Hello, JULES!'"
        test_repo_name = "Test-Jules-Repo-1"
        test_repo_url = f"https://github.com/{config.GITHUB_USERNAME}/{test_repo_name}"
        test_title = f"Test run for {test_repo_name}"

        print(f"Attempting to start JULES session for repo: {test_repo_url}")
        session_info = start_jules_build(test_repo_url, test_plan, test_title)

        if session_info:
            print("\n--- JULES Session Info ---")
            print(json.dumps(session_info, indent=2))
            print("--------------------------")
        else:
            print("\nFailed to start JULES session.")
    else:
        print("Skipping test: GITHUB_USERNAME not set in .env file.")

    print("--- Manual test finished ---")