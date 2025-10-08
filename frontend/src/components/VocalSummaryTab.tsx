import React, { useState } from 'react';

// Icons remain the same...
const PlayIcon = () => <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-8 h-8"><path fillRule="evenodd" d="M4.5 5.653c0-1.426 1.529-2.33 2.779-1.643l11.54 6.647c1.295.742 1.295 2.545 0 3.286L7.279 20.99c-1.25.717-2.779-.217-2.779-1.643V5.653z" clipRule="evenodd" /></svg>;
const PauseIcon = () => <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-8 h-8"><path fillRule="evenodd" d="M6.75 5.25a.75.75 0 00-.75.75v12c0 .414.336.75.75.75h3a.75.75 0 00.75-.75v-12a.75.75 0 00-.75-.75h-3zm7.5 0a.75.75 0 00-.75.75v12c0 .414.336.75.75.75h3a.75.75 0 00.75-.75v-12a.75.75 0 00-.75-.75h-3z" clipRule="evenodd" /></svg>;

interface VocalSummaryTabProps {
  paperId: string;
}

const VocalSummaryTab: React.FC<VocalSummaryTabProps> = ({ paperId }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [script, setScript] = useState<any[] | null>(null);

  const handleGenerateAudio = async () => {
    setIsLoading(true);
    setError(null);
    setScript(null);
    try {
      const res = await fetch(`/api/papers/${paperId}/vocal-summary`, { method: 'POST' });
      if (!res.ok) {
        throw new Error('Failed to generate audio script.');
      }
      const data = await res.json();
      // In a real app, you'd parse the JSON string in data.script
      setScript(data.script ? JSON.parse(data.script) : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h3 className="text-xl font-sans font-semibold text-text-primary mb-4">Two-Voice Audio Summary</h3>

      <div className="w-full bg-gray-100 p-4 rounded-lg">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="text-white bg-accent rounded-full p-3 hover:bg-blue-800 transition-colors focus:outline-none disabled:bg-gray-400"
            disabled={!script}
          >
            {isPlaying ? <PauseIcon /> : <PlayIcon />}
          </button>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-accent h-2 rounded-full"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="mt-4 text-center">
        {isLoading ? (
          <p className="text-text-secondary animate-pulse">Generating Audio Script...</p>
        ) : (
          <button
            onClick={handleGenerateAudio}
            className="text-accent font-sans font-medium hover:underline"
          >
            Generate Audio Script
          </button>
        )}
      </div>

      {error && <p className="text-red-500 text-center mt-4">{error}</p>}

      {script && (
        <div className="mt-6 space-y-2">
            <h4 className="font-sans font-semibold">Generated Script:</h4>
            <pre className="bg-gray-50 p-4 rounded-lg text-sm font-mono whitespace-pre-wrap overflow-x-auto">
                <code>{JSON.stringify(script, null, 2)}</code>
            </pre>
        </div>
      )}
    </div>
  );
};

export default VocalSummaryTab;