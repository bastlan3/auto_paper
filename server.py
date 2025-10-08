from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import arxiv_client
import gemini_client
import github_client
import jules_client
import logging
import re
from typing import List, Optional
import io
import os
import uuid
import wave
import time

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AI Science Brief API",
    description="API for fetching and processing arXiv papers.",
    version="1.1.0",
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-memory Cache ---
paper_cache: List[dict] = []

# --- System Prompts ---
SUMMARY_PROMPT_TEMPLATE = """You are an expert scientific communicator... Output ONLY the three-sentence summary. Abstract: `{abstract}`"""
METHOD_PROMPT_TEMPLATE = """You are a senior research engineer... Format as a Markdown-ready guide. CONTEXT: `{abstract}`"""
QA_PROMPT_TEMPLATE = """You are a specialized AI assistant with the full text of a research paper. Your task is to answer user questions based on the paper's content.
CONTEXT:
{paper_text}

RULES:
1. Base your answers entirely on the provided paper text.
2. If the answer is not in the text, state that clearly.
3. Be concise and directly answer the question.

User Question: {question}"""

DIALOGUE_PROMPT_TEMPLATE = """You are a scriptwriter for a science podcast. Your task is to create a 10-minute conversational script between an "Interviewer" and the "Author" of a research paper.

The script should be engaging and informative for a general audience with a keen interest in science.

**Interviewer's Role:**
- Inquisitive and curious.
- Asks clarifying questions.
- Probes for the paper's strengths, weaknesses, and broader implications.
- Keeps the conversation flowing and accessible.

**Author's Role:**
- The expert on the paper.
- Answers questions clearly and concisely, using the provided text as the source of truth.
- Explains complex concepts in an easy-to-understand manner.

**Script Guidelines:**
- The total length should be approximately 10 minutes of spoken dialogue.
- The dialogue must be formatted exactly as follows, with "Interviewer:" and "Author:" on new lines.
- The script must start with "TTS the following conversation between Interviewer and Author:"
- Ground all of the Author's responses in the provided paper text.

**Paper Text:**
---
{paper_text}
---

**Example Snippet:**
TTS the following conversation between Interviewer and Author:
Interviewer: Welcome to "Science Spotlight." Today, we're thrilled to discuss your latest paper. Can you start by giving us the elevator pitch? What is the core problem you're trying to solve?
Author: Thank you for having me. The central problem we address is catastrophic forgetting in neural networks, which is a major hurdle in continual learning scenarios where models need to learn from a continuous stream of data.
Interviewer: That sounds complex. How does your proposed method, Synaptic Metaplasticity Assimilation, tackle this?
Author: Our method works by...

Now, generate the full 10-minute script based on the paper text provided.
"""

# --- Pydantic Models ---
class BuildCodeRequest(BaseModel):
    repo_name: str
    implementation_plan: str

class ChatRequest(BaseModel):
    question: str

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "Kore"

class Paper(BaseModel):
    id: str
    title: str
    authors: List[str]
    publishedDate: str
    category: str
    abstract: str
    summary: str

# --- Helper Functions ---
def process_papers_with_summaries(papers: List[dict]) -> List[dict]:
    """Generates summaries for a list of papers."""
    for paper in papers:
        if not paper.get('summary'):
            logging.info(f"Generating summary for paper: {paper['title']}")
            prompt = SUMMARY_PROMPT_TEMPLATE.format(abstract=paper['abstract'])
            summary = gemini_client.get_gemini_response(prompt)
            paper['summary'] = summary or "Summary could not be generated at this time."
    return papers

# --- API Endpoints ---
@app.get("/api/papers", response_model=List[Paper])
def get_papers():
    """Fetches the latest papers from arXiv and generates summaries."""
    global paper_cache
    logging.info("Endpoint /api/papers called.")

    if not paper_cache:
        logging.info("Cache is empty. Fetching fresh papers.")
        papers = arxiv_client.fetch_new_papers()
        if not papers:
            return []
        paper_cache = process_papers_with_summaries(papers)

    return paper_cache

@app.get("/api/papers/{paper_id}", response_model=Paper)
def get_paper_details(paper_id: str):
    """Fetches details for a single paper from the cache."""
    logging.info(f"Endpoint /api/papers/{paper_id} called.")

    if not paper_cache:
        get_papers()

    paper = next((p for p in paper_cache if p['id'] == paper_id), None)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper

@app.post("/api/papers/{paper_id}/implementation-plan")
def get_implementation_plan(paper_id: str):
    """Generates a technical implementation plan for a given paper."""
    paper = get_paper_details(paper_id)
    prompt = METHOD_PROMPT_TEMPLATE.format(abstract=paper['abstract'])
    plan = gemini_client.get_gemini_response(prompt)
    if not plan:
        raise HTTPException(status_code=500, detail="Failed to generate implementation plan.")
    return {"plan": plan}

