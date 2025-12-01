
import React, { useState, useEffect, useRef } from 'react';
import { Chat } from '@google/genai';
import { createChatSession } from '../lib/gemini.ts';
import { ChatMessage } from '../types.ts';
import { Button } from './ui/Button.tsx';
import { Input } from './ui/Input.tsx';
import { Card } from './ui/Card.tsx';
import { Spinner } from './ui/Spinner.tsx';
import { PaperAirplaneIcon, UserCircleIcon, CpuChipIcon, BookOpenIcon, CheckCircleIcon, CircleIcon } from './icons/Icons.tsx';
import { AVAILABLE_DATA_SOURCES } from '../lib/dataSources.ts';

const AgentAssistant: React.FC = () => {
    const [chatSession, setChatSession] = useState<Chat | null>(null);
    const [history, setHistory] = useState<ChatMessage[]>([]);
    const [userInput, setUserInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [selectedSources, setSelectedSources] = useState<{ [key: string]: boolean }>({});
    const chatContainerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const initChat = () => {
            const session = createChatSession();
            setChatSession(session);
            setHistory([
                { role: 'model', content: 'Hello. I am your Transfer Pricing Assistant. How may I help you with your ad-hoc questions today?' }
            ]);
        };
        initChat();
    }, []);

    useEffect(() => {
        chatContainerRef.current?.scrollTo(0, chatContainerRef.current.scrollHeight);
    }, [history]);

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!userInput.trim() || isLoading || !chatSession) return;

        const newUserMessage: ChatMessage = { role: 'user', content: userInput };
        setHistory(prev => [...prev, newUserMessage]);
        setUserInput('');
        setIsLoading(true);

        let context = '';
        const selectedSourceNames: string[] = [];
        AVAILABLE_DATA_SOURCES.forEach(source => {
            if (selectedSources[source.id]) {
                context += `\n\n--- START OF DOCUMENT: ${source.name} ---\n${source.content}\n--- END OF DOCUMENT: ${source.name} ---\n`;
                selectedSourceNames.push(source.name);
            }
        });

        const promptWithContext = context
            ? `Based on the following documents (${selectedSourceNames.join(', ')}), please answer the user's question.\n${context}\n\nUser Question: ${userInput}`
            : userInput;

        try {
            const stream = await chatSession.sendMessageStream({ message: promptWithContext });
            
            let modelResponse = '';
            setHistory(prev => [...prev, { role: 'model', content: '' }]);

            for await (const chunk of stream) {
                modelResponse += chunk.text;
                setHistory(prev => {
                    const newHistory = [...prev];
                    newHistory[newHistory.length - 1].content = modelResponse;
                    return newHistory;
                });
            }
        } catch (error) {
            console.error("Error sending message:", error);
            setHistory(prev => [...prev, { role: 'model', content: 'Sorry, I encountered an error. Please try again.' }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto h-full flex flex-col">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-slate-800">Agent Assistant</h1>
                <p className="text-slate-600 mt-1">Engage in a conversation for quick answers and analysis.</p>
            </header>

            <Card className="mb-6">
                <div className="p-6">
                    <h3 className="font-semibold text-lg text-slate-800 mb-4 flex items-center">
                        <BookOpenIcon className="h-5 w-5 mr-2 text-slate-500" />
                        Contextual Sources (Optional)
                    </h3>
                    <p className="text-sm text-slate-500 mb-4">Select internal documents to provide context for your question.</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {AVAILABLE_DATA_SOURCES.map(source => {
                            const isSelected = !!selectedSources[source.id];
                            return (
                                <button
                                    key={source.id}
                                    onClick={() => setSelectedSources(prev => ({ ...prev, [source.id]: !prev[source.id] }))}
                                    className={`w-full text-left p-3 border rounded-lg flex items-center transition-colors ${isSelected ? 'bg-sky-50 border-sky-300' : 'bg-white hover:bg-slate-50'}`}
                                >
                                    {isSelected ? <CheckCircleIcon className="h-5 w-5 text-sky-600 mr-3 flex-shrink-0" /> : <CircleIcon className="h-5 w-5 text-slate-400 mr-3 flex-shrink-0" />}
                                    <span className="text-sm font-medium text-slate-700 truncate" title={source.name}>{source.name}</span>
                                </button>
                            );
                        })}
                    </div>
                </div>
            </Card>

            <Card className="flex-1 flex flex-col overflow-hidden">
                <div ref={chatContainerRef} className="flex-1 p-6 space-y-6 overflow-y-auto bg-slate-50">
                    {history.map((msg, index) => (
                        <div key={index} className={`flex items-start gap-4 ${msg.role === 'user' ? 'justify-end' : ''}`}>
                            {msg.role === 'model' && <CpuChipIcon className="h-8 w-8 text-slate-500 flex-shrink-0 mt-1" />}
                            <div className={`max-w-lg px-4 py-3 rounded-xl ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-white border border-slate-200 text-slate-700'}`}>
                                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                            </div>
                            {msg.role === 'user' && <UserCircleIcon className="h-8 w-8 text-slate-500 flex-shrink-0 mt-1" />}
                        </div>
                    ))}
                    {isLoading && history[history.length - 1]?.role === 'user' && (
                         <div className="flex items-start gap-4">
                            <CpuChipIcon className="h-8 w-8 text-slate-500 flex-shrink-0 mt-1" />
                            <div className="max-w-lg px-4 py-3 rounded-xl bg-white border border-slate-200 text-slate-700">
                                <Spinner />
                            </div>
                        </div>
                    )}
                </div>
                <div className="p-4 border-t border-slate-200 bg-white">
                    <form onSubmit={handleSendMessage} className="flex items-center gap-4">
                        <Input
                            type="text"
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            placeholder="Ask a question, e.g., 'What is the penalty for late filing in Italy?'"
                            className="flex-1"
                            disabled={isLoading}
                        />
                        <Button type="submit" disabled={isLoading || !userInput.trim()}>
                            <PaperAirplaneIcon className="h-5 w-5" />
                        </Button>
                    </form>
                </div>
            </Card>
        </div>
    );
};

export default AgentAssistant;
