import google.generativeai as genai
from google.generativeai import types
import os
import config
import wave

# --- Client Initialization ---
# Configure the client with the API key from the config file
# This will only be attempted if the key is actually set.
text_model = None
tts_model = None
if config.GOOGLE_API_KEY != "your_google_api_key_here":
    try:
        genai.configure(api_key=config.GOOGLE_API_KEY)
        text_model = genai.GenerativeModel('gemini-2.5-flash')
        tts_model = genai.GenerativeModel('gemini-2.5-flash-preview-tts')
        print("Gemini client initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Gemini client: {e}")
        text_model = None
        tts_model = None
else:
    print("Skipping Gemini client initialization: GOOGLE_API_KEY not set.")


def get_gemini_response(prompt_text: str):
    """
    Gets a text response from the configured Gemini model.
    """
    if not text_model:
        print("Cannot get Gemini response: client is not initialized.")
        return None

    try:
        response = text_model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        return None


def get_gemini_tts_response(text: str, voice: str = "Kore"):
    """
    Gets a TTS response from the configured Gemini model.
    """
    if not tts_model:
        print("Cannot get Gemini TTS response: client is not initialized.")
        return None

    try:
        response = tts_model.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=f"Say cheerfully: {text}",
            stream=True,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice,
                        )
                    )
                ),
            )
        )
        # Assuming streaming response for audio
        for chunk in response:
             if chunk.candidates[0].content.parts[0].inline_data.data:
                return chunk.candidates[0].content.parts[0].inline_data.data
    except Exception as e:
        print(f"An error occurred with the Gemini TTS API: {e}")
        return None

if __name__ == '__main__':
    # --- Testing ---
    test_abstract = "Catastrophic forgetting is a major obstacle in training neural networks for continual learning. We propose a novel method, Synaptic Metaplasticity Assimilation (SMA), which selectively freezes important weights identified through a secondary meta-network."
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
    summary = get_gemini_response(full_prompt)

    if summary:
        print("Generated Summary:")
        print(summary)
    else:
        print("Could not generate summary.")

    print("--- Manual test finished ---")