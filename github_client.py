import requests
import json
import config


def repo_exists(repo_name: str) -> bool:
    """Checks if a repository exists for the configured user."""
    if not config.GITHUB_TOKEN or config.GITHUB_TOKEN == "your_github_token":
        print("Skipping repo existence check: GITHUB_TOKEN is not set.")
        return False

    owner = config.GITHUB_USERNAME
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    headers = {
        "Authorization": f"token {config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"Repository '{owner}/{repo_name}' already exists.")
            return True
        elif response.status_code == 404:
            print(f"Repository '{owner}/{repo_name}' does not exist.")
            return False
        else:
            print(f"Error checking repo existence for '{owner}/{repo_name}'. Status: {response.status_code}")
            return False # Assume it doesn't exist to avoid breaking creation flow
    except requests.exceptions.RequestException as e:
        print(f"Network error while checking for repo existence: {e}")
        return False


def create_initial_commit(owner: str, repo_name: str) -> bool:
    """Creates an initial commit with a README to establish the main branch."""
    url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/README.md"
    headers = {
        "Authorization": f"token {config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    import base64
    readme_content = f"# {repo_name}\n\nThis repository was automatically created."
    encoded_content = base64.b64encode(readme_content.encode()).decode()
    
    data = {
        "message": "Initial commit",
        "content": encoded_content,
        "branch": "main"
    }
    
    try:
        response = requests.put(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print(f"Successfully created initial commit on main branch.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error creating initial commit: {e}")
        if e.response is not None:
            print(f"Response body: {e.response.text}")
        return False


def create_github_repo(repo_name, description):
    """Creates a new private GitHub repository."""
    # Do not attempt to run if credentials are not set
    if config.GITHUB_TOKEN == "your_github_token_here" or config.GITHUB_USERNAME == "your_github_username":
        print("Skipping GitHub repo creation: GITHUB_TOKEN or GITHUB_USERNAME not set.")
        return None

    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "name": repo_name,
        "description": description,
        "private": True,
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()

        repo_data = response.json()
        print(f"Successfully created repository: {repo_data['html_url']}")
        
        # Create initial commit to establish main branch
        create_initial_commit(config.GITHUB_USERNAME, repo_name)
        
        return repo_data['html_url']
    except requests.exceptions.RequestException as e:
        print(f"An error occurred with the GitHub API: {e}")
        if e.response is not None:
            if e.response.status_code == 403:
                print("GitHub API Error: 403 Forbidden. This likely means your GITHUB_TOKEN lacks the necessary 'repo' scope. Please create a new token with the 'repo' scope enabled.")
            print(f"Response body: {e.response.text}")
        return None

if __name__ == '__main__':
    print("--- Running manual test of GitHub API ---")
    test_repo_name = "SMA-Synaptic-Metaplasticity-Assimilation-2025"
    test_description = "AI-generated code implementation for the paper 'Synaptic Metaplasticity Assimilation'."

    # The function now handles the check internally
    create_github_repo(test_repo_name, test_description)

    print("--- Manual test finished ---")