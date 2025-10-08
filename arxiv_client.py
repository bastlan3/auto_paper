import arxiv
import logging
from datetime import datetime
import fitz  # PyMuPDF
import os

logging.basicConfig(level=logging.INFO)

def fetch_new_papers():
    """Fetches the 5 most recent papers from the cs.AI category."""
    print("Fetching new papers from arXiv...")
    try:
        search = arxiv.Search(
            query="cat:cs.AI",
            max_results=5,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )

        papers = []
        for result in search.results():
            paper_data = {
                "id": result.entry_id.split('/')[-1],
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "publishedDate": result.published.strftime('%Y-%m-%d'),
                "category": result.primary_category,
                "abstract": result.summary.replace('\n', ' ').strip(),
                "summary": "" # Placeholder for the Gemini summary
            }
            papers.append(paper_data)

        print(f"Successfully fetched {len(papers)} papers.")
        return papers

    except Exception as e:
        print(f"An error occurred while fetching from arXiv: {e}")
        return []

def fetch_paper_text(paper_id: str):
    """
    Fetches the full text of a paper from its PDF.
    """
    logging.info(f"Fetching full text for paper ID: {paper_id}")
    pdf_filename = f"{paper_id.replace('/', '_')}.pdf" # Create a safe filename
    try:
        # Search for the paper by its ID
        search = arxiv.Search(id_list=[paper_id])
        paper = next(search.results())

        # Download the PDF to a temporary file
        paper.download_pdf(filename=pdf_filename)
        logging.info(f"Successfully downloaded {pdf_filename}")

        # Extract text from the PDF
        text = ""
        with fitz.open(pdf_filename) as doc:
            for page in doc:
                text += page.get_text()

        # Clean up the downloaded PDF
        os.remove(pdf_filename)
        logging.info(f"Successfully removed {pdf_filename}")

        # A basic text cleaning step
        cleaned_text = " ".join(text.split())

        logging.info(f"Successfully extracted and cleaned text for paper {paper_id}.")
        return cleaned_text

    except Exception as e:
        logging.error(f"An error occurred while fetching or processing the paper text for {paper_id}: {e}")
        # Clean up if the file was created before the error
        if os.path.exists(pdf_filename):
            os.remove(pdf_filename)
            logging.info(f"Cleaned up partially downloaded file: {pdf_filename}")
        return None


if __name__ == '__main__':
    print("--- Running manual test of fetch_new_papers() ---")
    papers_data = fetch_new_papers()
    import json
    print(json.dumps(papers_data, indent=2))

    if papers_data:
        print("\n--- Running manual test of fetch_paper_text() ---")
        test_paper_id = papers_data[0]['id']
        full_text = fetch_paper_text(test_paper_id)
        if full_text:
            print(f"Successfully fetched text for paper {test_paper_id}.")
            print(f"First 500 characters: {full_text[:500]}...")
        else:
            print(f"Failed to fetch text for paper {test_paper_id}.")

    print("--- Manual test finished ---")