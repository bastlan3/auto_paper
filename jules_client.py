import requests
import json
import config

def start_jules_build(repo_url, implementation_plan):
    """Sends a request to the JULES API to start a build session."""
    # Do not attempt to run if the API key is not set
    if config.JULES_API_KEY == "your_jules_api_key_here":
        print("Skipping JULES build: JULES_API_KEY not set.")
        return None

    headers = {
        "Authorization": f"Bearer {config.JULES_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "source": {
            "type": "github",
            "url": repo_url
        },
        "task": "code_generation",
        "prompt": implementation_plan,
        "options": {
            "language": "python",
            "framework": "pytorch"
        }
    }

    try:
        print("Sending request to JULES API...")
        response = requests.post(config.JULES_API_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        session_data = response.json()
        print("JULES session started successfully!")
        return session_data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred with the JULES API: {e}")
        if e.response:
            print(f"Response body: {e.response.text}")
        return None

if __name__ == '__main__':
    print("--- Running manual test of JULES API ---")
    test_plan = "1. Create a file named 'app.py'.\n2. Add a main function."
    test_repo = f"https://github.com/{config.GITHUB_USERNAME}/Test-Repo"

    # The function now handles the check internally
    start_jules_build(test_repo, test_plan)

    print("--- Manual test finished ---")