import React, { useState, useEffect } from 'react';
import Link from 'next/link';

type BuildStep = 'idle' | 'generatingPlan' | 'planReady' | 'building' | 'buildComplete' | 'error';

// Icons remain the same
const CheckCircleIcon = () => <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5 text-green-500"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clipRule="evenodd" /></svg>;
const LoadingSpinner = () => <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-accent"></div>;

interface BuildCodeTabProps {
  paperId: string;
  paperTitle: string;
}

const BuildCodeTab: React.FC<BuildCodeTabProps> = ({ paperId, paperTitle }) => {
    const [step, setStep] = useState<BuildStep>('idle');
    const [repoName, setRepoName] = useState('');
    const [implementationPlan, setImplementationPlan] = useState('');
    const [buildStatus, setBuildStatus] = useState({ repo: '', jules: '' });
    const [repoUrl, setRepoUrl] = useState('');
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Sanitize paper title to create a default repo name
        const sanitized = paperTitle.replace(/[^a-zA-Z0-9\s-]/g, '').replace(/\s+/g, '-');
        setRepoName(sanitized);
    }, [paperTitle]);

    const handleGeneratePlan = async () => {
        setStep('generatingPlan');
        setError(null);
        try {
            const res = await fetch(`/api/papers/${paperId}/implementation-plan`, { method: 'POST' });
            if (!res.ok) {
                throw new Error('Failed to generate implementation plan.');
            }
            const data = await res.json();
            setImplementationPlan(data.plan);
            setStep('planReady');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unknown error occurred.');
            setStep('error');
        }
    };

    const handleBuildCode = async () => {
        setStep('building');
        setError(null);
        setBuildStatus({ repo: 'inProgress', jules: '' });

        try {
            const res = await fetch(`/api/papers/${paperId}/build-code`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ repo_name: repoName, implementation_plan: implementationPlan }),
            });
            if (!res.ok) {
                throw new Error('Failed to create repository and start build.');
            }
            const data = await res.json();
            setRepoUrl(data.repo_url);
            setBuildStatus({ repo: 'done', jules: 'done' });
            setStep('buildComplete');

        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unknown error occurred.');
            setStep('error');
        }
    };

    return (
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-6">
            {step === 'idle' && (
                <button onClick={handleGeneratePlan} className="w-full bg-accent text-white font-sans font-semibold py-2 px-4 rounded-lg hover:bg-blue-800">
                    Generate Implementation Plan
                </button>
            )}

            {step === 'generatingPlan' && (
                <div className="flex items-center justify-center gap-2 text-text-secondary"><LoadingSpinner /><span>Generating plan...</span></div>
            )}

            {step === 'planReady' && (
                <div>
                    <h3 className="text-lg font-sans font-semibold text-text-primary mb-2">Implementation Plan</h3>
                    <pre className="bg-gray-50 p-4 rounded-lg text-sm font-mono whitespace-pre-wrap overflow-x-auto"><code>{implementationPlan}</code></pre>
                </div>
            )}

            {(step === 'planReady' || step === 'building' || step === 'buildComplete') && (
                <div className="border-t border-gray-200 pt-6">
                    <div className="flex flex-col sm:flex-row items-center gap-4">
                        <input
                            type="text"
                            value={repoName}
                            onChange={(e) => setRepoName(e.target.value)}
                            className="flex-grow w-full px-4 py-2 border border-gray-300 rounded-lg"
                            disabled={step === 'building' || step === 'buildComplete'}
                        />
                        <button
                            onClick={handleBuildCode}
                            className="w-full sm:w-auto bg-accent text-white font-sans font-semibold py-2 px-4 rounded-lg disabled:bg-gray-400"
                            disabled={step === 'building' || step === 'buildComplete'}
                        >
                            {step === 'building' ? 'Building...' : 'Create GitHub Repo & Build Code'}
                        </button>
                    </div>
                </div>
            )}

            {step === 'building' && (
                <div className="space-y-3 mt-4">
                    <div className="flex items-center gap-2"><LoadingSpinner /><p>Creating GitHub repository...</p></div>
                </div>
            )}

            {step === 'buildComplete' && (
                 <div className="space-y-3 mt-4 text-green-600">
                    <div className="flex items-center gap-2"><CheckCircleIcon /><p>Repository created: <Link href={repoUrl} target="_blank" className="font-semibold underline">{repoUrl}</Link></p></div>
                    <div className="flex items-center gap-2"><CheckCircleIcon /><p>JULES build process initiated successfully.</p></div>
                </div>
            )}

            {step === 'error' && <p className="text-red-500 text-center mt-4">{error}</p>}
        </div>
    );
};

export default BuildCodeTab;