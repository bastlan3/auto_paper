import arxiv
import logging

logging.basicConfig(level=logging.INFO)

def fetch_new_papers():
    """Fetches the 5 most recent papers from the cs.AI category."""
    print("Executing scheduled job: Fetching new papers...")
    try:
        search = arxiv.Search(
            query="cat:cs.AI", # Category: Artificial Intelligence
            max_results=5,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )

        papers = []
        for result in search.results():
            paper_data = {
                "id": result.entry_id,
                "title": result.title,
                "published": result.published,
                "abstract": result.summary
            }
            papers.append(paper_data)
            print(f"--- Found Paper ---")
            print(f"ID: {result.entry_id}")
            print(f"Title: {result.title}")
            print(f"Published: {result.published}")
        return papers

    except Exception as e:
        print(f"An error occurred while fetching from arXiv: {e}")
        return []

if __name__ == '__main__':
    # To test immediately without waiting for the schedule, just call the function directly.
    print("--- Running manual test of fetch_new_papers() ---")
    fetch_new_papers()
    print("--- Manual test finished ---")