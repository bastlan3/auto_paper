import requests
import json
import config
from urllib.parse import urlparse
import logging
import time
import os

logging.basicConfig(level=logging.INFO)

def _parse_github_url(repo_url: str):
    """Parses a GitHub URL to extract the owner and repo name."""
    try:
        path = urlparse(repo_url).path
        parts = path.strip('/').split('/')
        if len(parts) >= 2:
            owner = parts[-2]
            repo = parts[-1].replace('.git', '')
            return owner, repo
    except Exception as e:
        logging.error(f"Failed to parse GitHub URL '{repo_url}': {e}")
    return None, None

def list_jules_sources():
    url = f"{config.JULES_API_BASE_URL}/sources"
    headers = {"X-Goog-Api-Key": config.JULES_API_KEY}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def list_jules_sessions(page_size=5):
    url = f"{config.JULES_API_BASE_URL}/sessions?pageSize={page_size}"
    headers = {"X-Goog-Api-Key": config.JULES_API_KEY}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_jules_session(session_name: str):
    """Gets the details of a specific Jules session."""
    url = f"{config.JULES_API_BASE_URL}/{session_name}"
    headers = {"X-Goog-Api-Key": config.JULES_API_KEY}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def approve_jules_plan(session_id):
    url = f"{config.JULES_API_BASE_URL}/sessions/{session_id}:approvePlan"
    headers = {
        "X-Goog-Api-Key": config.JULES_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()

def approve_jules_pull_request(session_name):
    """
    Approves the pull request through the JULES API.
    This tells JULES to create and push the PR to GitHub.
    """
    url = f"{config.JULES_API_BASE_URL}/{session_name}:approvePullRequest"
    headers = {
        "X-Goog-Api-Key": config.JULES_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()

def send_jules_message(session_id, prompt):
    url = f"{config.JULES_API_BASE_URL}/sessions/{session_id}:sendMessage"
    headers = {
        "X-Goog-Api-Key": config.JULES_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"prompt": prompt}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def start_jules_build(repo_url: str, implementation_plan: str, title: str, starting_branch: str = "main"):
    """
    Creates a new session in the JULES API to start a code generation task.
    Returns a tuple of (session_data, error_code).
    On success, error_code is None.
    On failure, session_data is None and error_code is the HTTP status code or -1.
    """
    if config.JULES_API_KEY == "your_jules_api_key_here":
        logging.warning("Skipping JULES build: JULES_API_KEY is not set.")
        return None, 0  # Special code for skipped

    owner, repo = _parse_github_url(repo_url)
    if not owner or not repo:
        logging.error(f"Could not parse owner and repo from URL: {repo_url}")
        return None, None

    url = f"{config.JULES_API_BASE_URL}/sessions"
    headers = {
        "X-Goog-Api-Key": config.JULES_API_KEY,
        "Content-Type": "application/json",
    }
    source_name = f"sources/github/{owner}/{repo}"

    try:
        logging.info("Checking for available JULES sources...")
        sources_response = list_jules_sources()
        available_sources = [s.get('name') for s in sources_response.get('sources', [])]
        
        if source_name not in available_sources:
            logging.error(f"Source '{source_name}' not found in JULES.")
            logging.error("Please ensure the JULES GitHub App is installed on the repository and has access.")
            logging.info(f"Available sources: {available_sources}")
            return None, 404 # Not Found
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to list JULES sources: {e}")
        if e.response is not None:
            return None, e.response.status_code
        return None, -1

    payload = {
        "prompt": implementation_plan,
        "sourceContext": {
            "source": source_name,
            "githubRepoContext": {"startingBranch": starting_branch}
        },
        "title": title
    }

    try:
        logging.info(f"Sending request to JULES API to create session for source: {source_name}")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        session_data = response.json()
        logging.info(f"JULES session created successfully: {session_data.get('name')}")
        return session_data, None
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred with the JULES API: {e}")
        if e.response is not None:
            status_code = e.response.status_code
            logging.error(f"Response status code: {status_code}")
            logging.error(f"Response body: {e.response.text}")
            return None, status_code
        return None, -1

def merge_github_pull_request(pr_url, github_token):
    """
    Merges a GitHub pull request using the GitHub API.
    """
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json"
    }
    # Extract owner, repo, and pull_number from PR URL
    try:
        path_parts = urlparse(pr_url).path.strip('/').split('/')
        owner, repo, _, pull_number = path_parts[0], path_parts[1], path_parts[2], path_parts[3]
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/merge"
        response = requests.put(api_url, headers=headers, json={"merge_method": "merge"})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Failed to merge PR: {e}")
        return None

if __name__ == '__main__':
    print("--- Running manual test of JULES API ---")

    if config.GITHUB_USERNAME != "your_github_username":
        test_plan = "1. Create a file named 'app.py'.\n2. Add a main function that prints 'Hello, JULES!'"
        test_repo_name = "Test-Jules-Repo-1"
        test_repo_url = f"https://github.com/{config.GITHUB_USERNAME}/{test_repo_name}"
        test_title = f"Test run for {test_repo_name}"

        print(f"Attempting to start JULES session for repo: {test_repo_url}")
        # You might need to change "main" to "master" if that's your default branch.
        session_info, error_code = start_jules_build(test_repo_url, test_plan, test_title, starting_branch="main")

        if session_info and session_info.get("name"):
            session_name = session_info["name"]
            print(f"\n--- JULES Session Info ---")
            print(json.dumps(session_info, indent=2))
            print("--------------------------")

            while True:
                print("Checking session status...")
                try:
                    session_details = get_jules_session(session_name)
                    session_state = session_details.get("state")
                    print(f"Current session state: {session_state}")
                except requests.exceptions.ConnectionError as e:
                    logging.error(f"Network error while checking session status: {e}")
                    print("\nNetwork connection lost. Retrying in 15 seconds...")
                    time.sleep(15)
                    continue
                except requests.exceptions.RequestException as e:
                    logging.error(f"Error checking session status: {e}")
                    print("\nError occurred while checking status. Retrying in 15 seconds...")
                    time.sleep(15)
                    continue

                if session_state == "COMPLETED":
                    print("Session completed successfully!")
                    
                    # Check if PR already exists
                    pr_exists = False
                    if session_details.get("outputs"):
                        for output in session_details["outputs"]:
                            if output.get("pullRequest"):
                                pr_exists = True
                                print("\n--- Pull Request Information ---")
                                print(json.dumps(output["pullRequest"], indent=2))
                                print("-----------------------------")
                                pr_url = output["pullRequest"].get("url")
                                print(f"\nPull request is available at: {pr_url}")
                                print("Please review and merge it manually on GitHub.")
                                break
                    
                    # If no PR exists, check the session state details
                    if not pr_exists:
                        print("\n--- Session Details ---")
                        print(json.dumps(session_details, indent=2))
                        print("----------------------")
                        print("\nNo pull request found in outputs.")
                        print("This may mean:")
                        print("1. The session completed but JULES couldn't create a PR (check permissions)")
                        print("2. You need to manually approve the PR in the JULES UI")
                        print("3. The code changes were too small or there were no changes to commit")
                        print("\nPlease check the JULES UI to see the session status and approve the PR if needed.")
                    break
                elif session_state == "AWAITING_PLAN_APPROVAL":
                    print("\nSession is waiting for plan approval.")
                    print("The implementation plan needs to be reviewed before JULES can proceed.")
                    user_input = input("Would you like to approve the plan now? (yes/no): ").strip().lower()
                    if user_input == "yes":
                        try:
                            print("Approving plan...")
                            session_id = session_name.split('/')[-1]
                            approve_jules_plan(session_id)
                            print("Plan approved! JULES will now start implementing the changes.")
                        except Exception as e:
                            logging.error(f"Failed to approve plan: {e}")
                            if hasattr(e, 'response') and e.response is not None:
                                logging.error(f"Response: {e.response.text}")
                            print("Failed to approve plan automatically. Please approve it manually in the JULES UI.")
                    else:
                        print("Plan approval skipped. Please approve manually in the JULES UI.")
                        break
                elif session_state == "AWAITING_USER_INPUT":
                    print("\nSession is waiting for user input.")
                    print("JULES may need clarification or approval before proceeding.")
                    print("Please check the JULES UI for details.")
                    break
                elif session_state == "FAILED":
                    print("Session failed.")
                    print("\n--- Session Failure Details ---")
                    print(json.dumps(session_details, indent=2))
                    print("-------------------------------")
                    print("\n--- Troubleshooting ---")
                    print(f"The session failed quickly, which often indicates a setup issue.")
                    print(f"1. Verify that the starting branch ('{session_details.get('sourceContext', {}).get('githubRepoContext', {}).get('startingBranch')}') exists in the repository '{test_repo_url}'. It might be 'master' instead of 'main'.")
                    print("2. Ensure the repository is not empty and has at least one commit on the starting branch.")
                    print("3. Check that the JULES GitHub App is installed and has permissions for this repository.")
                    print("-----------------------")
                    break
                else:
                    print("Session is still working...")
                
                time.sleep(10) # Wait for 10 seconds before checking again

        else:
            print(f"\nFailed to start JULES session. Error code: {error_code}")
    else:
        print("Skipping test: GITHUB_USERNAME not set in .env file.")

    print("--- Manual test finished ---")