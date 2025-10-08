from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import arxiv_client
import gemini_client
import github_client
import jules_client
import logging
import re
from typing import List

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AI Science Brief API",
    description="API for fetching and processing arXiv papers.",
    version="1.0.0",
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
# A simple cache to store fetched papers to avoid re-fetching from arXiv
# and re-generating summaries on every request.
# In a production app, this would be a proper cache like Redis.
paper_cache: List[dict] = []

# --- System Prompts ---
SUMMARY_PROMPT_TEMPLATE = """You are an expert scientific communicator... Output ONLY the three-sentence summary. Abstract: `{abstract}`"""
VOCAL_SCRIPT_PROMPT_TEMPLATE = """You are a scriptwriter specializing in educational dialogues... Format the output as a JSON array of objects. Abstract: `{abstract}`"""
METHOD_PROMPT_TEMPLATE = """You are a senior research engineer... Format as a Markdown-ready guide. CONTEXT: `{abstract}`"""
QA_PROMPT_TEMPLATE = """You are a specialized AI assistant for scientific paper analysis. Your sole function is to answer questions based exclusively on the provided text of a research paper.
CONTEXT:
`{abstract}`
RULES:
1. Analyze the user's question.
2. Formulate your answer using only the information contained within the provided CONTEXT.
3. If the answer is present in the context, provide a direct and concise answer.
4. If the answer CANNOT be found in the provided CONTEXT, you MUST respond with one of the following two phrases: 'The answer to that question is not available in the provided abstract.' or 'The provided text does not contain information on that topic.'
5. Do not infer, guess, or use any external knowledge. Your world is limited to the text I provide.
6. Do not apologize or use conversational filler. Be direct and factual.

User Question: {question}
"""

# --- Pydantic Models ---
class BuildCodeRequest(BaseModel):
    repo_name: str
    implementation_plan: str

class ChatRequest(BaseModel):
    question: str

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
        if not paper.get('summary'): # Only generate if summary doesn't exist
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
        logging.info("Cache is empty. Fetching fresh papers from arXiv.")
        papers = arxiv_client.fetch_new_papers()
        if not papers:
            return []
        paper_cache = process_papers_with_summaries(papers)

    return paper_cache

@app.get("/api/papers/{paper_id}", response_model=Paper)
def get_paper_details(paper_id: str):
    """Fetches details for a single paper from the cache."""
    logging.info(f"Endpoint /api/papers/{paper_id} called.")

    # Ensure the cache is populated
    if not paper_cache:
        get_papers()

    paper = next((p for p in paper_cache if p['id'] == paper_id), None)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper

@app.post("/api/papers/{paper_id}/vocal-summary")
def get_vocal_summary_script(paper_id: str):
    """Generates a two-voice dialogue script for a given paper."""
    logging.info(f"Endpoint /api/papers/{paper_id}/vocal-summary called.")
    paper = get_paper_details(paper_id) # Reuse the logic to find the paper
    prompt = VOCAL_SCRIPT_PROMPT_TEMPLATE.format(abstract=paper['abstract'])
    script = gemini_client.get_gemini_response(prompt)
    if not script:
        raise HTTPException(status_code=500, detail="Failed to generate vocal summary script.")
    return {"script": script}

@app.post("/api/papers/{paper_id}/implementation-plan")
def get_implementation_plan(paper_id: str):
    """Generates a technical implementation plan for a given paper."""
    logging.info(f"Endpoint /api/papers/{paper_id}/implementation-plan called.")
    paper = get_paper_details(paper_id)
    prompt = METHOD_PROMPT_TEMPLATE.format(abstract=paper['abstract'])
    plan = gemini_client.get_gemini_response(prompt)
    if not plan:
        raise HTTPException(status_code=500, detail="Failed to generate implementation plan.")
    return {"plan": plan}

@app.post("/api/papers/{paper_id}/build-code")
def build_code(paper_id: str, request: BuildCodeRequest):
    """Creates a GitHub repo and triggers the JULES build process."""
    logging.info(f"Endpoint /api/papers/{paper_id}/build-code called.")
    paper = get_paper_details(paper_id)

    # 1. Create GitHub Repo
    repo_description = f"AI-generated code for paper: {paper['title']}"
    repo_url = github_client.create_github_repo(request.repo_name, repo_description)
    if not repo_url:
        raise HTTPException(status_code=500, detail="Failed to create GitHub repository.")

    # 2. Start JULES Build
    session_data = jules_client.start_jules_build(repo_url, request.implementation_plan)
    if not session_data:
        raise HTTPException(status_code=500, detail="Failed to start JULES build session.")

    return {"repo_url": repo_url, "jules_session": session_data}

@app.post("/api/papers/{paper_id}/chat")
def chat_with_paper(paper_id: str, request: ChatRequest):
    """Handles a chat question about a paper."""
    logging.info(f"Endpoint /api/papers/{paper_id}/chat called.")
    paper = get_paper_details(paper_id)
    prompt = QA_PROMPT_TEMPLATE.format(abstract=paper['abstract'], question=request.question)
    answer = gemini_client.get_gemini_response(prompt)
    if not answer:
        raise HTTPException(status_code=500, detail="Failed to get a response from the AI.")
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)