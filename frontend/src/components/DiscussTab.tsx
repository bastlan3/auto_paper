import React, { useState } from 'react';

const SendIcon = () => <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5"><path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" /></svg>;

interface DiscussTabProps {
  paperId: string;
}

interface Message {
    id: number;
    sender: 'ai' | 'user';
    text: string;
}

const DiscussTab: React.FC<DiscussTabProps> = ({ paperId }) => {
    const [messages, setMessages] = useState<Message[]>([
        { id: 1, sender: 'ai', text: 'Hello! Ask me anything about the abstract of this paper.' },
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        const userMessage = inputValue.trim();
        if (!userMessage || isLoading) return;

        // Add user message to the chat
        setMessages(prev => [...prev, { id: Date.now(), sender: 'user', text: userMessage }]);
        setInputValue('');
        setIsLoading(true);

        try {
            const res = await fetch(`/api/papers/${paperId}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: userMessage }),
            });

            if (!res.ok) {
                throw new Error('The AI is taking a break. Please try again later.');
            }

            const data = await res.json();
            setMessages(prev => [...prev, { id: Date.now() + 1, sender: 'ai', text: data.answer }]);

        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred.';
            setMessages(prev => [...prev, { id: Date.now() + 1, sender: 'ai', text: errorMessage }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="bg-white border border-gray-200 rounded-lg p-6 flex flex-col h-[60vh]">
            {/* Conversation History */}
            <div className="flex-grow space-y-4 overflow-y-auto pr-2 mb-4">
                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex items-start gap-3 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        {message.sender === 'ai' && (
                             <div className="w-8 h-8 rounded-full bg-accent text-white flex items-center justify-center font-bold font-sans text-sm flex-shrink-0">AI</div>
                        )}
                        <div
                            className={`max-w-md rounded-2xl px-4 py-2 shadow-sm ${
                                message.sender === 'user'
                                    ? 'bg-accent text-white rounded-br-none'
                                    : 'bg-gray-100 text-text-primary rounded-bl-none'
                            }`}
                        >
                            <p className="font-serif">{message.text}</p>
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex items-start gap-3 justify-start">
                        <div className="w-8 h-8 rounded-full bg-accent text-white flex items-center justify-center font-bold font-sans text-sm flex-shrink-0">AI</div>
                        <div className="max-w-md rounded-2xl px-4 py-2 shadow-sm bg-gray-100 text-text-primary rounded-bl-none animate-pulse">
                            <p className="font-serif">Thinking...</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Text Input */}
            <div className="mt-auto pt-4 border-t">
                <form onSubmit={handleSendMessage} className="flex items-center gap-2">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder="Ask a question about the paper..."
                        className="flex-grow w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-accent"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        className="bg-accent text-white rounded-full p-3 hover:bg-blue-800 transition-colors focus:outline-none disabled:bg-gray-400"
                        aria-label="Send message"
                        disabled={isLoading}
                    >
                        <SendIcon />
                    </button>
                </form>
            </div>
        </div>
    );
};

export default DiscussTab;