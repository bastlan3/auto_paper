import requests
import json
import config

def start_jules_build(repo_url, implementation_plan):
    """Sends a request to the JULES API to start a build session."""
    headers = {
        "Authorization": f"Bearer {config.JULES_API_KEY}",
        "Content-Type": "application/json",
    }
    # This payload is HYPOTHETICAL and needs to be adapted
    # based on the actual JULES API documentation.
    payload = {
        "source": {
            "type": "github",
            "url": repo_url
        },
        "task": "code_generation",
        "prompt": implementation_plan,
        "options": {
            "language": "python",
            "framework": "pytorch" # You might be able to specify this
        }
    }

    try:
        print("Sending request to JULES API...")
        response = requests.post(config.JULES_API_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        session_data = response.json()
        print("JULES session started successfully!")
        print(f"Session ID: {session_data.get('id')}")
        print(f"Check status at: {session_data.get('status_url')}") # Hypothetical status URL
        return session_data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred with the JULES API: {e}")
        if e.response:
            print(f"Response body: {e.response.text}")
        return None

if __name__ == '__main__':
    # --- Testing ---
    # This test depends on the successful output of the previous steps
    print("--- Running manual test of JULES API ---")
    # 1. Get the implementation plan from Gemini (using the prompt from Part 2)
    test_implementation_plan = """
1. Data Preprocessing:
   * Input: Raw text corpus.
   * Action: Tokenize and pad sequences to 512.
2. Model Architecture:
   * Action: Implement multi-head self-attention with h=8, d_model=768.
"""
    # 2. Assume the GitHub repo was created
    test_repo_url = f"https://github.com/{config.GITHUB_USERNAME}/SMA-Synaptic-Metaplasticity-Assimilation-2025"

    # 3. Call the JULES API
    if config.JULES_API_KEY != "your_jules_api_key_here":
        start_jules_build(test_repo_url, test_implementation_plan)
    else:
        print("JULES API key not set. Skipping test.")
    print("--- Manual test finished ---")