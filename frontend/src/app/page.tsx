import Header from "@/components/Header";
import PaperCard from "@/components/PaperCard";
import Link from "next/link";

interface Paper {
  id: string;
  title: string;
  authors: string[];
  publishedDate: string;
  category: string;
  summary: string;
  abstract: string;
}

async function getPapers(): Promise<Paper[]> {
  try {
    // This fetch call will be proxied to http://localhost:8000/api/papers
    // by the Next.js development server.
    const res = await fetch('http://localhost:3000/api/papers', {
      cache: 'no-store', // Ensure fresh data on every request
    });

    if (!res.ok) {
      console.error("Failed to fetch papers:", res.statusText);
      return [];
    }
    return res.json();
  } catch (error) {
    console.error("An error occurred while fetching papers:", error);
    return [];
  }
}

const getCurrentDate = () => {
  return new Date().toLocaleDateString('en-CA', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
};

export default async function Home() {
  const papers = await getPapers();

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold font-sans text-text-primary mb-6">
          Today's Papers: {getCurrentDate()}
        </h1>
        {papers.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {papers.map((paper) => (
              <Link href={`/paper/${paper.id}`} key={paper.id}>
                <PaperCard paper={paper} />
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-10">
            <p className="text-text-secondary">Could not load papers at this time. The backend server may be offline.</p>
          </div>
        )}
      </main>
    </div>
  );
}