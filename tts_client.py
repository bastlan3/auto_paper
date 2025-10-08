from google.cloud import texttospeech
import os
import config

# Global client, lazily initialized
client = None
initialized = False

def init_client():
    """Initializes the TextToSpeech client."""
    global client, initialized
    if initialized:
        return

    initialized = True

    if config.GOOGLE_PROJECT_ID == "your-gcp-project-id":
        print("Skipping TTS client initialization: GOOGLE_PROJECT_ID not set.")
        return

    try:
        print("Initializing TTS client...")
        client = texttospeech.TextToSpeechClient()
        print("TTS client initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize TTS client: {e}")
        client = None

def text_to_audio_file(text, output_filename, voice_name):
    """Converts a string of text to an MP3 audio file."""
    init_client() # Ensure client is initialized

    if not client:
        print("Cannot generate audio: TTS client is not initialized.")
        return False

    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(language_code="en-US", name=voice_name)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        with open(output_filename, "wb") as out:
            out.write(response.audio_content)
            print(f'Audio content written to file "{output_filename}"')
        return True
    except Exception as e:
        print(f"An error occurred with the TTS API: {e}")
        return False

if __name__ == '__main__':
    # --- Testing ---
    print("--- Running manual test of TTS API ---")
    dialogue = [
      { "speaker": "Analyst", "line": "So, what was the main challenge you were trying to address?" },
      { "speaker": "Researcher", "line": "We were focused on the problem of catastrophic forgetting in neural networks." }
    ]
    voice_analyst = "en-US-Wavenet-B"
    voice_researcher = "en-US-Wavenet-F"

    # The function now handles initialization and config checks internally
    for i, item in enumerate(dialogue):
        success = False
        if item['speaker'] == 'Analyst':
            success = text_to_audio_file(item['line'], f"line_{i}_analyst.mp3", voice_analyst)
        else:
            success = text_to_audio_file(item['line'], f"line_{i}_researcher.mp3", voice_researcher)

        if not success:
            print(f"Could not generate audio for line {i}.")
            # Break because if one fails, they all will
            break

    print("--- Manual test finished ---")