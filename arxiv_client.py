import arxiv
import logging
from datetime import datetime

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

if __name__ == '__main__':
    print("--- Running manual test of fetch_new_papers() ---")
    papers_data = fetch_new_papers()
    import json
    print(json.dumps(papers_data, indent=2))
    print("--- Manual test finished ---")