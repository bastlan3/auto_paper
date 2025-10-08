import requests
import json
import config

def create_github_repo(repo_name, description):
    """Creates a new private GitHub repository."""
    # Do not attempt to run if credentials are not set
    if config.GITHUB_TOKEN == "your_personal_access_token_here" or config.GITHUB_USERNAME == "your_github_username":
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
        return repo_data['html_url']
    except requests.exceptions.RequestException as e:
        print(f"An error occurred with the GitHub API: {e}")
        if e.response:
            print(f"Response body: {e.response.text}")
        return None

if __name__ == '__main__':
    print("--- Running manual test of GitHub API ---")
    test_repo_name = "SMA-Synaptic-Metaplasticity-Assimilation-2025"
    test_description = "AI-generated code implementation for the paper 'Synaptic Metaplasticity Assimilation'."

    # The function now handles the check internally
    create_github_repo(test_repo_name, test_description)

    print("--- Manual test finished ---")