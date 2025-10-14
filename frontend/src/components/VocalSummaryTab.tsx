import React, { useState, useRef, useEffect } from 'react';

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
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Cleanup audio URL when component unmounts
  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  // Update progress as audio plays
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateProgress = () => {
      const percentage = (audio.currentTime / audio.duration) * 100;
      setProgress(percentage);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      setProgress(0);
    };

    audio.addEventListener('timeupdate', updateProgress);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', updateProgress);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [audioUrl]);

  const handleGenerateAudio = async () => {
    setIsLoading(true);
    setError(null);
    setAudioUrl(null);
    setProgress(0);
    
    try {
      // Fetch the audio file (not JSON!)
      const res = await fetch(`/api/papers/${paperId}/vocal-summary`, { 
        method: 'POST'
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Failed to generate audio summary: ${errorText}`);
      }
      
      // Get the audio file as a blob
      const audioBlob = await res.blob();
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);
      
      // Set up audio element
      if (audioRef.current) {
        audioRef.current.src = url;
      }
    } catch (err) {
      console.error('Error generating audio:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  const togglePlayPause = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h3 className="text-xl font-sans font-semibold text-text-primary mb-4">Two-Voice Audio Summary</h3>
      
      <p className="text-text-secondary mb-4">
        Generate a 5-minute conversational audio summary of this paper, featuring an interview-style dialogue between a host and the author.
      </p>

      <div className="w-full bg-gray-100 p-4 rounded-lg">
        <div className="flex items-center gap-4">
          <button
            onClick={togglePlayPause}
            className="text-white bg-accent rounded-full p-3 hover:bg-blue-800 transition-colors focus:outline-none disabled:bg-gray-400"
            disabled={!audioUrl || isLoading}
          >
            {isPlaying ? <PauseIcon /> : <PlayIcon />}
          </button>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-accent h-2 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="mt-4 text-center">
        {isLoading ? (
          <div className="space-y-2">
            <p className="text-text-secondary animate-pulse">Generating Audio Summary...</p>
            <p className="text-sm text-text-secondary">This may take several minutes. Please wait.</p>
          </div>
        ) : audioUrl ? (
          <p className="text-green-600 font-medium">✓ Audio ready! Click play to listen.</p>
        ) : (
          <button
            onClick={handleGenerateAudio}
            className="text-accent font-sans font-medium hover:underline"
          >
            Generate Audio Summary
          </button>
        )}
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600 text-center">{error}</p>
        </div>
      )}

      {/* Hidden audio element */}
      <audio ref={audioRef} className="hidden" />
    </div>
  );
};

export default VocalSummaryTab;