@app.post("/api/papers/{paper_id}/build-code")
def build_code(paper_id: str, request: BuildCodeRequest):
    """Creates a GitHub repo, waits, and then triggers the JULES build process."""
    paper = get_paper_details(paper_id)
    repo_url = github_client.create_github_repo(request.repo_name, f"Code for {paper['title']}")
    if not repo_url:
        raise HTTPException(status_code=500, detail="Failed to create GitHub repository.")

    # Add a delay to allow for GitHub API replication before JULES accesses it
    logging.info("Waiting 5 seconds for GitHub repository to be available...")
    time.sleep(5)

    session_data, error_code = jules_client.start_jules_build(
        repo_url=repo_url,
        implementation_plan=request.implementation_plan,
        title=f"AI-Gen for: {paper['title']}"
    )

    if not session_data:
        if error_code == 404:
            error_detail = (
                "JULES API could not find the source repository. "
                "This usually means the JULES GitHub App does not have permission to access it. "
                "Please ensure the app is installed on your GitHub account with access to 'All repositories' "
                "to allow it to see newly created ones."
            )
            raise HTTPException(status_code=404, detail=error_detail)

        raise HTTPException(status_code=500, detail=f"Failed to start JULES build session. Error code: {error_code}")

    return {"repo_url": repo_url, "jules_session": session_data}

@app.post("/api/papers/{paper_id}/chat")
def chat_with_paper(paper_id: str, request: ChatRequest):
    """Handles a chat question about a paper, using the full text."""
    logging.info(f"Endpoint /api/papers/{paper_id}/chat called.")

    # Fetch the full text of the paper
    paper_text = arxiv_client.fetch_paper_text(paper_id)
    if not paper_text:
        raise HTTPException(status_code=500, detail="Could not retrieve the full text of the paper.")

    # Create the prompt with the full text
    prompt = QA_PROMPT_TEMPLATE.format(paper_text=paper_text, question=request.question)

    answer = gemini_client.get_gemini_response(prompt)
    if not answer:
        raise HTTPException(status_code=500, detail="Failed to get a response from the AI.")

    return {"answer": answer}

@app.post("/api/papers/{paper_id}/vocal-summary")
async def get_vocal_summary(paper_id: str):
    """Generates a vocal summary of a paper's abstract."""
    logging.info(f"Endpoint /api/papers/{paper_id}/vocal-summary called.")
    paper = get_paper_details(paper_id)
    summary = paper.get("summary")
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found for this paper.")

    audio_data = gemini_client.get_gemini_tts_response(summary)
    if not audio_data:
        raise HTTPException(status_code=500, detail="Failed to generate vocal summary.")

    return StreamingResponse(io.BytesIO(audio_data), media_type="audio/wav")

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """Generates audio from text using the Gemini TTS model."""
    logging.info(f"Endpoint /api/tts called with voice: {request.voice}")
    audio_data = gemini_client.get_gemini_tts_response(request.text, request.voice)
    if not audio_data:
        raise HTTPException(status_code=500, detail="Failed to generate audio.")

    return StreamingResponse(io.BytesIO(audio_data), media_type="audio/wav")

# --- Helper for saving audio ---
def save_wave_file(filename: str, pcm_data: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2):
    """Saves PCM data to a WAV file."""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)

def cleanup_file(path: str):
    """Removes a file and logs the action."""
    try:
        os.remove(path)
        logging.info(f"Successfully cleaned up temporary file: {path}")
    except OSError as e:
        logging.error(f"Error cleaning up file {path}: {e}")

@app.post("/api/papers/{paper_id}/detailed-summary")
async def get_detailed_summary(paper_id: str, background_tasks: BackgroundTasks):
    """
    Generates a detailed, 10-minute conversational audio summary of a paper.
    """
    logging.info(f"Endpoint /api/papers/{paper_id}/detailed-summary called.")

    # 1. Fetch full paper text
    paper_text = arxiv_client.fetch_paper_text(paper_id)
    if not paper_text:
        raise HTTPException(status_code=500, detail="Could not retrieve the full text of the paper.")

    # 2. Generate dialogue script
    dialogue_prompt = DIALOGUE_PROMPT_TEMPLATE.format(paper_text=paper_text)
    dialogue_script = gemini_client.get_dialogue_summary(dialogue_prompt)
    if not dialogue_script:
        raise HTTPException(status_code=500, detail="Failed to generate dialogue script.")

    # 3. Generate multi-speaker audio
    audio_data = gemini_client.get_multi_speaker_tts_response(dialogue_script)
    if not audio_data:
        raise HTTPException(status_code=500, detail="Failed to generate multi-speaker audio.")

    # 4. Save audio to a temporary file
    temp_dir = "temp_audio"
    os.makedirs(temp_dir, exist_ok=True)
    temp_filename = f"{uuid.uuid4()}.wav"
    temp_filepath = os.path.join(temp_dir, temp_filename)

    save_wave_file(temp_filepath, audio_data)
    logging.info(f"Saved detailed summary to temporary file: {temp_filepath}")

    # 5. Add cleanup task and return file response
    background_tasks.add_task(cleanup_file, temp_filepath)
    return FileResponse(
        path=temp_filepath,
        media_type="audio/wav",
        filename=f"detailed_summary_{paper_id}.wav"
    )

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)