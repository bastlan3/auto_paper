from apscheduler.schedulers.blocking import BlockingScheduler
import config
import arxiv_client
import gemini_client
import tts_client
import github_client
import jules_client
import logging
import re
import os # os was used but not imported

logging.basicConfig(level=logging.INFO)

def process_papers():
    """
    Orchestrates the entire process from fetching papers to initiating code generation.
    """
    logging.info("Starting paper processing workflow...")
    papers = arxiv_client.fetch_new_papers()

    if not papers:
        logging.info("No new papers found. Exiting workflow.")
        return

    # For demonstration, we'll process only the first paper
    paper = papers[0]
    logging.info(f"Processing paper: {paper['title']}")

    # 1. Get Summary from Gemini
    summary_prompt = f"""You are an expert scientific communicator. Your task is to distill the essence of a research paper's abstract into a compelling and concise summary for a scientifically literate audience.
RULES:
1. The summary MUST be exactly three sentences long.
2. The first sentence must state the core problem.
3. The second sentence must describe the key method.
4. The third sentence must highlight the main finding.
5. Output ONLY the three-sentence summary.

Abstract:
`{paper['abstract']}`"""

    summary = gemini_client.get_gemini_response(summary_prompt)
    if summary:
        logging.info(f"Generated Summary: {summary}")
        paper['summary_gemini'] = summary
    else:
        logging.error("Failed to generate summary. Aborting further processing for this paper.")
        return

    # 2. Get Vocal Summary Script
    vocal_script_prompt = f"""You are a scriptwriter specializing in educational dialogues. Your task is to transform a scientific abstract into a two-voice dialogue script between a 'Curious Analyst' and an 'Expert Researcher'.
RULES:
1. The dialogue must be structured to explain the paper's core concepts.
2. The 'Curious Analyst' asks clarifying questions.
3. The 'Expert Researcher' provides clear, concise answers based strictly on the provided abstract.
4. The script must be formatted as a JSON array of objects. Each object must have 'speaker' and 'line' keys.
5. The dialogue should be 3-4 exchanges long.

Abstract:
`{paper['abstract']}`"""

    vocal_script_json = gemini_client.get_gemini_response(vocal_script_prompt)
    if vocal_script_json:
        # In a real app, you would parse this JSON and call tts_client for each line
        logging.info("Generated Vocal Script.")
    else:
        logging.warning("Failed to generate vocal script.")

    # 3. Get Method Explanation
    method_prompt = f"""You are a senior research engineer tasked with translating a paper's methodology into a detailed implementation plan for a software developer.
CONTEXT:
`{paper['abstract']}`
RULES:
1. Break down the process into a numbered list of actionable steps.
2. Be specific about algorithms, data structures, and I/O.
3. Format as a Markdown-ready guide.
4. If the abstract is ambiguous, state the ambiguity and suggest a default.
"""
    implementation_plan = gemini_client.get_gemini_response(method_prompt)
    if not implementation_plan:
        logging.error("Failed to generate implementation plan. Aborting code generation.")
        return
    logging.info("Generated Implementation Plan.")

    # 4. Create GitHub Repo
    # Sanitize title to be a valid repo name
    sanitized_title = re.sub(r'[^a-zA-Z0-9\s-]', '', paper['title']).strip()
    repo_name = re.sub(r'\s+', '-', sanitized_title)[:50]
    repo_description = f"AI-generated code for paper: {paper['title']}"

    repo_url = github_client.create_github_repo(repo_name, repo_description)
    if not repo_url:
        logging.error("Failed to create GitHub repo. Aborting JULES build.")
        return

    # 5. Start JULES build
    jules_client.start_jules_build(repo_url, implementation_plan)


def main():
    """Starts the blocking scheduler."""
    scheduler = BlockingScheduler(timezone=config.SCHEDULER_TIMEZONE)

    scheduler.add_job(
        process_papers,
        'cron',
        day_of_week='mon-fri',
        hour=config.SCHEDULER_HOUR,
        minute=config.SCHEDULER_MINUTE
    )

    logging.info(f"Scheduler started. Will run Mon-Fri at {config.SCHEDULER_HOUR:02d}:{config.SCHEDULER_MINUTE:02d} {config.SCHEDULER_TIMEZONE}.")
    logging.info("Press Ctrl+C to exit.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    # For immediate testing, run the workflow directly.
    # The individual clients will gracefully skip API calls if not configured.
    logging.info("--- Running manual test of the main workflow ---")
    process_papers()
    logging.info("--- Manual test finished ---")

    # The scheduler is not started in test mode. To run the scheduler, execute `python main.py`
    # and ensure it's not in the `if __name__ == "__main__"` block, or call main() directly.
    # For example:
    # main()