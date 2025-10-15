from google import genai
from google.genai import types
import os
import config
import wave

# --- Client Initialization ---
# Configure the client with the API key from the config file
# This will only be attempted if the key is actually set.
client = None
MODEL_ID = 'gemini-2.5-flash-preview-tts'
TEXT_MODEL_ID = 'gemini-2.5-flash'

if config.GOOGLE_API_KEY != "your_google_api_key_here":
    try:
        client = genai.Client(api_key=config.GOOGLE_API_KEY)
        print("Gemini client initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Gemini client: {e}")
        client = None
else:
    print("Skipping Gemini client initialization: GOOGLE_API_KEY not set.")


def get_gemini_response(prompt_text: str):
    """
    Gets a text response from the configured Gemini model.
    """
    if not client:
        print("Cannot get Gemini response: client is not initialized.")
        return None

    try:
        response = client.models.generate_content(
            model=TEXT_MODEL_ID,
            contents=prompt_text
        )
        return response.text
    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        return None


def get_gemini_tts_response(text: str, voice: str = "Kore"):
    """
    Gets a TTS response from the configured Gemini model.
    """
    if not client:
        print("Cannot get Gemini TTS response: client is not initialized.")
        return None

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=f"Say '{text}'",
            config={
                "response_modalities": ['Audio'],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": voice
                        }
                    }
                }
            },
        )
        return response.candidates[0].content.parts[0].inline_data.data
    except Exception as e:
        print(f"An error occurred with the Gemini TTS API: {e}")
        return None


def get_dialogue_summary(prompt: str):
    """
    Generates a dialogue summary from a given prompt.
    """
    return get_gemini_response(prompt)


def get_multi_speaker_tts_response(dialogue_script: str):
    """
    Generates a multi-speaker TTS response from a dialogue script.
    """
    if not client:
        print("Cannot get Gemini TTS response: client is not initialized.")
        return None

    try:
        config = types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker='Interviewer',
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name='Kore',
                                )
                            )
                        ),
                        types.SpeakerVoiceConfig(
                            speaker='Author',
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name='Puck',
                                )
                            )
                        ),
                    ]
                )
            )
        )
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=f"TTS the following conversation between Interviewer and Author: {dialogue_script}",
            config=config,
        )
        return response.candidates[0].content.parts[0].inline_data.data
    except Exception as e:
        print(f"An error occurred with the multi-speaker Gemini TTS API: {e}")
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

    print("\n--- Running manual test of multi-speaker TTS ---")
    test_dialogue = """
Interviewer: Hello and welcome to our show. Today, we're discussing a fascinating new paper on synaptic metaplasticity. Could you start by explaining the core problem the paper addresses?
Author: Of course. The core problem is catastrophic forgetting in neural networks during continual learning.
"""
    audio_data = get_multi_speaker_tts_response(test_dialogue)
    if audio_data:
        print("Successfully generated multi-speaker audio data.")
        # Save to file for testing
        with wave.open('test_output.wav', 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(24000)
            wav.writeframes(audio_data)
        print("Audio saved to test_output.wav")
    else:
        print("Failed to generate multi-speaker audio.")

    print("--- Manual test finished ---")