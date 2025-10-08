"use client";

import Header from "@/components/Header";
import Link from "next/link";
import React, { useState, useEffect } from 'react';

// Import the tab components
import VocalSummaryTab from '@/components/VocalSummaryTab';
import DiscussTab from '@/components/DiscussTab';
import BuildCodeTab from '@/components/BuildCodeTab';

interface Paper {
  id: string;
  title: string;
  authors: string[];
  publishedDate: string;
  category: string;
  summary: string;
  abstract: string;
}

const PaperPage = ({ params }: { params: { id: string } }) => {
    const [paper, setPaper] = useState<Paper | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('Vocal Summary');

    useEffect(() => {
        const fetchPaper = async () => {
            try {
                // Use the new, more efficient endpoint to fetch a single paper
                const res = await fetch(`http://localhost:3000/api/papers/${params.id}`, { cache: 'no-store' });
                if (!res.ok) {
                    throw new Error('Failed to fetch paper details');
                }
                const paper: Paper = await res.json();
                setPaper(paper);
            } catch (error) {
                console.error("Error fetching paper details:", error);
                setPaper(null); // Ensure paper is null on error
            } finally {
                setLoading(false);
            }
        };

        fetchPaper();
    }, [params.id]);

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <p>Loading paper details...</p>
            </div>
        );
    }

    if (!paper) {
        return (
            <div className="min-h-screen bg-background">
                <Header />
                <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <h1 className="text-2xl font-bold text-center">Paper not found</h1>
                    <p className="text-center text-text-secondary">Could not find a paper with the ID: {params.id}</p>
                </main>
            </div>
        );
    }

    const tabs = ['Vocal Summary', 'Discuss with Paper', 'Build the Code'];

    return (
        <div className="min-h-screen bg-background">
            <Header />
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex flex-col lg:flex-row gap-8">
                    {/* Left Panel: The Source */}
                    <div className="w-full lg:w-1/3 bg-white border border-gray-200 rounded-lg p-6 h-fit shadow-md">
                        <h1 className="text-2xl font-bold font-sans text-text-primary mb-3">{paper.title}</h1>
                        <p className="text-md font-serif italic text-text-secondary mb-4">{paper.authors.join(', ')}</p>
                        <div className="text-sm text-text-secondary mb-4">
                            <span>Published: {paper.publishedDate}</span>
                            <span className="mx-2">|</span>
                            <span>Category: {paper.category}</span>
                        </div>
                        <h2 className="text-xl font-sans font-semibold text-text-primary mt-6 mb-2">Abstract</h2>
                        <p className="font-serif text-text-primary leading-relaxed">{paper.abstract}</p>
                        <Link href={`http://arxiv.org/abs/${paper.id}`} target="_blank">
                            <button className="mt-6 w-full bg-accent text-white font-sans font-semibold py-2 px-4 rounded-lg hover:bg-blue-800 transition-colors">
                                View on arXiv
                            </button>
                        </Link>
                    </div>

                    {/* Right Panel: The AI Toolkit */}
                    <div className="w-full lg:w-2/3">
                        <div className="border-b border-gray-200">
                            <nav className="-mb-px flex space-x-6" aria-label="Tabs">
                                {tabs.map((tabName) => (
                                    <button
                                        key={tabName}
                                        onClick={() => setActiveTab(tabName)}
                                        className={`whitespace-nowrap py-4 px-1 border-b-2 font-sans font-medium text-md ${
                                            activeTab === tabName
                                                ? 'border-accent text-accent'
                                                : 'border-transparent text-text-secondary hover:text-gray-700 hover:border-gray-300'
                                        }`}
                                    >
                                        {tabName}
                                    </button>
                                ))}
                            </nav>
                        </div>
                        <div className="mt-4">
                            {activeTab === 'Vocal Summary' && <VocalSummaryTab paperId={paper.id} />}
                            {activeTab === 'Discuss with Paper' && <DiscussTab paperId={paper.id} />}
                            {activeTab === 'Build the Code' && <BuildCodeTab paperId={paper.id} paperTitle={paper.title} />}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default PaperPage;