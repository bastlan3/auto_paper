from google.cloud import aiplatform
import os
import config

# Global variables, lazily initialized
model = None
endpoint = None
initialized = False # To prevent re-trying initialization on failure

def init_client():
    """Initializes the Vertex AI client and model if not already done."""
    global model, endpoint, initialized
    if initialized:
        return

    initialized = True # Mark as attempted

    # Do not attempt to initialize if the placeholder project ID is still present
    if config.GOOGLE_PROJECT_ID == "your-gcp-project-id":
        print("Skipping Gemini client initialization: GOOGLE_PROJECT_ID not set.")
        return

    try:
        print("Initializing Gemini client...")
        aiplatform.init(project=config.GOOGLE_PROJECT_ID, location=config.GOOGLE_LOCATION)

        model = aiplatform.gapic.PredictionServiceClient(
            client_options={"api_endpoint": f"{config.GOOGLE_LOCATION}-aiplatform.googleapis.com"}
        )
        endpoint = f"projects/{config.GOOGLE_PROJECT_ID}/locations/{config.GOOGLE_LOCATION}/publishers/google/models/gemini-1.0-pro"
        print("Gemini client initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Gemini client: {e}")
        # Ensure model remains None on failure
        model = None
        endpoint = None

def get_gemini_response(prompt_text):
    """Gets a text response from the Gemini Pro model."""
    init_client() # Ensure client is initialized before use

    if not model:
        print("Cannot get Gemini response: client is not initialized.")
        return None

    try:
        instance = {"prompt": prompt_text}
        response = model.predict(endpoint=endpoint, instances=[instance])
        # The response structure can be complex; navigate it to get the content
        prediction = response.predictions[0]
        content = prediction['content']
        return content
    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        return None

if __name__ == '__main__':
    # --- Testing ---
    # Use the robust system prompt for summarization
    test_abstract = "Catastrophic forgetting is a major obstacle in training neural networks for continual learning. We propose a novel method, Synaptic Metaplasticity Assimilation (SMA), which selectively freezes important weights identified through a secondary meta-network. Our experiments on CIFAR-100 and TinyImageNet show that SMA reduces forgetting by up to 70% compared to baseline methods."
    system_prompt = """You are an expert scientific communicator. Your task is to distill the essence of a research paper's abstract into a compelling and concise summary for a scientifically literate audience.
RULES:
1. The summary MUST be exactly three sentences long.
2. The first sentence must state the core problem.
3. The second sentence must describe the key method.
4. The third sentence must highlight the main finding.
5. Output ONLY the three-sentence summary.
"""

    full_prompt = f"{system_prompt}\n\nAbstract:\n`{test_abstract}`"

    print("--- Running manual test of Gemini API ---")
    # The get_gemini_response function will handle initialization automatically.
    summary = get_gemini_response(full_prompt)

    if summary:
        print("Generated Summary:")
        print(summary)
    else:
        # This message will appear if the client failed to initialize.
        print("Could not generate summary because the client is not configured.")

    print("--- Manual test finished ---")